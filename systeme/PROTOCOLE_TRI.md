# Protocole de tri d'une recherche systématique

Idées reprises de Wu, C.-I. (2026), Academic Research Skills for Claude Code, module sr-screener, https://github.com/Imbad0202/academic-research-skills (licence CC BY-NC 4.0), adaptées. S'applique à toute recherche systématique du mémoire (preuve du manque, revue de littérature).

## Avant le tri

1. Écrire le protocole avant de lire les notices, dans sources/rapports/recherche_AAAA-MM-JJ/protocole.json : question, requêtes exactes, critères d'inclusion, codes d'exclusion numérotés dans un ordre fixe (E1, E2...), études témoins. Tout ajout en cours de route est daté et signalé.
2. **Études témoins.** Lister 3 à 5 études qu'on sait pertinentes (leur DOI). Si la recherche ne retrouve pas l'une d'elles, corriger les requêtes ou ajouter une base avant de trier : le tri ne rattrape jamais ce que la recherche n'a pas ramené. Les témoins ne prouvent pas que rien d'autre n'a été perdu.
3. Lancer `python3 systeme/outils/recherche_systematique.py sources/rapports/recherche_AAAA-MM-JJ` : il interroge OpenAlex, fusionne et dédoublonne les notices (corpus.csv), compte les effectifs à chaque étape (flux.json) et dit quels témoins manquent.

Exemple de protocole.json :

```json
{
  "question": "Que sait-on de la façon dont les salariés vivent l'indicateur X ?",
  "date_protocole": "2026-10-10",
  "requetes": [
    {"nom": "Q1_indicateur_salaries", "champ": "title_and_abstract.search", "valeur": "\"indicateur X\" AND (employee OR employees OR staff)"},
    {"nom": "Q2_citent_article_fondateur", "champ": "cites", "valeur": "W1234567890"}
  ],
  "filtre_commun": "",
  "maximum_par_requete": 2000,
  "temoins": ["10.1234/exemple.2019.001"],
  "criteres_inclusion": ["étude empirique", "porte sur des personnes au travail"],
  "codes_exclusion": ["E1 homonyme ou hors domaine", "E2 pas de données empiriques", "E3 population hors champ"]
}
```

Champs OpenAlex utiles : `title_and_abstract.search` (titres et résumés, opérateurs AND, OR, NOT, expressions entre guillemets ; pas de virgule dans la valeur), `cites` (identifiant OpenAlex W... de l'article cité, lisible sur openalex.org ; plusieurs séparés par « | » ; W1234567890 n'est qu'un exemple). `filtre_commun` s'ajoute à chaque requête (exemple : `publication_year:2010-2026`).

## Règles de décision (titre et résumé)

1. On juge la notice seule (titre, résumé, type de publication), jamais le souvenir qu'on a de l'étude.
2. Étiquettes : inclus, à vérifier (critères essentiels plausibles, texte insuffisant), exclu.
3. On exclut pour le premier code clairement non rempli, dans l'ordre du protocole. « Clairement » veut dire que la notice l'écrit, pas qu'on le soupçonne.
4. Un critère qui ne se juge qu'au texte intégral n'exclut jamais à ce stade : le silence du résumé n'est pas un échec.
5. Notice sans résumé : elle n'avance que si le titre suggère les critères essentiels ; on l'exclut si le titre ou le type de publication échoue clairement.
6. Le motif de chaque décision est un fait tiré de la notice, en 15 mots au plus (« questionnaire auprès d'étudiants », « modèle théorique sans données »), jamais une redite de l'étiquette (« hors sujet »).
7. Entre avancer et exclure une notice plausible, on avance.

Les décisions vont dans tri.csv, à côté du corpus : id;doi;titre;decision;code;motif;trieur.

## Contrôle

1. **Contrôle à l'aveugle.** Au moins 20 exclusions tirées au hasard (graine notée pour pouvoir refaire le tirage) sont relues par un relecteur qui ne voit ni l'étiquette ni le motif d'origine. Si plusieurs auraient dû avancer, on cherche la cause (un code, un lot, les notices sans résumé) avant de se fier au tri.
2. **Second trieur humain.** Une IA qui relit deux fois n'est pas deux relecteurs indépendants. L'auteur trie lui-même un échantillon de 20 à 30 notices (`--echantillon 25 --graine 7` produit echantillon_humain.csv : titre, résumé, colonnes vides pour sa décision et son motif), sans voir les décisions de l'IA ; on publie l'accord observé et les désaccords discutés.
3. **Deux trieurs IA (tri large).** Un « expert du sujet » et un « méthodologiste », chacun sans voir l'autre ; un arbitre tranche les désaccords en voyant les deux étiquettes, pas les raisons. Rapporter l'accord observé, le kappa de Cohen et le PABAK, avec les comptes : quand presque tout est exclu, le kappa est bas même si l'accord est excellent.
