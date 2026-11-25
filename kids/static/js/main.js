/* Умный ребёнок — клиентская логика: меню, поиск, фильтры, формы. */
(function () {
  'use strict';

  var PHONE_RE = /^\+7 \d{3} \d{3}-\d{2}-\d{2}$/;
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[a-zA-Zа-яА-Я]{2,}$/;

  /* ---------- Меню-бургер ---------- */
  var header = document.getElementById('site-header');
  var navToggle = header ? header.querySelector('.nav-toggle') : null;

  if (header && navToggle) {
    navToggle.addEventListener('click', function () {
      var opened = header.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', opened ? 'true' : 'false');
    });

    document.addEventListener('click', function (event) {
      if (!header.classList.contains('is-open')) return;
      if (header.contains(event.target)) return;
      header.classList.remove('is-open');
      navToggle.setAttribute('aria-expanded', 'false');
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && header.classList.contains('is-open')) {
        header.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.focus();
      }
    });
  }

  /* ---------- Поиск: модальное окно и живой поиск ---------- */
  var modal = document.getElementById('search-modal');
  var searchToggle = document.querySelector('.search-toggle');
  var searchInput = document.getElementById('site-search');
  var searchResults = document.getElementById('search-results');
  var searchClose = modal ? modal.querySelector('.search-modal__close') : null;

  function openSearch() {
    if (!modal) return;
    modal.hidden = false;
    document.body.classList.add('is-locked');
    if (searchInput) {
      searchInput.focus();
      searchInput.select();
    }
  }

  function closeSearch() {
    if (!modal) return;
    modal.hidden = true;
    document.body.classList.remove('is-locked');
    if (searchToggle) searchToggle.focus();
  }

  if (searchToggle && modal) {
    searchToggle.addEventListener('click', openSearch);
    if (searchClose) searchClose.addEventListener('click', closeSearch);
    modal.addEventListener('click', function (event) {
      if (event.target === modal) closeSearch();
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && !modal.hidden) closeSearch();
    });
  }

  function renderSuggestions(items, query) {
    if (!searchResults) return;
    searchResults.innerHTML = '';

    if (!query || query.length < 2) {
      searchResults.innerHTML = '<p class="search-modal__empty">Начните вводить название направления, фамилию педагога или мастер-класса.</p>';
      return;
    }

    if (!items.length) {
      searchResults.innerHTML = '<p class="search-modal__empty">Ничего не нашлось. Попробуйте «робототехника» или «рисование».</p>';
      return;
    }

    var list = document.createElement('div');
    list.className = 'suggest-list';

    items.forEach(function (item) {
      var link = document.createElement('a');
      link.className = 'suggest-item';
      link.href = item.url;
      link.innerHTML = '<b></b><span></span>';
      link.querySelector('b').textContent = item.title;
      link.querySelector('span').textContent = item.type;
      list.appendChild(link);
    });

    searchResults.appendChild(list);
  }

  if (searchInput && searchResults) {
    var suggestTimer = null;
    var suggestUrl = searchResults.dataset.suggestUrl || '/api/suggest/';

    searchInput.addEventListener('input', function () {
      var query = searchInput.value.trim();
      window.clearTimeout(suggestTimer);

      if (query.length < 2) {
        renderSuggestions([], query);
        return;
      }

      suggestTimer = window.setTimeout(function () {
        fetch(suggestUrl + '?q=' + encodeURIComponent(query), {
          headers: { 'X-Requested-With': 'fetch' }
        })
          .then(function (response) {
            if (!response.ok) throw new Error('HTTP ' + response.status);
            return response.json();
          })
          .then(function (data) { renderSuggestions(data.items, query); })
          .catch(function () {
            searchResults.innerHTML = '<p class="search-modal__empty">Поиск временно недоступен. Попробуйте ещё раз.</p>';
          });
      }, 250);
    });

    renderSuggestions([], '');
  }

  /* ---------- Каталог: фильтры и поиск без перезагрузки ---------- */
  var catalog = document.querySelector('[data-catalog]');

  if (catalog) {
    var grid = catalog.querySelector('[data-catalog-grid]');
    var counter = catalog.querySelector('[data-catalog-count]');
    var groupsCounter = catalog.querySelector('[data-catalog-groups]');
    var form = catalog.querySelector('[data-catalog-filters]');
    var search = catalog.querySelector('[data-catalog-search]');
    var apiUrl = catalog.dataset.api;
    var submitButton = form ? form.querySelector('[data-catalog-submit]') : null;
    var requestId = 0;

    function updateCatalog() {
      if (!apiUrl) return;
      var params = new URLSearchParams(new FormData(form));
      var query = search ? search.value.trim() : '';
      if (query) params.set('search', query);

      var current = ++requestId;
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.classList.add('is-loading');
      }
      grid.setAttribute('aria-busy', 'true');

      fetch(apiUrl + '?' + params.toString(), {
        headers: { 'X-Requested-With': 'fetch' }
      })
        .then(function (response) {
          if (!response.ok) throw new Error('HTTP ' + response.status);
          return response.json();
        })
        .then(function (data) {
          if (current !== requestId) return;
          grid.innerHTML = data.html;
          if (counter) counter.textContent = data.total + ' ' + plural(data.total, 'направление', 'направления', 'направлений');
          if (groupsCounter) groupsCounter.textContent = data.groups_total + ' ' + plural(data.groups_total, 'группа', 'группы', 'групп');
          var url = new URL(window.location.href);
          url.search = params.toString();
          window.history.replaceState({}, '', url);
        })
        .catch(function () {
          if (current === requestId) {
            grid.innerHTML = '<p class="search-modal__empty">Не удалось обновить список. Обновите страницу.</p>';
          }
        })
        .finally(function () {
          if (current === requestId) {
            grid.removeAttribute('aria-busy');
            if (submitButton) {
              submitButton.disabled = false;
              submitButton.classList.remove('is-loading');
            }
          }
        });
    }

    if (form) {
      form.addEventListener('change', function (event) {
        if (event.target.type === 'checkbox' || event.target.tagName === 'SELECT') {
          updateCatalog();
        }
      });
      form.addEventListener('submit', function (event) {
        event.preventDefault();
        updateCatalog();
      });
    }

    if (search) {
      var searchTimer = null;
      search.addEventListener('input', function () {
        window.clearTimeout(searchTimer);
        searchTimer = window.setTimeout(updateCatalog, 300);
      });
    }

    var filtersToggle = catalog.querySelector('[data-filters-toggle]');
    var filtersPanel = catalog.querySelector('.filters');
    if (filtersToggle && filtersPanel) {
      filtersToggle.addEventListener('click', function () {
        var opened = filtersPanel.classList.toggle('is-open');
        filtersToggle.setAttribute('aria-expanded', opened ? 'true' : 'false');
      });
    }
  }

  function plural(number, one, few, many) {
    var mod10 = number % 10;
    var mod100 = number % 100;
    if (mod10 === 1 && mod100 !== 11) return one;
    if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return few;
    return many;
  }

  /* ---------- FAQ на странице абонементов ---------- */
  document.querySelectorAll('[data-faq]').forEach(function (button) {
    var panel = document.getElementById(button.getAttribute('aria-controls'));
    if (!panel) return;

    button.addEventListener('click', function () {
      var expanded = button.getAttribute('aria-expanded') === 'true';
      button.setAttribute('aria-expanded', expanded ? 'false' : 'true');
      panel.hidden = expanded;
    });
  });

  /* ---------- Маска телефона ---------- */
  document.querySelectorAll('input[data-mask="phone"]').forEach(function (input) {
    input.addEventListener('input', function () {
      var digits = input.value.replace(/\D/g, '');
      if (digits.startsWith('8')) digits = '7' + digits.slice(1);
      if (!digits.startsWith('7')) digits = '7' + digits;
      digits = digits.slice(0, 11);

      var formatted = '+7';
      if (digits.length > 1) formatted += ' ' + digits.slice(1, 4);
      if (digits.length >= 5) formatted += ' ' + digits.slice(4, 7);
      if (digits.length >= 8) formatted += '-' + digits.slice(7, 9);
      if (digits.length >= 10) formatted += '-' + digits.slice(9, 11);

      input.value = digits.length === 1 ? '+' : formatted;
    });

    input.addEventListener('blur', function () {
      if (input.value === '+7' || input.value === '+') input.value = '';
    });
  });

  /* ---------- Клиентская валидация форм ---------- */
  function fieldError(field, message) {
    var wrapper = field.closest('.field') || field.closest('.checkbox-line');
    if (!wrapper) return;
    clearError(field);
    field.classList.add('is-error');
    field.setAttribute('aria-invalid', 'true');

    var note = document.createElement('p');
    note.className = 'error-text';
    note.dataset.jsError = '1';
    note.textContent = message;
    wrapper.appendChild(note);
  }

  function clearError(field) {
    var wrapper = field.closest('.field') || field.closest('.checkbox-line');
    field.classList.remove('is-error');
    field.removeAttribute('aria-invalid');
    if (!wrapper) return;
    var note = wrapper.querySelector('[data-js-error]');
    if (note) note.remove();
  }

  function validateField(field) {
    var value = (field.value || '').trim();

    if (field.type === 'checkbox') {
      if (field.required && !field.checked) {
        fieldError(field, 'Отметьте согласие — без него форму нельзя отправить');
        return false;
      }
      clearError(field);
      return true;
    }

    if (field.required && !value) {
      fieldError(field, field.dataset.errorRequired || 'Заполните поле');
      return false;
    }

    if (value && field.type === 'email' && !EMAIL_RE.test(value)) {
      fieldError(field, 'Проверьте адрес: он выглядит неполным');
      return false;
    }

    if (value && field.dataset.mask === 'phone' && !PHONE_RE.test(value)) {
      fieldError(field, 'Введите телефон в формате +7 900 000-00-00');
      return false;
    }

    if (value && field.dataset.minlength && value.length < Number(field.dataset.minlength)) {
      fieldError(field, 'Слишком короткий текст: нужно не меньше ' + field.dataset.minlength + ' символов');
      return false;
    }

    clearError(field);
    return true;
  }

  document.querySelectorAll('form[data-validate]').forEach(function (form) {
    form.setAttribute('novalidate', 'novalidate');

    form.addEventListener('submit', function (event) {
      var fields = Array.prototype.slice.call(form.querySelectorAll('input, textarea, select'));
      var firstInvalid = null;

      fields.forEach(function (field) {
        if (field.type === 'hidden' || field.disabled) return;
        if (!validateField(field) && !firstInvalid) firstInvalid = field;
      });

      if (firstInvalid) {
        event.preventDefault();
        firstInvalid.focus();
        return;
      }

      var button = form.querySelector('[type="submit"]');
      if (button) {
        button.classList.add('is-loading');
        button.disabled = true;
      }
    });

    form.addEventListener('input', function (event) {
      if (event.target.matches('input, textarea, select')) validateField(event.target);
    });
    form.addEventListener('blur', function (event) {
      if (event.target.matches('input, textarea, select')) validateField(event.target);
    }, true);
  });
})();
