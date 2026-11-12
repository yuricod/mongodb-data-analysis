import json
import tempfile
import unittest
import mongomock
from app import demo_data, seed, report, export_data


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.db = mongomock.MongoClient().portfolio
        seed(self.db)

    def test_seed_is_idempotent(self):
        seed(self.db)
        self.assertEqual(self.db.etudiants.count_documents({}), 30)
        self.assertEqual(self.db.entreprises.count_documents({}), 12)

    def test_city_totals(self):
        rows = report(self.db)['etudiants_par_ville']
        self.assertEqual(sum(x['effectif'] for x in rows), 30)
        self.assertEqual({x['_id'] for x in rows}, {'Paris', 'Lyon', 'Nantes'})

    def test_unwind_counts(self):
        rows = {x['_id']: x['effectif'] for x in report(self.db)['competences']}
        self.assertEqual(rows, {'Python': 30, 'SQL': 30, 'MongoDB': 15})

    def test_revenue_total(self):
        rows = report(self.db)['entreprises_par_secteur']
        self.assertEqual(sum(x['ca_total_eur'] for x in rows), 78000000)

    def test_filter_sort(self):
        rows = list(self.db.etudiants.find({'age': {'$gte': 25}}).sort('age', -1))
        self.assertTrue(rows)
        self.assertEqual([x['age'] for x in rows], sorted([x['age'] for x in rows], reverse=True))

    def test_export(self):
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            export_data(self.db, tmp)
            self.assertEqual(len(json.loads((Path(tmp)/'etudiants.json').read_text())), 30)


if __name__ == '__main__':
    unittest.main()
