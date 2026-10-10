# Sources

- **REGISTRE.csv** : le registre de vérité, une ligne par source. Une source absente du registre n'existe pas pour le mémoire. S'ouvre dans Excel, Numbers ou LibreOffice (séparateur « ; »).
- **resumes/** : résumés originaux des auteurs, téléchargés en texte brut depuis OpenAlex ou Crossref (niveau N2).
- **pdf/** : textes intégraux (niveau N3), nommés avec l'identifiant du registre (exemple : Dupont2021.pdf). Ce dossier n'est pas copié dans git (droits d'auteur).
- **fiches/** : fiches de lecture.
- **rapports/** : rapports de vérification du registre et recherches systématiques (un sous-dossier par recherche, avec son protocole.json).
- **A_TELECHARGER.md** : les textes qu'aucun accès libre et légal n'a permis d'obtenir, avec la marche à suivre pour l'auteur.

## Colonnes du registre

| Colonne | Contenu |
|---|---|
| id | identifiant unique, NomAnnée (Dupont2021 ; DupontMartin2021 en cas de doublon) |
| type | article, livre, chapitre, these, rapport, page_web, preprint |
| auteurs, annee, titre, revue_ou_editeur, volume, numero, pages | références exactes, telles que Crossref ou l'éditeur les donnent |
| doi, url | au moins l'un des deux |
| niveau | N1 (existence vérifiée), N2 (résumé brut lu), N3 (texte intégral lu) |
| methode_verification | comment le niveau a été atteint (exemple : « Crossref API + résumé brut OpenAlex (sources/resumes/Dupont2021.txt) ») |
| date_verification | AAAA-MM-JJ |
| classement_revue | rang dans les classements reconnus par l'école (exemple : « CNRS 2 ; FNEGE 2 »), ou a_verifier |
| acces_texte | libre, bibliotheque, a_telecharger, introuvable, a_determiner |
| statut | VERIFIE, A_VERIFIER, ECARTE |
| usage | où la source sert (exemple : « livrable 1 : définition du concept central ») |
| notes | tout ce qui mérite d'être su (pagination différente, version préprint...) |

## Faire passer une source au niveau N3

1. Claude cherche d'abord une version libre et légale (OpenAlex, Unpaywall, HAL, page de l'auteur).
2. À défaut, il l'inscrit dans A_TELECHARGER.md avec le lien exact et le nom de fichier attendu.
3. Tu télécharges le PDF depuis ta bibliothèque et tu l'enregistres dans sources/pdf/ sous ce nom.
4. Claude le lit en entier et met le registre à jour.
