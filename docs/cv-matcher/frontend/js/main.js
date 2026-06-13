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
  document.querySelectorAll("nav a").forEach(a => {
    a.classList.toggle("active", a.dataset.view === name);
  });

  if (name === "dashboard") loadDashboard();
  else if (name === "cvs") loadCVs();
  else if (name === "jobs") loadJobs();
  else if (name === "matching") loadMatchingView();
}

document.querySelectorAll("nav a[data-view]").forEach(a => {
  a.addEventListener("click", () => showView(a.dataset.view));
});

/* ── Dashboard ── */
async function loadDashboard() {
  try {
    [cvs, jobs] = await Promise.all([api.listCVs(), api.listJobs()]);
    const parsed = cvs.filter(c => c.status === "parsed").length;
    const allMatches = [];
    await Promise.all(jobs.map(async j => {
      const m = await api.getMatchesForJob(j.id);
      allMatches.push(...m);
    }));
    matches = allMatches;
    const strong = allMatches.filter(m => m.recommendation === "Strong Match").length;

    document.getElementById("stat-cvs").textContent = cvs.length;
    document.getElementById("stat-jobs").textContent = jobs.length;
    document.getElementById("stat-matches").textContent = allMatches.length;
    document.getElementById("stat-strong").textContent = strong;

    // Recent activity
    const recent = allMatches
      .filter(m => m.status === "completed")
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 5);
    const cvMap = Object.fromEntries(cvs.map(c => [c.id, c]));
    const jobMap = Object.fromEntries(jobs.map(j => [j.id, j]));
    const tbody = document.getElementById("recent-matches");
    tbody.innerHTML = recent.length
      ? recent.map(m => `
          <tr>
            <td>${cvMap[m.cv_id]?.candidate_name || "—"}</td>
            <td>${jobMap[m.job_id]?.title || "—"}</td>
            <td>
              <div class="score-circle ${scoreClass(m.overall_score || 0)}" style="width:40px;height:40px;font-size:13px">
                ${Math.round(m.overall_score || 0)}
              </div>
            </td>
            <td>${recommendationBadge(m.recommendation)}</td>
          </tr>`).join("")
      : '<tr><td colspan="4" class="text-muted text-sm" style="text-align:center;padding:24px">No matches yet</td></tr>';
  } catch (e) {
    toast("Failed to load dashboard: " + e.message, "error");
  }
}

/* ── CVs ── */
async function loadCVs() {
  try {
    cvs = await api.listCVs();
    renderCVTable();
  } catch (e) {
    toast(e.message, "error");
  }
}

function renderCVTable() {
  const tbody = document.getElementById("cv-table-body");
  if (!cvs.length) {
    tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state"><div class="icon">📄</div><p>No CVs uploaded yet</p></div></td></tr>';
    return;
  }
  tbody.innerHTML = cvs.map(cv =>
    cvRow(cv, viewCV.toString(), deleteCV.toString())
  ).join("");
}

async function viewCV(id) {
  const cv = cvs.find(c => c.id === id) || await api.getCV(id);
  const d = cv.parsed_data || {};
  const skills = d.skills || {};
  const allSkills = [...(skills.technical || []), ...(skills.programming_languages || []), ...(skills.tools || [])];

  openModal(`CV — ${cv.candidate_name || cv.filename}`, `
    <div class="grid-2 mb-4">
      <div>
        <div class="text-muted text-sm mb-2">Contact</div>
        <div style="font-size:13.5px">${d.email || "—"}</div>
        <div style="font-size:13.5px">${d.phone || "—"}</div>
        <div style="font-size:13.5px">${d.location || "—"}</div>
      </div>
      <div>
        <div class="text-muted text-sm mb-2">Experience</div>
        <div style="font-size:22px;font-weight:700">${d.total_years_experience ?? "—"} <span class="text-muted" style="font-size:13px">years</span></div>
      </div>
    </div>

    ${d.summary ? `<div class="card mb-4" style="font-size:13.5px;line-height:1.6;color:var(--text-muted)">${d.summary}</div>` : ""}

    ${allSkills.length ? `
    <div class="mb-4">
      <div class="card-title">Technical Skills</div>
      <div>${allSkills.map(s => `<span class="skill-pill pill-neutral">${s}</span>`).join("")}</div>
    </div>` : ""}

    ${skills.soft?.length ? `
    <div class="mb-4">
      <div class="card-title">Soft Skills</div>
      <div>${skills.soft.map(s => `<span class="skill-pill pill-neutral">${s}</span>`).join("")}</div>
    </div>` : ""}

    ${d.experience?.length ? `
    <div class="mb-4">
      <div class="card-title">Work Experience</div>
      ${d.experience.map(e => `
        <div class="card mb-2" style="padding:14px">
          <div class="flex justify-between">
            <div><strong>${e.title}</strong> @ ${e.company}</div>
            <div class="text-muted text-sm">${e.start_date} — ${e.end_date}</div>
          </div>
          ${e.technologies?.length ? `<div class="mt-4" style="margin-top:6px">${e.technologies.map(t => `<span class="skill-pill pill-neutral">${t}</span>`).join("")}</div>` : ""}
        </div>`).join("")}
    </div>` : ""}

    ${d.education?.length ? `
    <div>
      <div class="card-title">Education</div>
      ${d.education.map(e => `
        <div class="flex justify-between" style="font-size:13.5px;padding:6px 0;border-bottom:1px solid var(--border)">
          <span><strong>${e.degree}</strong> in ${e.field}</span>
          <span class="text-muted">${e.institution} · ${e.end_year || "ongoing"}</span>
        </div>`).join("")}
    </div>` : ""}`);
}

async function deleteCV(id) {
  if (!confirm("Delete this CV?")) return;
  try {
    await api.deleteCV(id);
    cvs = cvs.filter(c => c.id !== id);
    renderCVTable();
    toast("CV deleted", "success");
  } catch (e) {
    toast(e.message, "error");
  }
}

/* ── CV upload ── */
const uploadZone = document.getElementById("upload-zone");
const fileInput  = document.getElementById("file-input");

uploadZone?.addEventListener("click", () => fileInput.click());
uploadZone?.addEventListener("dragover", e => { e.preventDefault(); uploadZone.classList.add("drag-over"); });
uploadZone?.addEventListener("dragleave", () => uploadZone.classList.remove("drag-over"));
uploadZone?.addEventListener("drop", e => {
  e.preventDefault();
  uploadZone.classList.remove("drag-over");
  handleFiles(e.dataTransfer.files);
});
fileInput?.addEventListener("change", () => handleFiles(fileInput.files));

async function handleFiles(files) {
  for (const file of files) {
    try {
      toast(`Uploading ${file.name}…`, "info");
      const cv = await api.uploadCV(file);
      cvs.unshift(cv);
      renderCVTable();
      toast(`${file.name} uploaded — parsing…`, "success");
      pollCV(cv.id);
    } catch (e) {
      toast(`Upload failed: ${e.message}`, "error");
    }
  }
  fileInput.value = "";
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
        if (cv.status === "parsed") toast(`✓ ${cv.candidate_name || cv.filename} parsed`, "success");
        else toast(`Parse error: ${cv.error_message}`, "error");
      }
    } catch { clearInterval(t); }
  }, 3000);
}

/* ── Jobs ── */
async function loadJobs() {
  try {
    jobs = await api.listJobs();
    renderJobTable();
  } catch (e) {
    toast(e.message, "error");
  }
}

function renderJobTable() {
  const tbody = document.getElementById("job-table-body");
  if (!jobs.length) {
    tbody.innerHTML = '<tr><td colspan="4"><div class="empty-state"><div class="icon">💼</div><p>No job descriptions yet</p></div></td></tr>';
    return;
  }
  tbody.innerHTML = jobs.map(j =>
    jobRow(j, viewJob.toString(), openMatchModal.toString(), deleteJob.toString())
  ).join("");
}

document.getElementById("job-form")?.addEventListener("submit", async e => {
  e.preventDefault();
  const title = document.getElementById("job-title").value.trim();
  const company = document.getElementById("job-company").value.trim();
  const description = document.getElementById("job-desc").value.trim();
  if (!title || !description) return toast("Title and description are required", "error");

  try {
    const job = await api.createJob({ title, company: company || null, description });
    jobs.unshift(job);
    renderJobTable();
    e.target.reset();
    toast(`Job "${title}" created — parsing…`, "success");
    pollJob(job.id);
  } catch (err) {
    toast(err.message, "error");
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
        if (job.status === "parsed") toast(`✓ "${job.title}" parsed`, "success");
        else toast(`Parse error: ${job.error_message}`, "error");
      }
    } catch { clearInterval(t); }
  }, 3000);
}

async function viewJob(id) {
  const job = jobs.find(j => j.id === id) || await api.getJob(id);
  const d = job.parsed_data || {};
  const req = d.required_skills || [];
  const pref = d.preferred_skills || [];

  openModal(`Job — ${job.title}`, `
    <div class="grid-2 mb-4">
      <div>
        <div class="text-muted text-sm mb-1">Company</div>
        <div>${job.company || "—"}</div>
      </div>
      <div>
        <div class="text-muted text-sm mb-1">Experience</div>
        <div>${d.experience_required?.description || "—"}</div>
      </div>
    </div>

    ${req.length ? `
    <div class="mb-4">
      <div class="card-title">Required Skills</div>
      <div>${req.map(s => `<span class="skill-pill pill-missing">${s.skill || s} <span style="opacity:.6;font-size:10px">${s.importance || ""}</span></span>`).join("")}</div>
    </div>` : ""}

    ${pref.length ? `
    <div class="mb-4">
      <div class="card-title">Preferred Skills</div>
      <div>${pref.map(s => `<span class="skill-pill pill-preferred">${s.skill || s}</span>`).join("")}</div>
    </div>` : ""}

    ${d.responsibilities?.length ? `
    <div>
      <div class="card-title">Responsibilities</div>
      <ul style="padding-left:18px;display:grid;gap:5px">
        ${d.responsibilities.map(r => `<li style="font-size:13px;color:var(--text-muted)">${r}</li>`).join("")}
      </ul>
    </div>` : ""}`);
}

async function deleteJob(id) {
  if (!confirm("Delete this job?")) return;
  try {
    await api.deleteJob(id);
    jobs = jobs.filter(j => j.id !== id);
    renderJobTable();
    toast("Job deleted", "success");
  } catch (e) {
    toast(e.message, "error");
  }
}

/* ── Matching ── */
async function loadMatchingView() {
  try {
    [cvs, jobs] = await Promise.all([api.listCVs(), api.listJobs()]);
    renderJobSelector();
  } catch (e) {
    toast(e.message, "error");
  }
}

function renderJobSelector() {
  const sel = document.getElementById("match-job-select");
  sel.innerHTML = '<option value="">— Select a job —</option>' +
    jobs.map(j => `<option value="${j.id}">${j.title}${j.company ? " @ " + j.company : ""}</option>`).join("");
}

document.getElementById("match-job-select")?.addEventListener("change", async e => {
  currentJobId = e.target.value;
  if (!currentJobId) {
    document.getElementById("match-cv-list").innerHTML = "";
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
            <div class="text-muted text-sm">${cv.parsed_data?.total_years_experience ?? "?"} yrs exp</div>
          </div>
        </label>`).join("")
    : '<div class="text-muted text-sm">No parsed CVs available. Upload CVs first.</div>';
}

document.getElementById("run-match-btn")?.addEventListener("click", async () => {
  if (!currentJobId) return toast("Please select a job", "error");
  const checked = [...document.querySelectorAll("#match-cv-list input:checked")].map(i => i.value);
  if (!checked.length) return toast("Select at least one CV", "error");

  const btn = document.getElementById("run-match-btn");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Running…';

  try {
    await api.runMatch(currentJobId, checked);
    toast("Matching started — results will appear shortly", "info");
    await loadMatchResults();
    startPollingMatches();
  } catch (e) {
    toast(e.message, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Run Matching";
  }
});

async function loadMatchResults() {
  if (!currentJobId) return;
  try {
    matches = await api.getMatchesForJob(currentJobId);
    renderMatchResults();
    const section = document.getElementById("match-results-section");
    if (matches.length) section.classList.remove("hidden");
  } catch (e) {
    toast(e.message, "error");
  }
}

function renderMatchResults() {
  const tbody = document.getElementById("match-table-body");
  const cvMap = Object.fromEntries(cvs.map(c => [c.id, c]));

  if (!matches.length) {
    tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state"><div class="icon">🔍</div><p>No matching results yet</p></div></td></tr>';
    return;
  }

  tbody.innerHTML = matches.map(m =>
    matchRow(m, cvMap, viewMatchReport.toString())
  ).join("");
}

async function viewMatchReport(matchId) {
  const match = matches.find(m => m.id === matchId) || await api.getMatch(matchId);
  const cv = cvs.find(c => c.id === match.cv_id);
  const job = jobs.find(j => j.id === match.job_id);

  if (match.status === "pending") {
    openModal("Matching in progress…", `
      <div style="text-align:center;padding:40px">
        <div class="spinner" style="width:36px;height:36px;margin:0 auto 16px"></div>
        <p class="text-muted">DeepSeek is analyzing the CV against the job requirements…</p>
      </div>`);
    return;
  }
  if (match.status === "error") {
    openModal("Match Error", `<div class="text-muted">${match.error_message || "Unknown error"}</div>`);
    return;
  }

  openModal(
    "Match Report",
    matchReport(match, cv, job),
  );
}

function startPollingMatches() {
  if (pollInterval) clearInterval(pollInterval);
  pollInterval = setInterval(async () => {
    if (!currentJobId) return;
    const pending = matches.filter(m => m.status === "pending");
    if (!pending.length) { clearInterval(pollInterval); return; }
    await loadMatchResults();
  }, 4000);
}

/* ── Match from job view ── */
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
