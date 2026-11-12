"""Projet pédagogique MongoDB : étudiants et entreprises fictifs."""
import argparse
import json
import os
from pathlib import Path


def demo_data():
    students = [dict(_id=f'etudiant-{i}', age=18+i % 12,
                     classe=['L3', 'M1', 'M2'][i % 3],
                     ville=['Paris', 'Lyon', 'Nantes'][i % 3],
                     competences=['Python', 'SQL'] + (['MongoDB'] if i % 2 == 0 else []))
                for i in range(1, 31)]
    companies = [dict(_id=f'entreprise-{i}', nom=f'Entreprise fictive {i}',
                      secteur=['Finance', 'Commerce', 'Technologie'][i % 3],
                      chiffre_affaires_eur=i * 1000000) for i in range(1, 13)]
    return {'etudiants': students, 'entreprises': companies}


PIPELINES = {
    'etudiants_par_ville': ('etudiants', [
        {'$group': {'_id': '$ville', 'effectif': {'$sum': 1}, 'age_moyen': {'$avg': '$age'}}},
        {'$sort': {'effectif': -1, '_id': 1}}]),
    'competences': ('etudiants', [
        {'$unwind': '$competences'},
        {'$group': {'_id': '$competences', 'effectif': {'$sum': 1}}},
        {'$sort': {'effectif': -1, '_id': 1}}]),
    'entreprises_par_secteur': ('entreprises', [
        {'$group': {'_id': '$secteur', 'nombre': {'$sum': 1},
                     'ca_total_eur': {'$sum': '$chiffre_affaires_eur'}}},
        {'$sort': {'ca_total_eur': -1, '_id': 1}}]),
}


def seed(db):
    """Identifiants stables : réexécuter ne multiplie pas les documents."""
    for name, records in demo_data().items():
        for record in records:
            db[name].replace_one({'_id': record['_id']}, record, upsert=True)
    db.etudiants.create_index([('ville', 1), ('age', -1)])
    db.entreprises.create_index([('secteur', 1), ('chiffre_affaires_eur', -1)])


def report(db):
    return {name: list(db[collection].aggregate(pipeline))
            for name, (collection, pipeline) in PIPELINES.items()}


def export_data(db, directory):
    from bson.json_util import dumps
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name in demo_data():
        # Extended JSON conserve les types BSON pour un futur réimport.
        (directory / f'{name}.json').write_text(
            dumps(list(db[name].find().sort('_id', 1)), indent=2), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['seed', 'report', 'export', 'explain'])
    parser.add_argument('--output', default='exports')
    args = parser.parse_args()
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
    try:
        with MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'),
                         serverSelectionTimeoutMS=5000) as client:
            client.admin.command('ping')
            db = client[os.getenv('MONGODB_DATABASE', 'portfolio_mongodb')]
            if args.command == 'seed':
                seed(db)
                print('Données fictives chargées et index créés.')
            elif args.command == 'report':
                print(json.dumps(report(db), ensure_ascii=False, indent=2))
            elif args.command == 'export':
                export_data(db, args.output)
                print(f'Exports écrits dans {args.output}')
            else:
                query = db.etudiants.find({'ville': 'Paris', 'age': {'$gte': 20}}).sort('age', -1)
                print(json.dumps(query.explain(), default=str, indent=2))
    except PyMongoError:
        parser.exit(1, 'Erreur MongoDB : vérifier le service, les droits et MONGODB_URI.\n')


if __name__ == '__main__':
    main()
