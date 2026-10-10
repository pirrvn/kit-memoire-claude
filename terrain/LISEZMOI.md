# Terrain : protocole de confidentialité

## Les deux dossiers

- **Le dossier privé**, sur ta machine, hors du projet (son chemin est noté dans PROJET.md). Il reçoit les enregistrements, les transcriptions brutes, les consentements signés et la table de correspondance des codes. **Claude ne le lit pas, ne le liste pas et n'y écrit pas.** Crée-le toi-même : Claude ne doit pas parcourir tes dossiers personnels pour le faire (systeme/LECONS.md, L-003).
- **terrain/anonymise/**, dans le projet : uniquement les fichiers que tu as anonymisés et relus. Ce sont les seuls fichiers de terrain que Claude lit.

## Le protocole (avant toute collecte)

1. Accord de l'organisation si tu interroges ses salariés ou utilises ses documents, selon ses règles et celles de ton école.
2. Consentement écrit de chaque personne : objet du mémoire, enregistrement, anonymisation, droit de retrait, durée de conservation. Claude peut préparer le modèle.
3. Enregistrement et transcription sur ta machine, sans service en ligne, sauf outil autorisé par ton école ou l'organisation.
4. Anonymisation sur ta machine : personnes et organisations remplacées par des codes (R01, R02, « Organisation A »), suppression des lieux, des dates précises, des chiffres internes et de tout détail qui permettrait de reconnaître quelqu'un.
5. Tu relis le fichier anonymisé.
6. Tu le copies dans terrain/anonymise/. Alors seulement Claude peut le lire.
7. La table de correspondance entre codes et identités reste dans le dossier privé, jamais dans le projet.

## Blocage technique (facultatif)

La règle de confidentialité de CLAUDE.md suffit en général. Pour plus de sûreté, on peut interdire techniquement à Claude la lecture du dossier privé par une règle « deny » dans .claude/settings.json. Attention : une fois posée, seul toi pourras la retirer (L-009).
