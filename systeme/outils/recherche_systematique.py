#!/usr/bin/env python3
"""Recherche systématique reproductible dans OpenAlex (protocole : systeme/PROTOCOLE_TRI.md).

Usages :
  python3 systeme/outils/recherche_systematique.py sources/rapports/recherche_2026-10-10
      lance les requêtes de <dossier>/protocole.json et écrit dans <dossier> :
      brut_<requête>.jsonl.gz (notices brutes, hors git), corpus.csv (notices fusionnées et dédoublonnées,
      résumé reconstitué, triées par nombre de citations) et flux.json (effectifs à chaque étape, URL exactes
      des requêtes, études témoins retrouvées ou manquantes).
  python3 systeme/outils/recherche_systematique.py <dossier> --sans-telechargement
      refait la fusion à partir des notices brutes déjà téléchargées.
  python3 systeme/outils/recherche_systematique.py <dossier> --echantillon 25 --graine 7
      tire au hasard des notices du corpus pour le second trieur humain (echantillon_humain.csv, sans
      aucune décision de l'IA). La graine permet de refaire exactement le même tirage.

Seules les requêtes (et l'e-mail de contact de systeme/config.json s'il est réglé) sont envoyées à OpenAlex.
Bibliothèque standard de Python uniquement.
"""
import argparse
import csv
import datetime
import gzip
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request

from commun import avec_contact

BASE = "https://api.openalex.org/works"
ENTETES = {"User-Agent": "kit-memoire-recherche/1.0 (recherche systematique; python-urllib)"}
COLONNES = ["id", "doi", "annee", "titre", "revue", "type", "langue", "citations", "acces_libre",
            "resume_present", "resume", "requetes"]


def obtenir(url):
    for essai in range(5):
        try:
            req = urllib.request.Request(avec_contact(url), headers=ENTETES)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            print("  nouvel essai après erreur : {}".format(str(e)[:100]), file=sys.stderr)
            time.sleep(3 * (essai + 1))
    raise SystemExit("Échec répété de la requête : " + url)


def doi_court(doi):
    return (doi or "").lower().replace("https://doi.org/", "").strip()


def resume(w):
    index = w.get("abstract_inverted_index")
    if not index:
        return ""
    positions = {p: mot for mot, ps in index.items() for p in ps}
    return " ".join(positions[i] for i in sorted(positions))


def telecharger(dossier, protocole):
    comptes = {}
    maximum = int(protocole.get("maximum_par_requete", 2000))
    commun = protocole.get("filtre_commun", "").strip()
    for r in protocole["requetes"]:
        nom, filtre = r["nom"], "{}:{}".format(r["champ"], r["valeur"])
        if commun:
            filtre += "," + commun
        curseur, notices, total, url_requete = "*", [], None, ""
        print("{} ...".format(nom))
        while curseur and len(notices) < maximum:
            params = {"filter": filtre, "per-page": "200", "cursor": curseur}
            d = obtenir(BASE + "?" + urllib.parse.urlencode(params))
            if total is None:
                total = d["meta"]["count"]
                url_requete = BASE + "?" + urllib.parse.urlencode({"filter": filtre})
            if not d["results"]:
                break
            notices += d["results"]
            curseur = d["meta"].get("next_cursor")
        notices = notices[:maximum]
        with gzip.open(os.path.join(dossier, "brut_{}.jsonl.gz".format(nom)), "wt", encoding="utf-8") as f:
            for w in notices:
                f.write(json.dumps(w, ensure_ascii=False) + "\n")
        comptes[nom] = {"filtre": filtre, "url": url_requete, "resultats_annonces": total, "recuperes": len(notices)}
        if total and total > len(notices):
            comptes[nom]["attention"] = "plafond atteint : resserrer la requête ou relever maximum_par_requete"
        print("  {} résultats annoncés, {} récupérés".format(total, len(notices)))
    return comptes


def fusionner(dossier, protocole, comptes):
    corpus, flux = {}, {"requetes": comptes, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
    bruts = 0
    for r in protocole["requetes"]:
        chemin = os.path.join(dossier, "brut_{}.jsonl.gz".format(r["nom"]))
        if not os.path.exists(chemin):
            raise SystemExit("Notices brutes absentes pour {} : relancer sans --sans-telechargement.".format(r["nom"]))
        with gzip.open(chemin, "rt", encoding="utf-8") as f:
            for ligne in f:
                w = json.loads(ligne)
                bruts += 1
                a = resume(w)
                n = corpus.setdefault(w["id"], {
                    "id": w["id"], "doi": doi_court(w.get("doi")), "annee": w.get("publication_year") or "",
                    "titre": " ".join((w.get("title") or w.get("display_name") or "").split()),
                    "revue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or "",
                    "type": w.get("type") or "", "langue": w.get("language") or "",
                    "citations": w.get("cited_by_count") or 0,
                    "acces_libre": (w.get("open_access") or {}).get("oa_url") or "",
                    "resume_present": "oui" if a else "non", "resume": " ".join(a.split()), "requetes": set()})
                n["requetes"].add(r["nom"])
    flux["notices_brutes_toutes_requetes"] = bruts
    flux["apres_dedoublonnage_par_identifiant"] = len(corpus)
    vus, doublons = {}, 0
    for k, n in list(corpus.items()):
        cle = re.sub(r"[^a-z0-9]", "", n["titre"].lower())[:120]
        if cle and cle in vus:
            vus[cle]["requetes"] |= n["requetes"]
            del corpus[k]
            doublons += 1
        else:
            vus[cle] = n
    flux["doublons_par_titre"] = doublons
    flux["corpus_final"] = len(corpus)
    lignes = sorted(corpus.values(), key=lambda n: -n["citations"])
    with open(os.path.join(dossier, "corpus.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES, delimiter=";")
        w.writeheader()
        for n in lignes:
            w.writerow(dict(n, requetes="|".join(sorted(n["requetes"]))))
    dois = {n["doi"] for n in lignes if n["doi"]}
    temoins = [doi_court(t) for t in protocole.get("temoins", [])]
    flux["temoins"] = {"retrouves": [t for t in temoins if t in dois], "manquants": [t for t in temoins if t not in dois]}
    with open(os.path.join(dossier, "flux.json"), "w", encoding="utf-8") as f:
        json.dump(flux, f, ensure_ascii=False, indent=1)
    print("Corpus : {} notices ({} brutes, {} doublons de titre). Fichiers : corpus.csv, flux.json".format(
        len(corpus), bruts, doublons))
    if temoins:
        print("Études témoins retrouvées : {} sur {}".format(len(flux["temoins"]["retrouves"]), len(temoins)))
        for t in flux["temoins"]["manquants"]:
            print("  MANQUANTE : {} (corriger les requêtes avant de trier, PROTOCOLE_TRI.md)".format(t))


def echantillon(dossier, taille, graine):
    with open(os.path.join(dossier, "corpus.csv"), encoding="utf-8", newline="") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    tirage = random.Random(graine).sample(lignes, min(taille, len(lignes)))
    with open(os.path.join(dossier, "echantillon_humain.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["n", "id", "titre", "annee", "revue", "resume", "ta_decision", "ton_code", "ton_motif"])
        for i, n in enumerate(tirage, 1):
            w.writerow([i, n["id"], n["titre"], n["annee"], n["revue"], n["resume"], "", "", ""])
    print("Échantillon de {} notices (graine {}) : echantillon_humain.csv".format(len(tirage), graine))


def main():
    ap = argparse.ArgumentParser(description="Recherche systématique reproductible dans OpenAlex.")
    ap.add_argument("dossier", help="dossier de la recherche, contenant protocole.json")
    ap.add_argument("--sans-telechargement", action="store_true", help="refaire la fusion sans réinterroger OpenAlex")
    ap.add_argument("--echantillon", type=int, help="nombre de notices à tirer pour le second trieur humain")
    ap.add_argument("--graine", type=int, default=1, help="graine du tirage (à noter dans le rapport)")
    a = ap.parse_args()
    if a.echantillon:
        echantillon(a.dossier, a.echantillon, a.graine)
        return
    with open(os.path.join(a.dossier, "protocole.json"), encoding="utf-8") as f:
        protocole = json.load(f)
    if a.sans_telechargement:
        chemin = os.path.join(a.dossier, "flux.json")
        comptes = json.load(open(chemin, encoding="utf-8")).get("requetes", {}) if os.path.exists(chemin) else {}
    else:
        comptes = telecharger(a.dossier, protocole)
    fusionner(a.dossier, protocole, comptes)


if __name__ == "__main__":
    main()
