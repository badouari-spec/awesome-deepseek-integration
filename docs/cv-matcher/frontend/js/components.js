/* ── Toast ── */
export function toast(msg, type = "info") {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  const icons = { success: "✓", error: "✕", info: "ℹ" };
  el.innerHTML = `<span>${icons[type] || "ℹ"}</span><span>${msg}</span>`;
  document.getElementById("toast-container").appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

/* ── Modal ── */
export function openModal(titleText, contentHtml, footerHtml = "") {
  const existing = document.getElementById("app-modal");
  if (existing) existing.remove();

  const backdrop = document.createElement("div");
  backdrop.className = "modal-backdrop";
  backdrop.id = "app-modal";
  backdrop.innerHTML = `
    <div class="modal">
      <div class="modal-header">
        <h2>${titleText}</h2>
        <button class="close-btn" id="modal-close">✕</button>
      </div>
      <div id="modal-body">${contentHtml}</div>
      ${footerHtml ? `<div class="mt-4">${footerHtml}</div>` : ""}
    </div>`;
  document.body.appendChild(backdrop);
  document.getElementById("modal-close").onclick = closeModal;
  backdrop.addEventListener("click", (e) => { if (e.target === backdrop) closeModal(); });
  return backdrop;
}

export function closeModal() {
  const m = document.getElementById("app-modal");
  if (m) m.remove();
}

/* ── Score helpers ── */
export function scoreClass(score) {
  if (score >= 85) return "score-strong";
  if (score >= 70) return "score-good";
  if (score >= 50) return "score-partial";
  if (score >= 30) return "score-weak";
  return "score-poor";
}

export function progressColor(score) {
  if (score >= 70) return "green";
  if (score >= 50) return "amber";
  return "red";
}

export function recommendationBadge(rec) {
  const map = {
    "Strong Match": "background:rgba(34,197,94,.15);color:#4ade80",
    "Good Match": "background:rgba(132,204,22,.15);color:#a3e635",
    "Partial Match": "background:rgba(245,158,11,.15);color:#fbbf24",
    "Weak Match": "background:rgba(249,115,22,.15);color:#fb923c",
    "Poor Match": "background:rgba(239,68,68,.15);color:#f87171",
  };
  const style = map[rec] || "background:var(--surface2);color:var(--text-muted)";
  return `<span class="badge" style="${style}">${rec || "Pending"}</span>`;
}

/* ── CV card row ── */
export function cvRow(cv, onView, onDelete) {
  const name = cv.candidate_name || cv.filename;
  const skills = cv.parsed_data?.skills?.technical?.slice(0, 4) || [];
  const pillsHtml = skills.map(s => `<span class="skill-pill pill-neutral">${s}</span>`).join("");
  return `
    <tr data-id="${cv.id}">
      <td>
        <div class="font-bold" style="font-size:13.5px">${name}</div>
        <div class="text-muted text-sm mt-1">${cv.filename}</div>
      </td>
      <td>${cv.parsed_data?.total_years_experience ?? "—"} yrs</td>
      <td>${pillsHtml || '<span class="text-muted text-sm">—</span>'}</td>
      <td><span class="badge badge-${cv.status}">${cv.status}</span></td>
      <td>
        <div class="flex gap-2">
          <button class="btn btn-secondary btn-sm" onclick="(${onView})(${JSON.stringify(cv.id)})">View</button>
          <button class="btn btn-danger btn-sm" onclick="(${onDelete})(${JSON.stringify(cv.id)})">Delete</button>
        </div>
      </td>
    </tr>`;
}

/* ── Job card row ── */
export function jobRow(job, onView, onMatch, onDelete) {
  const req = job.parsed_data?.required_skills?.slice(0, 4).map(s => s.skill || s) || [];
  const pillsHtml = req.map(s => `<span class="skill-pill pill-neutral">${s}</span>`).join("");
  return `
    <tr data-id="${job.id}">
      <td>
        <div class="font-bold" style="font-size:13.5px">${job.title}</div>
        ${job.company ? `<div class="text-muted text-sm mt-1">${job.company}</div>` : ""}
      </td>
      <td>${pillsHtml || '<span class="text-muted text-sm">—</span>'}</td>
      <td><span class="badge badge-${job.status}">${job.status}</span></td>
      <td>
        <div class="flex gap-2">
          <button class="btn btn-primary btn-sm" onclick="(${onMatch})(${JSON.stringify(job.id)})">Match CVs</button>
          <button class="btn btn-secondary btn-sm" onclick="(${onView})(${JSON.stringify(job.id)})">View</button>
          <button class="btn btn-danger btn-sm" onclick="(${onDelete})(${JSON.stringify(job.id)})">Delete</button>
        </div>
      </td>
    </tr>`;
}

/* ── Match result row ── */
export function matchRow(match, cvMap, onView) {
  const cv = cvMap[match.cv_id];
  const name = cv?.candidate_name || cv?.filename || match.cv_id;
  const score = match.overall_score ?? null;
  const sc = scoreClass(score || 0);
  return `
    <tr data-id="${match.id}">
      <td>
        <div class="font-bold" style="font-size:13.5px">${name}</div>
      </td>
      <td>
        <div class="score-circle ${sc}" style="width:48px;height:48px;font-size:15px">
          ${score !== null ? Math.round(score) : "—"}
          <small>/ 100</small>
        </div>
      </td>
      <td>${recommendationBadge(match.recommendation)}</td>
      <td>
        ${score !== null ? `
        <div style="display:grid;gap:5px;min-width:140px">
          ${miniBar("Skills", match.skills_score)}
          ${miniBar("Exp.", match.experience_score)}
          ${miniBar("Edu.", match.education_score)}
        </div>` : '<span class="text-muted text-sm">' + match.status + '</span>'}
      </td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="(${onView})(${JSON.stringify(match.id)})">
          ${match.status === "completed" ? "Report" : "Status"}
        </button>
      </td>
    </tr>`;
}

function miniBar(label, val) {
  const v = val ?? 0;
  const color = progressColor(v);
  return `
    <div class="flex items-center gap-2" style="font-size:11px">
      <span class="text-muted" style="width:34px;flex-shrink:0">${label}</span>
      <div class="progress" style="flex:1"><div class="progress-bar ${color}" style="width:${v}%"></div></div>
      <span style="width:26px;text-align:right">${Math.round(v)}</span>
    </div>`;
}

/* ── Full match report ── */
export function matchReport(match, cv, job) {
  const d = match.match_data || {};
  const scores = d.scores || {};
  const sc = scoreClass(match.overall_score || 0);

  return `
    <div class="flex items-center gap-4 mb-6" style="flex-wrap:wrap">
      <div class="score-circle ${sc}" style="width:80px;height:80px;font-size:26px">
        ${Math.round(match.overall_score || 0)}
        <small>/ 100</small>
      </div>
      <div>
        <div style="font-size:18px;font-weight:700">${cv?.candidate_name || "Candidate"}</div>
        <div class="text-muted text-sm">${job?.title || "Position"} ${job?.company ? "@ " + job.company : ""}</div>
        <div class="mt-4">${recommendationBadge(match.recommendation)}</div>
      </div>
    </div>

    <!-- Score breakdown -->
    <div class="card mb-4">
      <div class="card-title">Score Breakdown</div>
      <div style="display:grid;gap:10px">
        ${scoreBar("Technical Skills", scores.skills, 35)}
        ${scoreBar("Work Experience", scores.experience, 30)}
        ${scoreBar("Education", scores.education, 15)}
        ${scoreBar("Culture Fit", scores.culture_fit, 20)}
      </div>
    </div>

    <!-- Skills analysis -->
    ${d.matched_skills?.length ? `
    <div class="report-section">
      <h3>Matched Skills</h3>
      <div>${d.matched_skills.map(s => `<span class="skill-pill pill-matched">✓ ${s}</span>`).join("")}</div>
    </div>` : ""}

    ${d.missing_critical_skills?.length ? `
    <div class="report-section" style="border-left-color:var(--danger)">
      <h3>Missing Critical Skills</h3>
      <div>${d.missing_critical_skills.map(s => `<span class="skill-pill pill-missing">✕ ${s}</span>`).join("")}</div>
    </div>` : ""}

    ${d.missing_preferred_skills?.length ? `
    <div class="report-section" style="border-left-color:var(--warning)">
      <h3>Missing Preferred Skills</h3>
      <div>${d.missing_preferred_skills.map(s => `<span class="skill-pill pill-preferred">◎ ${s}</span>`).join("")}</div>
    </div>` : ""}

    <!-- Strengths & Concerns -->
    ${d.strengths?.length ? `
    <div class="report-section">
      <h3>Strengths</h3>
      ${d.strengths.map(s => `
        <div class="strength-item">
          <strong>✓ ${s.point}</strong>
          <span class="text-muted text-sm">${s.explanation}</span>
        </div>`).join("")}
    </div>` : ""}

    ${d.concerns?.length ? `
    <div class="report-section" style="border-left-color:var(--warning)">
      <h3>Areas of Concern</h3>
      ${d.concerns.map(c => `
        <div class="concern-item">
          <strong>⚠ ${c.point}</strong>
          <span class="text-muted text-sm">${c.explanation}</span>
        </div>`).join("")}
    </div>` : ""}

    <!-- Detailed analysis -->
    ${d.overall_analysis ? `
    <div class="report-section">
      <h3>Overall Analysis</h3>
      <p style="font-size:13.5px;line-height:1.7;color:var(--text-muted)">${d.overall_analysis}</p>
    </div>` : ""}

    ${d.experience_analysis ? `
    <div class="report-section">
      <h3>Experience Analysis</h3>
      <p style="font-size:13.5px;line-height:1.7;color:var(--text-muted)">${d.experience_analysis}</p>
    </div>` : ""}

    <!-- Interview questions -->
    ${d.interview_questions?.length ? `
    <div class="report-section">
      <h3>Suggested Interview Questions</h3>
      <ol style="padding-left:18px;display:grid;gap:6px">
        ${d.interview_questions.map(q => `<li style="font-size:13.5px;color:var(--text-muted)">${q}</li>`).join("")}
      </ol>
    </div>` : ""}

    ${d.onboarding_notes ? `
    <div class="report-section" style="border-left-color:var(--info)">
      <h3>Onboarding Notes</h3>
      <p style="font-size:13.5px;line-height:1.7;color:var(--text-muted)">${d.onboarding_notes}</p>
    </div>` : ""}`;
}

function scoreBar(label, val, weight) {
  const v = val ?? 0;
  const color = progressColor(v);
  return `
    <div>
      <div class="flex justify-between mb-2" style="font-size:12.5px">
        <span>${label} <span class="text-muted">(${weight}%)</span></span>
        <span class="font-bold">${Math.round(v)}/100</span>
      </div>
      <div class="progress" style="height:8px">
        <div class="progress-bar ${color}" style="width:${v}%"></div>
      </div>
    </div>`;
}
