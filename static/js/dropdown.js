
(function () {
  // Find all dropdown wrappers
  const dropdowns = document.querySelectorAll('.header-action.dropdown');

  // Helper: close all dropdowns
  function closeAll() {
    dropdowns.forEach(dd => {
      dd.classList.remove('open');
      const toggle = dd.querySelector('.account-toggle');
      const menu = dd.querySelector('.dropdown-menu');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
      if (menu) {
        menu.style.opacity = '';
        menu.style.visibility = '';
        menu.style.transform = '';
      }
    });
  }

  // Toggle a specific dropdown
  function toggleDropdown(dropdown, open) {
    const toggle = dropdown.querySelector('.account-toggle');
    const menu = dropdown.querySelector('.dropdown-menu');

    if (open === undefined) open = !dropdown.classList.contains('open');

    if (open) {
      // close others first
      closeAll();
      dropdown.classList.add('open');
      if (toggle) toggle.setAttribute('aria-expanded', 'true');
      if (menu) {
        menu.style.opacity = '1';
        menu.style.visibility = 'visible';
        menu.style.transform = 'translateY(0)';
      }
    } else {
      dropdown.classList.remove('open');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
      if (menu) {
        menu.style.opacity = '';
        menu.style.visibility = '';
        menu.style.transform = '';
      }
    }
  }

  // Click handlers for toggles
  dropdowns.forEach(dd => {
    const toggle = dd.querySelector('.account-toggle');
    const menu = dd.querySelector('.dropdown-menu');

    if (!toggle) return;

    // Prevent default anchor action and toggle on click
    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      toggleDropdown(dd);
    });

    // Close dropdown when an internal link is clicked (optional)
    if (menu) {
      menu.addEventListener('click', function (e) {
        const target = e.target.closest('a');
        if (target) {
          // small delay to allow link to process; close immediately for SPA
          setTimeout(() => toggleDropdown(dd, false), 50);
        }
      });
    }
  });

  // Click outside closes dropdowns
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.header-action.dropdown')) {
      closeAll();
    }
  });

  // Close on ESC
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' || e.key === 'Esc') {
      closeAll();
    }
  });

  // Accessibility: close when focus leaves the dropdown
  document.addEventListener('focusin', function (e) {
    const focusedDropdown = e.target.closest('.header-action.dropdown');
    // If focus moved outside any open dropdown, close others
    const anyOpen = Array.from(dropdowns).some(dd => dd.classList.contains('open'));
    if (anyOpen && !focusedDropdown) {
      closeAll();
    }
  });

  // Optional: make hover still work on non-touch devices
  // (we won't rely on :hover; this just adds UX parity)
  dropdowns.forEach(dd => {
    dd.addEventListener('mouseenter', function () {
      // only show on non-touch devices
      if (!('ontouchstart' in window)) toggleDropdown(dd, true);
    });
    dd.addEventListener('mouseleave', function () {
      if (!('ontouchstart' in window)) toggleDropdown(dd, false);
    });
  });

})();

