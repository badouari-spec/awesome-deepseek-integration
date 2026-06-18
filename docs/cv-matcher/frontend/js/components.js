// ── Toast ─────────────────────────────────────────────────────────────────────
export function toast(msg, type = "info") {
  const icons = { success: "✅", error: "❌", info: "ℹ️" };
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.innerHTML = `<span>${icons[type] || "ℹ️"}</span><span>${msg}</span>`;
  document.getElementById("toast-container").appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

// ── Modal ─────────────────────────────────────────────────────────────────────
export function openModal(html, wide = false) {
  closeModal();
  const bd = document.createElement("div");
  bd.className = "modal-backdrop";
  bd.id = "active-modal";
  bd.innerHTML = `<div class="modal ${wide ? "modal-wide" : ""}">${html}</div>`;
  bd.addEventListener("click", e => { if (e.target === bd) closeModal(); });
  document.body.appendChild(bd);
}
export function closeModal() {
  document.getElementById("active-modal")?.remove();
}
window.closeModal = closeModal;

// ── Score helpers ─────────────────────────────────────────────────────────────
export function scoreClass(s) {
  if (s >= 85) return "score-strong";
  if (s >= 70) return "score-good";
  if (s >= 55) return "score-partial";
  if (s >= 40) return "score-weak";
  return "score-poor";
}
export function progressColor(s) {
  if (s >= 75) return "green";
  if (s >= 50) return "amber";
  return "red";
}

// ── SVG Score ring ────────────────────────────────────────────────────────────
export function scoreRing(score, size = 80) {
  const s = Math.round(score || 0);
  const r = size / 2 - 8;
  const circ = 2 * Math.PI * r;
  const offset = circ - (s / 100) * circ;
  const c = s >= 85 ? "#22c55e" : s >= 70 ? "#84cc16"
           : s >= 55 ? "#f59e0b" : s >= 40 ? "#f97316" : "#ef4444";
  return `<div class="score-ring" style="width:${size}px;height:${size}px;position:relative;flex-shrink:0">
    <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none" stroke="var(--surface2)" stroke-width="8"/>
      <circle cx="${size/2}" cy="${size/2}" r="${r}" fill="none" stroke="${c}" stroke-width="8"
        stroke-dasharray="${circ.toFixed(1)}" stroke-dashoffset="${offset.toFixed(1)}"
        stroke-linecap="round" transform="rotate(-90 ${size/2} ${size/2})"/>
    </svg>
    <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center">
      <span style="font-size:${size < 70 ? 13 : 17}px;font-weight:700;color:${c};line-height:1">${s}</span>
      <span style="font-size:9px;color:var(--text-muted);margin-top:1px">/100</span>
    </div>
  </div>`;
}

// ── Recommendation badge ──────────────────────────────────────────────────────
export function recommendationBadge(rec) {
  const map = {
    "PRIORITAIRE":  ["🌟", "#22c55e", "rgba(34,197,94,.15)"],
    "FORT":         ["✅", "#84cc16", "rgba(132,204,22,.15)"],
    "MOYEN":        ["🔶", "#f59e0b", "rgba(245,158,11,.15)"],
    "FAIBLE":       ["⚠️", "#f97316", "rgba(249,115,22,.15)"],
    "ÉLIMINATOIRE": ["🚫", "#ef4444", "rgba(239,68,68,.15)"],
  };
  const [icon, color, bg] = map[rec] || ["❓", "var(--text-muted)", "var(--surface2)"];
  return `<span class="badge" style="color:${color};background:${bg};border:1px solid ${color}33">${icon} ${rec || "—"}</span>`;
}

// ── Pipeline badge & select ───────────────────────────────────────────────────
export function pipelineBadge(status) {
  const map = {
    nouveau:    ["🆕", "Nouveau"],
    examen:     ["🔍", "En examen"],
    entretien:  ["🗓️",  "Entretien"],
    offre:      ["📨", "Offre"],
    recrute:    ["🎉", "Recruté"],
    rejete:     ["❌", "Rejeté"],
  };
  const [icon, label] = map[status] || ["⚪", status || "nouveau"];
  return `<span class="badge pl-${status || "nouveau"}">${icon} ${label}</span>`;
}

export function pipelineSelect(matchId, current) {
  const opts = [
    ["nouveau",   "🆕 Nouveau"],
    ["examen",    "🔍 En examen"],
    ["entretien", "🗓️ Entretien"],
    ["offre",     "📨 Offre"],
    ["recrute",   "🎉 Recruté"],
    ["rejete",    "❌ Rejeté"],
  ].map(([v, l]) => `<option value="${v}"${v===current?" selected":""}>${l}</option>`).join("");
  return `<select class="pl-select" data-match-id="${matchId}" onchange="window.onPipelineChange(this)">${opts}</select>`;
}

// ── Trajectory badge ──────────────────────────────────────────────────────────
function trajectoryBadge(t) {
  const icons = { ASCENDANTE:"📈", STABLE:"➡️", RECONVERSION:"🔄", LATERALE:"↔️" };
  if (!t) return "";
  return `<span class="traj-badge traj-${t}">${icons[t]||""} ${t}</span>`;
}

// ── Skill pills ───────────────────────────────────────────────────────────────
function skillPills(items = [], cls = "pill-neutral") {
  if (!items.length) return '<span class="text-muted text-sm">—</span>';
  return items.map(s => `<span class="skill-pill ${cls}">${s}</span>`).join("");
}

// ── Dimension bar ─────────────────────────────────────────────────────────────
function dimBar(label, score) {
  const s = Math.round(score || 0);
  const c = s >= 75 ? "green" : s >= 50 ? "amber" : "red";
  return `<div class="dim-item">
    <div class="dim-label">${label}<span>${s}%</span></div>
    <div class="progress"><div class="progress-bar ${c}" style="width:${s}%"></div></div>
  </div>`;
}

// ── CV row ────────────────────────────────────────────────────────────────────
export function cvRow(cv) {
  const p = cv.parsed_data || {};
  const name  = cv.candidate_name || p.nom_candidat || cv.filename || "—";
  const exp   = p.annees_experience != null ? `${p.annees_experience} an${p.annees_experience>1?"s":""}` : "—";
  const skills = (p.competences_techniques || []).slice(0, 4)
    .map(s => `<span class="skill-pill pill-neutral">${s}</span>`).join("") || "—";
  const stCls = { pending:"badge-pending", parsed:"badge-parsed", error:"badge-error" };
  return `<tr data-cv-id="${cv.id}" data-name="${name.toLowerCase()}">
    <td><strong>${name}</strong><br><span class="text-muted text-sm">${cv.filename}</span></td>
    <td>${exp}</td>
    <td style="max-width:260px">${skills}</td>
    <td><span class="badge ${stCls[cv.status]||"badge-pending"}">${cv.status}</span></td>
    <td style="display:flex;gap:6px">
      <button class="btn btn-secondary btn-sm" onclick="window.viewCV(${cv.id})">👁 Voir</button>
      <button class="btn btn-danger btn-sm" onclick="window.deleteCV(${cv.id})">🗑</button>
    </td>
  </tr>`;
}

// ── Job row ───────────────────────────────────────────────────────────────────
export function jobRow(job) {
  const p = job.parsed_data || {};
  const skills = (p.competences_obligatoires || []).slice(0, 3)
    .map(s => `<span class="skill-pill pill-neutral">${s}</span>`).join("") || "—";
  return `<tr data-job-id="${job.id}">
    <td><strong>${job.title}</strong><br><span class="text-muted text-sm">${job.company||""}</span></td>
    <td>${skills}</td>
    <td><span class="badge ${job.status==="parsed"?"badge-parsed":"badge-pending"}">${job.status}</span></td>
    <td style="display:flex;gap:6px">
      <button class="btn btn-secondary btn-sm" onclick="window.viewJob(${job.id})">👁 Voir</button>
      <button class="btn btn-danger btn-sm" onclick="window.deleteJob(${job.id})">🗑</button>
    </td>
  </tr>`;
}

// ── Match row ─────────────────────────────────────────────────────────────────
export function matchRow(m) {
  if (m.status === "pending") {
    return `<tr id="match-row-${m.id}">
      <td>${m.candidate_name||"—"}</td>
      <td><span class="spinner"></span></td>
      <td colspan="4" class="text-muted text-sm">Analyse IA en cours…</td>
    </tr>`;
  }
  if (m.status === "error") {
    return `<tr id="match-row-${m.id}">
      <td>${m.candidate_name||"—"}</td>
      <td>—</td><td>—</td>
      <td><span class="badge badge-error">Erreur IA</span></td>
      <td>—</td><td>—</td>
    </tr>`;
  }
  const d = m.match_data || {};
  const matched = (d.competences_matchees||[]).length;
  const missing = (d.competences_manquantes||[]).length;
  return `<tr id="match-row-${m.id}">
    <td>
      <strong>${m.candidate_name||"—"}</strong>
      ${d.trajectoire_carriere ? `<br>${trajectoryBadge(d.trajectoire_carriere)}`:""}
    </td>
    <td>${scoreRing(m.overall_score, 60)}</td>
    <td>
      ${matched ? `<span class="skill-pill pill-matched" title="Validées">✓ ${matched}</span>` : ""}
      ${missing ? `<span class="skill-pill pill-missing" title="Manquantes">✗ ${missing}</span>` : ""}
    </td>
    <td>${recommendationBadge(m.recommendation)}</td>
    <td>${pipelineSelect(m.id, m.pipeline_status)}</td>
    <td><button class="btn btn-secondary btn-sm" onclick="window.viewReport(${m.id})">📋 Rapport</button></td>
  </tr>`;
}

// ── Full match report ─────────────────────────────────────────────────────────
export function matchReport(m) {
  const d  = m.match_data || {};
  const sd = d.scores_detail || {};
  const dims = [
    ["Compétences techniques",    sd.competences_techniques],
    ["Expérience pertinente",     sd.experience_pertinente],
    ["Formation",                 sd.formation],
    ["Culture fit",               sd.culture_fit],
    ["Potentiel d'évolution",     sd.potentiel_evolution],
    ["Communication / Leadership",sd.communication_leadership],
  ];
  const interviewQs = (d.questions_entretien||[])
    .map((q,i)=>`<div class="interview-q"><div class="q-num">${i+1}</div><div>${q}</div></div>`).join("")
    || '<p class="text-muted text-sm">Non disponible</p>';
  const onboarding = (d.plan_integration||[])
    .map(o=>`<div class="onboarding-item"><div class="period">${o.periode||"—"}</div><div>${o.focus||"—"}</div></div>`).join("")
    || '<p class="text-muted text-sm">Non disponible</p>';

  return `
    <div class="modal-header">
      <div style="display:flex;align-items:center;gap:16px">
        ${scoreRing(m.overall_score, 72)}
        <div>
          <h2>${m.candidate_name||"Candidat"}</h2>
          <div style="margin-top:6px;display:flex;gap:8px;flex-wrap:wrap">
            ${recommendationBadge(m.recommendation)}
            ${d.trajectoire_carriere?trajectoryBadge(d.trajectoire_carriere):""}
          </div>
        </div>
      </div>
      <button class="close-btn" onclick="closeModal()">✕</button>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px">
      <div class="report-section">
        <h3>📊 Scores par dimension</h3>
        <div class="dim-grid">${dims.map(([l,v])=>dimBar(l,v)).join("")}</div>
      </div>
      <div class="report-section">
        <h3>🧠 Analyse des compétences</h3>
        ${(d.competences_matchees||[]).length?`<p class="text-sm text-muted" style="margin-bottom:4px">✅ Validées</p>
          <div style="margin-bottom:10px">${skillPills(d.competences_matchees,"pill-matched")}</div>`:""}
        ${(d.competences_manquantes||[]).length?`<p class="text-sm text-muted" style="margin-bottom:4px">❌ À développer</p>
          <div style="margin-bottom:10px">${skillPills(d.competences_manquantes,"pill-missing")}</div>`:""}
        ${(d.competences_bonus||[]).length?`<p class="text-sm text-muted" style="margin-bottom:4px">⭐ Compétences bonus</p>
          <div>${skillPills(d.competences_bonus,"pill-preferred")}</div>`:""}
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px">
      <div class="report-section">
        <h3>✅ Points forts</h3>
        ${(d.points_forts||[]).map(f=>`<div class="strength-item">${f}</div>`).join("")||"—"}
      </div>
      <div class="report-section">
        <h3>⚠️ Points de vigilance</h3>
        ${(d.risques||[]).map(r=>`<div class="concern-item">${r}</div>`).join("")||"—"}
      </div>
    </div>

    ${d.justification?`<div class="report-section" style="margin-bottom:20px">
      <h3>💬 Synthèse IA</h3>
      <p style="font-size:13.5px;line-height:1.7;color:var(--text)">${d.justification}</p>
    </div>`:""}

    <div class="report-section" style="margin-bottom:20px">
      <h3>🎤 Questions d'entretien personnalisées</h3>
      ${interviewQs}
    </div>

    <div class="report-section" style="margin-bottom:20px">
      <h3>🚀 Plan d'intégration recommandé</h3>
      ${onboarding}
    </div>

    <div class="report-section">
      <h3>🏗️ Pipeline &amp; Notes</h3>
      <div style="display:flex;gap:12px;align-items:center;margin-bottom:10px">
        <span class="text-muted text-sm">Statut :</span>
        ${pipelineSelect(m.id, m.pipeline_status)}
      </div>
      <textarea id="report-notes-${m.id}" rows="3"
        placeholder="Notes recruteur sur ce candidat…"
        style="margin-top:4px">${m.notes||""}</textarea>
      <button class="btn btn-primary btn-sm" style="margin-top:8px"
        onclick="window.saveNotes(${m.id})">💾 Enregistrer</button>
    </div>`;
}

// ── Kanban card ───────────────────────────────────────────────────────────────
export function kanbanCard(m) {
  const s = Math.round(m.overall_score||0);
  const c = s>=75?"#22c55e":s>=55?"#f59e0b":"#ef4444";
  return `<div class="kanban-card" onclick="window.viewReport(${m.id})">
    <div class="k-name">${m.candidate_name||"Candidat"}</div>
    <div class="k-job">${m.job_title||""}</div>
    <span class="k-score" style="color:${c}">● ${s}/100</span>
  </div>`;
}
