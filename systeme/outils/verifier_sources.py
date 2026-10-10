#!/usr/bin/env python3
"""Vérification du registre de vérité (sources/REGISTRE.csv).

Usages :
  python3 systeme/outils/verifier_sources.py
      vérifie tout le registre et écrit un rapport dans sources/rapports/
  python3 systeme/outils/verifier_sources.py --doi 10.1509/jm.15.0420 --id Lemon2016
      affiche une ligne prête à ajouter au registre (niveau N1)
  python3 systeme/outils/verifier_sources.py --resume 10.1509/jm.15.0420 --id Lemon2016
      télécharge le résumé brut des auteurs (OpenAlex, sinon Crossref) dans sources/resumes/

Bibliothèque standard de Python 3.9 uniquement. Seuls des DOI et des URL publiques sont envoyés
(avec l'e-mail de contact de systeme/config.json s'il est réglé).
"""
import argparse
import csv
import datetime
import difflib
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from commun import RACINE, avec_contact

REGISTRE = os.path.join(RACINE, "sources", "REGISTRE.csv")
RESUMES = os.path.join(RACINE, "sources", "resumes")
RAPPORTS = os.path.join(RACINE, "sources", "rapports")
ENTETES = {"User-Agent": "kit-memoire-verification/1.0 (verification bibliographique; python-urllib)"}
COLONNES = ["id", "type", "auteurs", "annee", "titre", "revue_ou_editeur", "volume", "numero", "pages",
            "doi", "url", "niveau", "methode_verification", "date_verification", "classement_revue",
            "acces_texte", "statut", "usage", "notes"]
AUJOURDHUI = datetime.date.today().isoformat()


def obtenir(url, json_attendu=True, delai=25):
    req = urllib.request.Request(avec_contact(url), headers=ENTETES)
    with urllib.request.urlopen(req, timeout=delai) as r:
        donnees = r.read()
    time.sleep(0.2)
    texte = donnees.decode("utf-8", "replace")
    return json.loads(texte) if json_attendu else texte


def normaliser(texte):
    texte = unicodedata.normalize("NFKD", texte or "")
    texte = "".join(c for c in texte if not unicodedata.combining(c)).lower()
    texte = re.sub(r"<[^>]+>", " ", texte)
    texte = re.sub(r"[^a-z0-9]+", " ", texte)
    return " ".join(texte.split())


def similarite(a, b):
    return difflib.SequenceMatcher(None, normaliser(a), normaliser(b)).ratio()


def initiales(prenom):
    return " ".join(p[0] + "." for p in re.split(r"[\s]+", prenom.replace("-", " -").strip()) if p and p[0].isalpha())


def crossref(doi):
    m = obtenir("https://api.crossref.org/works/" + urllib.parse.quote(doi))["message"]
    date = m.get("published-print") or m.get("published-online") or m.get("issued") or {}
    annee = (date.get("date-parts") or [[None]])[0][0]
    auteurs = ", ".join("{} {}".format(a.get("family", ""), initiales(a.get("given", ""))).strip()
                        for a in m.get("author", []))
    return {
        "titre": (m.get("title") or [""])[0],
        "annee": str(annee or ""),
        "revue": (m.get("container-title") or [""])[0],
        "volume": m.get("volume", ""),
        "numero": m.get("issue", ""),
        "pages": m.get("page", "") or m.get("article-number", ""),
        "auteurs": auteurs,
        "type": m.get("type", ""),
    }


def arxiv(identifiant):
    xml = obtenir("http://export.arxiv.org/api/query?id_list=" + identifiant, json_attendu=False)
    morceaux = xml.split("<entry>")
    if len(morceaux) < 2:
        raise ValueError("identifiant arXiv introuvable")
    e = morceaux[1]
    titre = re.sub(r"\s+", " ", re.search(r"<title>(.*?)</title>", e, re.S).group(1)).strip()
    annee = re.search(r"<published>(\d{4})", e).group(1)
    return {"titre": titre, "annee": annee}


def statut_url(url):
    try:
        req = urllib.request.Request(url, headers=ENTETES)
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        # Le Python d'Apple ne gère pas certains sites au chiffrement récent : on retente avec curl (déjà présent sur macOS).
        try:
            import subprocess
            code = subprocess.run(["curl", "-s", "-o", "/dev/null", "-L", "-A", ENTETES["User-Agent"], "-w", "%{http_code}",
                                   "--max-time", "25", url], capture_output=True, text=True).stdout.strip()
            return int(code), "(via curl)"
        except Exception:
            return None, str(e)[:80]


def lire_registre():
    with open(REGISTRE, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def verifier_registre():
    resultats = []
    lignes = lire_registre()
    if not lignes:
        print("Registre vide : rien à vérifier.")
        return
    for l in lignes:
        ident, doi, url = l["id"], l["doi"].strip(), l["url"].strip()
        try:
            if doi:
                meta = crossref(doi)
                s = similarite(l["titre"], meta["titre"])
                ecarts = []
                if s < 0.85:
                    ecarts.append("titre différent ({:.0%}) : « {} »".format(s, meta["titre"][:90]))
                if l["annee"] and meta["annee"] and l["annee"] != meta["annee"]:
                    ecarts.append("année registre {} / Crossref {}".format(l["annee"], meta["annee"]))
                if l["volume"] and meta["volume"] and l["volume"] != meta["volume"]:
                    ecarts.append("volume registre {} / Crossref {}".format(l["volume"], meta["volume"]))
                resultats.append((ident, "Crossref", "OK" if not ecarts else "ÉCART", "; ".join(ecarts)))
            elif "arxiv.org/abs/" in url:
                meta = arxiv(url.rstrip("/").split("arxiv.org/abs/")[1])
                s = similarite(l["titre"], meta["titre"])
                ecart = "" if s >= 0.85 else "titre arXiv actuel : « {} »".format(meta["titre"][:90])
                resultats.append((ident, "arXiv", "OK" if not ecart else "ÉCART", ecart))
            elif url:
                code, err = statut_url(url)
                if code == 200:
                    resultats.append((ident, "URL", "OK", ""))
                elif code in (401, 403, 429):
                    resultats.append((ident, "URL", "À VÉRIFIER À LA MAIN",
                                      "le site refuse les robots (code {})".format(code)))
                else:
                    resultats.append((ident, "URL", "ÉCHEC", "code {} {}".format(code, err)))
            else:
                resultats.append((ident, "aucune", "ÉCHEC", "ni DOI ni URL"))
        except Exception as e:
            resultats.append((ident, "erreur", "ÉCHEC", str(e)[:100]))
    compte = {}
    for r in resultats:
        compte[r[2]] = compte.get(r[2], 0) + 1
    os.makedirs(RAPPORTS, exist_ok=True)
    chemin = os.path.join(RAPPORTS, "verification_{}.md".format(AUJOURDHUI))
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("# Vérification du registre ({})\n\n".format(AUJOURDHUI))
        f.write("Bilan : " + ", ".join("{} {}".format(v, k) for k, v in sorted(compte.items())) + "\n\n")
        f.write("| Source | Vérifiée via | Verdict | Détail |\n|---|---|---|---|\n")
        for r in resultats:
            f.write("| {} | {} | {} | {} |\n".format(*[x.replace("|", "/") for x in r]))
    print("Registre : {} sources. Bilan : {}".format(len(resultats), compte))
    for r in resultats:
        if r[2] != "OK":
            print(" - {} [{}] {} {}".format(*r))
    print("Rapport : " + os.path.relpath(chemin, RACINE))


def ligne_pour_doi(doi, ident):
    m = crossref(doi)
    valeurs = {
        "id": ident, "type": "article" if m["type"] == "journal-article" else m["type"],
        "auteurs": m["auteurs"], "annee": m["annee"], "titre": m["titre"], "revue_ou_editeur": m["revue"],
        "volume": m["volume"], "numero": m["numero"], "pages": m["pages"], "doi": doi,
        "url": "https://doi.org/" + doi, "niveau": "N1", "methode_verification": "Crossref API",
        "date_verification": AUJOURDHUI, "classement_revue": "a_verifier",
        "acces_texte": "a_determiner", "statut": "VERIFIE", "usage": "", "notes": "",
    }
    print(";".join(str(valeurs[c]).replace(";", ",").replace("\n", " ") for c in COLONNES))


def resume(doi, ident):
    texte, origine = "", ""
    try:
        w = obtenir("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi))
        index = w.get("abstract_inverted_index")
        if index:
            positions = {}
            for mot, pos in index.items():
                for p in pos:
                    positions[p] = mot
            texte = " ".join(positions[i] for i in sorted(positions))
            origine = "OpenAlex (abstract_inverted_index) " + w.get("id", "")
    except Exception:
        pass
    if not texte:
        try:
            m = obtenir("https://api.crossref.org/works/" + urllib.parse.quote(doi))["message"]
            if m.get("abstract"):
                texte = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", m["abstract"])).split())
                origine = "Crossref (champ abstract)"
        except Exception:
            pass
    if not texte:
        print("Aucun résumé brut disponible pour {} : la source reste au niveau N1.".format(doi))
        return 1
    os.makedirs(RESUMES, exist_ok=True)
    chemin = os.path.join(RESUMES, "{}.txt".format(ident))
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("Source : {}\nDOI : {}\nOrigine du texte : {}\nTéléchargé le : {}\n"
                "Texte brut tel que fourni par la base, sans reformulation.\n\n{}\n"
                .format(ident, doi, origine, AUJOURDHUI, texte))
    print("Résumé brut enregistré : {} ({} mots, {})".format(os.path.relpath(chemin, RACINE), len(texte.split()), origine))
    return 0


def main():
    ap = argparse.ArgumentParser(description="Vérification du registre de vérité.")
    ap.add_argument("--doi", help="affiche une ligne de registre (N1) pour ce DOI")
    ap.add_argument("--resume", help="DOI dont il faut télécharger le résumé brut")
    ap.add_argument("--id", default="", help="identifiant de la source, NomAnnée (ex. Lemon2016)")
    a = ap.parse_args()
    if a.doi:
        ligne_pour_doi(a.doi, a.id)
    elif a.resume:
        if not a.id:
            sys.exit("--id est obligatoire avec --resume")
        sys.exit(resume(a.resume, a.id))
    else:
        verifier_registre()


if __name__ == "__main__":
    main()
