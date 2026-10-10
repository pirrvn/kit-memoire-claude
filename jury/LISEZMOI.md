# Le jury permanent : protocole

## Composition

| Juge | Agent | Grilles utilisées |
|---|---|---|
| Universitaire | jury-academique | grille officielle de l'étape (livrable 1, livrable 2 ou final) et grille d'excellence |
| Professionnel du secteur | jury-pro | grille_pro |
| Ingénieur IA | jury-ingenieur-ia | grille_ingenieur_ia |

Pour un choix entre plusieurs pistes (tournoi), les trois juges utilisent la même grille : grille_tournoi.

## Règles contre la complaisance

1. **Anonymat.** Le texte noté porte un label neutre (par exemple « Piste Alpha » ou « Document A »). Le juge ne sait ni qui l'a écrit, ni de quelle version il s'agit, ni ce que recommande le chef de projet. Il ne lit que les fichiers indiqués dans sa consigne.
2. **Nombre de passages.** Documents de travail : un passage par juge, sur sonnet. Livrables officiels : deux passages indépendants par juge, sur opus et sur sonnet ; on retient la moyenne de chaque critère (noter.py) et l'on signale tout écart de plus de 4 points entre passages. Pas de petit modèle : il note trop large (systeme/LECONS.md, L-007).
3. **Preuve obligatoire.** Chaque note est justifiée et accompagnée d'une courte citation du texte évalué. Une note maximale exige une preuve explicite.
4. **Pas de prime à la longueur.** Un texte plus long n'est pas meilleur pour autant ; les modèles qui jugent ont tendance à favoriser les réponses longues (Zheng et al., 2023, « Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena », arXiv:2306.05685).
5. **Ancrage humain.** Une fois par étape si possible, un lecteur humain note le même texte avec la même grille ; et quand l'école rend sa note, on la compare à celle du jury pour le calibrer.
6. **Grilles figées.** Les grilles de jury/grilles/ ne changent qu'avec l'OK de l'auteur ; on renote alors les versions déjà notées pour garder des notes comparables.
7. **Le fond, pas le style.** Une idée juste dite simplement vaut une idée juste bien tournée ; une phrase fluide ne prouve rien. Le juge isole d'abord l'affirmation et la confronte au texte et aux sources.
8. **Une exigence a une source.** Une critique fondée sur « on attend X dans ce type de travail » cite la grille ou le guide de l'école (consignes/SYNTHESE_ECOLE.md). Sinon, elle est marquée « [exigence non sourcée] » et ne fait pas perdre plus d'un quart de point.

## Repères de notation (communs à tous les juges)

| Note sur 20 | Signification |
|---|---|
| 8 | insuffisant : exigences minimales non remplies |
| 10 | passable : exigences minimales tout juste remplies |
| 12 | correct |
| 14 | bon |
| 16 | très bon |
| 18 | excellent, au niveau des meilleurs mémoires |
| 19 à 20 | exceptionnel, rarissime |

## Dossier d'une évaluation

jury/<étape>_<version>/ (exemple : jury/livrable1_v2/) contient : TEXTE.md (copie sous un label neutre), CONTEXTE.md (contexte neutre : discipline, niveau, consigne de l'étape, profil de l'auteur sans nom), une évaluation par juge, grille et modèle (<juge>_<grille>_<modèle>.txt), puis RESULTATS.md et COMMENTAIRES.md produits par noter.py. La commande /jury enchaîne tout.

## Format obligatoire d'une évaluation

Le juge écrit son évaluation dans le fichier qu'on lui indique, exactement sous cette forme (les colonnes sont séparées par « | », sans « | » à l'intérieur d'une colonne) :

```
=== EVALUATION ===
juge: jury-academique
modele: opus
passage: 1
texte: Document A
version: v1
grille: livrable1
CRITERE | NOTE | MAX | JUSTIFICATION | PREUVE
A1 | 1 | 1 | justification en une ou deux phrases | « courte citation du texte »
...
=== COMMENTAIRES ===
FORCES: ...
FAIBLESSES: ...
POUR GAGNER 2 POINTS: ...
=== FIN ===
```

## Enregistrement

`python3 systeme/outils/noter.py <dossier des évaluations> --sortie <dossier>/RESULTATS.md --commentaires <dossier>/COMMENTAIRES.md` ajoute les notes à jury/NOTES.csv (date;production;version;juge;modele;passage;grille;critere;note;max;justification;preuve), une seule fois par évaluation, et donne la note de chaque juge et la moyenne des juges, grille par grille.

Pour un tournoi par duels (deux pistes comparées), chaque fichier de duel contient les lignes `gauche:`, `droite:`, `vainqueur:`, `critere decisif:` et `modele:` ; `python3 systeme/outils/noter.py --duels <dossier>` compte les victoires.
