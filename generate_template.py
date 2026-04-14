import json

# Read components
css = open('styles.css', 'r', encoding='utf-8').read()
js = open('script.js', 'r', encoding='utf-8').read()
menutable = open('menutable.json', 'r', encoding='utf-8').read()

html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MAFR Countries Performance Analysis</title>
  <style>
{css}
  </style>
  <script>
    // This is where Power BI will inject data via DAX string manipulation.
    // For local testing, we provide the sample JSON fallback.
    const PBI_JSON_STRING = /*PBI_DATA_START*/'{json.dumps(json.loads(menutable)).replace("'", "")}'/*PBI_DATA_END*/;
    
    let menuData = [];
    try {{
      menuData = typeof PBI_JSON_STRING === "string" && PBI_JSON_STRING.length > 5 && !PBI_JSON_STRING.includes("PBI_DATA_START") 
                 ? JSON.parse(PBI_JSON_STRING) 
                 : {menutable};
    }} catch (e) {{
      console.error("Failed to parse PowerBI data. Falling back to default.");
      menuData = {menutable};
    }}
  </script>
</head>
<body>
  <!-- ===== Header ===== -->
  <header class="header">
    <div class="header-left">
      <!-- Note: In Power BI you usually need an absolute URL for images if they aren't Base64 -->
      <!-- <img src="https://your-domain.com/img/MAF-logo.png" alt="MAF Logo" class="header-logo"> -->
      <h1 class="header-title">MAFR Countries Performance Analysis</h1>
    </div>
    <div class="search-container">
      <svg class="search-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"
        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
      <input type="text" id="searchInput" class="search-input" placeholder="Search dashboards... (⌘K or Ctrl+K)"
        autocomplete="off">
      <button id="searchClear" class="search-clear" aria-label="Clear search">✕</button>
    </div>
  </header>

  <!-- ===== Accordion ===== -->
  <main class="accordion-container" id="accordionContainer">
    <!-- Content will be injected here dynamically -->
  </main>

  <!-- Search Results Toast -->
  <div id="resultsCount" class="search-results-count"></div>

  <script>
    // ===== Dynamic Rendering Logic =====
    function renderMenu() {{
      const container = document.getElementById('accordionContainer');
      container.innerHTML = '';
      
      // Group by SectionId
      const sections = [];
      const sectionMap = {{}};
      
      menuData.forEach(row => {{
        if (!sectionMap[row.SectionId]) {{
          sectionMap[row.SectionId] = {{
            id: row.SectionId,
            title: row.SectionTitle,
            subtitle: row.SectionSubtitle,
            bgImage: row.SectionBgImage,
            icon: row.SectionIconSVGPath,
            dashboards: []
          }};
          sections.push(sectionMap[row.SectionId]);
        }}
        
        sectionMap[row.SectionId].dashboards.push({{
          title: row.DashboardTitle,
          url: row.DashboardURL,
          icon: row.DashboardIconSVGPath
        }});
      }});
      
      let isFirst = true;
      sections.forEach(sec => {{
        const sectionEl = document.createElement('div');
        sectionEl.className = 'accordion-section' + (isFirst ? ' active' : '');
        sectionEl.setAttribute('data-section', sec.id);
        
        const cardsHtml = sec.dashboards.map(card => `
          <a href="${{card.url}}" class="dashboard-card" target="_blank">
            <div class="card-icon"><svg viewBox="0 0 24 24">${{card.icon}}</svg></div>
            <span class="card-title">${{card.title}}</span>
            <span class="card-arrow"><img src="img/arrow.svg" alt="" onerror="this.style.display='none'"></span>
          </a>
        `).join('');

        sectionEl.innerHTML = `
          <div class="section-bg" style="background-image: url('${{sec.bgImage}}')"></div>
          <div class="section-overlay-collapsed"></div>
          <div class="section-overlay-active"></div>

          <div class="collapsed-content">
            <div class="collapsed-icon"><svg viewBox="0 0 24 24">${{sec.icon}}</svg></div>
            <span class="collapsed-title">${{sec.title}}</span>
          </div>

          <div class="expanded-content">
            <div class="section-header">
              <div class="section-icon"><svg viewBox="0 0 24 24">${{sec.icon}}</svg></div>
              <h2 class="section-title">${{sec.title}}</h2>
            </div>
            <p class="section-subtitle">${{sec.subtitle}}</p>
            <div class="section-divider"></div>
            <div class="cards-grid">
              ${{cardsHtml}}
            </div>
          </div>
        `;
        
        container.appendChild(sectionEl);
        isFirst = false;
      }});
    }}
    
    // Call render before existing script binds events
    renderMenu();

{js}
  </script>
</body>
</html>
"""

with open('powerbi-template.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("Generated powerbi-template.html successfully.")
