#!/usr/bin/env python3
"""Convertit un texte Markdown du mémoire en document Word (.docx), avec page de garde.

Usages :
  python3 systeme/outils/md2docx.py memoire/livrable1/livrable1_v1.md --livrable "Livrable 1" --remise "14 octobre 2026"
  python3 systeme/outils/md2docx.py texte.md --annexe annexe.md --sortie Livrable1_v1.docx

Page de garde : école, programme, auteur, direction du mémoire et année lus dans systeme/config.json (rubrique
« page_de_garde ») ; titre = première ligne du texte (# ...), sous-titre = ligne en italique qui la suit.
Mise en page : police de config.json (Times New Roman par défaut), corps 12, interligne 1,5, marges 2,5 cm,
notes de bas de page, tableaux, bibliographie en retrait, pages numérotées après la page de garde.
Le nombre de mots (compter_mots.py) est indiqué sur la page de garde. Aucune métadonnée d'auteur n'est écrite.
Markdown reconnu : # titre, ## et ### titres, *italique*, **gras**, ***les deux***, notes [^1] et [^1]: texte,
listes à puces (- ...), tableaux | a | b |. Bibliothèque standard de Python uniquement.
"""
import argparse
import os
import re
import zipfile
from xml.sax.saxutils import escape

from commun import config, rempli
from compter_mots import compter

GARDE = config().get("page_de_garde", {})
FONT = GARDE.get("police") or "Times New Roman"
REFERENCES = re.compile(r"^(références|bibliographie)\b", re.I)


def runs(text, base_b=False, base_i=False, size=24):
    out = []
    for tok in re.split(r'(\[\^\d+\]|\*\*\*.+?\*\*\*|\*\*.+?\*\*|\*.+?\*|`.+?`)', text):
        if not tok:
            continue
        m = re.fullmatch(r'\[\^(\d+)\]', tok)
        if m:
            out.append(f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/><w:vertAlign w:val="superscript"/></w:rPr>'
                       f'<w:footnoteReference w:id="{m.group(1)}"/></w:r>')
            continue
        b, i = base_b, base_i
        if tok.startswith('***'):
            tok, b, i = tok[3:-3], True, True
        elif tok.startswith('**'):
            tok, b = tok[2:-2], True
        elif tok.startswith('*') and len(tok) > 1:
            tok, i = tok[1:-1], True
        elif tok.startswith('`'):
            tok = tok[1:-1]
        rpr = f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>'
        rpr += '<w:b/>' if b else ''
        rpr += '<w:i/>' if i else ''
        rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
        out.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(tok)}</w:t></w:r>')
    return ''.join(out)


def para(text, jc="both", b=False, i=False, size=24, before=0, after=120, line=360,
         hanging=False, keep=False, page_break=False):
    ppr = f'<w:spacing w:before="{before}" w:after="{after}" w:line="{line}" w:lineRule="auto"/>'
    ppr += f'<w:jc w:val="{jc}"/>'
    if hanging:
        ppr += '<w:ind w:left="567" w:hanging="567"/>'
    if keep:
        ppr += '<w:keepNext/>'
    if page_break:
        ppr += '<w:pageBreakBefore/>'
    return f'<w:p><w:pPr>{ppr}</w:pPr>{runs(text, b, i, size)}</w:p>'


def table(rows):
    ncol = max(len(r) for r in rows)
    total = 9070
    w = total // ncol
    xml = ['<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/>' % total,
           '<w:tblBorders>' + ''.join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                                      for s in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV')) +
           '</w:tblBorders><w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>']
    xml += [f'<w:gridCol w:w="{w}"/>' for _ in range(ncol)]
    xml.append('</w:tblGrid>')
    for k, row in enumerate(rows):
        row = row + [''] * (ncol - len(row))
        xml.append('<w:tr>')
        for cell in row:
            shade = '<w:shd w:val="clear" w:color="auto" w:fill="E7E6E6"/>' if k == 0 else ''
            xml.append(f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{shade}</w:tcPr>'
                       + para(cell.strip(), jc="left", b=(k == 0), size=18, after=0, line=240) + '</w:tc>')
        xml.append('</w:tr>')
    xml.append('</w:tbl>')
    return ''.join(xml) + para('', after=120)


def convert(md, first_page_break=False):
    body, lines, k = [], md.split('\n'), 0
    pending_break, in_refs = first_page_break, False
    while k < len(lines):
        l = lines[k].rstrip()
        if l.startswith('|'):
            rows = []
            while k < len(lines) and lines[k].startswith('|'):
                cells = lines[k].strip().strip('|').split('|')
                if not re.match(r'^\s*:?-+:?\s*$', cells[0]):
                    rows.append(cells)
                k += 1
            if rows:
                body.append(table(rows))
            continue
        if not l.strip():
            k += 1
            continue
        if l.startswith('# '):
            body.append(para(l[2:], jc="left", b=True, size=28, after=240, keep=True, page_break=pending_break))
            pending_break, in_refs = False, False
        elif l.startswith('## '):
            titre = l[3:]
            in_refs = bool(REFERENCES.match(titre))
            body.append(para(titre, jc="left", b=True, size=24, before=240, after=120, keep=True,
                             page_break=in_refs or pending_break))
            pending_break = False
        elif l.startswith('### '):
            body.append(para(l[4:], jc="left", b=True, i=True, size=24, before=120, after=120, keep=True))
        elif re.match(r'^\s*[-*+]\s+', l) and not in_refs:
            body.append(para('\u2022\t' + re.sub(r'^\s*[-*+]\s+', '', l), jc="left", hanging=True, after=60))
        else:
            body.append(para(l, hanging=in_refs, jc="left" if in_refs else "both"))
        k += 1
    return ''.join(body)


def page_de_garde(titre, sous_titre, livrable, remise, nb_mots):
    lignes = []
    if rempli(GARDE.get("ecole")):
        lignes.append(para(GARDE["ecole"], jc="center", b=True, size=28, before=1200, after=120))
    if rempli(GARDE.get("programme")):
        lignes.append(para(GARDE["programme"], jc="center", size=24, after=1200))
    if livrable:
        lignes.append(para(livrable, jc="center", size=24, after=480))
    lignes.append(para(titre, jc="center", b=True, size=36, after=240 if sous_titre else 1200, line=300))
    if sous_titre:
        lignes.append(para(sous_titre, jc="center", i=True, size=26, after=1200, line=300))
    for cle, etiquette in (("auteur", "Auteur"), ("direction_du_memoire", "Direction du mémoire"),
                           ("annee_universitaire", "Année universitaire")):
        if rempli(GARDE.get(cle)):
            lignes.append(para(f'{etiquette} : {GARDE[cle]}', jc="center", size=24, after=120))
    if remise:
        lignes.append(para(f'Remis le {remise}', jc="center", size=24, after=120))
    lignes.append(para(f'Nombre de mots : {nb_mots} (hors page de garde, notes et bibliographie)',
                       jc="center", size=22, after=0))
    return ''.join(lignes)


def main():
    ap = argparse.ArgumentParser(description="Convertit un texte Markdown du mémoire en Word.")
    ap.add_argument("texte", help="fichier Markdown du texte")
    ap.add_argument("--annexe", help="fichier Markdown des annexes (après un saut de page)")
    ap.add_argument("--sortie", help="fichier .docx à écrire (par défaut : même nom que le texte)")
    ap.add_argument("--livrable", default="", help='intitulé de l\'étape sur la page de garde (ex. "Livrable 1")')
    ap.add_argument("--remise", default="", help='date de remise (ex. "14 octobre 2026")')
    a = ap.parse_args()
    sortie = a.sortie or os.path.splitext(a.texte)[0] + ".docx"

    with open(a.texte, encoding='utf-8') as f:
        texte = f.read()
    nb_mots = compter(texte)
    lignes = texte.split('\n')
    if not lignes[0].startswith('# '):
        raise SystemExit("La première ligne du texte doit être son titre (« # Titre »).")
    titre, reste = lignes[0][2:].strip(), lignes[1:]
    while reste and not reste[0].strip():
        reste = reste[1:]
    sous_titre = ''
    if reste and re.fullmatch(r'\*[^*].*\*', reste[0].strip()):
        sous_titre, reste = reste[0].strip()[1:-1], reste[1:]
    notes, corps = {}, []
    for l in reste:
        m = re.match(r'^\[\^(\d+)\]:\s*(.*)$', l)
        if m:
            notes[m.group(1)] = m.group(2)
        else:
            corps.append(l)
    annexe = ''
    if a.annexe:
        with open(a.annexe, encoding='utf-8') as f:
            annexe = f.read()

    marges = ('<w:pgSz w:w="11906" w:h="16838"/>'
              '<w:pgMar w:top="1418" w:right="1418" w:bottom="1418" w:left="1418" w:header="709" w:footer="709" w:gutter="0"/>')
    sect_garde = f'<w:p><w:pPr><w:sectPr>{marges}</w:sectPr></w:pPr></w:p>'  # la page de garde n'est pas numérotée
    sect_final = f'<w:sectPr><w:footerReference w:type="default" r:id="rIdFooter"/>{marges}<w:pgNumType w:start="1"/></w:sectPr>'
    W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           f'<w:document {W} xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>'
           + page_de_garde(titre, sous_titre, a.livrable, a.remise, nb_mots) + sect_garde
           + convert('\n'.join(corps)) + (convert(annexe, first_page_break=True) if annexe else '')
           + sect_final + '</w:body></w:document>')

    rpr_pied = f'<w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/><w:sz w:val="20"/></w:rPr>'
    footer = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              f'<w:ftr {W}><w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
              f'<w:r>{rpr_pied}<w:fldChar w:fldCharType="begin"/></w:r>'
              f'<w:r>{rpr_pied}<w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
              f'<w:r>{rpr_pied}<w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')
    styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              f'<w:styles {W}>'
              f'<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="{FONT}" w:eastAsia="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>'
              '<w:sz w:val="24"/><w:szCs w:val="24"/><w:lang w:val="fr-FR"/></w:rPr></w:rPrDefault>'
              '<w:pPrDefault><w:pPr><w:spacing w:line="360" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
              '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>'
              '</w:styles>')
    fn = ['<w:footnote w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:footnote>',
          '<w:footnote w:type="continuationSeparator" w:id="0"><w:p><w:r><w:continuationSeparator/></w:r></w:p></w:footnote>']
    for k, v in notes.items():
        fn.append(f'<w:footnote w:id="{k}"><w:p><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr>'
                  f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/><w:vertAlign w:val="superscript"/><w:sz w:val="20"/></w:rPr><w:footnoteRef/></w:r>'
                  + runs(' ' + v, size=20) + '</w:p></w:footnote>')
    footnotes = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:footnotes {W}>' + ''.join(fn) + '</w:footnotes>'
    settings = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:settings {W}>'
                '<w:footnotePr><w:footnote w:id="-1"/><w:footnote w:id="0"/></w:footnotePr></w:settings>')
    ct = 'application/vnd.openxmlformats-officedocument.wordprocessingml.'
    content_types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="xml" ContentType="application/xml"/>'
                     f'<Override PartName="/word/document.xml" ContentType="{ct}document.main+xml"/>'
                     f'<Override PartName="/word/styles.xml" ContentType="{ct}styles+xml"/>'
                     f'<Override PartName="/word/footer1.xml" ContentType="{ct}footer+xml"/>'
                     f'<Override PartName="/word/footnotes.xml" ContentType="{ct}footnotes+xml"/>'
                     f'<Override PartName="/word/settings.xml" ContentType="{ct}settings+xml"/>'
                     '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
                     '</Types>')
    rel = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="rId1" Type="{rel}officeDocument" Target="word/document.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '</Relationships>')
    doc_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f'<Relationship Id="rIdStyles" Type="{rel}styles" Target="styles.xml"/>'
                f'<Relationship Id="rIdFooter" Type="{rel}footer" Target="footer1.xml"/>'
                f'<Relationship Id="rIdFootnotes" Type="{rel}footnotes" Target="footnotes.xml"/>'
                f'<Relationship Id="rIdSettings" Type="{rel}settings" Target="settings.xml"/>'
                '</Relationships>')
    core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            f'xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>{escape(titre)}</dc:title><dc:language>fr-FR</dc:language>'
            '</cp:coreProperties>')

    with zipfile.ZipFile(sortie, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', rels)
        z.writestr('word/document.xml', doc)
        z.writestr('word/_rels/document.xml.rels', doc_rels)
        z.writestr('word/styles.xml', styles)
        z.writestr('word/footer1.xml', footer)
        z.writestr('word/footnotes.xml', footnotes)
        z.writestr('word/settings.xml', settings)
        z.writestr('docProps/core.xml', core)
    print('Écrit : {} ({} mots)'.format(sortie, nb_mots))


if __name__ == '__main__':
    main()
