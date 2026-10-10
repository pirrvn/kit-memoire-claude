---
name: jury
description: Faire évaluer un texte du mémoire (livrable officiel ou document de travail). Vérification d'abord, puis jury à l'aveugle de trois juges, enregistrement des notes et propositions d'amélioration à valider par l'auteur.
---

# Faire passer un texte devant le jury

Protocole complet : jury/LISEZMOI.md. Dire en une phrase où l'on en est à chaque étape.

## 1. Cadrer

- Quel texte, quelle étape, quelle version ? Livrable officiel (deux passages par juge : opus et sonnet) ou document de travail (un passage : sonnet) ?
- Grilles : jury-academique, grille officielle de l'étape (jury/grilles/grille_<étape>.md) et grille_excellence ; jury-pro, grille_pro ; jury-ingenieur-ia, grille_ingenieur_ia.

## 2. Vérifier d'abord

- Le vérificateur contrôle le texte et écrit memoire/<étape>/VERIFICATION_<texte>.md.
- BLOQUANT : on corrige (rédacteur), puis on ne refait vérifier que les passages modifiés. Pas de jury sur un texte bloqué.
- Compter les mots : `python3 systeme/outils/compter_mots.py <texte>`.

## 3. Préparer le dossier à l'aveugle

Dossier jury/<étape>_<version>/ (exemple : jury/livrable1_v2/) :
- TEXTE.md : copie du texte sous un label neutre (exemple : « Document A »), sans numéro de version, sans commentaire, sans nom.
- CONTEXTE.md : discipline, niveau, consigne de l'école pour cette étape (longueur, attendus), profil de l'auteur sans nom. Rien sur les versions précédentes ni sur ce qu'on espère.

## 4. Lancer les juges (en parallèle)

Pour chaque juge, chaque grille et chaque modèle, un agent (subagent_type = le juge, model = opus ou sonnet) avec une consigne courte :
- fichiers à lire : jury/LISEZMOI.md, la grille, CONTEXTE.md, TEXTE.md ; en plus consignes/SYNTHESE_ECOLE.md pour jury-academique, et sources/REGISTRE.csv (plus les textes sources à contrôler, si on veut un contrôle des citations) pour jury-ingenieur-ia ;
- fichier de sortie : jury/<étape>_<version>/<juge>_<grille>_<modèle>.txt ;
- en-tête à reprendre : texte (le label neutre), version, passage (1 pour opus, 2 pour sonnet), grille.

Un modèle indisponible se remplace par un autre modèle de premier rang, et le remplacement est signalé (L-006).

## 5. Enregistrer et lire

- `python3 systeme/outils/noter.py jury/<étape>_<version> --sortie jury/<étape>_<version>/RESULTATS.md --commentaires jury/<étape>_<version>/COMMENTAIRES.md`
- Lire RESULTATS.md et COMMENTAIRES.md, pas les évaluations brutes. Signaler tout écart de plus de 4 points entre passages.

## 6. Rendre compte à l'auteur

- Les notes par grille, comparées aux versions précédentes (jury/NOTES.csv).
- Les critiques convergentes (au moins deux juges), puis les isolées.
- Des propositions numérotées (C1, C2...) : le changement, sa raison, son effet attendu sur la note, son coût. L'auteur choisit ; on applique en une fois dans la version suivante (L-012).
- Pour un livrable officiel : proposer de lancer le contradicteur et d'alimenter memoire/CARNET_DE_MAITRISE.md avec les questions difficiles.
