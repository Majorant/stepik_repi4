import json
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql




    with open('data.json', 'r') as jf:
        data = json.load(jf)
    bulk_list = []
    for goal, name in data['goals'].items():
        bulk_list.append({'goal': goal, 'name': name})
    op.bulk_insert(goals, bulk_list)

    bulk_list = []
    for t in data['teachers']:
        bulk_list.append({
                        'name': t['name'],
                        'about': t['about'],
                        'rating': t['rating'],
                        'picture': t['picture'],
                        'price': t['price'],
        })
    op.bulk_insert(teachers, bulk_list)
