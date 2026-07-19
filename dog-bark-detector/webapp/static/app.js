const folderInput = document.getElementById("folder");
const folderStatus = document.getElementById("folder-status");
const analyzeBtn = document.getElementById("analyze-btn");
const form = document.getElementById("analyze-form");
const resultSection = document.getElementById("result");
const resultSummary = document.getElementById("result-summary");
const resultLog = document.getElementById("result-log");
const errorSection = document.getElementById("error");
const errorMessage = document.getElementById("error-message");

if (form) {
  let validateTimer = null;

  folderInput.addEventListener("input", () => {
    clearTimeout(validateTimer);
    analyzeBtn.disabled = true;
    folderStatus.textContent = "";
    folderStatus.className = "status";
    validateTimer = setTimeout(validateFolder, 500);
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hide(resultSection);
    hide(errorSection);
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analisi in corso...";

    const folder = folderInput.value.trim();
    const soundType = document.getElementById("sound-type").value;

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder, sound_type: soundType }),
      });
      const data = await res.json();

      if (!res.ok) {
        showError(data.error || "Errore sconosciuto", data.log);
        return;
      }

      showResult(data);
    } catch (err) {
      showError("Errore di connessione al server: " + err.message, []);
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "Analizza";
    }
  });
}

async function validateFolder() {
  const folder = folderInput.value.trim();
  if (!folder) return;

  folderStatus.textContent = "Verifico...";
  const res = await fetch("/api/validate-folder", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ folder }),
  });
  const data = await res.json();
  folderStatus.textContent = data.message;
  folderStatus.className = "status " + (data.valid ? "ok" : "bad");
  analyzeBtn.disabled = !data.valid;
}

function showResult(data) {
  let html = "";
  if (data.total_sequences > 0) {
    html += `<p class="ok">Trovate ${data.total_sequences} sequenze in totale.</p>`;
    html += `<p>File di output creato su OneDrive: <code>${data.output_name}</code></p>`;
  } else {
    html += `<p class="bad">Nessuna sequenza trovata in nessun file.</p>`;
  }
  html += `<p>${data.moved_count} file spostati nella sottocartella <code>FileAnalizzati</code></p>`;
  html += "<ul>";
  for (const f of data.files) {
    html += `<li>${f.name}: ${f.duration_s}s, ${f.sequence_count} sequenze (${f.candidate_count} candidati grezzi)</li>`;
  }
  html += "</ul>";
  resultSummary.innerHTML = html;
  resultLog.textContent = (data.log || []).join("\n");
  show(resultSection);
}

function showError(message, log) {
  errorMessage.textContent = message;
  if (log && log.length) {
    errorMessage.textContent += "\n\n" + log.join("\n");
  }
  show(errorSection);
}

function show(el) { el.classList.remove("hidden"); }
function hide(el) { el.classList.add("hidden"); }
