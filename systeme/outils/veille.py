#!/usr/bin/env python3
"""Veille automatique : nouvelles publications sur le sujet du mémoire (OpenAlex et arXiv).
Les requêtes se règlent dans systeme/config.json (rubrique « veille »).

Usages :
  python3 systeme/outils/veille.py                       # depuis la dernière veille (30 jours la première fois)
  python3 systeme/outils/veille.py --depuis 2026-09-01 --essai   # essai, sans mettre à jour l'état

Seuls des mots-clés sont envoyés. Résultat : veille/AAAA-MM-JJ.md. Les publications trouvées ne sont pas
vérifiées au-delà de leur existence dans la base : le documentaliste doit les vérifier avant tout usage.
"""
import argparse
import csv
import datetime
import json
import os
import re
import time
import urllib.parse
import urllib.request

from commun import RACINE, avec_contact, config, rempli

DOSSIER = os.path.join(RACINE, "veille")
ETAT = os.path.join(DOSSIER, ".derniere_veille")
DEJA_VUS = os.path.join(DOSSIER, ".deja_vus.txt")
REGISTRE = os.path.join(RACINE, "sources", "REGISTRE.csv")
ENTETES = {"User-Agent": "kit-memoire-veille/1.0 (veille bibliographique; python-urllib)"}


def requetes(base):
    """Requêtes de la veille lues dans systeme/config.json ; celles qui contiennent encore « À REMPLIR » sont ignorées."""
    sortie = []
    for r in config().get("veille", {}).get(base, []):
        if rempli(r.get("nom")) and rempli(r.get("requete")):
            sortie.append((r["nom"], r["requete"]))
    return sortie


def obtenir(url, json_attendu=True):
    req = urllib.request.Request(avec_contact(url), headers=ENTETES)
    with urllib.request.urlopen(req, timeout=30) as r:
        texte = r.read().decode("utf-8", "replace")
    time.sleep(0.3)
    return json.loads(texte) if json_attendu else texte


def dois_du_registre():
    if not os.path.exists(REGISTRE):
        return set()
    with open(REGISTRE, encoding="utf-8-sig", newline="") as f:
        return {l["doi"].strip().lower() for l in csv.DictReader(f, delimiter=";") if l.get("doi")}


def deja_vus():
    if not os.path.exists(DEJA_VUS):
        return set()
    with open(DEJA_VUS, encoding="utf-8") as f:
        return {l.strip() for l in f if l.strip()}


def openalex(requete, depuis, jusqu):
    # Recherche limitée aux titres et résumés, avec expressions exactes, pour éviter le bruit.
    params = {"filter": "title_and_abstract.search:{},primary_location.source.type:journal,from_publication_date:{},to_publication_date:{}".format(
                  requete, depuis, jusqu),
              "sort": "publication_date:desc", "per-page": "8",
              "select": "id,doi,display_name,publication_date,authorships,primary_location,type"}
    resultats = obtenir("https://api.openalex.org/works?" + urllib.parse.urlencode(params)).get("results", [])
    sortie = []
    for w in resultats:
        source = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or "lieu inconnu"
        noms = [a["author"]["display_name"] for a in w.get("authorships", []) if a.get("author")]
        auteurs = ", ".join(noms[:3]) + (" et al." if len(noms) > 3 else "")
        sortie.append({"cle": w["id"], "titre": w.get("display_name") or "(sans titre)",
                       "date": w.get("publication_date") or "", "auteurs": auteurs or "auteurs inconnus",
                       "lieu": source, "type": w.get("type") or "", "lien": w.get("doi") or w["id"],
                       "doi": (w.get("doi") or "").replace("https://doi.org/", "").lower()})
    return sortie


def arxiv(requete, depuis):
    params = {"search_query": requete, "sortBy": "submittedDate", "sortOrder": "descending", "max_results": "8"}
    xml = obtenir("http://export.arxiv.org/api/query?" + urllib.parse.urlencode(params), json_attendu=False)
    sortie = []
    for e in xml.split("<entry>")[1:]:
        date = re.search(r"<published>(.*?)</published>", e).group(1)[:10]
        if date < depuis:
            continue
        ident = re.search(r"<id>(.*?)</id>", e).group(1).strip()
        titre = re.sub(r"\s+", " ", re.search(r"<title>(.*?)</title>", e, re.S).group(1)).strip()
        noms = [re.sub(r"\s+", " ", n).strip() for n in re.findall(r"<name>(.*?)</name>", e, re.S)]
        auteurs = ", ".join(noms[:3]) + (" et al." if len(noms) > 3 else "")
        sortie.append({"cle": ident, "titre": titre, "date": date, "auteurs": auteurs, "lieu": "arXiv (préprint)",
                       "type": "preprint", "lien": ident, "doi": ""})
    return sortie


def main():
    ap = argparse.ArgumentParser(description="Veille bibliographique du mémoire.")
    ap.add_argument("--depuis", help="date de début AAAA-MM-JJ")
    ap.add_argument("--essai", action="store_true", help="ne met pas à jour l'état de la veille")
    a = ap.parse_args()
    aujourdhui = datetime.date.today()
    depuis = a.depuis
    if not depuis and os.path.exists(ETAT):
        depuis = open(ETAT, encoding="utf-8").read().strip()
    if not depuis:
        depuis = (aujourdhui - datetime.timedelta(days=30)).isoformat()
    vus, connus, cette_fois, titres_vus = deja_vus(), dois_du_registre(), set(), set()
    sections, total = [], 0
    taches = [(n, "openalex", q) for n, q in requetes("openalex")] + [(n, "arxiv", q) for n, q in requetes("arxiv")]
    if not taches:
        print("Aucune requête de veille réglée : remplir la rubrique « veille » de systeme/config.json.")
        return
    for nom, base, requete in taches:
        try:
            items = openalex(requete, depuis, aujourdhui.isoformat()) if base == "openalex" else arxiv(requete, depuis)
        except Exception as e:
            sections.append((nom, base, requete, None, str(e)[:120]))
            continue
        gardes = []
        for i in items:
            titre_norm = re.sub(r"[^a-z0-9]+", " ", i["titre"].lower()).strip()
            if (i["cle"] in vus or i["cle"] in cette_fois or titre_norm in titres_vus
                    or (i["doi"] and i["doi"] in connus)):
                continue
            cette_fois.add(i["cle"])
            titres_vus.add(titre_norm)
            gardes.append(i)
        total += len(gardes)
        sections.append((nom, base, requete, gardes, ""))
    os.makedirs(DOSSIER, exist_ok=True)
    chemin = os.path.join(DOSSIER, "{}.md".format(aujourdhui.isoformat()))
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("# Veille du {}\n\n".format(aujourdhui.isoformat()))
        f.write("Période : publications depuis le {}. Bases : OpenAlex et arXiv. {} nouveauté(s).\n\n".format(depuis, total))
        f.write("Rien ici n'est vérifié au-delà de l'existence dans la base. Avant tout usage, le documentaliste "
                "vérifie la source et l'ajoute au registre.\n")
        for nom, base, requete, items, erreur in sections:
            f.write("\n## {} ({}, requête : {})\n\n".format(nom, base, requete))
            if items is None:
                f.write("Erreur d'accès à la base : {}\n".format(erreur))
            elif not items:
                f.write("Rien de nouveau.\n")
            else:
                for i in items:
                    f.write("- **{}** ({}). {}. *{}*. {}. {}\n".format(i["titre"], i["date"], i["auteurs"],
                                                                       i["lieu"], i["type"], i["lien"]))
    if not a.essai:
        with open(ETAT, "w", encoding="utf-8") as f:
            f.write(aujourdhui.isoformat())
        with open(DEJA_VUS, "a", encoding="utf-8") as f:
            for c in sorted(cette_fois):
                f.write(c + "\n")
    print("Veille : {} nouveauté(s) depuis le {}. Rapport : {}{}".format(
        total, depuis, os.path.relpath(chemin, RACINE), " (essai, état non mis à jour)" if a.essai else ""))


if __name__ == "__main__":
    main()
