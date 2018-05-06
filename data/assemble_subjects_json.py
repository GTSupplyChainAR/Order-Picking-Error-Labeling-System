"""
Creates a subjects.json file that enumerates all subjects/methods/tasks (testing-only) for use in error-labelling.
"""

import os
import csv
import json


METHOD_IDS = ['HUD/RFID', 'Paper/None', 'Paper/Barcode', 'Light/Button']

subjects_to_methods = {}
with open('subjects_to_methods.csv') as f:
    reader = csv.DictReader(f)
    for data_row in reader:
        ordered_methods_ids = [data_row['Method %d' % method_num] for method_num in range(1, 5)]
        assert set(ordered_methods_ids) == set(METHOD_IDS)
        subjects_to_methods[int(data_row['Subject ID'])] = ordered_methods_ids


def read_json(*path):
    with open(os.path.join(*path)) as f:
        return json.load(f)


method_id_to_tasks = {
    'HUD/RFID':         read_json('RFID-Study-Task-Generation', 'output', 'pick-by-hud_rfid', 'tasks-pick-by-hud_rfid-testing.json')['tasks'],
    'Paper/None':       read_json('RFID-Study-Task-Generation', 'output', 'pick-by-paper_none', 'tasks-pick-by-paper_none-testing.json')['tasks'],
    'Paper/Barcode':    read_json('RFID-Study-Task-Generation', 'output', 'pick-by-paper_barcode', 'tasks-pick-by-paper_barcode-testing.json')['tasks'],
    'Light/Button':     read_json('RFID-Study-Task-Generation', 'output', 'pick-by-light_button', 'tasks-pick-by-light_button-testing.json')['tasks'],
}

subjects = []
for subject_id in range(1, 13):

    subject_methods = []
    for method_id in subjects_to_methods[subject_id]:
        subject_methods.append({
            'methodId': method_id,
            'tasks': method_id_to_tasks[method_id]
        })

    subjects.append({
        'subjectId': subject_id,
        'methods': subject_methods,
    })

with open('subjects.json', mode='w+') as f:
    json.dump(subjects, f, indent=4)
