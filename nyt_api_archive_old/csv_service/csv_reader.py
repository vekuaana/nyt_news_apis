import csv
from typing import Dict, Any

class CSVReader:
    """
    Cette classe lit et parse des données des candidats depuis le fichier election_candidate.csv.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_candidates(self) -> Dict[str, Dict[str, Any]]:
        candidates_data = {}
        with open(self.file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                year = row['year']
                if year not in candidates_data:
                    candidates_data[year] = {'candidates': [], 'election_date': row['election_date']}
                candidates_data[year]['candidates'].append({'name': row['name'], 'party': row['party']})
        return candidates_data
