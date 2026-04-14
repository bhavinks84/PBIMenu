html_content = open('powerbi-template.html', 'r', encoding='utf-8').read()

escaped_html = html_content.replace('"', '""')

dax_measure = """DynamicMenuHTML = 
VAR TemplateBase = "[[ESCAPED_HTML]]"

// Build the array string from the imported menutable
VAR JsonData = 
    "[" & 
    CONCATENATEX(
        'menutable', 
        "{\\"SectionId\\":\\"" & 'menutable'[SectionId] & 
        "\\", \\"SectionTitle\\":\\"" & 'menutable'[SectionTitle] & 
        "\\", \\"SectionSubtitle\\":\\"" & 'menutable'[SectionSubtitle] & 
        "\\", \\"SectionBgImage\\":\\"" & 'menutable'[SectionBgImage] & 
        "\\", \\"SectionIconSVGPath\\":\\"" & 'menutable'[SectionIconSVGPath] & 
        "\\", \\"DashboardTitle\\":\\"" & 'menutable'[DashboardTitle] & 
        "\\", \\"DashboardIconSVGPath\\":\\"" & 'menutable'[DashboardIconSVGPath] & 
        "\\", \\"DashboardURL\\":\\"" & 'menutable'[DashboardURL] & "\\"}",
        ","
    ) & "]"

// Insert the dynamic JSON data into the HTML template
RETURN SUBSTITUTE(TemplateBase, "/*PBI_DATA_START*/'...'/*PBI_DATA_END*/", JsonData)
"""

dax_measure = dax_measure.replace('[[ESCAPED_HTML]]', escaped_html)

with open('dax_measure.txt', 'w', encoding='utf-8') as f:
    f.write(dax_measure)

print("Generated dax_measure.txt successfully.")
