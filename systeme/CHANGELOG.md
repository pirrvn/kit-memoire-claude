# Journal des changements du système

Les petits changements (consigne d'un agent, outil corrigé) sont notés ici au fil de l'eau ; les gros (nouvel agent, grille modifiée, nouvelle méthode) sont d'abord validés par l'auteur (DECISIONS.md).

## Kit v1.1 · 2026-10-10 · Modèle Word de l'école et contrôle avant remise

- Nouvel outil remplir_modele.py : remplit le modèle Word fourni par l'école (styles, logo, en-têtes, numérotation gardés ; commentaires d'exemple, métadonnées et noms retirés ; styles reconnus par leur nom interne Word, quelle que soit la langue ; espaces insécables et apostrophes typographiques gérées). Réglages : rubrique modele_word de config.json.
- Nouvel outil verifier_word.py : signale sans les afficher les informations cachées d'un Word (auteur, dernier modificateur, société, compte d'entreprise, e-mail, commentaires, suivi des modifications) ; --nettoyer écrit une copie propre et active le retrait automatique de ces informations à l'enregistrement.
- Quatre leçons (L-015 à L-018) : adresse e-mail de l'auteur, propriétés d'un Word, modèle officiel de l'école, nom du compte d'entreprise ; règles reportées dans CLAUDE.md ; /demarrer demande le modèle Word.

## Kit v1.0 · 2026-10-10 · Version initiale

Tirée d'un premier mémoire de master mené avec ce système (sciences de gestion, démarche qualitative), puis rendue générique :
- sept agents (documentaliste, vérificateur, rédacteur, jury académique, jury professionnel, jury ingénieur IA, contradicteur) ;
- quatre commandes : /demarrer, /tournoi, /jury, /fin-de-session ;
- registre de vérité à trois niveaux de preuve et outil de vérification (Crossref, arXiv, OpenAlex, repli sur curl) ;
- jury à l'aveugle avec grilles figées (excellence, professionnel, ingénieur IA, tournoi ; grilles officielles transcrites par /demarrer) et outil de notation, moyennes séparées par grille ;
- recherche systématique reproductible (OpenAlex, études témoins, échantillon pour un trieur humain) et protocole de tri ;
- veille réglable dans config.json, compteur de mots, conversion en Word avec page de garde ;
- quatorze leçons héritées du premier mémoire, boîte à idées amorcée.
