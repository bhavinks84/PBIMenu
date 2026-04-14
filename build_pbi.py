import html.parser
import json
import re

html_content = open('index.html', 'r', encoding='utf-8').read()

sections = []

# Simple regex extraction since the HTML structure is regular
section_blocks = re.finditer(r'<div class="accordion-section.*?data-section="(.*?)".*?<div class="section-bg" style="background-image: url\(\'(.*?)\'\).*?<span class="collapsed-title">(.*?)</span>.*?<p class="section-subtitle">(.*?)</p>.*?<div class="cards-grid">(.*?)</div>\s*</div>\s*</div>', html_content, re.DOTALL)

menutable = []

for block in section_blocks:
    section_id = block.group(1)
    section_bg = block.group(2)
    section_title = block.group(3)
    section_subtitle = block.group(4)
    cards_html = block.group(5)
    
    # Extract Section Icon by finding first SVG in section header
    # wait, the regex grabbed everything including header. Let's just hardcode section icons since there's only 6
    if section_id == "performance": section_icon = '<path d="M3 3v18h18M9 17V9m4 8v-5m4 5V6" />'
    elif section_id == "financial": section_icon = '<path d="M12 1v22M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />'
    elif section_id == "human-capital": section_icon = '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M9 7a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />'
    elif section_id == "market": section_icon = '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />'
    elif section_id == "monthly": section_icon = '<path d="M19 4H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zM16 2v4M8 2v4M3 10h18" />'
    elif section_id == "realtime": section_icon = '<path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />'
    else: section_icon = ''

    cards = re.finditer(r'<a href="(.*?)".*?<svg viewBox="0 0 24 24">(.*?)</svg>.*?<span class="card-title">(.*?)</span>', cards_html, re.DOTALL)
    for card in cards:
        menutable.append({
            "SectionId": section_id,
            "SectionTitle": section_title,
            "SectionSubtitle": section_subtitle,
            "SectionBgImage": section_bg,
            "SectionIconSVGPath": section_icon,
            "DashboardURL": card.group(1),
            "DashboardIconSVGPath": card.group(2).strip(),
            "DashboardTitle": card.group(3)
        })

# Output JSON
with open('menutable.json', 'w', encoding='utf-8') as f:
    json.dump(menutable, f, indent=2)

# Output CSV
import csv
with open('menutable.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=menutable[0].keys())
    writer.writeheader()
    writer.writerows(menutable)

print(f"Generated {len(menutable)} rows in menutable")
