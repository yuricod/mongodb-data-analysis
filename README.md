# MongoDB — Analyse d'étudiants et d'entreprises

Projet académique de Soualiho Kamagate, enrichi pour présenter la manipulation de données NoSQL avec Python et PyMongo.

## Objectif
Organiser des documents, répondre à des questions analytiques avec des agrégations et exporter les données. Deux collections indépendantes : `etudiants` et `entreprises`. Les 30 étudiants et 12 entreprises sont **entièrement fictifs**. Aucune relation professionnelle entre ces collections n'est supposée.

## Démarrage
Prérequis : Python 3.10+ et Docker Compose.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell : .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
docker compose up -d --wait
python app.py seed
python app.py report
python app.py export
python app.py explain
python -m unittest discover -s tests -v
```

Le service local utilise le port 27017, lié uniquement à localhost. Ce Compose est destiné au développement. Pour Atlas ou un serveur authentifié, définir `MONGODB_URI` dans l'environnement et éventuellement `MONGODB_DATABASE`. Ne jamais commiter une URI contenant un mot de passe.

## Analyses
- Effectif et âge moyen par ville : `$group`, `$avg`, `$sort`.
- Fréquence des compétences : `$unwind`, `$group`.
- Chiffre d'affaires total par secteur : sommes numériques en euros.
- Filtrage par ville et âge, tri décroissant et plan d'exécution via `explain`.

Le jeu de démonstration produit 30 étudiants, 15 occurrences de MongoDB et 78 millions d'euros de CA fictif cumulé. Ces chiffres décrivent uniquement les données générées, pas un résultat métier réel.

## Modèle et choix
Les identifiants textuels stables permettent un chargement par upsert sans doublons. Les champs simples (`ville`, `age`, `classe`) sont directement accessibles ; `competences` est un tableau de chaînes. Le CA est numérique, contrairement aux chaînes « milliards » du prototype. Deux index composés correspondent aux filtres et tris proposés. Sur ce petit jeu, MongoDB peut choisir un parcours complet : aucun gain de performance n'est revendiqué sans mesure.

`seed` remplace uniquement les documents portant les identifiants du jeu de démonstration ; utiliser une base dédiée. `export` produit du MongoDB Extended JSON en écrasant les deux fichiers de sortie existants. Aucune commande de suppression de base n'est fournie.

## Améliorations du prototype
Correction de la syntaxe de tri PyMongo, de la collection mal orthographiée, de la variable de pipeline incorrecte et des chemins de champs imbriqués. Ajout d'une CLI, d'exports reproductibles, d'index, de tests et d'un environnement Docker. Les anciens fichiers personnels et les données de session Spyder ne sont pas publiés.

## Validation
Les tests unitaires utilisent mongomock : ils vérifient les résultats des agrégations, les filtres, l'export et l'absence de doublons. Ils ne valident pas le moteur de stockage ou les plans d'exécution. Le workflow GitHub exécute aussi les commandes sur un service MongoDB 8.0 réel ; consulter son état après publication. Aucun résultat de CI n'est présumé.

## Limites et suite
Projet pédagogique à faible volume, sans API REST ni interface Web. Une extension pertinente serait d'ajouter une validation JSON Schema côté MongoDB et un benchmark sur un jeu plus volumineux. Les nouvelles fonctionnalités doivent être comprises et exécutées avant d'être revendiquées en entretien.

## Présentation CV
Gestion et analyse de données NoSQL avec MongoDB et Python/PyMongo : requêtes de filtrage, pipelines d'agrégation, chargement idempotent, indexation et exports JSON.
