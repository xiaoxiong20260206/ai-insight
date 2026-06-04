import re
import sys

with open('index.html', 'r') as f:
    c = f.read()

start = c.find('深度调研时间轴')
if start < 0:
    print("No timeline found")
    sys.exit(1)

# Find all month sections
months = re.findall(r'data-month="([^"]+)"', c[start:])
print('Months in timeline:', months)

for m in months:
    month_start = c.find(f'data-month="{m}"', start)
    # Find next month or end of timeline section
    next_month_start = len(c)
    for m2 in months:
        pos = c.find(f'data-month="{m2}"', month_start + 1)
        if pos > month_start and pos < next_month_start:
            next_month_start = pos
    
    section = c[month_start:next_month_start]
    titles = re.findall(r'<div class="timeline-card-title[^>]*>([^<]+)<', section)
    dates = re.findall(r'<div class="timeline-card-date[^>]*>([^<]+)<', section)
    links = re.findall(r'<a href="([^"]+)"[^>]*class="timeline-card-link', section)
    
    print(f'\n{m}: {len(titles)} reports')
    for i, t in enumerate(titles):
        date_str = dates[i] if i < len(dates) else "?"
        link = links[i] if i < len(links) else "?"
        print(f'  [{date_str}] {t.strip()} → {link}')
