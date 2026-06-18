const BASE = "/api";

async function request(method, path, body, isFile = false) {
  const opts = { method, headers: {} };
  if (body) {
    if (isFile) {
      opts.body = body;
    } else {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }
  }
  const res = await fetch(BASE + path, opts);
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try { msg = (await res.json()).detail || msg; } catch {}
    throw new Error(msg);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // ── CVs ──
  uploadCV(file) {
    const fd = new FormData();
    fd.append("file", file);
    return request("POST", "/cv/upload", fd, true);
  },
  listCVs()    { return request("GET",    "/cv/"); },
  getCV(id)    { return request("GET",    `/cv/${id}`); },
  deleteCV(id) { return request("DELETE", `/cv/${id}`); },

  // ── Jobs ──
  createJob(data) { return request("POST",   "/jobs/", data); },
  listJobs()      { return request("GET",    "/jobs/"); },
  getJob(id)      { return request("GET",    `/jobs/${id}`); },
  deleteJob(id)   { return request("DELETE", `/jobs/${id}`); },

  uploadJobFile(file, title, company) {
    const fd = new FormData();
    fd.append("file",    file);
    fd.append("title",   title);
    if (company) fd.append("company", company);
    return request("POST", "/jobs/upload", fd, true);
  },

  // ── Matching ──
  runMatch(jobId, cvIds)      { return request("POST", "/matching/run", { job_id: jobId, cv_ids: cvIds }); },
  getMatchesForJob(jobId)     { return request("GET",  `/matching/job/${jobId}`); },
  getMatch(matchId)           { return request("GET",  `/matching/${matchId}`); },
  deleteMatch(matchId)        { return request("DELETE", `/matching/${matchId}`); },
  getStats()                  { return request("GET",  "/matching/stats/overview"); },

  updatePipeline(matchId, status, notes = null) {
    return request("PATCH", `/matching/${matchId}/pipeline`, { pipeline_status: status, notes });
  },
};
