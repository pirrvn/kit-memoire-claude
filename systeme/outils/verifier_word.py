#!/usr/bin/env python3
"""Contrôle les informations cachées d'un fichier Word avant la remise, sans afficher leurs valeurs.

Usages :
  python3 systeme/outils/verifier_word.py memoire/livrable1/Livrable1.docx
  python3 systeme/outils/verifier_word.py memoire/livrable1/Livrable1.docx --nettoyer

Signale : champs de propriétés remplis (auteur, dernier modificateur, société, responsable), propriétés
personnalisées, auteurs de commentaires, suivi des modifications, surlignage, adresses e-mail, et les noms
au format des comptes d'entreprise (« Nom, Prénom (service) »), qui peuvent révéler l'employeur (L-018).
Les valeurs ne sont jamais affichées : le contrôle se fait sans les recopier dans la conversation.

--nettoyer écrit une copie <nom>_propre.docx : auteur et dernier modificateur remplacés par l'auteur de
config.json (page_de_garde.auteur), société et responsable vidés, et option « retirer les informations
personnelles à l'enregistrement » activée, pour que Word ne les réinscrive pas. Le texte n'est pas touché ;
les commentaires et le suivi des modifications non plus : les accepter ou les supprimer dans Word avant la remise.
Bibliothèque standard de Python uniquement.
"""
import argparse
import os
import re
import zipfile
from xml.dom import minidom
from xml.sax.saxutils import escape

from commun import config, rempli

CHAMPS_CORE = ("dc:creator", "cp:lastModifiedBy", "dc:title", "dc:subject", "cp:keywords", "dc:description")
CHAMPS_APP = ("Company", "Manager")


def valeur(xml, balise):
    m = re.search(r"<{0}(?:\s[^>]*)?>([^<]*)</{0}>".format(re.escape(balise)), xml)
    return m.group(1) if m else None


def nom_entreprise(v):
    """Vrai si un nom ressemble à un compte d'entreprise (virgule ou parenthèse)."""
    return bool(v) and ("(" in v or "," in v or "@" in v)


def controler(chemin):
    z = zipfile.ZipFile(chemin)
    noms = z.namelist()
    lire = lambda n: z.read(n).decode("utf-8", "ignore") if n in noms else ""
    core, app, doc = lire("docProps/core.xml"), lire("docProps/app.xml"), lire("word/document.xml")
    alertes = []
    print("Fichier :", chemin)
    for b in CHAMPS_CORE:
        v = valeur(core, b)
        if v is not None:
            etat = "rempli" if v.strip() else "vide"
            if nom_entreprise(v):
                etat += " (FORMAT DE COMPTE D'ENTREPRISE)"
                alertes.append(b)
            print("  propriété {} : {}".format(b, etat))
    for b in CHAMPS_APP:
        v = valeur(app, b)
        if v is not None and v.strip():
            print("  propriété {} : REMPLIE".format(b))
            alertes.append(b)
    if "docProps/custom.xml" in noms:
        print("  propriétés personnalisées : présentes")
        alertes.append("custom.xml")
    auteurs = set(re.findall(r'w:author="([^"]*)"', " ".join(lire(n) for n in noms if n.startswith("word/"))))
    if auteurs:
        print("  auteurs de commentaires ou de modifications : {}".format(len(auteurs)))
        if any(nom_entreprise(a) for a in auteurs):
            alertes.append("w:author")
            print("    dont au format de compte d'entreprise")
    print("  commentaires :", "oui" if "word/comments.xml" in noms else "non",
          "| suivi des modifications :", len(re.findall(r"<w:(?:ins|del) ", doc)),
          "| surlignage :", "oui" if "w:highlight" in doc else "non")
    tout = " ".join(lire(n) for n in noms if n.endswith(".xml"))
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", tout):
        print("  adresse e-mail : PRÉSENTE")
        alertes.append("e-mail")
    print("  retrait des informations personnelles à l'enregistrement :",
          "activé" if "removePersonalInformation" in lire("word/settings.xml") else "non")
    print("Bilan :", "à nettoyer ({})".format(", ".join(alertes)) if alertes else "rien de personnel détecté")
    return alertes


def nettoyer(chemin):
    auteur = config().get("page_de_garde", {}).get("auteur", "")
    auteur = auteur if rempli(auteur) else ""
    z = zipfile.ZipFile(chemin)
    parts = {n: z.read(n) for n in z.namelist()}
    z.close()
    core = parts.get("docProps/core.xml", b"").decode("utf-8-sig")
    for b in ("dc:creator", "cp:lastModifiedBy"):
        core = re.sub(r"<{0}(\s[^>]*)?>[^<]*</{0}>".format(re.escape(b)),
                      "<{0}>{1}</{0}>".format(b, escape(auteur)), core)
    if core:
        parts["docProps/core.xml"] = core.encode("utf-8")
    app = parts.get("docProps/app.xml", b"").decode("utf-8-sig")
    for b in CHAMPS_APP:
        app = re.sub(r"<((?:\w+:)?{0})>[^<]*</\1>".format(b), r"<\1></\1>", app)
    if app:
        parts["docProps/app.xml"] = app.encode("utf-8")
    st = parts.get("word/settings.xml", b"").decode("utf-8-sig")
    if st and "removePersonalInformation" not in st:
        if re.search(r"<w:zoom [^>]*/>", st):
            st = re.sub(r"(<w:zoom [^>]*/>)", r"\1<w:removePersonalInformation/>", st, count=1)
        else:
            st = re.sub(r"(<w:settings[^>]*>)", r"\1<w:removePersonalInformation/>", st, count=1)
        parts["word/settings.xml"] = st.encode("utf-8")
    for n in ("docProps/core.xml", "docProps/app.xml", "word/settings.xml"):
        if n in parts:
            minidom.parseString(parts[n])
    sortie = os.path.splitext(chemin)[0] + "_propre.docx"
    with zipfile.ZipFile(sortie, "w", zipfile.ZIP_DEFLATED) as out:
        out.writestr("[Content_Types].xml", parts.pop("[Content_Types].xml"))
        for n, v in parts.items():
            out.writestr(n, v)
    print("Copie nettoyée :", sortie)
    return sortie


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("fichier")
    p.add_argument("--nettoyer", action="store_true", help="écrit une copie <nom>_propre.docx nettoyée")
    a = p.parse_args()
    controler(a.fichier)
    if a.nettoyer:
        print()
        controler(nettoyer(a.fichier))
