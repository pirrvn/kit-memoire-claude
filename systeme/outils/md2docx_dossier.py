"""Convertit un document de travail Markdown en Word lisible (dossier, carnet, compte rendu).

Usage : python3 systeme/outils/md2docx_dossier.py dossier.md sortie.docx

Pour les documents de travail, pas pour les livrables (ceux-ci passent par md2docx_modele.py et le modèle de l'école).
Reconnaît : # titre, ## ### #### intertitres (vrais styles de titre Word, visibles dans le volet de navigation),
paragraphes, listes à puces (- ) et numérotées (1. ), tableaux | a | b |, *italique*, **gras**, ***les deux***,
notes [^1] et [^1]: texte (vraies notes de bas de page). Ajoute un sommaire des intertitres ## et les numéros de page.
Propriétés neutres ; Word retirera les informations personnelles à chaque enregistrement. Bibliothèque standard.
"""
import re
import sys
import zipfile
from xml.dom import minidom
from xml.sax.saxutils import escape

SOURCE, SORTIE = sys.argv[1:3]
W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" ' \
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
POLICE = "Times New Roman"


def runs(text):
    out = []
    for tok in re.split(r'(\[\^\d+\]|\*\*\*.+?\*\*\*|\*\*.+?\*\*|\*[^*\s][^*]*?\*)', text):
        if not tok:
            continue
        m = re.fullmatch(r'\[\^(\d+)\]', tok)
        if m:
            out.append(f'<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteReference w:id="{m.group(1)}"/></w:r>')
            continue
        b = i = False
        if tok.startswith('***') and tok.endswith('***') and len(tok) > 6:
            tok, b, i = tok[3:-3], True, True
        elif tok.startswith('**') and tok.endswith('**') and len(tok) > 4:
            tok, b = tok[2:-2], True
        elif tok.startswith('*') and tok.endswith('*') and len(tok) > 2:
            tok, i = tok[1:-1], True
        rpr = ('<w:b/>' if b else '') + ('<w:i/>' if i else '')
        out.append(f'<w:r>{"<w:rPr>" + rpr + "</w:rPr>" if rpr else ""}<w:t xml:space="preserve">{escape(tok)}</w:t></w:r>')
    return ''.join(out)


def para(text, style=None, num=None, keep=False):
    ppr = ''
    if style:
        ppr += f'<w:pStyle w:val="{style}"/>'
    if keep:
        ppr += '<w:keepNext/>'
    if num:
        ppr += f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num}"/></w:numPr>'
    return f'<w:p>{"<w:pPr>" + ppr + "</w:pPr>" if ppr else ""}{runs(text)}</w:p>'


def table(rows):
    ncol = max(len(r) for r in rows)
    larg = 9638 // ncol
    bords = ''.join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
                    for s in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'))
    xml = [f'<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/><w:tblBorders>{bords}</w:tblBorders>'
           '<w:tblCellMar><w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>']
    xml += [f'<w:gridCol w:w="{larg}"/>'] * ncol
    xml.append('</w:tblGrid>')
    for k, row in enumerate(rows):
        row = row + [''] * (ncol - len(row))
        tr = '<w:trPr><w:tblHeader/></w:trPr>' if k == 0 else ''
        cells = ''
        for c in row:
            fond = '<w:shd w:val="clear" w:color="auto" w:fill="E7E6E6"/>' if k == 0 else ''
            texte = f'**{c.strip()}**' if k == 0 and c.strip() else c.strip()
            cells += f'<w:tc><w:tcPr><w:tcW w:w="{larg}" w:type="dxa"/>{fond}</w:tcPr>{para(texte, "TableText")}</w:tc>'
        xml.append(f'<w:tr>{tr}{cells}</w:tr>')
    xml.append('</w:tbl>')
    return ''.join(xml) + '<w:p><w:pPr><w:pStyle w:val="TableText"/></w:pPr></w:p>'


# --- lecture ---
lignes = open(SOURCE, encoding='utf-8').read().split('\n')
notes, corps = {}, []
for l in lignes:
    m = re.match(r'^\[\^(\d+)\]:\s*(.*)$', l)
    if m:
        notes[m.group(1)] = m.group(2)
    else:
        corps.append(l.rstrip())

# --- corps ---
body, nums, k, sommaire_fait = [], [], 0, False
titres2 = [l[3:] for l in corps if l.startswith('## ')]
while k < len(corps):
    l = corps[k]
    if l.startswith('|'):
        rows = []
        while k < len(corps) and corps[k].startswith('|'):
            cells = corps[k].strip().strip('|').split('|')
            if not re.match(r'^\s*:?-+:?\s*$', cells[0]):
                rows.append(cells)
            k += 1
        body.append(table(rows))
        continue
    if re.match(r'^(- |\d+\. )', l):
        ordonnee = bool(re.match(r'^\d+\. ', l))
        nums.append('decimal' if ordonnee else 'bullet')
        num_id = len(nums)
        while k < len(corps) and re.match(r'^(- |\d+\. )', corps[k]):
            body.append(para(re.sub(r'^(- |\d+\. )', '', corps[k]), 'ListParagraph', num_id))
            k += 1
        continue
    k += 1
    if not l.strip():
        continue
    if l.startswith('# '):
        body.append(para(l[2:], 'Title'))
    elif l.startswith('#### '):
        body.append(para(l[5:], 'Heading3'))
    elif l.startswith('### '):
        body.append(para(l[4:], 'Heading2'))
    elif l.startswith('## '):
        if titres2 and not sommaire_fait:
            body.append(para('Sommaire', 'Heading4', keep=True))
            nums.append('decimal')
            body += [para(t, 'ListParagraph', len(nums)) for t in titres2]
            sommaire_fait = True
        body.append(para(l[3:], 'Heading1'))
    else:
        body.append(para(l))

sect = ('<w:sectPr><w:footerReference w:type="default" r:id="rIdPied"/><w:footnotePr><w:numFmt w:val="decimal"/></w:footnotePr>'
        '<w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" '
        'w:header="567" w:footer="567" w:gutter="0"/></w:sectPr>')
document = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {W}><w:body>{"".join(body)}{sect}</w:body></w:document>'

# --- styles ---
def style(sid, nom, ppr='', rpr='', base='Normal', suivant='Normal', niveau=None):
    out = f'<w:style w:type="paragraph" w:styleId="{sid}"><w:name w:val="{nom}"/><w:basedOn w:val="{base}"/><w:next w:val="{suivant}"/><w:qFormat/>'
    if niveau is not None:
        ppr += f'<w:outlineLvl w:val="{niveau}"/>'
    return out + f'<w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>'

styles = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles {W}>'
          f'<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="{POLICE}" w:hAnsi="{POLICE}" w:eastAsia="{POLICE}" w:cs="{POLICE}"/>'
          '<w:sz w:val="23"/><w:szCs w:val="23"/><w:lang w:val="fr-FR"/></w:rPr></w:rPrDefault>'
          '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
          '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/><w:pPr><w:jc w:val="both"/></w:pPr></w:style>'
          + style('Title', 'Title', '<w:spacing w:after="240"/><w:jc w:val="left"/>', '<w:b/><w:sz w:val="40"/><w:szCs w:val="40"/>')
          + style('Heading1', 'heading 1', '<w:keepNext/><w:pageBreakBefore/><w:spacing w:before="0" w:after="200"/><w:jc w:val="left"/>', '<w:b/><w:color w:val="1F3864"/><w:sz w:val="32"/><w:szCs w:val="32"/>', niveau=0)
          + style('Heading2', 'heading 2', '<w:keepNext/><w:spacing w:before="280" w:after="120"/><w:jc w:val="left"/>', '<w:b/><w:color w:val="1F3864"/><w:sz w:val="27"/><w:szCs w:val="27"/>', niveau=1)
          + style('Heading3', 'heading 3', '<w:keepNext/><w:spacing w:before="200" w:after="80"/><w:jc w:val="left"/>', '<w:b/><w:sz w:val="24"/><w:szCs w:val="24"/>', niveau=2)
          + style('Heading4', 'heading 4', '<w:keepNext/><w:spacing w:before="120" w:after="60"/><w:jc w:val="left"/>', '<w:b/><w:i/>', niveau=3)
          + style('ListParagraph', 'List Paragraph', '<w:spacing w:after="60"/><w:ind w:left="567" w:hanging="283"/>')
          + style('TableText', 'Table Text', '<w:spacing w:before="20" w:after="20" w:line="240" w:lineRule="auto"/><w:jc w:val="left"/>', '<w:sz w:val="20"/><w:szCs w:val="20"/>')
          + style('FootnoteText', 'footnote text', '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/>', '<w:sz w:val="18"/><w:szCs w:val="18"/>')
          + '<w:style w:type="character" w:styleId="FootnoteReference"><w:name w:val="footnote reference"/><w:rPr><w:vertAlign w:val="superscript"/></w:rPr></w:style>'
          '</w:styles>')

# --- listes ---
def abstrait(i, t):
    fmt, texte, retrait = ('decimal', '%1.', 397) if t == 'decimal' else ('bullet', '•', 283)
    return (f'<w:abstractNum w:abstractNumId="{i}"><w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/>'
            f'<w:numFmt w:val="{fmt}"/><w:lvlText w:val="{texte}"/><w:lvlJc w:val="left"/>'
            f'<w:pPr><w:ind w:left="567" w:hanging="{retrait}"/></w:pPr></w:lvl></w:abstractNum>')


# une définition par liste : chaque liste numérotée repart à 1, quel que soit le logiciel de lecture
abstraits = ''.join(abstrait(i, t) for i, t in enumerate(nums, 1))
instances = ''.join(f'<w:num w:numId="{i}"><w:abstractNumId w:val="{i}"/></w:num>' for i in range(1, len(nums) + 1))
numbering = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:numbering {W}>{abstraits}{instances}</w:numbering>'

# --- notes, pied de page, paquet ---
fn = ''.join(f'<w:footnote w:id="{n}"><w:p><w:pPr><w:pStyle w:val="FootnoteText"/></w:pPr>'
             f'<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteRef/></w:r>'
             f'<w:r><w:t xml:space="preserve"> </w:t></w:r>{runs(t)}</w:p></w:footnote>' for n, t in notes.items())
footnotes = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:footnotes {W}>'
             '<w:footnote w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:footnote>'
             '<w:footnote w:type="continuationSeparator" w:id="0"><w:p><w:r><w:continuationSeparator/></w:r></w:p></w:footnote>'
             f'{fn}</w:footnotes>')
pied = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:ftr {W}><w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
        '<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')
settings = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:settings {W}><w:removePersonalInformation/>'
            '<w:defaultTabStop w:val="708"/><w:footnotePr><w:footnote w:id="-1"/><w:footnote w:id="0"/></w:footnotePr></w:settings>')
titre = next((l[2:] for l in corps if l.startswith('# ')), 'Document de travail')
parts = {
    '[Content_Types].xml': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
        '<Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>'
        '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
        '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>',
    '_rels/.rels': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/></Relationships>',
    'word/_rels/document.xml.rels': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '<Relationship Id="rIdNum" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
        '<Relationship Id="rIdNotes" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>'
        '<Relationship Id="rIdPied" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
        '<Relationship Id="rIdSettings" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/></Relationships>',
    'word/document.xml': document,
    'word/styles.xml': styles,
    'word/numbering.xml': numbering,
    'word/footnotes.xml': footnotes,
    'word/footer1.xml': pied,
    'word/settings.xml': settings,
    'docProps/core.xml': '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties '
        'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/">'
        f'<dc:title>{escape(titre)}</dc:title><dc:language>fr-FR</dc:language></cp:coreProperties>',
}
for n, v in parts.items():
    minidom.parseString(v.encode('utf-8'))
manquantes = set(re.findall(r'footnoteReference w:id="(\d+)"', document)) - set(notes)
if manquantes:
    sys.exit('Appels de note sans texte : ' + ', '.join(sorted(manquantes)))
with zipfile.ZipFile(SORTIE, 'w', zipfile.ZIP_DEFLATED) as z:
    for n, v in parts.items():
        z.writestr(n, v)
print(f'écrit {SORTIE} ({len(notes)} notes, {len(nums)} listes)')
