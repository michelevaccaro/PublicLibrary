/* ==========================================================================
   NovaLuce Energia — Demo behaviour
   No real backend: authentication and workflow triggers are simulated
   client-side purely for demo purposes.
   ========================================================================== */

// ---- Mobile nav toggle -----------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.querySelector(".nav-toggle");
  var links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      links.classList.toggle("open");
    });
  }
});

// ---- Toast helper -----------------------------------------------------------
function nlToast(message) {
  var existing = document.querySelector(".nl-toast");
  if (existing) existing.remove();

  var toast = document.createElement("div");
  toast.className = "nl-toast";
  toast.innerHTML =
    '<i class="bi bi-info-circle-fill"></i>' +
    '<span>' + message + '</span>' +
    '<span class="close-toast"><i class="bi bi-x-lg"></i></span>';
  document.body.appendChild(toast);

  requestAnimationFrame(function () {
    toast.classList.add("show");
  });

  var closeBtn = toast.querySelector(".close-toast");
  closeBtn.addEventListener("click", function () {
    toast.classList.remove("show");
    setTimeout(function () { toast.remove(); }, 250);
  });

  setTimeout(function () {
    toast.classList.remove("show");
    setTimeout(function () { toast.remove(); }, 250);
  }, 5000);
}

// ---- Prospect area: Docusign trigger placeholders --------------------------
// Each button below carries data-service / data-href. Once a Docusign
// Workflow Builder trigger link exists for a service, replace the href="#"
// on the matching <a class="docusign-link" data-service="..."> element in
// diventa-cliente.html with the real trigger URL — no JS changes required.
document.addEventListener("DOMContentLoaded", function () {
  var docusignLinks = document.querySelectorAll(".docusign-link");
  docusignLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      var href = link.getAttribute("href");
      if (!href || href === "#") {
        e.preventDefault();
        var service = link.getAttribute("data-service-label") || "questo servizio";
        nlToast("Link Docusign non ancora configurato per: <strong>" + service + "</strong>.");
      }
    });
  });
});

// ---- Login page: show which service the user is being redirected to -------
document.addEventListener("DOMContentLoaded", function () {
  var hintBox = document.getElementById("login-redirect-hint");
  if (!hintBox) return;
  var redirect = new URLSearchParams(window.location.search).get("redirect");
  if (!redirect) return;
  var hash = redirect.split("#")[1] || "";
  var label = hash
    .split("-")
    .map(function (w) { return w.charAt(0).toUpperCase() + w.slice(1); })
    .join(" ");
  if (label) {
    hintBox.textContent = "Accedi per continuare verso: " + label;
    hintBox.style.display = "block";
  }
});

// ---- Customer area: demo login ---------------------------------------------
var NL_DEMO_USER = "cliente@novaluce.it";
var NL_DEMO_PASS = "novaluce2026";

function nlHandleLogin(event) {
  event.preventDefault();
  var email = document.getElementById("login-email").value.trim();
  var pass = document.getElementById("login-password").value;
  var errorBox = document.getElementById("login-error");

  if (email.toLowerCase() === NL_DEMO_USER && pass === NL_DEMO_PASS) {
    sessionStorage.setItem("nlLoggedIn", "true");
    sessionStorage.setItem("nlUserEmail", email);
    var redirect = new URLSearchParams(window.location.search).get("redirect");
    window.location.href = redirect || "area-clienti-dashboard.html";
  } else {
    errorBox.classList.add("show");
  }
  return false;
}

// ---- Customer area: dashboard guard + logout -------------------------------
function nlGuardDashboard() {
  if (sessionStorage.getItem("nlLoggedIn") !== "true") {
    window.location.href = "area-clienti.html";
    return;
  }
  var email = sessionStorage.getItem("nlUserEmail") || "cliente@novaluce.it";
  var nameEl = document.getElementById("dashboard-user-name");
  var emailEl = document.getElementById("dashboard-user-email");
  var initialsEl = document.getElementById("dashboard-user-initials");
  if (emailEl) emailEl.textContent = email;
  if (nameEl) nameEl.textContent = "Mario Rossi";
  if (initialsEl) initialsEl.textContent = "MR";
}

function nlLogout() {
  sessionStorage.removeItem("nlLoggedIn");
  sessionStorage.removeItem("nlUserEmail");
  window.location.href = "index.html";
}

// ---- Customer area: service action placeholders ----------------------------
// In a future phase these buttons will open an HTTP form whose data is
// submitted to a Docusign Workflow via API instead of showing this toast.
document.addEventListener("DOMContentLoaded", function () {
  var serviceButtons = document.querySelectorAll(".service-action");
  serviceButtons.forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      var service = btn.getAttribute("data-service-label") || "questo servizio";
      nlToast("Funzionalità in arrivo: modulo per <strong>" + service + "</strong> collegato a Docusign via API.");
    });
  });
});
