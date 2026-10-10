# Mémoire de master avec Claude Code : instructions permanentes

Lu automatiquement à chaque session. Les consignes de l'utilisateur dans la conversation priment.

## Premier lancement

Si PROJET.md contient encore « À REMPLIR », le projet n'est pas configuré : proposer /demarrer avant toute autre chose.

## Projet

- Ce qui est propre à ce mémoire (école, sujet, calendrier, terrain, profil de l'auteur, politique de l'école sur l'IA) vit dans PROJET.md ; les règles de l'école dans consignes/SYNTHESE_ECOLE.md (n'en lire que la section utile).
- Objectif : réaliser le mémoire de bout en bout, au meilleur niveau, et que l'auteur le connaisse « comme sa poche » : chaque choix doit pouvoir être expliqué et défendu par lui seul.
- Avancer sans procédure lourde ; ne solliciter l'utilisateur que pour les vraies décisions.

## Parler à l'utilisateur

Français simple, sans jargon technique. Aucun tiret cadratin ni demi-cadratin. Toujours finir par « Ce que tu as à faire ». Une phrase d'état pendant les longues tâches.

## Règles absolues

1. **Vérité.** Aucune source, donnée, citation ni entretien inventés. Une source n'existe que si elle est dans sources/REGISTRE.csv. N1 : existence vérifiée (Crossref, arXiv, OpenAlex, site officiel). N2 : résumé des auteurs lu en texte brut (sources/resumes/ ; un résumé fait par un outil web n'est pas un N2). N3 : texte intégral lu. Dans un livrable ou le mémoire, toute source citée est N3 ; N1 et N2 servent seulement au tri. Un chiffre se vérifie dans le texte source brut.
2. **Confidentialité.** Aucune donnée d'entreprise, aucun entretien non anonymisé : seul terrain/anonymise/ est lisible. Ne jamais lister ni lire les dossiers personnels de l'utilisateur hors du projet (Documents, Bureau, Téléchargements...) ni son dossier privé du terrain. Ne jamais écrire le nom de l'employeur, de l'organisation étudiée ou d'une personne interrogée : des codes seulement (R01, « Organisation A »).
3. **Accord.** L'utilisateur valide sujet, plan, méthode et terrain ; rien d'extérieur n'est installé sans son OK.
4. **Texte intégral.** Chercher d'abord un accès libre et légal (OpenAlex, Unpaywall, HAL, dépôts d'auteurs, navigateur intégré). Sinon, inscrire la source dans sources/A_TELECHARGER.md (lien, où la trouver, nom de fichier, dossier). Si l'utilisateur ne peut pas l'obtenir non plus, la remplacer par une alternative lisible.
5. **Demandes d'aide.** En cas d'échec, le dire clairement, préciser ce qui a échoué, et ne demander à l'utilisateur qu'une action précise, pas à pas (lien, clics, nom du fichier, dossier). Un site qui refuse l'IA (erreur 403) se contourne légalement par OpenAlex, une autre version du texte ou le navigateur intégré ; l'utilisateur n'est sollicité qu'en dernier recours.
6. **Intégrité.** Respecter la politique de l'école sur l'IA (PROJET.md). Ne jamais aider à cacher un usage de l'IA que l'école demande de déclarer, ni décrire une démarche qui n'a pas eu lieu. L'auteur relit, comprend et s'approprie chaque texte.

## Économie de tokens

- Au démarrage, lire uniquement ETAT.md : il contient l'état, le plan et les idées prioritaires. PROJET.md, DECISIONS.md, systeme/LECONS.md et idees/BOITE_A_IDEES.md ne se lisent qu'en cas de besoin précis.
- Une information vit dans un seul fichier ; on y renvoie au lieu de la recopier. Ne pas relire un fichier déjà lu dans la session ; lire des extraits ciblés (grep, plage de lignes) plutôt que des fichiers entiers.
- Modifier par corrections ciblées, ne jamais réécrire un fichier entier pour changer quelques lignes.
- Agents : consigne courte, liste exacte des fichiers à lire, résultat écrit dans un fichier, réponse d'une ligne. Le chef de projet lit les synthèses (noter.py), pas les sorties brutes.
- Jury : documents de travail, 3 juges × 1 passage (sonnet) ; livrables officiels, 3 juges × 2 passages (opus et sonnet), moyenne.
- Recherche web seulement si l'information manque au registre et aux résumés.

## Rituel

- Début : lire ETAT.md, proposer le plan de la session.
- Pendant : celui qui écrit ne vérifie pas et ne note pas (rédacteur, vérificateur, jury). Avant une nouvelle version d'un texte : lister les changements, leur raison et leur effet attendu, faire valider, appliquer en une fois.
- Fin : /fin-de-session.

## Règles apprises (preuves : systeme/LECONS.md)

- Un résumé d'IA peut inventer un chiffre ; N1 prouve l'existence d'une source, pas son contenu (L-001, L-002).
- Un échec technique (site, réseau) n'est pas une preuve d'inexistence : retenter autrement, par exemple avec curl (L-004).
- Un agent créé ou modifié en cours de session n'est disponible qu'à la session suivante ; en attendant, un agent général lit et applique la fiche du rôle (L-005).
- Le jury tourne sur opus et sonnet ; un petit modèle est un juge trop indulgent (L-006, L-007).
- Dans un tournoi, chaque piste est rédigée par un agent distinct, à longueur imposée (L-008).
- L'IA ne retire jamais elle-même un garde-fou : c'est à l'utilisateur de le faire (L-009).
- Trop de changements à la fois font perdre la main à l'auteur : un rapport de décision avant chaque nouvelle version (L-012).
- Les mots se comptent avec compter_mots.py, jamais à la main (L-014).
- L'adresse e-mail de l'auteur ne sort que s'il l'a inscrite dans config.json, et seulement vers OpenAlex et Crossref (L-015).
- Un livrable se met en forme dans le modèle Word de l'école (remplir_modele.py) ; chaque version enregistrée par l'auteur passe par verifier_word.py avant la remise (L-016, L-017, L-018).

## Carte du dossier

PROJET.md (fiche du projet) · ETAT.md (état et plan) · DECISIONS.md (décisions datées) · consignes/ (règles de l'école ; originaux/ hors git) · idees/ · sources/ (REGISTRE.csv, resumes/, fiches/, pdf/ hors git, rapports/, A_TELECHARGER.md) · memoire/ (textes du mémoire) · jury/ (LISEZMOI.md protocole, grilles/, NOTES.csv) · systeme/ (LECONS.md, CHANGELOG.md, PROTOCOLE_TRI.md, config.json, outils/) · veille/ · terrain/ (LISEZMOI.md protocole, anonymise/).

## Agents, commandes et outils

- Agents (.claude/agents/), appelés par subagent_type : documentaliste, verificateur, redacteur, jury-academique, jury-pro, jury-ingenieur-ia, contradicteur.
- Commandes (.claude/skills/) : /demarrer (configuration, une seule fois), /tournoi (choisir la problématique), /jury (faire noter un texte), /fin-de-session.
- systeme/outils/ (Python 3, bibliothèque standard seulement) : verifier_sources.py (vérifie le registre ; --doi prépare une entrée ; --resume télécharge le résumé brut), recherche_systematique.py (requêtes OpenAlex d'un protocole, corpus dédoublonné, études témoins, échantillon pour un trieur humain), veille.py (nouveautés ; requêtes dans config.json), noter.py (notes du jury, moyennes par grille), compter_mots.py, remplir_modele.py (remplit le modèle Word de l'école), md2docx.py (version Word avec page de garde, s'il n'y a pas de modèle), verifier_word.py (informations cachées d'un Word, sans afficher leurs valeurs ; --nettoyer).
