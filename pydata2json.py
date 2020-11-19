import json
import data

prepared_data = {'goals': data.goals,
                'teachers': data.teachers,
                }
with open('data.json', 'w') as json_file:
    json.dump(prepared_data, json_file, ensure_ascii=False)
