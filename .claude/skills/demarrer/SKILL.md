---
name: demarrer
description: Premier lancement du kit. Configure le projet de mémoire (école, sujet, calendrier, terrain, jury, veille) par un court entretien, puis tire des documents de l'école la synthèse des consignes et les grilles du jury. À lancer une seule fois, au tout début.
---

# Démarrer un nouveau mémoire

But : en une session, passer du kit vierge à un projet configuré, prêt pour /tournoi. Parler en français simple, une étape à la fois, et dire en une phrase où l'on en est.

## 1. Entretien (une dizaine de questions au plus)

Poser les questions par petits groupes (AskUserQuestion quand il y a des options, sinon question ouverte). Ne jamais demander le nom réel de l'employeur, de l'organisation étudiée ou des personnes à interroger : des codes suffisent.

1. École, programme, année universitaire ; dates de remise et poids de chaque étape ; soutenance ou non.
2. Thème ou idée de sujet, même vague ; discipline ; langue de rédaction ; démarche pressentie (qualitative, quantitative, ne sait pas).
3. Profil de l'auteur : métier, expérience utile, ce qu'il veut maîtriser en priorité.
4. Terrain possible : à qui ou à quoi il a vraiment accès (entretiens, questionnaires, données, archives), avec quel accord, quelles contraintes de confidentialité.
5. Sources : bibliothèque et bases accessibles ; classements de revues reconnus par l'école.
6. Politique de l'école sur l'IA : permise ou non, pour quelles parties, à déclarer ou non et comment. Si l'auteur ne sait pas, noter « à vérifier » et l'ajouter à ETAT.md comme action prioritaire.
7. Le lecteur professionnel idéal : quel décideur du secteur lirait ce mémoire avec intérêt ? (sert au juge jury-pro)
8. Pour la page de garde : nom de l'auteur et de la direction du mémoire (ils restent dans systeme/config.json ; prévenir que ce fichier ne doit pas être publié).

## 2. Remplir les fichiers du projet

- PROJET.md : toutes les rubriques « À REMPLIR ».
- systeme/config.json : page de garde, et e-mail de contact pour OpenAlex et Crossref si l'auteur le souhaite.
- .claude/agents/jury-academique.md et .claude/agents/jury-pro.md : le bloc « Profil », en deux ou trois lignes concrètes.
- jury/grilles/grille_pro.md : adapter les exemples des quatre critères au secteur (réglementation, métiers), sans changer leur structure ; mettre la date de figement.
- DECISIONS.md : D-001 (lancement : sujet de départ, école, calendrier, terrain envisagé), avec les mots de l'auteur.

## 3. Consignes de l'école

- Si consignes/originaux/ contient des documents : les lire (PDF avec l'outil Read et le paramètre pages ; sur Mac, sans installation, voir systeme/LECONS.md L-013) ; remplir consignes/SYNTHESE_ECOLE.md section par section, chaque règle suivie de la section d'origine entre parenthèses ; transcrire chaque grille officielle dans jury/grilles/ selon grille_officielle_MODELE.md et mettre à jour le tableau du calendrier de PROJET.md.
- Sinon : dire précisément quels documents déposer (guide du mémoire, grilles d'évaluation de chaque étape, fiches pratiques) et où (consignes/originaux/), puis continuer le reste. La synthèse et les grilles se feront dès leur arrivée.
- Repérer dans ces documents ce qu'ils disent de l'IA et le reporter dans PROJET.md.

## 4. Veille

- Proposer 4 à 6 requêtes OpenAlex sur le sujet (expressions exactes entre guillemets, recherche dans les titres et résumés) ; les écrire dans systeme/config.json ; tester avec `python3 systeme/outils/veille.py --essai --depuis <date d'il y a 60 jours>` ; resserrer les requêtes trop bruyantes.
- Proposer, avec l'OK de l'auteur, une tâche programmée chaque semaine qui lance la veille et ajoute les nouveautés pertinentes à idees/BOITE_A_IDEES.md avec le statut « nouvelle, à vérifier ».

## 5. Historique et sauvegarde

- Si le dossier vient d'un `git clone` du kit, il pointe encore vers le dépôt public du kit : proposer `git remote remove origin` pour ne jamais y envoyer le mémoire par erreur.
- Si git n'est pas encore utilisé : proposer `git init` (si git est absent, on s'en passe).
- Premier commit en français : « Configuration du projet ».

## 6. Fin

- ETAT.md : état (« projet configuré »), plan de la prochaine session (/tournoi, ou dépôt des documents de l'école s'ils manquent), trois idées prioritaires.
- Dire à l'auteur, en cinq lignes au plus : ce qui est prêt, ce qui manque, et qu'il faut ouvrir une nouvelle session pour que les agents personnalisés soient chargés.
- Finir par « Ce que tu as à faire ».
