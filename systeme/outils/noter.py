#!/usr/bin/env python3
"""Enregistre les évaluations du jury et calcule les notes (moyenne des passages, puis moyenne des juges, par grille).

Usages :
  python3 systeme/outils/noter.py <dossier_des_evaluations> [--sortie resume.md] [--commentaires comm.md]
  python3 systeme/outils/noter.py --duels <dossier_des_duels> [--sortie duels.md]

Format attendu des évaluations et des duels : voir jury/LISEZMOI.md.
Les notes sont ajoutées une seule fois à jury/NOTES.csv (empreintes dans jury/.importes.txt).
"""
import argparse
import collections
import csv
import datetime
import glob
import hashlib
import os
import re
import statistics

RACINE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
NOTES = os.path.join(RACINE, "jury", "NOTES.csv")
IMPORTES = os.path.join(RACINE, "jury", ".importes.txt")
COLONNES = ["date", "production", "version", "juge", "modele", "passage", "grille", "critere", "note", "max",
            "justification", "preuve"]


def nombre(x):
    return float(x.strip().replace(",", "."))


def ordre_naturel(code):
    m = re.match(r"([A-Za-z]+)(\d+)", code)
    return (m.group(1), int(m.group(2))) if m else (code, 0)


def lire_evaluation(chemin):
    entete, notes, commentaires, zone = {}, [], [], "entete"
    with open(chemin, encoding="utf-8") as f:
        for brut in f:
            l = brut.strip().strip("`")
            if not l:
                continue
            if l.startswith("=== EVALUATION"):
                zone = "entete"
                continue
            if l.startswith("=== COMMENTAIRES"):
                zone = "commentaires"
                continue
            if l.startswith("=== FIN"):
                break
            if zone == "entete":
                if l.upper().startswith("CRITERE") or l.upper().startswith("CRITÈRE"):
                    zone = "notes"
                elif ":" in l:
                    cle, valeur = l.split(":", 1)
                    entete[cle.strip().lower()] = valeur.strip()
            elif zone == "notes":
                parties = [p.strip() for p in l.split("|")]
                if len(parties) < 3 or parties[0].upper().startswith("TOTAL"):
                    continue
                if len(parties) > 5:
                    parties = parties[:4] + [" / ".join(parties[4:])]
                while len(parties) < 5:
                    parties.append("")
                try:
                    note, maxi = nombre(parties[1]), nombre(parties[2])
                except ValueError:
                    continue
                notes.append({"critere": parties[0], "note": note, "max": maxi,
                              "justification": parties[3], "preuve": parties[4]})
            else:
                commentaires.append(l)
    return entete, notes, commentaires


def importer(dossier):
    deja = set()
    if os.path.exists(IMPORTES):
        with open(IMPORTES, encoding="utf-8") as f:
            deja = {l.strip() for l in f if l.strip()}
    evaluations, nouvelles = [], []
    for chemin in sorted(glob.glob(os.path.join(dossier, "**", "*.txt"), recursive=True)):
        entete, notes, commentaires = lire_evaluation(chemin)
        if not notes:
            print("Ignoré (format non reconnu) : " + os.path.relpath(chemin, RACINE))
            continue
        evaluations.append((chemin, entete, notes, commentaires))
        with open(chemin, "rb") as f:
            empreinte = hashlib.sha256(f.read()).hexdigest()
        if empreinte in deja:
            continue
        for n in notes:
            nouvelles.append({"date": datetime.date.today().isoformat(), "production": entete.get("texte", "?"),
                              "version": entete.get("version", "?"), "juge": entete.get("juge", "?"),
                              "modele": entete.get("modele", "?"), "passage": entete.get("passage", "?"),
                              "grille": entete.get("grille", "?"), "critere": n["critere"],
                              "note": str(n["note"]).replace(".", ","), "max": str(n["max"]).replace(".", ","),
                              "justification": n["justification"], "preuve": n["preuve"]})
        deja.add(empreinte)
    if nouvelles:
        existe = os.path.exists(NOTES)
        with open(NOTES, "a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLONNES, delimiter=";")
            if not existe:
                w.writeheader()
            w.writerows(nouvelles)
    with open(IMPORTES, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(deja)) + "\n")
    print("{} évaluation(s) lue(s), {} note(s) ajoutée(s) à jury/NOTES.csv".format(len(evaluations), len(nouvelles)))
    return evaluations


def resumer(evaluations):
    """Une note par juge et par grille (moyenne des passages), puis la moyenne des juges, grille par grille.
    Les grilles ne sont jamais additionnées entre elles (une grille officielle et la grille d'excellence restent séparées)."""
    par_critere = collections.defaultdict(lambda: collections.defaultdict(list))
    totaux = collections.defaultdict(list)
    maxima = {}
    commentaires = collections.defaultdict(list)
    for chemin, e, notes, comm in evaluations:
        cle = (e.get("texte", "?"), e.get("version", "?"), e.get("grille", "?"), e.get("juge", "?"))
        for n in notes:
            par_critere[cle][n["critere"]].append(n["note"])
        totaux[cle].append(sum(n["note"] for n in notes))
        maxima[cle] = sum(n["max"] for n in notes)
        commentaires[(cle[0], cle[1])].append((cle[3], cle[2], e.get("modele", "?"), comm))
    lignes = ["| Texte | Version | Grille | Juge | Passages | Note (moyenne des passages) | Écart entre passages |",
              "|---|---|---|---|---|---|---|"]
    par_grille = collections.defaultdict(list)
    for cle in sorted(par_critere):
        total = sum(statistics.mean(v) for v in par_critere[cle].values())
        ecart = max(totaux[cle]) - min(totaux[cle])
        alerte = " : plus de 4 points, à signaler" if ecart > 4 else ""
        lignes.append("| {} | {} | {} | {} | {} | {:.2f} / {:g} | {:.1f}{} |".format(
            cle[0], cle[1], cle[2], cle[3], len(totaux[cle]), total, maxima[cle], ecart, alerte))
        par_grille[cle[:3]].append((total, maxima[cle]))
    lignes += ["", "| Texte | Version | Grille | Note du jury (moyenne des juges) | Juges |", "|---|---|---|---|---|"]
    for k in sorted(par_grille):
        notes = par_grille[k]
        lignes.append("| {} | {} | {} | {:.2f} / {:g} | {} |".format(
            k[0], k[1], k[2], statistics.mean(t for t, m in notes), notes[0][1], len(notes)))
    lignes += ["", "Moyennes par critère :", ""]
    for grille in sorted({c[2] for c in par_critere}):
        cles = [c for c in sorted(par_critere) if c[2] == grille]
        criteres = sorted({cr for c in cles for cr in par_critere[c]}, key=ordre_naturel)
        lignes += ["| Texte | Version | Grille | Juge | " + " | ".join(criteres) + " |",
                   "|---|---|---|---|" + "---|" * len(criteres)]
        for c in cles:
            valeurs = ["{:g}".format(round(statistics.mean(par_critere[c][cr]), 2)) if cr in par_critere[c] else ""
                       for cr in criteres]
            lignes.append("| {} | {} | {} | {} | ".format(*c) + " | ".join(valeurs) + " |")
        lignes.append("")
    bloc_comm = []
    for (texte, version) in sorted(commentaires):
        bloc_comm.append("## {} ({})\n".format(texte, version))
        for juge, grille, modele, comm in sorted(commentaires[(texte, version)]):
            if not comm:
                continue
            bloc_comm.append("### {} / {} / {}\n".format(juge, grille, modele))
            bloc_comm += ["- " + c for c in comm]
            bloc_comm.append("")
    return "\n".join(lignes), "\n".join(bloc_comm)


def duels(dossier):
    victoires, details = collections.Counter(), []
    for chemin in sorted(glob.glob(os.path.join(dossier, "**", "*.txt"), recursive=True)):
        d = {}
        with open(chemin, encoding="utf-8") as f:
            for l in f:
                if ":" in l:
                    cle, valeur = l.split(":", 1)
                    d[cle.strip().lower()] = valeur.strip()
        if "vainqueur" not in d:
            print("Ignoré (pas de VAINQUEUR) : " + os.path.relpath(chemin, RACINE))
            continue
        victoires[d["vainqueur"]] += 1
        details.append("| {} | {} | {} | {} | {} |".format(d.get("gauche", "?"), d.get("droite", "?"),
                                                           d["vainqueur"], d.get("critere decisif", "?"),
                                                           d.get("modele", "?")))
    lignes = ["| Piste | Victoires |", "|---|---|"] + ["| {} | {} |".format(p, v) for p, v in victoires.most_common()]
    lignes += ["", "| Gauche | Droite | Vainqueur | Critère décisif | Modèle |", "|---|---|---|---|---|"] + details
    return "\n".join(lignes)


def main():
    ap = argparse.ArgumentParser(description="Enregistrement des notes du jury.")
    ap.add_argument("dossier", nargs="?", help="dossier contenant les évaluations (.txt)")
    ap.add_argument("--duels", help="dossier contenant les duels (.txt)")
    ap.add_argument("--sortie", help="fichier markdown où écrire le résumé")
    ap.add_argument("--commentaires", help="fichier markdown où regrouper les commentaires des juges")
    a = ap.parse_args()
    if a.duels:
        texte = duels(a.duels)
    elif a.dossier:
        resume, comm = resumer(importer(a.dossier))
        texte = resume
        if a.commentaires:
            with open(a.commentaires, "w", encoding="utf-8") as f:
                f.write("# Commentaires des juges\n\n" + comm + "\n")
    else:
        ap.error("indique un dossier d'évaluations ou --duels")
    print(texte)
    if a.sortie:
        with open(a.sortie, "w", encoding="utf-8") as f:
            f.write(texte + "\n")


if __name__ == "__main__":
    main()
