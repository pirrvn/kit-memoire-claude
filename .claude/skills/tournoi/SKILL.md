---
name: tournoi
description: Choisir la problématique du mémoire. Prépare un état de l'art court et deux à quatre pistes, les fait rédiger par des agents distincts à longueur égale, vérifier, puis noter à l'aveugle par le jury ; l'auteur tranche ensuite.
---

# Tournoi des problématiques

Dossier de travail : jury/tournoi_AAAA-MM/ (date du jour). Dire en une phrase où l'on en est à chaque étape.

## 1. Cadrage

1. Lire PROJET.md (sections « Sujet », « Terrain », « Auteur ») et la section 2 de consignes/SYNTHESE_ECOLE.md.
2. Confier au documentaliste un état de l'art court sur le thème : conversations académiques, débats, manques plausibles, 10 à 20 sources vérifiées (N1 au moins, N2 de préférence). Fusionner ses lignes dans sources/REGISTRE.csv après contrôle (`python3 systeme/outils/verifier_sources.py`).
3. En tirer deux à quatre pistes, chacune avec un manque identifié selon une technique admise par le guide, une problématique en une question, une démarche et un terrain réalistes pour cet auteur.
4. Présenter les pistes à l'auteur (titre et une ligne chacune) et les faire valider : il peut en retirer, en ajouter ou en modifier.

## 2. Rédaction des fiches

- Un agent redacteur distinct par piste (L-008), avec le même gabarit et la même longueur (600 à 700 mots) : manque visé et technique utilisée ; problématique ; concepts clés définis ; démarche, terrain et faisabilité ; intérêt théorique et managérial ; risques ; cinq sources clés du registre.
- Labels neutres : Alpha, Beta, Gamma, Delta, attribués au hasard. Fiches dans fiches/<label>.md ; correspondance dans CORRESPONDANCE.md, que le jury ne lit jamais.
- CONTEXTE.md : contexte neutre pour le jury (niveau, discipline, profil de l'auteur sans nom, terrain accessible, calendrier, minimums empiriques de l'école).

## 3. Vérification

Un vérificateur par fiche ; une fiche BLOQUANTE est corrigée par son rédacteur avant le jury.

## 4. Jury

- Trois juges (jury-academique, jury-pro, jury-ingenieur-ia), un passage sur sonnet par juge et par fiche, grille jury/grilles/grille_tournoi.md pour tous.
- Chaque juge lit : jury/LISEZMOI.md, la grille, CONTEXTE.md et une fiche ; il écrit evaluations/<juge>_<label>_sonnet.txt (en-tête : texte = « Piste <label> », version v1, grille tournoi).
- `python3 systeme/outils/noter.py jury/tournoi_AAAA-MM/evaluations --sortie jury/tournoi_AAAA-MM/RESULTATS.md --commentaires jury/tournoi_AAAA-MM/COMMENTAIRES.md`

## 5. Contradicteur

Le contradicteur passe la piste en tête aux neuf attaques ; son rapport va dans jury/tournoi_AAAA-MM/CONTRADICTEUR.md.

## 6. Décision

- Écrire SYNTHESE.md : classement, notes par critère, critiques convergentes des juges, failles relevées par le contradicteur, risque de biais (qui a recommandé quoi), recommandation argumentée.
- Présenter le choix à l'auteur (AskUserQuestion), avec la recommandation en premier. L'auteur tranche ; il peut aussi demander d'améliorer une piste ou de fusionner deux pistes.
- Noter la décision dans DECISIONS.md avec ses mots, la problématique dans PROJET.md, l'étape suivante dans ETAT.md.
