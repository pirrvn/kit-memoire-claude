# Textes du mémoire

Un dossier par étape : cadrage/ (documents de travail du début), livrable1/, livrable2/, final/ (adapter aux étapes de ton école).

Dans chaque dossier :
- **PLAN.md** : le plan validé par l'auteur avant toute rédaction ;
- **<étape>_vN.md** : chaque version, jamais écrasée (livrable1_v1.md, livrable1_v2.md...) ;
- **VERIFICATION_<étape>_vN.md** : le rapport du vérificateur ;
- **RAPPORT_DECISIONS_vN.md** : avant une nouvelle version, la liste des changements proposés, leur raison et leur effet attendu, que l'auteur valide (systeme/LECONS.md, L-012) ;
- **<Étape>_vN.docx** : la version Word, produite par systeme/outils/md2docx.py.

**CARNET_DE_MAITRISE.md** (à la racine de memoire/) : les notions, auteurs, chiffres et réponses aux questions difficiles que l'auteur doit savoir expliquer seul. Il grossit à chaque passage du contradicteur.

## Écrire en Markdown simple

`# Titre` (première ligne, va sur la page de garde), une ligne en *italique* juste dessous pour un sous-titre éventuel, `## Parties`, `### Sous-parties`, *italique*, **gras**, notes de bas de page `[^1]` (avec `[^1]: texte de la note` plus bas), tableaux, et une partie `## Références` (ou `## Bibliographie`) à la fin.

Puis : `python3 systeme/outils/md2docx.py memoire/livrable1/livrable1_v1.md --livrable "Livrable 1" --remise "date de remise"` produit le Word à côté du texte : page de garde, police et interligne réglés, notes de bas de page, bibliographie en retrait, pages numérotées, nombre de mots calculé.
