# Leçons du système

Chaque leçon part d'un fait constaté, porte sa preuve et produit une règle. Les leçons L-001 à L-014 viennent du premier mémoire mené avec ce système (automne 2026) ; elles sont livrées avec le kit pour qu'on ne refasse pas les mêmes erreurs. Les nouvelles leçons s'ajoutent à la suite, numérotées à partir de L-015.

## Modèle de rétrospective (fin de chaque session)

1. Chiffres : notes du jury (par production et version), sources par niveau (N1, N2, N3), erreurs repérées avant le jury.
2. Garder, arrêter, essayer.
3. Leçons nouvelles, au format ci-dessous.
4. Changements du système : les petits sont appliqués et notés dans CHANGELOG.md ; les gros sont proposés à l'auteur.

## L-001 · Un résumé d'IA peut inventer un chiffre

- Constat : l'outil de lecture web a résumé le communiqué officiel d'un organisme public en annonçant un chiffre annuel près de quatre fois plus petit que celui du PDF original.
- Règle : un chiffre se vérifie dans le texte source brut, jamais dans un résumé produit par une IA.
- Appliquée dans : CLAUDE.md (règle Vérité), agents documentaliste, vérificateur et rédacteur.

## L-002 · Des détails « vérifiés » ne l'étaient qu'à moitié

- Constat : quatre détails attribués à des articles dont l'existence était vérifiée (N1) venaient en fait de résumés d'outils et non des résumés originaux. Deux ont été confirmés par une autre version de la source (préprint, version acceptée en libre accès) ; deux n'ont pas pu l'être.
- Règle : le niveau N1 prouve qu'une source existe, pas ce qu'elle dit. Tout contenu attribué à une source est confirmé au niveau N2 ou N3 avant d'entrer dans le mémoire, et N3 pour toute source citée dans un livrable.

## L-003 · Lister un dossier personnel expose des informations

- Constat : pour créer le dossier privé du terrain, l'IA a listé les sous-dossiers du dossier Documents de l'utilisateur ; l'un d'eux révélait le nom de son employeur. Il n'a pas été ouvert et ce nom n'a été écrit nulle part.
- Règle : ne jamais lister ni parcourir les dossiers personnels ; l'auteur crée lui-même son dossier privé et en donne le chemin.

## L-004 · Un échec technique n'est pas une preuve d'inexistence

- Constat : la vérification d'une page web a échoué à cause du chiffrement (le Python fourni par Apple est ancien), alors que la page existe.
- Règle : en cas d'échec technique, retenter autrement (curl, navigateur intégré) avant de conclure.
- Appliquée dans : systeme/outils/verifier_sources.py (repli automatique sur curl).

## L-005 · Un agent créé en cours de session n'est disponible qu'à la session suivante

- Constat : l'appel d'un agent juste après la création de sa fiche a échoué (« agent introuvable »).
- Règle : dans la session où un agent est créé ou modifié, passer par un agent général qui lit et applique la fiche du rôle. Limite : cet agent général n'est pas techniquement restreint ; seule sa consigne l'est. C'est pourquoi /demarrer demande d'ouvrir une nouvelle session à la fin.

## L-006 · Un modèle peut devenir indisponible en plein travail

- Constat : les passages confiés à un modèle ont échoué (crédits épuisés pour ce modèle sur le compte), alors que les autres fonctionnaient.
- Règle : prévoir un modèle de remplacement de premier rang pour chaque passage du jury et signaler tout remplacement dans les résultats.

## L-007 · Tous les modèles ne sont pas de bons juges

- Constat : au premier tournoi, le plus petit modèle (haiku) a noté de 1 à 8 points plus haut qu'opus et sonnet, avec des écarts qui ne suivaient pas les critiques qu'il écrivait lui-même. Opus et sonnet étaient cohérents entre eux.
- Règle : le jury tourne sur opus et sonnet seulement. Tout écart de plus de 4 points entre passages est signalé.

## L-008 · Le chef de projet ne rédige pas seul les pièces qu'il a recommandées

- Constat : les fiches d'un tournoi avaient toutes été rédigées par le chef de projet, qui en recommandait une ; la fiche recommandée était aussi la plus longue.
- Règle : chaque piste est rédigée par un agent rédacteur distinct, à partir d'un gabarit commun et à longueur imposée ; le risque de biais est signalé dans la synthèse.

## L-009 · L'IA ne retire pas elle-même un garde-fou

- Constat : avec l'accord de l'utilisateur, l'IA a voulu désactiver un garde-fou qu'elle avait installé ; le système de sécurité de Claude Code a refusé.
- Règle : un garde-fou, quel qu'il soit, se retire par l'utilisateur lui-même. L'IA explique l'enjeu et laisse décider ; elle ne cherche pas de contournement. D'où : ne poser un blocage technique que si l'auteur y tient vraiment.

## L-010 · Le système coûtait trop cher en tokens

- Constat : chaque évaluation du jury lancée par un agent général consommait 80 000 à 95 000 tokens, surtout pour relire les mêmes fichiers ; un tournoi a coûté 27 passages. Les débuts de session relisaient quatre fichiers ; plusieurs informations existaient en double.
- Règle : section « Économie de tokens » de CLAUDE.md (une information dans un seul fichier, lecture minimale au démarrage, jury allégé, consignes d'agents courtes avec la liste exacte des fichiers).

## L-011 · Demander une recherche à la main est une solution de facilité

- Constat : des bases bloquaient les requêtes automatiques ; l'IA a demandé à l'utilisateur de refaire les recherches, sans protocole précis, et a appuyé des sources sur leur seul résumé. Constaté en octobre 2026 : Google Scholar répond dans le navigateur intégré de Claude ; Cairn renvoie une erreur 403 même dans ce navigateur (passer par OpenAlex, éditeur Cairn, DOI en 10.3917) ; la version OpenEdition d'un article n'a pas toujours la pagination de la revue ; un PDF de base de données peut être une image scannée (lecture par l'outil Read).
- Règle : CLAUDE.md, règles 4 et 5. Épuiser les accès légaux, dire précisément ce qui échoue, ne demander qu'une action précise ; texte intégral pour toute source citée.

## L-012 · Trop de changements à la fois font perdre la main à l'auteur

- Constat : sur plusieurs versions d'un livrable, chaque version changeait plusieurs choses (problématique, manque, recherche, style), souvent décidées en cours de route ; l'auteur ne savait plus ce qui avait changé ni pourquoi, et la note n'a pas progressé. Une version a même été bloquée parce qu'une consigne donnée au rédacteur reposait sur une affirmation non vérifiée dans la source.
- Règle : avant une nouvelle version, présenter la liste complète des changements, leur raison et leur effet attendu (memoire/<étape>/RAPPORT_DECISIONS_vN.md) ; la faire valider ; l'appliquer en une fois. Vérifier dans la source toute affirmation donnée en consigne au rédacteur.

## L-013 · Lire un PDF sans rien installer (Mac)

- Constat : pypdf, pdftotext et pdftoppm étaient absents ; le juge ingénieur IA n'a pu contrôler que les sources déjà en texte brut.
- Règle : sur Mac, extraire le texte avec PDFKit, sans installation : `osascript -l JavaScript -e 'ObjC.import("PDFKit"); var d=$.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath("CHEMIN_ABSOLU")); var o=""; for(var i=0;i<d.pageCount;i++){o+="\n=== PAGE "+(i+1)+"\n"+ObjC.unwrap(d.pageAtIndex(i).string)}; o'`. Enregistrer le résultat en .txt à côté du PDF (sources/pdf/, hors git) pour les agents qui n'ont pas Bash. Sur Windows ou Linux, l'outil Read lit les PDF ; pour une extraction en masse, demander l'OK de l'auteur avant d'installer pypdf.

## L-014 · Le rédacteur compte mal les mots

- Constat : compté à la main par le rédacteur, un livrable s'est trouvé 15 % plus long que ce qu'il annonçait.
- Règle : les mots se comptent avec systeme/outils/compter_mots.py (hors titre, notes et bibliographie, comme le demandent la plupart des écoles), jamais à la main.
