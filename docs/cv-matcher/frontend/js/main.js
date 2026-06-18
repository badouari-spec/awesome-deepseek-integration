import { api } from "./api.js";
import {
  toast, openModal, closeModal,
  cvRow, jobRow, matchRow, matchReport, kanbanCard,
  scoreRing, recommendationBadge, pipelineBadge,
} from "./components.js";

/* ── State ── */
let cvs = [], jobs = [], matches = [];
let currentJobId = null;
let pollInterval = null;

/* ── Navigation ── */
const VIEWS = ["dashboard", "cvs", "jobs", "matching", "pipeline"];

function showView(name) {
  VIEWS.forEach(v => {
    document.getElementById(`view-${v}`)?.classList.toggle("hidden", v !== name);
  });
  document.querySelectorAll("nav a[data-view]").forEach(a => {
    a.classList.toggle("active", a.dataset.view === name);
  });
  if      (name === "dashboard") loadDashboard();
  else if (name === "cvs")       loadCVs();
  else if (name === "jobs")      loadJobs();
  else if (name === "matching")  loadMatchingView();
  else if (name === "pipeline")  loadPipeline();
}

document.querySelectorAll("nav a[data-view]").forEach(a =>
  a.addEventListener("click", () => showView(a.dataset.view))
);

/* ════════════ DASHBOARD ════════════ */
async function loadDashboard() {
  try {
    const stats = await api.getStats();

    document.getElementById("stat-cvs").textContent     = stats.nb_cvs    ?? "—";
    document.getElementById("stat-jobs").textContent    = stats.nb_jobs   ?? "—";
    document.getElementById("stat-matches").textContent = stats.nb_matches ?? "—";
    document.getElementById("stat-strong").textContent  = stats.nb_top    ?? "—";

    /* Pipeline summary */
    const pl = stats.pipeline || {};
    const plLabels = {
      nouveau:"🆕 Nouveau", examen:"🔍 En examen", entretien:"🗓️ Entretien",
      offre:"📨 Offre", recrute:"🎉 Recruté", rejete:"❌ Rejeté",
    };
    const total = Object.values(pl).reduce((a, b) => a + b, 0) || 1;
    document.getElementById("pipeline-summary").innerHTML = Object.entries(pl)
      .map(([k, v]) => `
        <div class="dist-row">
          <span style="min-width:120px;font-size:13px">${plLabels[k] || k}</span>
          <div class="progress" style="flex:1"><div class="progress-bar green" style="width:${(v/total*100).toFixed(0)}%"></div></div>
          <span style="min-width:24px;text-align:right;font-size:13px;font-weight:600">${v}</span>
        </div>`).join("") || '<p class="text-muted text-sm">Aucun candidat en pipeline</p>';

    /* Score distribution */
    const dist = stats.score_distribution || {};
    const distLabels = {
      "≥85":"🌟 Prioritaire (≥85)", "70-84":"✅ Fort (70-84)",
      "55-69":"🔶 Moyen (55-69)", "40-54":"⚠️ Faible (40-54)", "<40":"🚫 Éliminatoire (<40)",
    };
    const distTotal = Object.values(dist).reduce((a, b) => a + b, 0) || 1;
    document.getElementById("score-distribution").innerHTML = Object.entries(distLabels)
      .map(([k, label]) => {
        const v = dist[k] || 0;
        const color = k === "≥85" || k === "70-84" ? "green" : k === "55-69" ? "amber" : "red";
        return `
          <div class="dist-row">
            <span style="min-width:160px;font-size:12px">${label}</span>
            <div class="progress" style="flex:1"><div class="progress-bar ${color}" style="width:${(v/distTotal*100).toFixed(0)}%"></div></div>
            <span style="min-width:24px;text-align:right;font-size:13px;font-weight:600">${v}</span>
          </div>`;
      }).join("");

    /* Recent matches */
    const recent = (stats.recent_matches || []).slice(0, 8);
    document.getElementById("recent-matches").innerHTML = recent.length
      ? recent.map(m => `
          <tr>
            <td><strong>${m.candidate_name || "—"}</strong></td>
            <td>${m.job_title || "—"}</td>
            <td>${scoreRing(m.overall_score, 44)}</td>
            <td>${recommendationBadge(m.recommendation)}</td>
            <td>${pipelineBadge(m.pipeline_status)}</td>
          </tr>`).join("")
      : '<tr><td colspan="5" class="text-muted text-sm" style="text-align:center;padding:24px">Aucun matching encore</td></tr>';

  } catch (e) {
    toast("Erreur tableau de bord : " + e.message, "error");
  }
}

document.getElementById("refresh-dashboard")?.addEventListener("click", loadDashboard);

/* ════════════ CVs ════════════ */
async function loadCVs() {
  try {
    cvs = await api.listCVs();
    renderCVTable();
  } catch (e) { toast(e.message, "error"); }
}

function renderCVTable(filter = "") {
  const tbody = document.getElementById("cv-table-body");
  const list  = filter
    ? cvs.filter(c => {
        const name = (c.candidate_name || c.filename || "").toLowerCase();
        return name.includes(filter.toLowerCase());
      })
    : cvs;

  const badge = document.getElementById("cv-count-badge");
  if (badge) { badge.textContent = `${cvs.length} CV`; badge.style.display = cvs.length ? "" : "none"; }

  tbody.innerHTML = list.length
    ? list.map(cv => cvRow(cv)).join("")
    : `<tr><td colspan="5" class="text-muted text-sm" style="text-align:center;padding:24px">${
        filter ? "Aucun candidat ne correspond à la recherche" : "Aucun CV importé"
      }</td></tr>`;
}

document.getElementById("cv-search")?.addEventListener("input", e => renderCVTable(e.target.value));

window.viewCV = async function(id) {
  let cv = cvs.find(c => c.id === id);
  if (!cv) cv = await api.getCV(id);
  const d = cv.parsed_data || {};
  const skills = (d.competences_techniques || []).slice(0, 20);
  const softSkills = (d.soft_skills || []);
  const experiences = (d.experiences || []);
  const formations = (d.formations || []);

  openModal(`
    <div class="modal-header">
      <div>
        <h2>${cv.candidate_name || cv.filename}</h2>
        <div class="text-muted text-sm" style="margin-top:4px">${cv.filename}</div>
      </div>
      <button class="close-btn" onclick="closeModal()">✕</button>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
      <div class="report-section">
        <h3>📋 Informations</h3>
        <div style="font-size:13.5px;display:grid;gap:6px">
          ${d.email    ? `<div>📧 ${d.email}</div>`    : ""}
          ${d.telephone ? `<div>📞 ${d.telephone}</div>` : ""}
          ${d.localisation ? `<div>📍 ${d.localisation}</div>` : ""}
          ${d.annees_experience != null ? `<div>⏱ <strong>${d.annees_experience} an${d.annees_experience > 1 ? "s" : ""}</strong> d'expérience</div>` : ""}
          ${d.niveau_etudes ? `<div>🎓 ${d.niveau_etudes}</div>` : ""}
        </div>
      </div>
      ${d.resume_ia ? `<div class="report-section"><h3>💬 Résumé IA</h3><p style="font-size:13px;line-height:1.6;color:var(--text-muted)">${d.resume_ia}</p></div>` : ""}
    </div>
    ${skills.length ? `<div class="report-section" style="margin-bottom:16px">
      <h3>🛠 Compétences techniques</h3>
      <div>${skills.map(s => `<span class="skill-pill pill-matched">${s}</span>`).join("")}</div>
    </div>` : ""}
    ${softSkills.length ? `<div class="report-section" style="margin-bottom:16px">
      <h3>🤝 Soft skills</h3>
      <div>${softSkills.map(s => `<span class="skill-pill pill-neutral">${s}</span>`).join("")}</div>
    </div>` : ""}
    ${experiences.length ? `<div class="report-section" style="margin-bottom:16px">
      <h3>💼 Expériences</h3>
      ${experiences.map(e => `<div style="border-left:3px solid var(--primary);padding-left:12px;margin-bottom:10px">
        <div style="font-weight:600;font-size:13.5px">${e.poste || e.title || "—"} ${e.entreprise || e.company ? `@ ${e.entreprise || e.company}` : ""}</div>
        <div class="text-muted text-sm">${e.debut || e.start_date || ""} — ${e.fin || e.end_date || "Présent"}</div>
      </div>`).join("")}
    </div>` : ""}
    ${formations.length ? `<div class="report-section">
      <h3>🎓 Formation</h3>
      ${formations.map(f => `<div style="font-size:13.5px;padding:6px 0;border-bottom:1px solid var(--border)">
        <strong>${f.diplome || f.degree || "—"}</strong>${f.ecole || f.institution ? ` — ${f.ecole || f.institution}` : ""}
        ${f.annee || f.end_year ? `<span class="text-muted text-sm" style="margin-left:8px">${f.annee || f.end_year}</span>` : ""}
      </div>`).join("")}
    </div>` : ""}
  `, true);
};

window.deleteCV = async function(id) {
  if (!confirm("Supprimer ce CV ?")) return;
  try {
    await api.deleteCV(id);
    cvs = cvs.filter(c => c.id !== id);
    renderCVTable(document.getElementById("cv-search")?.value || "");
    toast("CV supprimé", "success");
  } catch (e) { toast(e.message, "error"); }
};

/* ── CV upload zone ── */
const uploadZone = document.getElementById("upload-zone");
const fileInput  = document.getElementById("file-input");

uploadZone?.addEventListener("click", () => fileInput.click());
uploadZone?.addEventListener("dragover",  e => { e.preventDefault(); uploadZone.classList.add("drag-over"); });
uploadZone?.addEventListener("dragleave", ()  => uploadZone.classList.remove("drag-over"));
uploadZone?.addEventListener("drop", e => {
  e.preventDefault();
  uploadZone.classList.remove("drag-over");
  handleCVFiles(e.dataTransfer.files);
});
fileInput?.addEventListener("change", () => { handleCVFiles(fileInput.files); fileInput.value = ""; });

async function handleCVFiles(files) {
  for (const file of files) {
    try {
      toast(`Importation de ${file.name}…`, "info");
      const cv = await api.uploadCV(file);
      cvs.unshift(cv);
      renderCVTable();
      toast(`${file.name} importé — analyse IA en cours…`, "success");
      pollCV(cv.id);
    } catch (e) {
      toast(`Échec ${file.name} : ${e.message}`, "error");
    }
  }
}

function pollCV(id) {
  const t = setInterval(async () => {
    try {
      const cv  = await api.getCV(id);
      const idx = cvs.findIndex(c => c.id === id);
      if (idx !== -1) cvs[idx] = cv;
      renderCVTable(document.getElementById("cv-search")?.value || "");
      if (cv.status !== "pending") {
        clearInterval(t);
        toast(cv.status === "parsed"
          ? `✓ ${cv.candidate_name || cv.filename} analysé`
          : `Erreur analyse : ${cv.error_message}`, cv.status === "parsed" ? "success" : "error");
      }
    } catch { clearInterval(t); }
  }, 3000);
}

/* ════════════ JOBS ════════════ */
async function loadJobs() {
  try {
    jobs = await api.listJobs();
    renderJobTable();
  } catch (e) { toast(e.message, "error"); }
}

function renderJobTable() {
  const tbody = document.getElementById("job-table-body");
  tbody.innerHTML = jobs.length
    ? jobs.map(j => jobRow(j)).join("")
    : '<tr><td colspan="4" class="text-muted text-sm" style="text-align:center;padding:24px">Aucun poste créé</td></tr>';
}

/* ── Onglets source du poste ── */
document.querySelectorAll("#job-source-tabs .tab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#job-source-tabs .tab").forEach(t => t.classList.remove("active"));
    btn.classList.add("active");
    const tab = btn.dataset.tab;
    document.getElementById("job-src-text").classList.toggle("hidden", tab !== "text");
    document.getElementById("job-src-file").classList.toggle("hidden", tab !== "file");
  });
});

document.getElementById("job-text-submit")?.addEventListener("click", async () => {
  const title   = document.getElementById("job-title").value.trim();
  const company = document.getElementById("job-company").value.trim();
  const desc    = document.getElementById("job-desc").value.trim();
  if (!title) return toast("Le titre est requis", "error");
  if (!desc)  return toast("La description est requise", "error");

  const btn = document.getElementById("job-text-submit");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Création…';
  try {
    const job = await api.createJob({ title, company: company || null, description: desc });
    jobs.unshift(job);
    renderJobTable();
    document.getElementById("job-title").value   = "";
    document.getElementById("job-company").value = "";
    document.getElementById("job-desc").value    = "";
    toast(`Poste « ${title} » créé — analyse IA en cours…`, "success");
    pollJob(job.id);
  } catch (e) {
    toast(e.message, "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = "✦ Créer &amp; Analyser avec l'IA";
  }
});

/* ── Téléversement fichier de poste ── */
const jdZone      = document.getElementById("jd-upload-zone");
const jdFileInput = document.getElementById("jd-file-input");
const jdFileName  = document.getElementById("jd-file-name");
const jdUploadBtn = document.getElementById("jd-upload-btn");
let   selectedJdFile = null;

jdZone?.addEventListener("click",     () => jdFileInput.click());
jdZone?.addEventListener("dragover",  e => { e.preventDefault(); jdZone.classList.add("drag-over"); });
jdZone?.addEventListener("dragleave", ()  => jdZone.classList.remove("drag-over"));
jdZone?.addEventListener("drop", e => {
  e.preventDefault();
  jdZone.classList.remove("drag-over");
  if (e.dataTransfer.files[0]) selectJdFile(e.dataTransfer.files[0]);
});
jdFileInput?.addEventListener("change", () => {
  if (jdFileInput.files[0]) selectJdFile(jdFileInput.files[0]);
  jdFileInput.value = "";
});

function selectJdFile(file) {
  selectedJdFile = file;
  jdFileName.textContent = `📎 ${file.name} (${(file.size / 1024).toFixed(0)} Ko)`;
  jdZone.style.borderColor = "var(--primary)";
  jdUploadBtn.disabled = false;
}

jdUploadBtn?.addEventListener("click", async () => {
  if (!selectedJdFile) return;
  const title   = document.getElementById("job-title").value.trim();
  const company = document.getElementById("job-company").value.trim();
  if (!title) return toast("Le titre du poste est requis", "error");

  jdUploadBtn.disabled = true;
  jdUploadBtn.innerHTML = '<span class="spinner"></span> Traitement…';
  try {
    const job = await api.uploadJobFile(selectedJdFile, title, company || null);
    jobs.unshift(job);
    renderJobTable();
    toast(`Poste « ${title} » créé depuis ${selectedJdFile.name}`, "success");
    pollJob(job.id);
    selectedJdFile = null;
    jdFileName.textContent = "";
    jdZone.style.borderColor = "";
    document.getElementById("job-title").value   = "";
    document.getElementById("job-company").value = "";
  } catch (e) {
    toast(e.message, "error");
  } finally {
    jdUploadBtn.disabled = false;
    jdUploadBtn.innerHTML = "✦ Créer depuis le fichier";
  }
});

function pollJob(id) {
  const t = setInterval(async () => {
    try {
      const job = await api.getJob(id);
      const idx = jobs.findIndex(j => j.id === id);
      if (idx !== -1) jobs[idx] = job;
      renderJobTable();
      if (job.status !== "pending") {
        clearInterval(t);
        toast(job.status === "parsed"
          ? `✓ « ${job.title} » analysé`
          : `Erreur : ${job.error_message}`, job.status === "parsed" ? "success" : "error");
      }
    } catch { clearInterval(t); }
  }, 3000);
}

window.viewJob = async function(id) {
  let job = jobs.find(j => j.id === id);
  if (!job) job = await api.getJob(id);
  const d    = job.parsed_data || {};
  const req  = d.competences_obligatoires || [];
  const pref = d.competences_souhaitees   || [];

  openModal(`
    <div class="modal-header">
      <div>
        <h2>${job.title}</h2>
        ${job.company ? `<div class="text-muted text-sm" style="margin-top:4px">🏢 ${job.company}</div>` : ""}
      </div>
      <button class="close-btn" onclick="closeModal()">✕</button>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
      ${d.experience_requise ? `<div class="report-section"><h3>⏱ Expérience requise</h3><p style="font-size:13.5px">${d.experience_requise}</p></div>` : ""}
      ${d.niveau_etudes ? `<div class="report-section"><h3>🎓 Formation</h3><p style="font-size:13.5px">${d.niveau_etudes}</p></div>` : ""}
    </div>
    ${req.length ? `<div class="report-section" style="margin-bottom:16px">
      <h3>🔴 Compétences obligatoires</h3>
      <div>${req.map(s => `<span class="skill-pill pill-missing">${s}</span>`).join("")}</div>
    </div>` : ""}
    ${pref.length ? `<div class="report-section" style="margin-bottom:16px">
      <h3>⭐ Compétences souhaitées</h3>
      <div>${pref.map(s => `<span class="skill-pill pill-preferred">${s}</span>`).join("")}</div>
    </div>` : ""}
    ${d.responsabilites?.length ? `<div class="report-section">
      <h3>📋 Responsabilités</h3>
      <ul style="padding-left:18px;display:grid;gap:5px">
        ${d.responsabilites.map(r => `<li style="font-size:13px;color:var(--text-muted)">${r}</li>`).join("")}
      </ul>
    </div>` : ""}
  `, true);
};

window.deleteJob = async function(id) {
  if (!confirm("Supprimer ce poste ?")) return;
  try {
    await api.deleteJob(id);
    jobs = jobs.filter(j => j.id !== id);
    renderJobTable();
    toast("Poste supprimé", "success");
  } catch (e) { toast(e.message, "error"); }
};

/* ════════════ MATCHING ════════════ */
async function loadMatchingView() {
  try {
    [cvs, jobs] = await Promise.all([api.listCVs(), api.listJobs()]);
    renderJobSelector();
    populatePipelineJobFilter();
  } catch (e) { toast(e.message, "error"); }
}

function renderJobSelector() {
  const sel = document.getElementById("match-job-select");
  if (!sel) return;
  sel.innerHTML = '<option value="">— Sélectionnez un poste —</option>' +
    jobs.map(j => `<option value="${j.id}">${j.title}${j.company ? " @ " + j.company : ""}</option>`).join("");
}

document.getElementById("match-job-select")?.addEventListener("change", async e => {
  currentJobId = e.target.value ? +e.target.value : null;
  if (!currentJobId) {
    document.getElementById("match-cv-list").innerHTML = '<div class="text-muted text-sm">Sélectionnez un poste d\'abord</div>';
    document.getElementById("match-results-section").classList.add("hidden");
    return;
  }
  renderCVCheckboxes();
  await loadMatchResults();
});

function renderCVCheckboxes(filter = "") {
  const parsed = cvs.filter(c => c.status === "parsed" &&
    (!filter || (c.candidate_name || c.filename || "").toLowerCase().includes(filter.toLowerCase())));
  const container = document.getElementById("match-cv-list");
  if (!container) return;
  container.innerHTML = parsed.length
    ? parsed.map(cv => `
        <label class="card" style="display:flex;align-items:center;gap:10px;cursor:pointer;padding:10px 14px">
          <input type="checkbox" value="${cv.id}" style="accent-color:var(--primary);width:16px;height:16px;flex-shrink:0">
          <div>
            <div style="font-size:13.5px;font-weight:600">${cv.candidate_name || cv.filename}</div>
            ${cv.parsed_data?.annees_experience != null
              ? `<div class="text-muted text-sm">${cv.parsed_data.annees_experience} an${cv.parsed_data.annees_experience > 1 ? "s" : ""} d'expérience</div>`
              : ""}
          </div>
        </label>`).join("")
    : `<div class="text-muted text-sm">${filter ? "Aucun candidat trouvé" : "Aucun CV analysé. Importez des CV d'abord."}</div>`;
}

document.getElementById("match-cv-search")?.addEventListener("input", e =>
  renderCVCheckboxes(e.target.value)
);

document.getElementById("select-all-btn")?.addEventListener("click", () => {
  document.querySelectorAll("#match-cv-list input[type=checkbox]").forEach(cb => cb.checked = true);
});
document.getElementById("deselect-all-btn")?.addEventListener("click", () => {
  document.querySelectorAll("#match-cv-list input[type=checkbox]").forEach(cb => cb.checked = false);
});

document.getElementById("run-match-btn")?.addEventListener("click", async () => {
  if (!currentJobId) return toast("Sélectionnez un poste", "error");
  const checked = [...document.querySelectorAll("#match-cv-list input:checked")].map(i => +i.value);
  if (!checked.length) return toast("Sélectionnez au moins un candidat", "error");

  const btn = document.getElementById("run-match-btn");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Analyse en cours…';
  try {
    await api.runMatch(currentJobId, checked);
    toast("Matching lancé — résultats dans quelques secondes…", "info");
    await loadMatchResults();
    startPollingMatches();
  } catch (e) {
    toast(e.message, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "✦ Lancer le matching IA";
  }
});

async function loadMatchResults() {
  if (!currentJobId) return;
  try {
    matches = await api.getMatchesForJob(currentJobId);
    renderMatchResults();
    if (matches.length) document.getElementById("match-results-section")?.classList.remove("hidden");
  } catch (e) { toast(e.message, "error"); }
}

function renderMatchResults(filter = "") {
  const tbody = document.getElementById("match-table-body");
  if (!tbody) return;
  const list = filter
    ? matches.filter(m => (m.candidate_name || "").toLowerCase().includes(filter.toLowerCase()))
    : matches;
  list.sort((a, b) => (b.overall_score || 0) - (a.overall_score || 0));
  tbody.innerHTML = list.length
    ? list.map(m => matchRow(m)).join("")
    : '<tr><td colspan="6" class="text-muted text-sm" style="text-align:center;padding:24px">Aucun résultat</td></tr>';
}

document.getElementById("results-filter")?.addEventListener("input", e =>
  renderMatchResults(e.target.value)
);
document.getElementById("refresh-results")?.addEventListener("click", loadMatchResults);

function startPollingMatches() {
  if (pollInterval) clearInterval(pollInterval);
  pollInterval = setInterval(async () => {
    if (!currentJobId || !matches.some(m => m.status === "pending")) {
      clearInterval(pollInterval);
      pollInterval = null;
      return;
    }
    await loadMatchResults();
  }, 5000);
}

window.viewReport = async function(matchId) {
  try {
    const m = matches.find(x => x.id === matchId) || await api.getMatch(matchId);
    if (m.status === "pending") {
      openModal(`<div class="modal-header"><h2>Analyse en cours…</h2><button class="close-btn" onclick="closeModal()">✕</button></div>
        <div style="text-align:center;padding:40px">
          <div class="spinner" style="width:36px;height:36px;margin:0 auto 16px"></div>
          <p class="text-muted">L'IA analyse le CV par rapport au poste…</p>
        </div>`);
      return;
    }
    if (m.status === "error") {
      openModal(`<div class="modal-header"><h2>Erreur IA</h2><button class="close-btn" onclick="closeModal()">✕</button></div>
        <p class="text-muted" style="padding:20px">${m.error_message || "Erreur inconnue"}</p>`);
      return;
    }
    openModal(matchReport(m), true);
  } catch (e) { toast(e.message, "error"); }
};

window.onPipelineChange = async function(select) {
  const matchId = +select.dataset.matchId;
  const status  = select.value;
  try {
    await api.updatePipeline(matchId, status);
    const idx = matches.findIndex(m => m.id === matchId);
    if (idx !== -1) matches[idx].pipeline_status = status;
    toast("Statut mis à jour", "success");
  } catch (e) {
    toast("Erreur mise à jour pipeline : " + e.message, "error");
    select.value = matches.find(m => m.id === matchId)?.pipeline_status || "nouveau";
  }
};

window.saveNotes = async function(matchId) {
  const textarea = document.getElementById(`report-notes-${matchId}`);
  if (!textarea) return;
  const notes  = textarea.value;
  const match  = matches.find(m => m.id === matchId);
  const status = match?.pipeline_status || "nouveau";
  try {
    await api.updatePipeline(matchId, status, notes);
    const idx = matches.findIndex(m => m.id === matchId);
    if (idx !== -1) matches[idx].notes = notes;
    toast("Notes enregistrées", "success");
  } catch (e) { toast(e.message, "error"); }
};

/* ════════════ PIPELINE / KANBAN ════════════ */
const KANBAN_COLS = [
  { key: "nouveau",   label: "🆕 Nouveau"     },
  { key: "examen",    label: "🔍 En examen"   },
  { key: "entretien", label: "🗓️ Entretien"   },
  { key: "offre",     label: "📨 Offre"       },
  { key: "recrute",   label: "🎉 Recruté"     },
  { key: "rejete",    label: "❌ Rejeté"      },
];

async function loadPipeline() {
  const board = document.getElementById("kanban-board");
  if (!board) return;
  board.innerHTML = KANBAN_COLS
    .map(c => `<div class="kanban-col" data-col="${c.key}">
      <div class="kanban-col-header pl-${c.key}">${c.label} <span class="kanban-count" id="kc-${c.key}"></span></div>
      <div class="kanban-col-body" id="kb-${c.key}">
        <div class="text-muted text-sm" style="padding:12px">Chargement…</div>
      </div>
    </div>`).join("");

  try {
    jobs = await api.listJobs();
    populatePipelineJobFilter();
    await renderKanban();
  } catch (e) { toast(e.message, "error"); }
}

async function renderKanban() {
  const filterJobId = document.getElementById("pipeline-job-filter")?.value;
  const jobsToFetch = filterJobId ? jobs.filter(j => j.id === +filterJobId) : jobs;

  const allMatches = [];
  await Promise.all(jobsToFetch.map(async j => {
    try {
      const ms = await api.getMatchesForJob(j.id);
      ms.forEach(m => { m.job_title = j.title; });
      allMatches.push(...ms.filter(m => m.status === "completed"));
    } catch {}
  }));

  const grouped = {};
  KANBAN_COLS.forEach(c => { grouped[c.key] = []; });
  allMatches.forEach(m => {
    const key = m.pipeline_status || "nouveau";
    if (grouped[key]) grouped[key].push(m);
    else grouped["nouveau"].push(m);
  });

  KANBAN_COLS.forEach(c => {
    const body  = document.getElementById(`kb-${c.key}`);
    const count = document.getElementById(`kc-${c.key}`);
    if (!body) return;
    const cards = grouped[c.key] || [];
    if (count) count.textContent = cards.length ? `(${cards.length})` : "";
    body.innerHTML = cards.length
      ? cards.sort((a, b) => (b.overall_score || 0) - (a.overall_score || 0))
             .map(m => kanbanCard(m)).join("")
      : '<div class="text-muted text-sm" style="padding:12px;font-size:12px">Aucun candidat</div>';
  });
}

function populatePipelineJobFilter() {
  const sel = document.getElementById("pipeline-job-filter");
  if (!sel) return;
  const current = sel.value;
  sel.innerHTML = '<option value="">Tous les postes</option>' +
    jobs.map(j => `<option value="${j.id}"${j.id === +current ? " selected" : ""}>${j.title}</option>`).join("");
}

document.getElementById("pipeline-job-filter")?.addEventListener("change", renderKanban);
document.getElementById("refresh-pipeline")?.addEventListener("click", renderKanban);

/* ── Init ── */
showView("dashboard");
