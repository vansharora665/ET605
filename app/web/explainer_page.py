from __future__ import annotations


def render_explainer_page() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Recommendation Engine Explainer</title>
  <style>
    :root {
      --bg: #f5efe6;
      --surface: #fffaf3;
      --surface-strong: #ffffff;
      --ink: #1d232b;
      --muted: #66707c;
      --line: #ddd2c2;
      --accent: #af562d;
      --teal: #19675d;
      --teal-soft: #dbece7;
      --success: #2b7b47;
      --success-soft: #ddeedf;
      --danger: #a4342a;
      --danger-soft: #f6dfdb;
      --warn: #9b610d;
      --warn-soft: #f4e5cb;
      --shadow: 0 18px 44px rgba(47, 29, 11, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(175, 86, 45, 0.12), transparent 24%),
        radial-gradient(circle at top right, rgba(25, 103, 93, 0.1), transparent 28%),
        linear-gradient(180deg, #faf5ee 0%, var(--bg) 100%);
    }
    .page {
      max-width: 1220px;
      margin: 0 auto;
      padding: 26px 18px 40px;
    }
    .hero, .panel {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 24px;
      box-shadow: var(--shadow);
    }
    .hero {
      padding: 24px;
      margin-bottom: 20px;
    }
    .eyebrow {
      display: inline-flex;
      padding: 6px 12px;
      border-radius: 999px;
      background: #f6ddd2;
      color: #8d3514;
      font-size: 0.83rem;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }
    h1 {
      margin: 14px 0 10px;
      font-size: clamp(2rem, 4vw, 3.4rem);
      line-height: 1.05;
    }
    p {
      color: var(--muted);
      line-height: 1.6;
    }
    .controls {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 16px;
    }
    input, button {
      font: inherit;
      border-radius: 14px;
      padding: 12px 14px;
    }
    input {
      min-width: 260px;
      border: 1px solid #d4c7b6;
      background: #fff;
    }
    button {
      border: 0;
      cursor: pointer;
    }
    .primary {
      background: var(--accent);
      color: white;
    }
    .secondary {
      background: #efe5d8;
      color: var(--ink);
    }
    .layout {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }
    .panel {
      padding: 20px;
    }
    .panel h2 {
      margin: 0 0 12px;
      font-size: 1.24rem;
    }
    .stack {
      display: grid;
      gap: 12px;
    }
    .step {
      border: 1px solid var(--line);
      background: var(--surface-strong);
      border-radius: 18px;
      padding: 14px;
    }
    .step h3 {
      margin: 0 0 8px;
      font-size: 1rem;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 0.8rem;
      margin-bottom: 8px;
    }
    .badge.pass, .badge.meets_threshold { background: var(--success-soft); color: var(--success); }
    .badge.fail, .badge.below_threshold { background: var(--danger-soft); color: var(--danger); }
    .badge.completed, .badge.advance { background: var(--success-soft); color: var(--success); }
    .badge.exited_midway, .badge.continue_current, .badge.remediation, .badge.complete_path { background: var(--warn-soft); color: var(--warn); }
    .metric {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 8px 0;
      border-top: 1px dashed #e8ddce;
      font-size: 0.94rem;
    }
    .metric:first-of-type { border-top: 0; padding-top: 0; }
    pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      background: #1d2229;
      color: #edf1f4;
      border-radius: 18px;
      padding: 14px;
      font-size: 0.86rem;
      line-height: 1.58;
    }
    .status {
      margin-top: 10px;
      min-height: 22px;
      font-size: 0.95rem;
    }
    .status.error { color: var(--danger); }
    .status.ok { color: var(--success); }
    .empty { color: var(--muted); font-style: italic; }
    @media (max-width: 980px) {
      .layout { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <span class="eyebrow">Engine Explainer</span>
      <h1>Step-by-step scoring and recommendation logic</h1>
      <p>This window explains how the Merge System processed the final session-end payload for a student. Use it alongside the main demo window to show validation, scoring, threshold comparison, and next-chapter recommendation.</p>
      <div class="controls">
        <input id="studentId" placeholder="Enter student ID" />
        <button class="primary" id="loadExplanationBtn" type="button">Load Explanation</button>
        <button class="secondary" id="openMainBtn" type="button">Open Main Demo</button>
      </div>
      <div class="status" id="status"></div>
    </section>

    <section class="layout">
      <div class="stack">
        <section class="panel">
          <h2>Validation</h2>
          <div id="validationList" class="empty">Load a student to see validation checks.</div>
        </section>
        <section class="panel">
          <h2>Scoring Engine</h2>
          <div id="scoringList" class="empty">Scoring steps will appear here.</div>
        </section>
      </div>
      <div class="stack">
        <section class="panel">
          <h2>Recommendation Decision Tree</h2>
          <div id="decisionList" class="empty">Decision steps will appear here.</div>
        </section>
        <section class="panel">
          <h2>Derived Recommendation Parameters</h2>
          <div id="parameterList" class="empty">Recommendation parameters will appear here.</div>
        </section>
        <section class="panel">
          <h2>Final Payload</h2>
          <pre id="payloadOutput">No payload loaded yet.</pre>
        </section>
      </div>
    </section>
  </div>

  <script>
    const statusEl = document.getElementById("status");
    const studentIdEl = document.getElementById("studentId");
    const validationListEl = document.getElementById("validationList");
    const scoringListEl = document.getElementById("scoringList");
    const decisionListEl = document.getElementById("decisionList");
    const parameterListEl = document.getElementById("parameterList");
    const payloadOutputEl = document.getElementById("payloadOutput");

    function setStatus(message, kind = "") {
      statusEl.textContent = message;
      statusEl.className = `status ${kind}`.trim();
    }

    function renderValidation(checks) {
      validationListEl.innerHTML = checks.map((check) => `
        <article class="step">
          <span class="badge ${check.passed ? "pass" : "fail"}">${check.passed ? "passed" : "failed"}</span>
          <h3>${check.name.replaceAll("_", " ")}</h3>
          <p>${check.detail}</p>
        </article>
      `).join("");
    }

    function renderScoring(data) {
      scoringListEl.innerHTML = `
        <article class="step">
          <h3>Profile: ${data.score_profile}</h3>
          <div class="metric"><strong>Threshold</strong><span>${data.threshold}</span></div>
          <div class="metric"><strong>Final score</strong><span>${data.final_score ?? "N/A"}</span></div>
          <p>${data.normalized_score_summary}</p>
        </article>
        ${data.score_steps.map((step) => `
          <article class="step">
            <span class="badge ${step.included ? "pass" : "fail"}">${step.included ? "included" : "excluded"}</span>
            <h3>${step.name.replaceAll("_", " ")}</h3>
            <div class="metric"><strong>Formula</strong><span>${step.formula}</span></div>
            <div class="metric"><strong>Value</strong><span>${step.value ?? "N/A"}</span></div>
            <div class="metric"><strong>Normalized weight</strong><span>${step.weight ?? "N/A"}</span></div>
            <div class="metric"><strong>Contribution</strong><span>${step.contribution ?? "N/A"}</span></div>
          </article>
        `).join("")}
      `;
    }

    function renderParameters(parameters) {
      parameterListEl.innerHTML = Object.entries(parameters).map(([key, value]) => `
        <article class="step">
          <h3>${key.replaceAll("_", " ")}</h3>
          <div class="metric"><strong>Value</strong><span>${value ?? "N/A"}</span></div>
        </article>
      `).join("");
    }

    function renderDecision(data) {
      decisionListEl.innerHTML = `
        ${data.decision_steps.map((step) => `
          <article class="step">
            <span class="badge ${step.outcome}">${step.outcome.replaceAll("_", " ")}</span>
            <h3>${step.step.replaceAll("_", " ")}</h3>
            <p>${step.detail}</p>
          </article>
        `).join("")}
        <article class="step">
          <h3>Final recommendation</h3>
          <div class="metric"><strong>Decision type</strong><span>${data.decision_type}</span></div>
          <div class="metric"><strong>Next chapter</strong><span>${data.next_chapter_name || "No next chapter configured"}</span></div>
          <div class="metric"><strong>Prerequisite recommendations</strong><span>${data.prerequisite_recommendations.join(", ") || "None"}</span></div>
          <div class="metric"><strong>Weak subtopics</strong><span>${data.weak_subtopics.join(", ") || "None"}</span></div>
          <p>${data.rationale}</p>
        </article>
      `;
    }

    async function loadExplanation(studentId) {
      if (!studentId) {
        setStatus("Enter a student ID to load the explanation.", "error");
        return;
      }
      setStatus("Loading engine explanation...");
      const response = await fetch(`/demo/engine-explanation/${encodeURIComponent(studentId)}`);
      const data = await response.json();

      if (!response.ok) {
        validationListEl.innerHTML = '<div class="empty">No validation data available.</div>';
        scoringListEl.innerHTML = '<div class="empty">No scoring data available.</div>';
        decisionListEl.innerHTML = '<div class="empty">No decision data available.</div>';
        parameterListEl.innerHTML = '<div class="empty">No parameter data available.</div>';
        payloadOutputEl.textContent = JSON.stringify(data, null, 2);
        setStatus(data.detail || "Unable to load the engine explanation.", "error");
        return;
      }

      renderValidation(data.validation_checks);
      renderScoring(data);
      renderDecision(data);
      renderParameters(data.recommendation_parameters);
      payloadOutputEl.textContent = JSON.stringify(data.payload, null, 2);
      setStatus("Engine explanation loaded.", "ok");
    }

    document.getElementById("loadExplanationBtn").addEventListener("click", () => loadExplanation(studentIdEl.value.trim()));
    document.getElementById("openMainBtn").addEventListener("click", () => window.open("/", "_blank"));

    const params = new URLSearchParams(window.location.search);
    const studentId = params.get("student_id");
    if (studentId) {
      studentIdEl.value = studentId;
      loadExplanation(studentId);
    }
  </script>
</body>
</html>
"""
