import json

import requests


def is_pc_event(event: dict) -> bool:
    for tag in event['tagGroups']:
        if tag['slug'] == 'diffusion-sur-le-pass-culture':
            return True


agenda_id = ''
api_key = ''
all_events = []
offset = 0
total = 0

while offset <= total:
    response = requests.get(
        f"https://openagenda.com/agendas/{agenda_id}/admin/events.json"
        f"?oaq[passed]=1"
        f"&key={api_key}"
        f"&limit=200"
        f"&offset={offset}"
    )

    data = response.json()
    total = data['total']
    offset += 200
    events = data['events']

    published_events = filter(lambda e: e['state'] == 'published', events)
    pc_events = filter(is_pc_event, published_events)
    all_events.extend(pc_events)

    print(
        f"\n"
        f"------------\n"
        f"total : {total}\n"
        f"offset : {offset}\n"
        f"events : {len(all_events)}\n"
        f"------------\n"
    )

with open('./results.json', 'wb') as f:
    result = json.dumps(all_events)
    f.write(result.encode('utf-8'))
