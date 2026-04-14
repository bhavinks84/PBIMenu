"""
generate_dax.py
Generates dax_measure.txt — a Power BI DAX measure that:
  - Builds a JSON array from the 'menutable' Power BI table (all data at runtime, nothing hardcoded)
  - Wraps it in a minimal HTML shell that loads CSS/JS from GitHub via jsDelivr CDN
  - Produces a tiny DAX file (no embedded CSS or JS)
"""

CDN_BASE = "https://cdn.jsdelivr.net/gh/bhavinks84/PBIMenu@main"
RAW_BASE = "https://raw.githubusercontent.com/bhavinks84/PBIMenu/refs/heads/main"

CSS_URL  = CDN_BASE + "/styles.css"
JS_URL   = CDN_BASE + "/script.js"
LOGO_URL = RAW_BASE + "/img/MAF-logo.png"


def dax_str(s):
    """
    Wrap a Python string in a DAX string literal.
    In DAX, the only string escape is doubling double-quotes: " becomes "".
    """
    return '"' + s.replace('"', '""') + '"'


def svg_safe(col):
    """
    Return a DAX expression that JSON-escapes a menutable SVG column:
      - Replaces literal " with \\" so the resulting JSON string is valid
      - Strips CR and LF characters that would break single-line JSON strings
    DAX note: backslash is a literal character in DAX (no escape sequences),
    so the replacement string for " is the two-byte sequence \\ + " which is
    valid JSON.  UNICHAR(10)=LF, UNICHAR(13)=CR.
    """
    field      = "'menutable'[" + col + "]"
    search_q   = dax_str(chr(34))              # """"  — search: one double-quote
    replace_q  = dax_str(chr(92) + chr(34))    # "\\""  — replace: backslash + quote
    replace_lf = dax_str(chr(92) + "n")        # "\\n"  — JSON newline escape literal
    empty      = dax_str("")                   # ""    — empty string (removes CR)
    return (
        "SUBSTITUTE(SUBSTITUTE(SUBSTITUTE("
        + field    + ", "
        + search_q + ", " + replace_q  + "), "
        + "UNICHAR(10), " + replace_lf + "), "
        + "UNICHAR(13), " + empty      + ")"
    )


def fld(col):
    return "'menutable'[" + col + "]"


def kv_open(key):
    """DAX string literal: {key":  (JSON object open + first key)"""
    return dax_str('{"' + key + '":"')


def kv_sep(key):
    """DAX string literal: ","key":  (field separator)"""
    return dax_str('","' + key + '":"')


KV_CLOSE = dax_str('"}')   # DAX string literal: "}


# CONCATENATEX row expression
# Each row in 'menutable' becomes one JSON object.
# Safe text columns (no " in values): SectionId, SectionTitle, SectionSubtitle,
#   SectionBgImage, DashboardTitle, DashboardURL
# SVG columns (contain " and newlines): SectionIconSVGPath, DashboardIconSVGPath
concat_row_parts = [
    kv_open("SectionId")           + " & " + fld("SectionId"),
    kv_sep("SectionTitle")         + " & " + fld("SectionTitle"),
    kv_sep("SectionSubtitle")      + " & " + fld("SectionSubtitle"),
    kv_sep("SectionBgImage")       + " & " + fld("SectionBgImage"),
    kv_sep("SectionIconSVGPath")   + " & " + svg_safe("SectionIconSVGPath"),
    kv_sep("DashboardTitle")       + " & " + fld("DashboardTitle"),
    kv_sep("DashboardIconSVGPath") + " & " + svg_safe("DashboardIconSVGPath"),
    kv_sep("DashboardURL")         + " & " + fld("DashboardURL"),
    KV_CLOSE,
]
concat_row = " &\n        ".join(concat_row_parts)


# Minimal HTML skeleton
# Static structure only; all CSS and JS are loaded from jsDelivr CDN.
# window.MENU_DATA is injected between html_pre and html_post at runtime.
html_pre = (
    '<!DOCTYPE html><html lang="en"><head>'
    '<meta charset="UTF-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
    '<title>MAFR Countries Performance Analysis</title>'
    '<link rel="stylesheet" href="' + CSS_URL + '">'
    '</head><body>'
    '<header class="header"><div class="header-left">'
    '<img src="' + LOGO_URL + '" alt="MAF Logo" class="header-logo">'
    '<h1 class="header-title">MAFR Countries Performance Analysis</h1>'
    '</div><div class="search-container">'
    '<svg class="search-icon" viewBox="0 0 24 24" width="18" height="18"'
    ' fill="none" stroke="currentColor" stroke-width="2"'
    ' stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="11" cy="11" r="8"/>'
    '<line x1="21" y1="21" x2="16.65" y2="16.65"/>'
    '</svg>'
    '<input type="text" id="searchInput" class="search-input"'
    ' placeholder="Search dashboards... (Ctrl+K)" autocomplete="off">'
    '<button id="searchClear" class="search-clear" aria-label="Clear search">\u2715</button>'
    '</div></header>'
    '<main class="accordion-container" id="accordionContainer"></main>'
    '<div id="resultsCount" class="search-results-count"></div>'
    '<script>window.MENU_DATA='
)

html_post = (
    ';</script>'
    '<script src="' + JS_URL + '"></script>'
    '</body></html>'
)


# Assemble DAX
dax = (
    "DynamicMenuHTML =\n\n"
    "VAR JsonData =\n"
    '    "[" &\n'
    "    CONCATENATEX(\n"
    "        'menutable',\n"
    "        " + concat_row + ",\n"
    '        ","\n'
    '    ) & "]"\n\n'
    "RETURN " + dax_str(html_pre) + " & JsonData & " + dax_str(html_post) + "\n"
)

with open('dax_measure.txt', 'w', encoding='utf-8') as out:
    out.write(dax)

print("Generated dax_measure.txt successfully.")
