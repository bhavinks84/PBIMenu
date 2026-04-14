/* ===== MAF Navigation Landing Page ===== */

var RAW_BASE = 'https://raw.githubusercontent.com/bhavinks84/PBIMenu/refs/heads/main';

function renderMenu() {
  var container = document.getElementById('accordionContainer');
  if (!container) return;
  container.innerHTML = '';

  var data = window.MENU_DATA || [];
  var sections = [];
  var sectionMap = {};

  data.forEach(function(row) {
    if (!sectionMap[row.SectionId]) {
      sectionMap[row.SectionId] = {
        id: row.SectionId,
        title: row.SectionTitle,
        subtitle: row.SectionSubtitle,
        bgImage: row.SectionBgImage,
        icon: row.SectionIconSVGPath,
        dashboards: []
      };
      sections.push(sectionMap[row.SectionId]);
    }
    sectionMap[row.SectionId].dashboards.push({
      title: row.DashboardTitle,
      url: row.DashboardURL,
      icon: row.DashboardIconSVGPath
    });
  });

  var isFirst = true;
  sections.forEach(function(sec) {
    var sectionEl = document.createElement('div');
    sectionEl.className = 'accordion-section' + (isFirst ? ' active' : '');
    sectionEl.setAttribute('data-section', sec.id);

    var cardsHtml = sec.dashboards.map(function(card) {
      return (
        '<a href="' + card.url + '" class="dashboard-card" target="_blank">' +
        '<div class="card-icon"><svg viewBox="0 0 24 24">' + card.icon + '</svg></div>' +
        '<span class="card-title">' + card.title + '</span>' +
        '<span class="card-arrow"><img src="' + RAW_BASE + '/img/arrow.svg" alt="" onerror="this.style.display=\'none\'"></span>' +
        '</a>'
      );
    }).join('');

    sectionEl.innerHTML =
      '<div class="section-bg" style="background-image: url(\'' + sec.bgImage + '\')"></div>' +
      '<div class="section-overlay-collapsed"></div>' +
      '<div class="section-overlay-active"></div>' +
      '<div class="collapsed-content">' +
        '<div class="collapsed-icon"><svg viewBox="0 0 24 24">' + sec.icon + '</svg></div>' +
        '<span class="collapsed-title">' + sec.title + '</span>' +
      '</div>' +
      '<div class="expanded-content">' +
        '<div class="section-header">' +
          '<div class="section-icon"><svg viewBox="0 0 24 24">' + sec.icon + '</svg></div>' +
          '<h2 class="section-title">' + sec.title + '</h2>' +
        '</div>' +
        '<p class="section-subtitle">' + sec.subtitle + '</p>' +
        '<div class="section-divider"></div>' +
        '<div class="cards-grid">' + cardsHtml + '</div>' +
      '</div>';

    container.appendChild(sectionEl);
    isFirst = false;
  });
}

function bindEvents() {
  var sections = document.querySelectorAll('.accordion-section');
  var searchInput = document.getElementById('searchInput');
  var searchClear = document.getElementById('searchClear');
  var resultsCount = document.getElementById('resultsCount');
  var searchTimeout = null;

  function activateSection(targetSection) {
    sections.forEach(function(s) { s.classList.remove('active'); });
    targetSection.classList.add('active');
    targetSection.querySelectorAll('.dashboard-card').forEach(function(card) {
      card.style.opacity = '0';
      requestAnimationFrame(function() { card.style.opacity = ''; });
    });
  }

  // ===== Accordion Toggle =====
  sections.forEach(function(section) {
    section.addEventListener('click', function(e) {
      if (section.classList.contains('active') && e.target.closest('.expanded-content')) return;
      if (!section.classList.contains('active')) activateSection(section);
    });
  });

  // ===== Search =====
  searchInput.addEventListener('input', function() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(handleSearch, 150);
  });

  searchInput.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') { searchInput.value = ''; handleSearch(); searchInput.blur(); }
  });

  searchClear.addEventListener('click', function() {
    searchInput.value = ''; handleSearch(); searchInput.focus();
  });

  function handleSearch() {
    var query = searchInput.value.trim().toLowerCase();
    searchClear.classList.toggle('visible', query.length > 0);
    if (query.length === 0) { resetSearch(); return; }

    var totalMatches = 0;
    var firstMatchSection = null;

    sections.forEach(function(section) {
      var cards = section.querySelectorAll('.dashboard-card');
      var sectionHasMatch = false;
      cards.forEach(function(card) {
        var title = card.querySelector('.card-title').textContent.toLowerCase();
        if (title.includes(query)) {
          card.classList.remove('hidden');
          card.classList.add('search-match');
          sectionHasMatch = true;
          totalMatches++;
        } else {
          card.classList.add('hidden');
          card.classList.remove('search-match');
        }
      });
      if (sectionHasMatch) {
        section.classList.remove('no-match');
        if (!firstMatchSection) firstMatchSection = section;
      } else {
        section.classList.add('no-match');
      }
    });

    if (firstMatchSection && !firstMatchSection.classList.contains('active')) {
      activateSection(firstMatchSection);
    }
    showResultsCount(totalMatches, query);
  }

  function resetSearch() {
    sections.forEach(function(section) {
      section.classList.remove('no-match');
      section.querySelectorAll('.dashboard-card').forEach(function(card) {
        card.classList.remove('hidden', 'search-match');
      });
    });
    hideResultsCount();
  }

  function showResultsCount(count, query) {
    resultsCount.textContent = count === 0
      ? 'No dashboards found for "' + query + '"'
      : count + ' dashboard' + (count !== 1 ? 's' : '') + ' found';
    resultsCount.classList.add('visible');
  }

  function hideResultsCount() {
    resultsCount.classList.remove('visible');
  }

  // ===== Keyboard Navigation =====
  document.addEventListener('keydown', function(e) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      searchInput.focus();
    }
    if (document.activeElement !== searchInput) {
      var activeSection = document.querySelector('.accordion-section.active');
      var activeIndex = Array.from(sections).indexOf(activeSection);
      if (e.key === 'ArrowRight' && activeIndex < sections.length - 1) activateSection(sections[activeIndex + 1]);
      else if (e.key === 'ArrowLeft' && activeIndex > 0) activateSection(sections[activeIndex - 1]);
    }
  });
}

var _initialized = false;
function init() {
  if (_initialized) return;
  _initialized = true;
  renderMenu();
  bindEvents();
}

// Power BI mode: data is already set inline before this script loads — init immediately.
// Local preview mode: data arrives via fetch; powerbi-template.html calls window._menuInit().
window._menuInit = init;

if (window.MENU_DATA && window.MENU_DATA.length > 0) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}
