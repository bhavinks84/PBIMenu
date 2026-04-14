/* ===== MAF Navigation Landing Page - Script ===== */

document.addEventListener('DOMContentLoaded', () => {
  const sections = document.querySelectorAll('.accordion-section');
  const searchInput = document.getElementById('searchInput');
  const searchClear = document.getElementById('searchClear');
  const resultsCount = document.getElementById('resultsCount');
  let searchTimeout = null;

  // ===== Accordion Toggle =====
  sections.forEach(section => {
    section.addEventListener('click', (e) => {
      // Don't toggle if clicking inside expanded content (cards, links, etc.)
      if (section.classList.contains('active') && e.target.closest('.expanded-content')) {
        return;
      }
      
      // If clicking a collapsed section, expand it
      if (!section.classList.contains('active')) {
        activateSection(section);
      }
    });
  });

  function activateSection(targetSection) {
    sections.forEach(s => s.classList.remove('active'));
    targetSection.classList.add('active');
    
    // Reset card animations by briefly removing and re-adding the active class effect
    const cards = targetSection.querySelectorAll('.dashboard-card');
    cards.forEach(card => {
      card.style.opacity = '0';
      requestAnimationFrame(() => {
        card.style.opacity = '';
      });
    });
  }

  // ===== Search Functionality =====
  searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(handleSearch, 150);
  });

  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      searchInput.value = '';
      handleSearch();
      searchInput.blur();
    }
  });

  searchClear.addEventListener('click', () => {
    searchInput.value = '';
    handleSearch();
    searchInput.focus();
  });

  function handleSearch() {
    const query = searchInput.value.trim().toLowerCase();
    
    // Toggle clear button
    searchClear.classList.toggle('visible', query.length > 0);
    
    if (query.length === 0) {
      // Reset everything
      resetSearch();
      return;
    }

    let totalMatches = 0;
    let firstMatchSection = null;

    sections.forEach(section => {
      const cards = section.querySelectorAll('.dashboard-card');
      let sectionHasMatch = false;

      cards.forEach(card => {
        const title = card.querySelector('.card-title').textContent.toLowerCase();
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

    // Auto-expand first matching section
    if (firstMatchSection && !firstMatchSection.classList.contains('active')) {
      activateSection(firstMatchSection);
    }

    // Show results indicator
    showResultsCount(totalMatches, query);
  }

  function resetSearch() {
    sections.forEach(section => {
      section.classList.remove('no-match');
      const cards = section.querySelectorAll('.dashboard-card');
      cards.forEach(card => {
        card.classList.remove('hidden', 'search-match');
      });
    });
    hideResultsCount();
  }

  function showResultsCount(count, query) {
    resultsCount.textContent = count === 0 
      ? `No dashboards found for "${query}"`
      : `${count} dashboard${count !== 1 ? 's' : ''} found`;
    resultsCount.classList.add('visible');
  }

  function hideResultsCount() {
    resultsCount.classList.remove('visible');
  }

  // ===== Keyboard Navigation =====
  document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus search
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      searchInput.focus();
    }

    // Arrow left/right to navigate sections (when search is not focused)
    if (document.activeElement !== searchInput) {
      const activeSection = document.querySelector('.accordion-section.active');
      const activeIndex = Array.from(sections).indexOf(activeSection);

      if (e.key === 'ArrowRight' && activeIndex < sections.length - 1) {
        activateSection(sections[activeIndex + 1]);
      } else if (e.key === 'ArrowLeft' && activeIndex > 0) {
        activateSection(sections[activeIndex - 1]);
      }
    }
  });
});
