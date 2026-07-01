/* ==========================================================================
   NovaLuce Energia — i18n engine
   Reads/writes the selected language to localStorage so it persists across
   pages, applies translations to every [data-i18n] / [data-i18n-placeholder]
   element, and wires the language switcher dropdown in the nav.
   ========================================================================== */

function nlGetLang() {
  var lang = localStorage.getItem("nlLang");
  return NL_LANGS.indexOf(lang) !== -1 ? lang : "it";
}

function nlT(key, vars) {
  var entry = NL_I18N[key];
  if (!entry) return "";
  var lang = nlGetLang();
  var text = entry[lang] || entry.it || "";
  if (vars) {
    Object.keys(vars).forEach(function (k) {
      text = text.split("{" + k + "}").join(vars[k]);
    });
  }
  return text;
}

function nlApplyLanguage(lang) {
  if (NL_LANGS.indexOf(lang) === -1) lang = "it";
  localStorage.setItem("nlLang", lang);
  document.documentElement.setAttribute("lang", lang);

  document.querySelectorAll("[data-i18n]").forEach(function (el) {
    el.textContent = nlT(el.getAttribute("data-i18n"));
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
    el.setAttribute("placeholder", nlT(el.getAttribute("data-i18n-placeholder")));
  });

  var currentLabel = document.getElementById("lang-switcher-current");
  if (currentLabel) currentLabel.textContent = lang.toUpperCase();

  document.querySelectorAll(".lang-menu button[data-lang]").forEach(function (b) {
    b.classList.toggle("active", b.getAttribute("data-lang") === lang);
  });

  if (typeof nlUpdateRedirectHint === "function") nlUpdateRedirectHint();
}

document.addEventListener("DOMContentLoaded", function () {
  var btn = document.getElementById("lang-switcher-btn");
  var menu = document.getElementById("lang-menu");

  if (btn && menu) {
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var isOpen = menu.classList.toggle("open");
      btn.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
    menu.querySelectorAll("button[data-lang]").forEach(function (b) {
      b.addEventListener("click", function () {
        nlApplyLanguage(b.getAttribute("data-lang"));
        menu.classList.remove("open");
        btn.setAttribute("aria-expanded", "false");
      });
    });
    document.addEventListener("click", function () {
      menu.classList.remove("open");
      btn.setAttribute("aria-expanded", "false");
    });
  }

  nlApplyLanguage(nlGetLang());
});
