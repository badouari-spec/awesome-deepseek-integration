import { api } from "./api.js";
import {
  toast, openModal, closeModal,
  cvRow, jobRow, matchRow, matchReport,
  scoreClass, recommendationBadge,
} from "./components.js";

/* ── State ── */
let cvs = [], jobs = [], matches = [];
let currentJobId = null;
let pollInterval = null;

/* ── Navigation ── */
const views = ["dashboard", "cvs", "jobs", "matching"];

function showView(name) {
  views.forEach(v => {
    document.getElementById(`view-${v}`).classList.toggle("hidden", v !== name);
  });
  document.querySelectorAll("nav a[data-view]").forEach(a => {
    a.classList.toggle("active", a.dataset.view === name);
  });
  if (name === "dashboard") loadDashboard();
  else if (name === "cvs")  loadCVs();
  else if (name === "jobs") loadJobs();
  else if (name === "matching") loadMatchingView();
}

document.querySelectorAll("nav a[data-view]").forEach(a =>
  a.addEventListener("click", () => showView(a.dataset.view))
);

/* ════════════ DASHBOARD ════════════ */
async function loadDashboard() {
  try {
    [cvs, jobs] = await Promise.all([api.listCVs(), api.listJobs()]);
    const allMatches = [];
    await Promise.all(jobs.map(async j => {
      const m = await api.getMatchesForJob(j.id);
      allMatches.push(...m);
    }));
    matches = allMatches;

    document.getElementById("stat-cvs").textContent    = cvs.length;
    document.getElementById("stat-jobs").textContent   = jobs.length;
    document.getElementById("stat-matches").textContent = allMatches.length;
    document.getElementById("stat-strong").textContent  =
      allMatches.filter(m => m.recommendation === "Strong Match").length;

    const recent  = allMatches
      .filter(m => m.status === "completed")
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 5);
    const cvMap  = Object.fromEntries(cvs.map(c => [c.id, c]));
    const jobMap = Object.fromEntries(jobs.map(j => [j.id, j]));

    document.getElementById("recent-matches").innerHTML = recent.length
      ? recent.map(m => `
          <tr>
            <td>${cvMap[m.cv_id]?.candidate_name || "—"}</td>
            <td>${jobMap[m.job_id]?.title || "—"}</td>
            <td>
              <div class="score-circle ${scoreClass(m.overall_score || 0)}"
                   style="width:40px;height:40px;font-size:13px">
                ${Math.round(m.overall_score || 0)}
              </div>
            </td>
            <td>${recommendationBadge(m.recommendation)}</td>
          </tr>`).join("")
      : '<tr><td colspan="4" class="text-muted text-sm" style="text-align:center;padding:24px">Aucun matching encore</td></tr>';
  } catch (e) {
    toast("Erreur tableau de bord : " + e.message, "error");
  }
}

/* ════════════ CVs ════════════ */
async function loadCVs() {
  try {
    cvs = await api.listCVs();
    renderCVTable();
  } catch (e) { toast(e.message, "error"); }
}

function renderCVTable() {
  const tbody = document.getElementById("cv-table-body");
  tbody.innerHTML = cvs.length
    ? cvs.map(cv => cvRow(cv, viewCV.toString(), deleteCV.toString())).join("")
    : '<tr><td colspan="5"><div class="empty-state"><div class="icon">📄</div><p>Aucun CV importé</p></div></td></tr>';
}

async function viewCV(id) {
  const cv = cvs.find(c => c.id === id) || await api.getCV(id);
  const d  = cv.parsed_data || {};
  const skills = d.skills || {};
  const allSkills = [
    ...(skills.technical || []),
    ...(skills.programming_languages || []),
    ...(skills.tools || []),
  ];

  openModal(`CV — ${cv.candidate_name || cv.filename}`, `
    <div class="grid-2 mb-4">
      <div>
        <div class="text-muted text-sm mb-2">Contact</div>
        <div style="font-size:13.5px">${d.email || "—"}</div>
        <div style="font-size:13.5px">${d.phone || "—"}</div>
        <div style="font-size:13.5px">${d.location || "—"}</div>
      </div>
      <div>
        <div class="text-muted text-sm mb-2">Expérience totale</div>
        <div style="font-size:22px;font-weight:700">${d.total_years_experience ?? "—"}
          <span class="text-muted" style="font-size:13px">ans</span></div>
      </div>
    </div>
    ${d.summary ? `<div class="card mb-4" style="font-size:13.5px;line-height:1.6;color:var(--text-muted)">${d.summary}</div>` : ""}
    ${allSkills.length ? `
      <div class="mb-4">
        <div class="card-title">Compétences techniques</div>
        <div>${allSkills.map(s => `<span class="skill-pill pill-neutral">${s}</span>`).join("")}</div>
      </div>` : ""}
    ${skills.soft?.length ? `
      <div class="mb-4">
        <div class="card-title">Soft skills</div>
        <div>${skills.soft.map(s => `<span class="skill-pill pill-neutral">${s}</span>`).join("")}</div>
      </div>` : ""}
    ${d.experience?.length ? `
      <div class="mb-4">
        <div class="card-title">Expériences</div>
        ${d.experience.map(e => `
          <div class="card mb-2" style="padding:14px">
            <div class="flex justify-between">
              <div><strong>${e.title}</strong> @ ${e.company}</div>
              <div class="text-muted text-sm">${e.start_date} — ${e.end_date}</div>
            </div>
            ${e.technologies?.length
              ? `<div style="margin-top:6px">${e.technologies.map(t => `<span class="skill-pill pill-neutral">${t}</span>`).join("")}</div>`
              : ""}
          </div>`).join("")}
      </div>` : ""}
    ${d.education?.length ? `
      <div>
        <div class="card-title">Formation</div>
        ${d.education.map(e => `
          <div class="flex justify-between" style="font-size:13.5px;padding:6px 0;border-bottom:1px solid var(--border)">
            <span><strong>${e.degree}</strong> en ${e.field}</span>
            <span class="text-muted">${e.institution} · ${e.end_year || "en cours"}</span>
          </div>`).join("")}
      </div>` : ""}`);
}

async function deleteCV(id) {
  if (!confirm("Supprimer ce CV ?")) return;
  try {
    await api.deleteCV(id);
    cvs = cvs.filter(c => c.id !== id);
    renderCVTable();
    toast("CV supprimé", "success");
  } catch (e) { toast(e.message, "error"); }
}

/* ── CV upload zone ── */
const uploadZone = document.getElementById("upload-zone");
const fileInput  = document.getElementById("file-input");

uploadZone?.addEventListener("click", () => fileInput.click());
uploadZone?.addEventListener("dragover", e => { e.preventDefault(); uploadZone.classList.add("drag-over"); });
uploadZone?.addEventListener("dragleave", () => uploadZone.classList.remove("drag-over"));
uploadZone?.addEventListener("drop", e => {
  e.preventDefault();
  uploadZone.classList.remove("drag-over");
  handleCVFiles(e.dataTransfer.files);
});
fileInput?.addEventListener("change", () => {
  handleCVFiles(fileInput.files);
  fileInput.value = "";
});

async function handleCVFiles(files) {
  for (const file of files) {
    try {
      toast(`Importation de ${file.name}…`, "info");
      const cv = await api.uploadCV(file);
      cvs.unshift(cv);
      renderCVTable();
      toast(`${file.name} importé — analyse en cours…`, "success");
      pollCV(cv.id);
    } catch (e) {
      toast(`Échec : ${e.message}`, "error");
    }
  }
}

function pollCV(id) {
  const t = setInterval(async () => {
    try {
      const cv = await api.getCV(id);
      const idx = cvs.findIndex(c => c.id === id);
      if (idx !== -1) cvs[idx] = cv;
      renderCVTable();
      if (cv.status !== "pending") {
        clearInterval(t);
        if (cv.status === "parsed")
          toast(`✓ ${cv.candidate_name || cv.filename} analysé`, "success");
        else
          toast(`Erreur d'analyse : ${cv.error_message}`, "error");
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
    ? jobs.map(j => jobRow(j, viewJob.toString(), openMatchModal.toString(), deleteJob.toString())).join("")
    : '<tr><td colspan="4"><div class="empty-state"><div class="icon">💼</div><p>Aucun poste créé</p></div></td></tr>';
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

/* ── Soumission texte ── */
document.getElementById("job-text-submit")?.addEventListener("click", async () => {
  const title       = document.getElementById("job-title").value.trim();
  const company     = document.getElementById("job-company").value.trim();
  const description = document.getElementById("job-desc").value.trim();
  if (!title)       return toast("Le titre est requis", "error");
  if (!description) return toast("La description est requise", "error");

  const btn = document.getElementById("job-text-submit");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Création…';
  try {
    const job = await api.createJob({ title, company: company || null, description });
    jobs.unshift(job);
    renderJobTable();
    document.getElementById("job-title").value   = "";
    document.getElementById("job-company").value = "";
    document.getElementById("job-desc").value    = "";
    toast(`Poste « ${title} » créé — analyse en cours…`, "success");
    pollJob(job.id);
  } catch (e) {
    toast(e.message, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "✦ Créer & Analyser avec l'IA";
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
jdZone?.addEventListener("dragleave", () => jdZone.classList.remove("drag-over"));
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
    // Reset
    selectedJdFile = null;
    jdFileName.textContent = "";
    jdZone.style.borderColor = "";
    document.getElementById("job-title").value   = "";
    document.getElementById("job-company").value = "";
  } catch (e) {
    toast(e.message, "error");
  } finally {
    jdUploadBtn.disabled = false;
    jdUploadBtn.textContent = "✦ Créer depuis le fichier";
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
        if (job.status === "parsed") toast(`✓ « ${job.title} » analysé`, "success");
        else toast(`Erreur : ${job.error_message}`, "error");
      }
    } catch { clearInterval(t); }
  }, 3000);
}

async function viewJob(id) {
  const job = jobs.find(j => j.id === id) || await api.getJob(id);
  const d   = job.parsed_data || {};
  const req  = d.required_skills || [];
  const pref = d.preferred_skills || [];

  openModal(`Poste — ${job.title}`, `
    <div class="grid-2 mb-4">
      <div><div class="text-muted text-sm mb-1">Entreprise</div><div>${job.company || "—"}</div></div>
      <div><div class="text-muted text-sm mb-1">Expérience</div><div>${d.experience_required?.description || "—"}</div></div>
    </div>
    ${req.length ? `
      <div class="mb-4">
        <div class="card-title">Compétences requises</div>
        <div>${req.map(s => `<span class="skill-pill pill-missing">${s.skill || s}</span>`).join("")}</div>
      </div>` : ""}
    ${pref.length ? `
      <div class="mb-4">
        <div class="card-title">Compétences souhaitées</div>
        <div>${pref.map(s => `<span class="skill-pill pill-preferred">${s.skill || s}</span>`).join("")}</div>
      </div>` : ""}
    ${d.responsibilities?.length ? `
      <div>
        <div class="card-title">Responsabilités</div>
        <ul style="padding-left:18px;display:grid;gap:5px">
          ${d.responsibilities.map(r => `<li style="font-size:13px;color:var(--text-muted)">${r}</li>`).join("")}
        </ul>
      </div>` : ""}`);
}

async function deleteJob(id) {
  if (!confirm("Supprimer ce poste ?")) return;
  try {
    await api.deleteJob(id);
    jobs = jobs.filter(j => j.id !== id);
    renderJobTable();
    toast("Poste supprimé", "success");
  } catch (e) { toast(e.message, "error"); }
}

/* ════════════ MATCHING ════════════ */
async function loadMatchingView() {
  try {
    [cvs, jobs] = await Promise.all([api.listCVs(), api.listJobs()]);
    renderJobSelector();
  } catch (e) { toast(e.message, "error"); }
}

function renderJobSelector() {
  const sel = document.getElementById("match-job-select");
  sel.innerHTML = '<option value="">— Sélectionnez un poste —</option>' +
    jobs.map(j => `<option value="${j.id}">${j.title}${j.company ? " @ " + j.company : ""}</option>`).join("");
}

document.getElementById("match-job-select")?.addEventListener("change", async e => {
  currentJobId = e.target.value;
  if (!currentJobId) {
    document.getElementById("match-cv-list").innerHTML = "<div class='text-muted text-sm'>Sélectionnez un poste d'abord</div>";
    document.getElementById("match-results-section").classList.add("hidden");
    return;
  }
  renderCVCheckboxes();
  await loadMatchResults();
});

function renderCVCheckboxes() {
  const parsed = cvs.filter(c => c.status === "parsed");
  const container = document.getElementById("match-cv-list");
  container.innerHTML = parsed.length
    ? parsed.map(cv => `
        <label class="card" style="display:flex;align-items:center;gap:10px;cursor:pointer;padding:12px 16px">
          <input type="checkbox" value="${cv.id}" style="accent-color:var(--primary);width:16px;height:16px">
          <div>
            <div style="font-size:13.5px;font-weight:600">${cv.candidate_name || cv.filename}</div>
            <div class="text-muted text-sm">${cv.parsed_data?.total_years_experience ?? "?"} ans d'expérience</div>
          </div>
        </label>`).join("")
    : '<div class="text-muted text-sm">Aucun CV analysé disponible. Importez des CV d\'abord.</div>';
}

document.getElementById("run-match-btn")?.addEventListener("click", async () => {
  if (!currentJobId) return toast("Sélectionnez un poste", "error");
  const checked = [...document.querySelectorAll("#match-cv-list input:checked")].map(i => i.value);
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
    if (matches.length) document.getElementById("match-results-section").classList.remove("hidden");
  } catch (e) { toast(e.message, "error"); }
}

function renderMatchResults() {
  const tbody = document.getElementById("match-table-body");
  const cvMap = Object.fromEntries(cvs.map(c => [c.id, c]));
  tbody.innerHTML = matches.length
    ? matches.map(m => matchRow(m, cvMap, viewMatchReport.toString())).join("")
    : '<tr><td colspan="5"><div class="empty-state"><div class="icon">🔍</div><p>Aucun résultat</p></div></td></tr>';
}

async function viewMatchReport(matchId) {
  const match = matches.find(m => m.id === matchId) || await api.getMatch(matchId);
  const cv    = cvs.find(c => c.id === match.cv_id);
  const job   = jobs.find(j => j.id === match.job_id);

  if (match.status === "pending") {
    openModal("Analyse en cours…", `
      <div style="text-align:center;padding:40px">
        <div class="spinner" style="width:36px;height:36px;margin:0 auto 16px"></div>
        <p class="text-muted">L'IA analyse le CV par rapport au poste…</p>
      </div>`);
    return;
  }
  if (match.status === "error") {
    openModal("Erreur", `<div class="text-muted">${match.error_message || "Erreur inconnue"}</div>`);
    return;
  }
  openModal("Rapport de matching", matchReport(match, cv, job));
}

function startPollingMatches() {
  if (pollInterval) clearInterval(pollInterval);
  pollInterval = setInterval(async () => {
    if (!currentJobId) return;
    if (!matches.filter(m => m.status === "pending").length) {
      clearInterval(pollInterval);
      return;
    }
    await loadMatchResults();
  }, 4000);
}

async function openMatchModal(jobId) {
  showView("matching");
  await new Promise(r => setTimeout(r, 100));
  const sel = document.getElementById("match-job-select");
  sel.value = jobId;
  sel.dispatchEvent(new Event("change"));
}

/* ── Init ── */
window.addEventListener("refresh-matches", loadMatchResults);
showView("dashboard");
