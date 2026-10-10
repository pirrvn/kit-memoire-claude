#!/usr/bin/env python3
"""Remplit le modèle Word officiel de l'école avec un texte Markdown du mémoire (L-017).

Usages :
  python3 systeme/outils/remplir_modele.py memoire/livrable1/livrable1_v3.md
  python3 systeme/outils/remplir_modele.py texte.md --sortie Livrable1.docx --modele consignes/originaux/Modele_L1.docx
  python3 systeme/outils/remplir_modele.py texte.md --debut "Corps du texte" --remplacer "Titre du livrable 1={titre}"

Réglages dans systeme/config.json, rubrique « modele_word » (les options de la ligne de commande priment) :
  chemin          le modèle (.docx) fourni par l'école, en général dans consignes/originaux/ ;
  debut_du_corps  début du premier paragraphe d'exemple du modèle : tout ce qui précède (page de garde,
                  bloc de titre) est gardé, tout ce qui suit est remplacé par le texte ;
  remplacements   textes d'exemple du modèle à remplacer, dans le bloc de titre et les en-têtes ; une valeur
                  peut contenir {titre}, {titre_court} et les champs de « page_de_garde » ({auteur}, ...) ;
  remplacements_en_tete  mêmes règles, pour les seuls en-têtes et pieds de page (par exemple un titre court).
Ce qui est gardé du modèle : styles, logos, en-têtes, pieds de page, numérotation, marges.
Ce qui est retiré : commentaires d'exemple, métadonnées de l'école, noms dans les propriétés ; l'option
« retirer les informations personnelles à l'enregistrement » est activée.
Styles trouvés par leur nom interne Word (« heading 2 », « footnote text »...), quelle que soit la langue.
Markdown reconnu : # titre (première ligne, pour le bloc de titre), ## et ### titres, *italique*, **gras**,
***les deux***, notes [^1] et [^1]: texte, listes (- ...), tableaux | a | b |, section « ## Références ».
Bibliothèque standard de Python uniquement. Ne jamais écrire sur un Word ouvert par l'auteur (fichier ~$).
"""
import argparse
import os
import re
import sys
import zipfile
from xml.dom import minidom
from xml.sax.saxutils import escape

from commun import RACINE, config, rempli

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
REFERENCES = re.compile(r"^(références|bibliographie|references|bibliography)\b", re.I)
A_RETIRER = ("word/comments.xml", "word/commentsExtended.xml", "word/commentsIds.xml",
             "word/commentsExtensible.xml", "word/people.xml", "docProps/custom.xml")


def texte_de(noeud):
    return "".join(t.firstChild.data if t.firstChild else "" for t in noeud.getElementsByTagName("w:t"))


def styles_par_nom(styles_xml):
    """Associe le nom interne de chaque style (en minuscules) à son identifiant ; liste aussi les styles de paragraphe."""
    d, paragraphes = {}, []
    for m in re.finditer(r'<w:style ([^>]*)>(.*?)</w:style>', styles_xml, re.S):
        sid = re.search(r'w:styleId="([^"]+)"', m.group(1))
        nom = re.search(r'<w:name w:val="([^"]+)"', m.group(2))
        if sid and nom:
            d.setdefault(nom.group(1).lower(), sid.group(1))
            if 'w:type="paragraph"' in m.group(1):
                paragraphes.append((nom.group(1).lower(), sid.group(1)))
    return d, paragraphes


def motif(cle):
    """Expression qui reconnaît un texte malgré les espaces insécables et les apostrophes typographiques."""
    out = []
    for c in cle:
        if c in " \u00a0\u202f":
            out.append("[ \u00a0\u202f]")
        elif c in "'\u2019":
            out.append("['\u2019]")
        else:
            out.append(re.escape(c))
    return re.compile("".join(out))


def fusionner_runs(p):
    """Fusionne les morceaux de texte voisins de même mise en forme (Word coupe souvent un mot en plusieurs)."""
    runs = [r for r in p.childNodes if r.nodeType == r.ELEMENT_NODE and r.tagName == "w:r"]
    prec = None
    for r in runs:
        enfants = [c for c in r.childNodes if c.nodeType == c.ELEMENT_NODE]
        simple = all(c.tagName in ("w:rPr", "w:t") for c in enfants) and r.getElementsByTagName("w:t")
        rpr = "".join(c.toxml() for c in enfants if c.tagName == "w:rPr")
        if simple and prec is not None and prec[1] == rpr and r.previousSibling is prec[0]:
            t_prec = prec[0].getElementsByTagName("w:t")[-1]
            ajout = texte_de(r)
            t_prec.firstChild.data = (t_prec.firstChild.data if t_prec.firstChild else "") + ajout
            t_prec.setAttribute("xml:space", "preserve")
            p.removeChild(r)
            continue
        prec = (r, rpr) if simple else None
    # les marques de relecture orthographique séparent les morceaux : on les retire
    for e in list(p.getElementsByTagName("w:proofErr")):
        e.parentNode.removeChild(e)


def remplacer(noeud, remplacements):
    paragraphes = [noeud] if getattr(noeud, "tagName", "") == "w:p" else []
    for p in paragraphes + list(noeud.getElementsByTagName("w:p")):
        for _ in range(2):  # deux passes : retirer les marques, puis fusionner
            fusionner_runs(p)
        for t in p.getElementsByTagName("w:t"):
            if t.firstChild:
                for cle, val in remplacements.items():
                    if motif(cle).search(t.firstChild.data):
                        t.firstChild.data = motif(cle).sub(lambda m: val, t.firstChild.data)
                        t.setAttribute("xml:space", "preserve")


def runs(text, ref_style):
    out = []
    for tok in re.split(r"(\[\^\d+\]|\*\*\*.+?\*\*\*|\*\*.+?\*\*|\*.+?\*)", text):
        if not tok:
            continue
        m = re.fullmatch(r"\[\^(\d+)\]", tok)
        if m:
            rpr = '<w:rPr><w:rStyle w:val="{}"/></w:rPr>'.format(ref_style) if ref_style else \
                  '<w:rPr><w:vertAlign w:val="superscript"/></w:rPr>'
            out.append('<w:r>{}<w:footnoteReference w:id="{}"/></w:r>'.format(rpr, "@" + m.group(1)))
            continue
        b = i = False
        if tok.startswith("***"):
            tok, b, i = tok[3:-3], True, True
        elif tok.startswith("**"):
            tok, b = tok[2:-2], True
        elif tok.startswith("*") and len(tok) > 1:
            tok, i = tok[1:-1], True
        rpr = ("<w:b/>" if b else "") + ("<w:i/>" if i else "")
        out.append('<w:r>{}<w:t xml:space="preserve">{}</w:t></w:r>'.format(
            "<w:rPr>{}</w:rPr>".format(rpr) if rpr else "", escape(tok)))
    return "".join(out)


def para(text, style=None, ref_style=None):
    ppr = '<w:pPr><w:pStyle w:val="{}"/></w:pPr>'.format(style) if style else ""
    return "<w:p>{}{}</w:p>".format(ppr, runs(text, ref_style))


def tableau(lignes, ref_style):
    ncol = len(lignes[0])
    bords = "".join('<w:{} w:val="single" w:sz="4" w:space="0" w:color="000000"/>'.format(s)
                    for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
    xml = ['<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/><w:tblBorders>{}</w:tblBorders></w:tblPr><w:tblGrid>'.format(bords)]
    xml += ['<w:gridCol w:w="{}"/>'.format(9000 // ncol)] * ncol
    xml.append("</w:tblGrid>")
    for k, ligne in enumerate(lignes):
        cells = "".join("<w:tc><w:tcPr><w:tcW w:w=\"{}\" w:type=\"dxa\"/></w:tcPr>{}</w:tc>".format(
            9000 // ncol, para(("**{}**" if k == 0 else "{}").format(c.strip()), None, ref_style)) for c in ligne)
        xml.append("<w:tr>{}</w:tr>".format(cells))
    xml.append("</w:tbl><w:p/>")
    return "".join(xml)


def lire_markdown(chemin):
    lignes = open(chemin, encoding="utf-8").read().split("\n")
    titre = lignes[0].lstrip("#").strip() if lignes and lignes[0].startswith("# ") else ""
    notes, blocs = {}, []
    for l in lignes[1 if titre else 0:]:
        m = re.match(r"^\[\^(\d+)\]:\s*(.*)$", l)
        if m:
            notes[m.group(1)] = m.group(2)
        else:
            blocs.append(l.rstrip())
    # la ligne en italique qui suit le titre (sous-titre) va au bloc de titre, pas au corps
    while blocs and (not blocs[0].strip() or re.fullmatch(r"\*[^*].*\*", blocs[0].strip())):
        blocs.pop(0)
    return titre, notes, blocs


def corps_xml(blocs, st, paragraphes, ref_style):
    section = st.get("heading 2") or st.get("heading 1")
    sous_section = st.get("heading 3") or section
    titre_refs = st.get("heading 1") or section
    style_refs = next((sid for nom, sid in paragraphes if re.match(r"(r[ée]f[ée]rences?|bibliograph)", nom)), None)
    puce = st.get("list bullet") or st.get("list paragraph")
    xml, dans_refs, k = [], False, 0
    while k < len(blocs):
        l = blocs[k]
        if l.startswith("|"):
            lignes = []
            while k < len(blocs) and blocs[k].startswith("|"):
                cells = blocs[k].strip().strip("|").split("|")
                if not re.match(r"^\s*:?-+:?\s*$", cells[0]):
                    lignes.append(cells)
                k += 1
            xml.append(tableau(lignes, ref_style))
            continue
        k += 1
        if not l.strip():
            continue
        if l.startswith("## ") and REFERENCES.match(l[3:].strip()):
            dans_refs = True
            xml.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
            xml.append(para(l[3:].strip(), titre_refs))
        elif l.startswith("### "):
            xml.append(para(l[4:], sous_section, ref_style))
        elif l.startswith("## "):
            xml.append(para(l[3:], section, ref_style))
        elif l.startswith("- "):
            xml.append(para(l[2:], puce, ref_style))
        else:
            xml.append(para(l, style_refs if dans_refs else None, ref_style))
    return "".join(xml)


def main():
    reglages = config().get("modele_word", {})
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("texte")
    p.add_argument("--sortie", help="fichier .docx produit (par défaut : nom du texte en .docx)")
    p.add_argument("--modele", default=reglages.get("chemin", ""))
    p.add_argument("--debut", default=reglages.get("debut_du_corps", ""))
    p.add_argument("--remplacer", action="append", default=[], help="« texte du modèle=nouveau texte », répétable")
    p.add_argument("--remplacer-en-tete", action="append", default=[], help="idem, pour les en-têtes et pieds de page")
    p.add_argument("--titre-court", default="", help="titre pour l'en-tête des pages (par défaut : avant les deux-points)")
    a = p.parse_args()

    modele = a.modele if os.path.isabs(a.modele) else os.path.join(RACINE, a.modele)
    if not rempli(a.modele) or not os.path.isfile(modele):
        sys.exit("Modèle introuvable : régler modele_word.chemin dans systeme/config.json ou passer --modele.")
    if not rempli(a.debut):
        sys.exit("Indiquer le début du premier paragraphe d'exemple du modèle (modele_word.debut_du_corps ou --debut).")
    sortie = a.sortie or os.path.splitext(a.texte)[0] + ".docx"
    if os.path.exists(os.path.join(os.path.dirname(sortie) or ".", "~$" + os.path.basename(sortie)[2:])):
        sys.exit("Ce fichier est ouvert dans Word : le fermer, ou choisir un autre nom avec --sortie.")

    titre, notes, blocs = lire_markdown(a.texte)
    titre_court = a.titre_court or titre.split(" : ")[0]
    champs = {k: v for k, v in config().get("page_de_garde", {}).items() if rempli(v)}
    champs.update(titre=titre, titre_court=titre_court)
    remplacements = dict(reglages.get("remplacements", {}))
    remplacements.update(r.split("=", 1) for r in a.remplacer if "=" in r)
    remplacements = {k: v.format(**champs) if "{" in v else v for k, v in remplacements.items() if not k.startswith("_")}
    en_tete = dict(remplacements)
    en_tete.update(reglages.get("remplacements_en_tete", {}))
    en_tete.update(r.split("=", 1) for r in a.remplacer_en_tete if "=" in r)
    en_tete = {k: v.format(**champs) if "{" in v else v for k, v in en_tete.items() if not k.startswith("_")}

    z = zipfile.ZipFile(modele)
    parts = {n: z.read(n) for n in z.namelist() if n not in A_RETIRER
             and not n.startswith("customXml/") and not n.startswith("[trash]/")}
    st, paragraphes = styles_par_nom(parts["word/styles.xml"].decode("utf-8-sig"))
    ref_style = st.get("footnote reference")

    # bloc de titre : gardé jusqu'au premier paragraphe d'exemple, avec les remplacements
    doc_txt = parts["word/document.xml"].decode("utf-8-sig")
    dom = minidom.parseString(doc_txt.encode("utf-8"))
    body = dom.getElementsByTagName("w:body")[0]
    elements = [e for e in body.childNodes if e.nodeType == e.ELEMENT_NODE]
    debut = next((i for i, e in enumerate(elements) if texte_de(e).strip().startswith(a.debut.strip())), None)
    if debut is None:
        sys.exit("« {} » introuvable dans le modèle : vérifier modele_word.debut_du_corps.".format(a.debut))
    garde = elements[:debut]
    for e in garde:
        if e.getElementsByTagName("w:commentReference") or e.getElementsByTagName("w:commentRangeStart"):
            for tag in ("w:commentRangeStart", "w:commentRangeEnd"):
                for c in list(e.getElementsByTagName(tag)):
                    c.parentNode.removeChild(c)
            for c in list(e.getElementsByTagName("w:commentReference")):
                c.parentNode.parentNode.removeChild(c.parentNode)
        remplacer(e, remplacements)
    sectpr = [e for e in elements if e.tagName == "w:sectPr"]
    entete = doc_txt[:doc_txt.index("<w:body>") + len("<w:body>")]
    nouveau = entete + "".join(e.toxml() for e in garde) + corps_xml(blocs, st, paragraphes, ref_style) + \
        "".join(e.toxml() for e in sectpr) + "</w:body></w:document>"

    # notes de bas de page : numérotées après les séparateurs du modèle
    fn = parts.get("word/footnotes.xml", b"").decode("utf-8-sig")
    if not fn:
        fn = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:footnotes xmlns:w="{}">'
              '<w:footnote w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:footnote>'
              '<w:footnote w:type="continuationSeparator" w:id="0"><w:p><w:r><w:continuationSeparator/></w:r></w:p></w:footnote>'
              '</w:footnotes>').format(W)
        r = parts["word/_rels/document.xml.rels"].decode("utf-8-sig")
        parts["word/_rels/document.xml.rels"] = r.replace("</Relationships>", '<Relationship Id="rIdNotesKit" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/></Relationships>').encode("utf-8")
        ct = parts["[Content_Types].xml"].decode("utf-8-sig")
        parts["[Content_Types].xml"] = ct.replace("</Types>", '<Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/></Types>').encode("utf-8")
    premier = max([int(i) for i in re.findall(r'<w:footnote [^>]*w:id="(-?\d+)"', fn)] + [0]) + 1
    ids = {n: premier + k for k, n in enumerate(sorted(notes, key=int))}
    style_note = st.get("footnote text")
    ppr = '<w:pPr><w:pStyle w:val="{}"/></w:pPr>'.format(style_note) if style_note else ""
    rpr = '<w:rPr><w:rStyle w:val="{}"/></w:rPr>'.format(ref_style) if ref_style else '<w:rPr><w:vertAlign w:val="superscript"/></w:rPr>'
    fn = fn.replace("</w:footnotes>", "".join(
        '<w:footnote w:id="{}"><w:p>{}<w:r>{}<w:footnoteRef/></w:r><w:r><w:t xml:space="preserve"> </w:t></w:r>{}</w:p></w:footnote>'.format(
            ids[n], ppr, rpr, runs(notes[n], ref_style)) for n in sorted(notes, key=int)) + "</w:footnotes>")
    nouveau = re.sub(r'w:id="@(\d+)"', lambda m: 'w:id="{}"'.format(ids.get(m.group(1), 0)), nouveau)
    manquantes = set(re.findall(r'w:id="@(\d+)"', nouveau))
    if manquantes:
        sys.exit("Appels de note sans texte : " + ", ".join(sorted(manquantes)))
    parts["word/document.xml"] = nouveau.encode("utf-8")
    parts["word/footnotes.xml"] = fn.encode("utf-8")

    # en-têtes et pieds de page : mêmes remplacements
    for n in list(parts):
        if re.match(r"word/(header|footer)\d*\.xml$", n):
            d = minidom.parseString(parts[n])
            remplacer(d, en_tete)
            parts[n] = d.toxml(encoding="UTF-8")

    # relations et types : retirer ce qui pointe vers les parties supprimées
    r = parts["word/_rels/document.xml.rels"].decode("utf-8-sig")
    parts["word/_rels/document.xml.rels"] = re.sub(
        r'<Relationship [^>]*Target="(?:comments\w*\.xml|people\.xml|\.\./customXml/[^"]*)"[^>]*/>', "", r).encode("utf-8")
    r = parts["_rels/.rels"].decode("utf-8-sig")
    parts["_rels/.rels"] = re.sub(r'<Relationship [^>]*Target="docProps/custom\.xml"[^>]*/>', "", r).encode("utf-8")
    ct = parts["[Content_Types].xml"].decode("utf-8-sig")
    parts["[Content_Types].xml"] = re.sub(
        r'<Override PartName="/(?:word/comments\w*\.xml|word/people\.xml|customXml/[^"]*|docProps/custom\.xml)"[^>]*/>', "", ct).encode("utf-8")

    # propriétés neutres, et Word retirera les informations personnelles à chaque enregistrement
    parts["docProps/core.xml"] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties '
        'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>{}</dc:title></cp:coreProperties>').format(escape(titre)).encode("utf-8")
    parts["docProps/app.xml"] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties '
        'xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Template>Normal</Template></Properties>').encode("utf-8")
    s = parts["word/settings.xml"].decode("utf-8-sig")
    if "removePersonalInformation" not in s:
        if re.search(r"<w:zoom [^>]*/>", s):
            s = re.sub(r"(<w:zoom [^>]*/>)", r"\1<w:removePersonalInformation/>", s, count=1)
        else:
            s = re.sub(r"(<w:settings[^>]*>)", r"\1<w:removePersonalInformation/>", s, count=1)
    parts["word/settings.xml"] = s.encode("utf-8")

    for n, v in parts.items():
        if n.endswith(".xml") or n.endswith(".rels"):
            minidom.parseString(v)
    with zipfile.ZipFile(sortie, "w", zipfile.ZIP_DEFLATED) as out:
        out.writestr("[Content_Types].xml", parts.pop("[Content_Types].xml"))
        for n, v in parts.items():
            out.writestr(n, v)
    restes = [k for k, v in remplacements.items() if motif(k).search(nouveau) and not motif(k).search(v)]
    print("Écrit : {} ({} notes). Textes d'exemple encore présents : {}".format(
        sortie, len(notes), ", ".join(restes) if restes else "aucun"))


if __name__ == "__main__":
    main()
