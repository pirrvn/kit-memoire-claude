#!/usr/bin/env python3
"""Compte les mots d'un texte Markdown comme le ferait Word, hors titre, notes et bibliographie.

Usages :
  python3 systeme/outils/compter_mots.py memoire/livrable1/livrable1_v1.md
  python3 systeme/outils/compter_mots.py memoire/livrable1/livrable1_v1.md --tout

Exclus par défaut : la première ligne si c'est le titre (# ...) et le sous-titre en italique qui la suit
(ils vont sur la page de garde), les définitions de notes ([^1]: ...), les parties dont le titre commence par
Références, Bibliographie, Annexe ou Notes, et tout ce qui suit une ligne <!-- fin du texte compté -->.
--tout compte le fichier entier. Un mot est une suite de caractères sans espace contenant au moins une lettre
ou un chiffre (« l'entreprise » compte pour un mot, comme dans Word).
"""
import argparse
import re

EXCLUES = re.compile(r"^#{1,6}\s+(références|bibliographie|annexes?|notes)\b", re.I)


def lignes_comptees(texte, tout=False):
    lignes = texte.split("\n")
    if tout:
        return lignes
    gardees, exclue = [], False
    if lignes and lignes[0].startswith("# "):
        lignes = lignes[1:]
        while lignes and not lignes[0].strip():
            lignes = lignes[1:]
        if lignes and re.fullmatch(r"\*[^*].*\*", lignes[0].strip()):
            lignes = lignes[1:]
    for l in lignes:
        if l.strip() == "<!-- fin du texte compté -->":
            break
        if re.match(r"^#{1,6}\s", l):
            exclue = bool(EXCLUES.match(l))
        if exclue or re.match(r"^\[\^[^\]]+\]:", l):
            continue
        gardees.append(l)
    return gardees


def compter(texte, tout=False):
    total = 0
    for l in lignes_comptees(texte, tout):
        if re.fullmatch(r"\s*\|?[\s:|-]+\|?\s*", l) and "-" in l:
            continue  # ligne de séparation d'un tableau
        l = re.sub(r"\[\^[^\]]+\]", "", l)          # appels de note
        l = re.sub(r"<!--.*?-->", "", l)             # commentaires
        l = re.sub(r"^#{1,6}\s+", "", l)             # marques de titre
        l = re.sub(r"^\s*([-*+]|\d+[.)])\s+", "", l)  # puces et numéros de liste
        l = l.replace("|", " ").replace("*", "").replace("`", "")
        total += sum(1 for m in l.split() if re.search(r"\w", m))
    return total


def main():
    ap = argparse.ArgumentParser(description="Compte les mots d'un texte Markdown.")
    ap.add_argument("fichier")
    ap.add_argument("--tout", action="store_true", help="compter le fichier entier")
    a = ap.parse_args()
    with open(a.fichier, encoding="utf-8") as f:
        n = compter(f.read(), a.tout)
    print("{} mots{}".format(n, "" if a.tout else " (hors titre, notes, références et annexes)"))


if __name__ == "__main__":
    main()
