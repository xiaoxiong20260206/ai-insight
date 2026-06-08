import json

data = json.load(open('data/daily-content-2026-06-07.json', encoding='utf-8'))

# Convert all news items' details from string to dict format
for tab in data['tabs']:
    news = tab.get('news', {})
    for region in ['overseas', 'china']:
        items = news.get(region, [])
        for item in items:
            if isinstance(item, dict) and isinstance(item.get('details'), str):
                details_str = item['details']
                item['details'] = {
                    'finding': details_str,
                    'chips': [item.get('tag', '')],
                    'impact': ''
                }

json.dump(data, open('data/daily-content-2026-06-07.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('Fixed details format')