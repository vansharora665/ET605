from __future__ import annotations


def render_demo_page() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ET605 Adaptive Learning Platform Demo</title>
  <style>
    :root {
      --bg: #f7f0e7;
      --surface: rgba(255, 250, 244, 0.92);
      --surface-strong: #fffdf9;
      --ink: #1f232b;
      --muted: #6f7480;
      --line: #ddd2c2;
      --accent: #b5542f;
      --accent-dark: #873716;
      --accent-soft: #f5ddd2;
      --teal: #196c63;
      --teal-soft: #d7ebe8;
      --success: #2c7c49;
      --success-soft: #dceddf;
      --warn: #a06010;
      --warn-soft: #f4e5cb;
      --danger: #a4342a;
      --danger-soft: #f7dfdb;
      --shadow: 0 18px 46px rgba(49, 29, 9, 0.09);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(181, 84, 47, 0.12), transparent 24%),
        radial-gradient(circle at top right, rgba(25, 108, 99, 0.12), transparent 26%),
        linear-gradient(180deg, #faf4ec 0%, var(--bg) 100%);
    }

    .page {
      max-width: 1340px;
      margin: 0 auto;
      padding: 28px 18px 50px;
    }

    .hero {
      padding: 28px;
      border-radius: 28px;
      border: 1px solid rgba(221, 210, 194, 0.9);
      background: var(--surface);
      box-shadow: var(--shadow);
      backdrop-filter: blur(8px);
    }

    .eyebrow {
      display: inline-flex;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent-dark);
      padding: 6px 12px;
      font-size: 0.83rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    h1 {
      margin: 14px 0 10px;
      font-size: clamp(2.1rem, 5vw, 4rem);
      line-height: 1.03;
    }

    .lead {
      margin: 0;
      max-width: 920px;
      color: var(--muted);
      line-height: 1.65;
      font-size: 1.05rem;
    }

    .hero-actions {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 22px;
    }

    button,
    .link-btn,
    select,
    input {
      font: inherit;
    }

    button,
    .link-btn {
      border: 0;
      border-radius: 14px;
      padding: 12px 16px;
      cursor: pointer;
      transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }

    button:hover,
    .link-btn:hover {
      transform: translateY(-1px);
    }

    .primary {
      background: var(--accent);
      color: #fff;
      box-shadow: 0 10px 24px rgba(181, 84, 47, 0.24);
    }

    .secondary {
      background: #efe5d9;
      color: var(--ink);
    }

    .layout {
      display: grid;
      grid-template-columns: 300px 1.25fr 1fr;
      gap: 20px;
      margin-top: 22px;
      align-items: start;
    }

    .panel {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 24px;
      box-shadow: var(--shadow);
      padding: 22px;
    }

    .panel h2 {
      margin: 0 0 8px;
      font-size: 1.32rem;
    }

    .panel p,
    .panel li {
      color: var(--muted);
      line-height: 1.58;
    }

    .left-rail {
      position: sticky;
      top: 20px;
    }

    .student-bar {
      display: grid;
      gap: 12px;
      margin-top: 16px;
    }

    label {
      display: block;
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 0.92rem;
    }

    input,
    select {
      width: 100%;
      padding: 12px 13px;
      border-radius: 14px;
      border: 1px solid #d0c4b2;
      background: #fff;
      color: var(--ink);
    }

    .course-list {
      display: grid;
      gap: 10px;
      margin-top: 18px;
    }

    .stack {
      display: grid;
      gap: 14px;
      margin-top: 16px;
    }

    .subpanel {
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--surface-strong);
      padding: 14px;
    }

    .subpanel h3 {
      margin: 0 0 8px;
      font-size: 1rem;
    }

    .subpanel p {
      margin: 0;
      font-size: 0.92rem;
    }

    .range-wrap {
      display: grid;
      gap: 4px;
    }

    .range-meta {
      display: flex;
      justify-content: space-between;
      font-size: 0.84rem;
      color: var(--muted);
    }

    input[type="range"] {
      padding: 0;
    }

    .check-line {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 0.92rem;
      color: var(--muted);
    }

    .check-line input {
      width: auto;
    }

    .course-card {
      border-radius: 18px;
      border: 1px solid var(--line);
      background: var(--surface-strong);
      padding: 14px;
      cursor: pointer;
      transition: border-color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
    }

    .course-card:hover {
      transform: translateY(-1px);
      border-color: #c9b39c;
    }

    .course-card.active {
      border-color: var(--accent);
      box-shadow: 0 8px 24px rgba(181, 84, 47, 0.12);
    }

    .course-card h3 {
      margin: 0 0 4px;
      font-size: 1rem;
    }

    .micro {
      font-size: 0.88rem;
      color: var(--muted);
      margin: 0;
    }

    .chapter-head {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: start;
      margin-bottom: 14px;
    }

    .chip {
      display: inline-flex;
      align-items: center;
      padding: 7px 11px;
      border-radius: 999px;
      font-size: 0.84rem;
      background: #f0e7da;
      color: #5b4f40;
    }

    .goal-box {
      border: 1px dashed #d4c6b5;
      border-radius: 18px;
      padding: 14px;
      background: #fffdf9;
      margin-bottom: 16px;
    }

    .question-list {
      display: grid;
      gap: 16px;
    }

    .question-card {
      border: 1px solid var(--line);
      border-radius: 20px;
      background: var(--surface-strong);
      padding: 16px;
    }

    .question-title {
      margin: 0 0 12px;
      font-size: 1.05rem;
      line-height: 1.45;
    }

    .option-list {
      display: grid;
      gap: 9px;
    }

    .option {
      display: flex;
      gap: 10px;
      padding: 10px 12px;
      border-radius: 14px;
      border: 1px solid #dfd4c6;
      background: #fff;
      cursor: pointer;
    }

    .option input {
      width: auto;
      margin-top: 2px;
    }

    .question-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 14px;
    }

    .hint-box,
    .feedback-box {
      margin-top: 12px;
      border-radius: 16px;
      padding: 12px 14px;
      font-size: 0.94rem;
      line-height: 1.5;
    }

    .hint-box {
      background: var(--teal-soft);
      color: var(--teal);
    }

    .feedback-box.correct {
      background: var(--success-soft);
      color: var(--success);
    }

    .feedback-box.wrong {
      background: var(--danger-soft);
      color: var(--danger);
    }

    .footer-bar {
      margin-top: 18px;
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }

    .status {
      min-height: 22px;
      margin-top: 14px;
      font-size: 0.95rem;
    }

    .status.ok { color: var(--success); }
    .status.error { color: var(--danger); }

    .summary-stack {
      display: grid;
      gap: 16px;
    }

    .summary-card {
      border: 1px solid var(--line);
      border-radius: 20px;
      background: var(--surface-strong);
      padding: 18px;
    }

    .summary-card h3 {
      margin: 0 0 12px;
      font-size: 1.06rem;
    }

    .metric-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 12px;
    }

    .metric-box {
      border-radius: 16px;
      border: 1px solid #eadfce;
      background: #fff;
      padding: 12px;
    }

    .metric-box strong {
      display: block;
      margin-bottom: 4px;
      font-size: 0.88rem;
    }

    .metric-box span {
      font-size: 1.1rem;
      font-weight: 700;
    }

    .band-pill {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 7px 12px;
      font-size: 0.84rem;
      font-weight: 700;
      margin-bottom: 12px;
      text-transform: capitalize;
    }

    .band-pill.excellent {
      background: var(--success-soft);
      color: var(--success);
    }

    .band-pill.on_track {
      background: var(--teal-soft);
      color: var(--teal);
    }

    .band-pill.needs_support,
    .band-pill.intensive_support {
      background: var(--danger-soft);
      color: var(--danger);
    }

    .band-pill.insufficient_data {
      background: var(--warn-soft);
      color: var(--warn);
    }

    .pill-list {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 10px;
    }

    .tag {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 7px 11px;
      font-size: 0.82rem;
      background: #f2eadf;
      color: #5d5246;
    }

    .guide-list {
      display: grid;
      gap: 10px;
      margin-top: 10px;
    }

    .guide-item {
      border-left: 4px solid var(--accent);
      padding: 10px 12px;
      background: #fff8f1;
      border-radius: 14px;
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.5;
    }

    .explain-box {
      border-radius: 16px;
      border: 1px dashed #d7c6b2;
      background: #fff8f0;
      padding: 12px 14px;
      margin-top: 12px;
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.55;
    }

    .summary-row {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 8px 0;
      border-top: 1px dashed #e7dccd;
      font-size: 0.94rem;
    }

    .summary-row:first-of-type {
      border-top: 0;
      padding-top: 0;
    }

    .decision-pill {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 7px 12px;
      font-size: 0.84rem;
      font-weight: 700;
      text-transform: capitalize;
    }

    .decision-pill.advance { background: var(--success-soft); color: var(--success); }
    .decision-pill.remediation { background: var(--danger-soft); color: var(--danger); }
    .decision-pill.continue_current,
    .decision-pill.start_path,
    .decision-pill.complete_path { background: var(--warn-soft); color: var(--warn); }

    .api-card pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 0.86rem;
      line-height: 1.58;
      background: #1d2229;
      color: #edf1f4;
      border-radius: 18px;
      padding: 16px;
      overflow: auto;
    }

    .note {
      margin-top: 10px;
      font-size: 0.9rem;
      color: var(--muted);
    }

    .empty {
      color: var(--muted);
      font-style: italic;
    }

    @media (max-width: 1180px) {
      .layout {
        grid-template-columns: 1fr;
      }

      .left-rail {
        position: static;
      }
    }

    @media (max-width: 720px) {
      .chapter-head,
      .summary-row {
        flex-direction: column;
      }

      .metric-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <span class="eyebrow">Professor Presentation Demo</span>
      <h1>Student chapter experience + team API call + Merge System recommendation</h1>
      <p class="lead">
        This page demonstrates the full end-to-end adaptive learning flow. A student attempts one of 4 dummy math chapters with 5 questions each, the chapter module creates one final session-end API payload, and the Merge System returns the recommendation that decides whether the learner should advance or revisit prerequisites.
      </p>
      <div class="hero-actions">
        <button class="primary" id="reloadCoursesBtn" type="button">Reload Demo Courses</button>
        <button class="secondary" id="weakDemoBtn" type="button">Weak Student Preset</button>
        <button class="secondary" id="averageDemoBtn" type="button">Average Student Preset</button>
        <button class="secondary" id="strongDemoBtn" type="button">Strong Student Preset</button>
        <button class="secondary" id="openExplainerBtn" type="button">Open Engine Explainer</button>
        <a class="link-btn secondary" href="/docs" target="_blank" rel="noreferrer">Swagger Docs</a>
      </div>
    </section>

    <section class="layout">
      <aside class="panel left-rail">
        <h2>Demo Setup</h2>
        <p>Pick a chapter from the dummy catalog, answer as a student, and then end the chapter. The right side will show the exact API payload the team module sends to the Merge System and the final recommendation our system gives back.</p>

        <div class="student-bar">
          <div>
            <label for="studentId">Student ID</label>
            <input id="studentId" value="student_live_demo" />
          </div>
          <div>
            <label for="courseSelect">Choose Chapter</label>
            <select id="courseSelect"></select>
          </div>
        </div>

        <div class="stack">
          <div class="subpanel">
            <h3>Learner Signals</h3>
            <div class="student-bar">
              <div class="range-wrap">
                <label for="confidenceLevel">Confidence Level</label>
                <input id="confidenceLevel" type="range" min="1" max="5" value="3" />
                <div class="range-meta"><span>Low</span><span id="confidenceLabel">3 / 5</span><span>High</span></div>
              </div>
              <div class="range-wrap">
                <label for="focusLevel">Focus Level</label>
                <input id="focusLevel" type="range" min="1" max="5" value="3" />
                <div class="range-meta"><span>Low</span><span id="focusLabel">3 / 5</span><span>High</span></div>
              </div>
              <div>
                <label for="studyMode">Study Mode</label>
                <select id="studyMode">
                  <option value="guided">Guided</option>
                  <option value="independent">Independent</option>
                  <option value="revision">Revision</option>
                </select>
              </div>
              <label class="check-line" for="endedEarly">
                <input id="endedEarly" type="checkbox" />
                Student ended the session early
              </label>
            </div>
          </div>

          <div class="subpanel">
            <h3>Best Demo Guide</h3>
            <div class="guide-list">
              <div class="guide-item"><strong>Weak learner:</strong> use the weak preset, open hints, leave low confidence and low focus, then end the chapter to show remediation.</div>
              <div class="guide-item"><strong>Average learner:</strong> use the average preset to show a learner who is improving but may still stay on the same chapter or remain near threshold.</div>
              <div class="guide-item"><strong>Strong learner:</strong> use the strong preset to show clean advancement to the next configured chapter.</div>
              <div class="guide-item"><strong>Session resilience:</strong> if the tab closes or the network drops, the demo now queues and retries an <code>exited_midway</code> payload automatically.</div>
            </div>
          </div>
        </div>

        <div class="course-list" id="courseList">
          <div class="empty">Loading chapters...</div>
        </div>
      </aside>

      <main class="panel">
        <div class="chapter-head">
          <div>
            <h2 id="chapterTitle">Choose a chapter</h2>
            <p id="chapterDescription">The student-facing chapter experience will appear here.</p>
          </div>
          <span class="chip" id="chapterMeta">Waiting for chapter data</span>
        </div>

        <div class="goal-box">
          <strong>Learning Goal</strong>
          <p id="learningGoal" class="micro">Load a chapter to begin.</p>
        </div>

        <div class="question-list" id="questionList">
          <div class="empty">Load a course to start answering questions.</div>
        </div>

        <div class="footer-bar">
          <button class="primary" id="endChapterBtn" type="button">End Chapter And Send Final Payload</button>
          <button class="secondary" id="resetChapterBtn" type="button">Reset This Chapter</button>
          <span class="chip" id="sessionTimer">Session time: 0s</span>
        </div>
        <div class="status" id="pageStatus"></div>
      </main>

      <section class="summary-stack">
        <div class="panel summary-card">
          <h3>Student Outcome</h3>
          <div id="studentOutcome" class="empty">Finish a chapter to see the learner outcome.</div>
        </div>

        <div class="panel summary-card">
          <h3>Merge Recommendation</h3>
          <div id="recommendationOutcome" class="empty">The Merge System decision will appear here.</div>
          <div class="footer-bar">
            <button class="secondary" id="openExplainerInlineBtn" type="button">Explain This Recommendation In New Window</button>
          </div>
        </div>

        <div class="panel summary-card">
          <h3>Why This Demo Works</h3>
          <div id="guideOutcome">
            <div class="guide-item"><strong>Student side:</strong> answer 5 chapter questions, open hints, retry by changing answers, or leave early.</div>
            <div class="guide-item"><strong>Team side:</strong> the module sends one final session-end payload only, using <code>/demo/session/complete</code> or <code>/demo/session/exit</code>.</div>
            <div class="guide-item"><strong>Merge side:</strong> scoring, prerequisite logic, and next-chapter prediction happen after submission.</div>
          </div>
        </div>

        <div class="panel summary-card api-card">
          <h3>Team Module API Call</h3>
          <p class="note">This is the final session-end payload the chapter team would send to <code>/merge/interactions</code>.</p>
          <pre id="payloadOutput">No payload sent yet.</pre>
        </div>
      </section>
    </section>
  </div>

  <script>
    const state = {
      courses: [],
      activeCourseId: null,
      activeCourse: null,
      questionState: {},
      sessionId: null,
      sessionStartedAt: null,
      timerHandle: null,
      lastResult: null,
      sessionClosed: false,
      exitDeliveryInFlight: false
    };
    const PENDING_EXIT_QUEUE_KEY = "et605_pending_exit_queue";

    const courseListEl = document.getElementById("courseList");
    const courseSelectEl = document.getElementById("courseSelect");
    const questionListEl = document.getElementById("questionList");
    const studentIdEl = document.getElementById("studentId");
    const confidenceLevelEl = document.getElementById("confidenceLevel");
    const focusLevelEl = document.getElementById("focusLevel");
    const confidenceLabelEl = document.getElementById("confidenceLabel");
    const focusLabelEl = document.getElementById("focusLabel");
    const studyModeEl = document.getElementById("studyMode");
    const endedEarlyEl = document.getElementById("endedEarly");
    const pageStatusEl = document.getElementById("pageStatus");
    const payloadOutputEl = document.getElementById("payloadOutput");
    const recommendationOutcomeEl = document.getElementById("recommendationOutcome");
    const studentOutcomeEl = document.getElementById("studentOutcome");
    const sessionTimerEl = document.getElementById("sessionTimer");

    function setStatus(message, kind = "") {
      pageStatusEl.textContent = message;
      pageStatusEl.className = `status ${kind}`.trim();
    }

    function formatList(items) {
      return items && items.length ? items.join(", ") : "None";
    }

    function buildSessionId(studentId, chapterId) {
      const safeStudent = (studentId || "student_live_demo")
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "_")
        .replace(/^_+|_+$/g, "") || "student_live_demo";
      const suffix = (self.crypto && self.crypto.randomUUID ? self.crypto.randomUUID() : String(Date.now()))
        .replaceAll("-", "")
        .slice(0, 8);
      return `play_${safeStudent}_${chapterId}_${suffix}`;
    }

    function readPendingExitQueue() {
      try {
        const raw = localStorage.getItem(PENDING_EXIT_QUEUE_KEY);
        if (!raw) return [];
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : [];
      } catch {
        return [];
      }
    }

    function writePendingExitQueue(queue) {
      if (!queue.length) {
        localStorage.removeItem(PENDING_EXIT_QUEUE_KEY);
        return;
      }
      localStorage.setItem(PENDING_EXIT_QUEUE_KEY, JSON.stringify(queue.slice(-10)));
    }

    function upsertPendingExitPayload(payload) {
      const queue = readPendingExitQueue().filter((item) => item.session_id !== payload.session_id);
      queue.push(payload);
      writePendingExitQueue(queue);
    }

    function removePendingExitPayload(sessionId) {
      const queue = readPendingExitQueue().filter((item) => item.session_id !== sessionId);
      writePendingExitQueue(queue);
    }

    function initializeDraftSession() {
      if (!state.activeCourse) return;
      state.sessionId = buildSessionId(studentIdEl.value, state.activeCourse.chapter_id);
      state.sessionStartedAt = null;
      state.sessionClosed = false;
      state.exitDeliveryInFlight = false;
      updateTimer();
    }

    function syncSignalLabels() {
      confidenceLabelEl.textContent = `${confidenceLevelEl.value} / 5`;
      focusLabelEl.textContent = `${focusLevelEl.value} / 5`;
    }

    function derivedTimeSpentSeconds() {
      if (!state.activeCourse || !state.sessionStartedAt) return 0;
      return Math.max(1, Math.round((Date.now() - state.sessionStartedAt) / 1000));
    }

    function updateTimer() {
      const elapsed = derivedTimeSpentSeconds();
      sessionTimerEl.textContent = state.sessionStartedAt
        ? `Session time: ${elapsed}s`
        : "Session time: 0s (starts on first action)";
    }

    function startTimer() {
      if (state.timerHandle) clearInterval(state.timerHandle);
      state.timerHandle = setInterval(updateTimer, 1000);
      updateTimer();
    }

    function stopTimer() {
      if (state.timerHandle) clearInterval(state.timerHandle);
      state.timerHandle = null;
    }

    function ensureSessionStarted() {
      if (!state.sessionStartedAt) {
        state.sessionStartedAt = Date.now();
      }
      updateTimer();
    }

    function hasOpenSession() {
      return Boolean(state.activeCourse && state.sessionId && !state.sessionClosed);
    }

    async function flushPendingExitQueue() {
      if (!navigator.onLine) return;
      const queue = readPendingExitQueue();
      for (const payload of queue) {
        try {
          const response = await fetch("/demo/session/exit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
            keepalive: true
          });
          if (response.ok) {
            removePendingExitPayload(payload.session_id);
          }
        } catch {
          return;
        }
      }
    }

    function renderCourseCards() {
      if (!state.courses.length) {
        courseListEl.innerHTML = '<div class="empty">No chapters available.</div>';
        return;
      }

      courseListEl.innerHTML = state.courses.map((course) => `
        <article class="course-card ${course.chapter_id === state.activeCourseId ? "active" : ""}" data-course-id="${course.chapter_id}">
          <h3>${course.chapter_name}</h3>
          <p class="micro">Grade ${course.grade} • Difficulty ${course.difficulty}</p>
          <p class="micro">Prerequisites: ${formatList(course.prerequisites)}</p>
          <p class="micro">Next: ${course.next_chapter_id || "End of path"}</p>
        </article>
      `).join("");

      courseListEl.querySelectorAll("[data-course-id]").forEach((card) => {
        card.addEventListener("click", () => {
          selectCourse(card.dataset.courseId);
        });
      });
    }

    function renderCourseSelect() {
      courseSelectEl.innerHTML = state.courses.map((course) => `
        <option value="${course.chapter_id}">${course.chapter_name}</option>
      `).join("");
      courseSelectEl.value = state.activeCourseId || state.courses[0]?.chapter_id || "";
    }

    function createQuestionState(course) {
      const result = {};
      course.questions.forEach((question) => {
        result[question.question_id] = {
          selectedOptionIndex: null,
          attempts: 0,
          hintOpened: false,
          lastCorrect: null
        };
      });
      return result;
    }

    function renderChapter() {
      const course = state.activeCourse;
      if (!course) {
        questionListEl.innerHTML = '<div class="empty">Load a chapter to start.</div>';
        return;
      }

      document.getElementById("chapterTitle").textContent = `${course.chapter_name}`;
      document.getElementById("chapterDescription").textContent = course.description;
      document.getElementById("learningGoal").textContent = course.learning_goal;
      document.getElementById("chapterMeta").textContent = `Grade ${course.grade} • ${course.questions.length} questions • Expected ${course.expected_completion_time}s`;

      questionListEl.innerHTML = course.questions.map((question, questionIndex) => {
        const local = state.questionState[question.question_id];
        const hintHtml = local.hintOpened
          ? `<div class="hint-box"><strong>Hint:</strong> ${question.hint}</div>`
          : "";
        const feedbackHtml = local.lastCorrect === null
          ? ""
          : local.lastCorrect
            ? `<div class="feedback-box correct">Correct. This answer will count as correct in the final session payload.</div>`
            : `<div class="feedback-box wrong">Currently incorrect. The student can retry before the module sends the final session-end payload.</div>`;

        return `
          <article class="question-card">
            <p class="question-title"><strong>Q${questionIndex + 1}.</strong> ${question.prompt}</p>
            <div class="option-list">
              ${question.options.map((option) => `
                <label class="option">
                  <input type="radio" name="${question.question_id}" value="${option.index}" ${local.selectedOptionIndex === option.index ? "checked" : ""} />
                  <span>${option.text}</span>
                </label>
              `).join("")}
            </div>
            <div class="question-actions">
              <button class="secondary" type="button" data-hint-question="${question.question_id}">${local.hintOpened ? "Hint Opened" : "Open Hint"}</button>
              <span class="chip">Attempts: ${local.attempts}</span>
              <span class="chip">Selecting an option counts as an attempt</span>
            </div>
            ${hintHtml}
            ${feedbackHtml}
          </article>
        `;
      }).join("");

      questionListEl.querySelectorAll("[data-hint-question]").forEach((button) => {
        button.addEventListener("click", () => openHint(button.dataset.hintQuestion));
      });
      questionListEl.querySelectorAll("input[type=radio]").forEach((input) => {
        input.addEventListener("change", () => {
          selectAnswer(input.name, Number(input.value));
        });
      });
    }

    function selectAnswer(questionId, optionIndex) {
      if (state.sessionClosed) return;
      const courseQuestion = state.activeCourse.questions.find((question) => question.question_id === questionId);
      const local = state.questionState[questionId];
      ensureSessionStarted();
      local.selectedOptionIndex = optionIndex;
      local.attempts += 1;
      local.lastCorrect = local.selectedOptionIndex === courseQuestion.correct_option_index;
      renderChapter();
      updateTimer();
      setStatus(
        local.lastCorrect
          ? "Nice. That answer is correct and has been counted immediately."
          : "Answer recorded. The student can change the option to retry before ending the chapter.",
        local.lastCorrect ? "ok" : ""
      );
    }

    function openHint(questionId) {
      if (state.sessionClosed) return;
      ensureSessionStarted();
      state.questionState[questionId].hintOpened = true;
      renderChapter();
      updateTimer();
      setStatus("Hint opened. The module will count this in the final session payload.");
    }

    async function loadCourses() {
      setStatus("Loading demo chapters...");
      const response = await fetch("/demo/courses");
      const data = await response.json();
      state.courses = data;
      state.activeCourseId = data[0]?.chapter_id || null;
      renderCourseCards();
      renderCourseSelect();
      if (state.activeCourseId) {
        await loadCourseDetail(state.activeCourseId);
      }
      setStatus("Chapters ready. Choose a chapter and start solving.", "ok");
    }

    async function loadCourseDetail(chapterId) {
      const response = await fetch(`/demo/courses/${encodeURIComponent(chapterId)}`);
      const data = await response.json();
      state.activeCourseId = chapterId;
      state.activeCourse = data;
      state.questionState = createQuestionState(data);
      state.lastResult = null;
      initializeDraftSession();
      renderCourseCards();
      renderCourseSelect();
      renderChapter();
      studentOutcomeEl.innerHTML = '<div class="empty">Solve the chapter questions and then end the chapter session.</div>';
      recommendationOutcomeEl.innerHTML = '<div class="empty">The Merge System recommendation will appear after submission.</div>';
      payloadOutputEl.textContent = "No payload sent yet.";
      startTimer();
    }

    async function selectCourse(chapterId) {
      courseSelectEl.value = chapterId;
      await loadCourseDetail(chapterId);
    }

    function useWeakPreset() {
      if (!state.activeCourse) return;
      const defaultChapter = "grade8_linear_equations";
      selectCourse(defaultChapter).then(() => {
        confidenceLevelEl.value = 1;
        focusLevelEl.value = 2;
        studyModeEl.value = "guided";
        endedEarlyEl.checked = true;
        syncSignalLabels();
        ensureSessionStarted();
        const ids = state.activeCourse.questions.map((question) => question.question_id);
        state.questionState[ids[0]].selectedOptionIndex = 0;
        state.questionState[ids[0]].attempts = 1;
        state.questionState[ids[0]].hintOpened = true;
        state.questionState[ids[0]].lastCorrect = false;

        state.questionState[ids[1]].selectedOptionIndex = 0;
        state.questionState[ids[1]].attempts = 2;
        state.questionState[ids[1]].hintOpened = true;
        state.questionState[ids[1]].lastCorrect = false;

        state.questionState[ids[2]].selectedOptionIndex = 1;
        state.questionState[ids[2]].attempts = 2;
        state.questionState[ids[2]].hintOpened = true;
        state.questionState[ids[2]].lastCorrect = false;
        renderChapter();
        updateTimer();
        setStatus("Weak student preset loaded.");
      });
    }

    function useAveragePreset() {
      if (!state.activeCourse) return;
      const defaultChapter = "grade8_linear_equations";
      selectCourse(defaultChapter).then(() => {
        confidenceLevelEl.value = 3;
        focusLevelEl.value = 3;
        studyModeEl.value = "revision";
        endedEarlyEl.checked = false;
        syncSignalLabels();
        ensureSessionStarted();
        const ids = state.activeCourse.questions.map((question) => question.question_id);
        state.questionState[ids[0]].selectedOptionIndex = state.activeCourse.questions[0].correct_option_index;
        state.questionState[ids[0]].attempts = 1;
        state.questionState[ids[0]].hintOpened = false;
        state.questionState[ids[0]].lastCorrect = true;

        state.questionState[ids[1]].selectedOptionIndex = 0;
        state.questionState[ids[1]].attempts = 2;
        state.questionState[ids[1]].hintOpened = true;
        state.questionState[ids[1]].lastCorrect = false;

        state.questionState[ids[2]].selectedOptionIndex = state.activeCourse.questions[2].correct_option_index;
        state.questionState[ids[2]].attempts = 1;
        state.questionState[ids[2]].hintOpened = false;
        state.questionState[ids[2]].lastCorrect = true;
        renderChapter();
        updateTimer();
        setStatus("Average student preset loaded.");
      });
    }

    function useStrongPreset() {
      if (!state.activeCourse) return;
      const defaultChapter = "grade7_algebraic_expressions";
      selectCourse(defaultChapter).then(() => {
        confidenceLevelEl.value = 5;
        focusLevelEl.value = 5;
        studyModeEl.value = "independent";
        endedEarlyEl.checked = false;
        syncSignalLabels();
        ensureSessionStarted();
        state.activeCourse.questions.forEach((question) => {
          const local = state.questionState[question.question_id];
          local.selectedOptionIndex = question.correct_option_index;
          local.attempts = 1;
          local.hintOpened = false;
          local.lastCorrect = true;
        });
        renderChapter();
        updateTimer();
        setStatus("Strong student preset loaded.", "ok");
      });
    }

    function buildStudentSessionPayload(forceEndedEarly = false) {
      return {
        student_id: studentIdEl.value.trim(),
        session_id: state.sessionId,
        chapter_id: state.activeCourse.chapter_id,
        session_started_at: state.sessionStartedAt ? new Date(state.sessionStartedAt).toISOString() : null,
        time_spent_seconds: derivedTimeSpentSeconds(),
        confidence_level: Number(confidenceLevelEl.value),
        focus_level: Number(focusLevelEl.value),
        study_mode: studyModeEl.value,
        ended_early: forceEndedEarly || endedEarlyEl.checked,
        answers: state.activeCourse.questions.map((question) => {
          const local = state.questionState[question.question_id];
          return {
            question_id: question.question_id,
            selected_option_index: local.selectedOptionIndex,
            attempts: local.attempts,
            hint_opened: local.hintOpened
          };
        })
      };
    }

    function openExplainerWindow() {
      const studentId = studentIdEl.value.trim();
      if (!studentId) {
        setStatus("Enter a student ID first so the explainer knows which learner to load.", "error");
        return;
      }
      window.open(`/engine-explainer?student_id=${encodeURIComponent(studentId)}`, "_blank");
    }

    function renderStudentOutcome(result) {
      const attempted = result.student_results.filter((item) => item.attempts > 0 && item.selected_option_index !== null).length;
      const correct = result.student_results.filter((item) => item.is_correct).length;
      const hints = result.student_results.filter((item) => item.hint_opened).length;
      const retries = result.student_results.reduce((sum, item) => sum + Math.max(item.attempts - 1, 0), 0);

      studentOutcomeEl.innerHTML = `
        <div class="band-pill ${result.performance_band}">${result.performance_band.replaceAll("_", " ")}</div>
        <div class="metric-grid">
          <div class="metric-box"><strong>Performance score</strong><span>${result.performance_score ?? "N/A"}</span></div>
          <div class="metric-box"><strong>Next chapter</strong><span>${result.next_chapter_name || "No next chapter"}</span></div>
        </div>
        <div class="summary-row"><strong>Chapter finished</strong><span>${result.chapter_name}</span></div>
        <div class="summary-row"><strong>Questions attempted</strong><span>${attempted}/${result.student_results.length}</span></div>
        <div class="summary-row"><strong>Correct answers</strong><span>${correct}</span></div>
        <div class="summary-row"><strong>Hints opened</strong><span>${hints}</span></div>
        <div class="summary-row"><strong>Retries</strong><span>${retries}</span></div>
        <div class="summary-row"><strong>Confidence / Focus</strong><span>${result.learner_signals.confidence_level}/5 • ${result.learner_signals.focus_level}/5</span></div>
        <div class="summary-row"><strong>Study mode</strong><span>${result.learner_signals.study_mode}</span></div>
        <div class="explain-box">
          <strong>How the score is normalized</strong><br />
          ${result.normalized_score_explanation.summary}<br /><br />
          <code>${result.normalized_score_explanation.formula}</code><br />
          Weights used in this session sum to <strong>${result.normalized_score_explanation.weights_sum}</strong>.
        </div>
      `;
    }

    async function deliverExitSession({ useBeacon = false, silent = false } = {}) {
      if (!hasOpenSession() || state.exitDeliveryInFlight) {
        return false;
      }

      const sessionPayload = buildStudentSessionPayload(true);
      upsertPendingExitPayload(sessionPayload);
      state.exitDeliveryInFlight = true;
      state.sessionClosed = true;
      stopTimer();

      if (useBeacon && navigator.sendBeacon) {
        const blob = new Blob([JSON.stringify(sessionPayload)], { type: "application/json" });
        navigator.sendBeacon("/demo/session/exit", blob);
        return true;
      }

      try {
        const response = await fetch("/demo/session/exit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(sessionPayload),
          keepalive: true
        });
        if (response.ok) {
          removePendingExitPayload(sessionPayload.session_id);
          if (!silent) {
            setStatus("Exited-midway session delivered successfully.", "ok");
          }
          return true;
        }
      } catch {
        // Keep the payload queued locally for retry after reconnect.
      } finally {
        state.exitDeliveryInFlight = false;
      }

      if (!silent) {
        setStatus("Session exit queued locally and will retry when the connection returns.", "error");
      }
      return false;
    }

    function renderRecommendationOutcome(result) {
      const summary = result.admin_summary;
      recommendationOutcomeEl.innerHTML = `
        <div class="decision-pill ${summary.decision_type}">${summary.decision_type.replaceAll("_", " ")}</div>
        <div class="band-pill ${result.performance_band}">${result.performance_band.replaceAll("_", " ")}</div>
        <div class="summary-row"><strong>Recommended next chapter</strong><span>${summary.next_chapter_name || "No next chapter configured"}</span></div>
        <div class="summary-row"><strong>Needs support</strong><span>${summary.needs_support ? "Yes" : "No"}</span></div>
        <div class="summary-row"><strong>Prerequisite suggestions</strong><span>${formatList(summary.support_recommendations)}</span></div>
        <div class="summary-row"><strong>Weak subtopics</strong><span>${formatList(summary.weak_subtopics)}</span></div>
        <div class="summary-row"><strong>Observed patterns</strong><span>${formatList(result.observed_patterns)}</span></div>
        <div class="summary-row"><strong>Struggle index</strong><span>${result.recommendation_parameters.struggle_index ?? "N/A"}</span></div>
        <div class="summary-row"><strong>Readiness index</strong><span>${result.recommendation_parameters.readiness_index ?? "N/A"}</span></div>
        <div class="summary-row"><strong>Prerequisite pressure</strong><span>${result.recommendation_parameters.prerequisite_pressure ?? "N/A"}</span></div>
        <div class="pill-list">${result.coaching_tips.map((tip) => `<span class="tag">${tip}</span>`).join("")}</div>
        <div class="explain-box">
          <strong>New recommendation parameters</strong><br />
          These are derived from official metrics to make the recommendation engine stronger:
          accuracy, hint dependency, retry pressure, time pressure, completion gap, chapter difficulty,
          weak subtopic ratio, struggle index, readiness index, and prerequisite pressure.
        </div>
        <p class="note">${summary.rationale}</p>
      `;
    }

    async function endChapter() {
      if (!state.activeCourse) {
        setStatus("Choose a chapter first.", "error");
        return;
      }
      if (!studentIdEl.value.trim()) {
        setStatus("Enter a student ID before ending the chapter.", "error");
        return;
      }

      ensureSessionStarted();
      setStatus("Ending the chapter and sending the final session-end payload...");
      const sessionPayload = buildStudentSessionPayload(false);
      const response = await fetch("/demo/session/complete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sessionPayload)
      });
      const data = await response.json();

      if (!response.ok) {
        setStatus(data.detail || "Chapter submission failed.", "error");
        payloadOutputEl.textContent = JSON.stringify(data, null, 2);
        return;
      }

      state.lastResult = data;
      state.sessionClosed = true;
      removePendingExitPayload(sessionPayload.session_id);
      stopTimer();
      renderStudentOutcome(data);
      renderRecommendationOutcome(data);
      payloadOutputEl.textContent = JSON.stringify(data.team_api_submission, null, 2);
      setStatus("Session processed. The module payload and Merge System recommendation are ready for presentation.", "ok");
    }

    function resetCurrentChapter() {
      if (!state.activeCourse) return;
      state.questionState = createQuestionState(state.activeCourse);
      state.lastResult = null;
      initializeDraftSession();
      renderChapter();
      studentOutcomeEl.innerHTML = '<div class="empty">Solve the chapter questions and then end the chapter session.</div>';
      recommendationOutcomeEl.innerHTML = '<div class="empty">The Merge System recommendation will appear after submission.</div>';
      payloadOutputEl.textContent = "No payload sent yet.";
      setStatus("Chapter reset. The student can try again.");
      startTimer();
    }

    document.getElementById("reloadCoursesBtn").addEventListener("click", loadCourses);
    document.getElementById("weakDemoBtn").addEventListener("click", useWeakPreset);
    document.getElementById("averageDemoBtn").addEventListener("click", useAveragePreset);
    document.getElementById("strongDemoBtn").addEventListener("click", useStrongPreset);
    document.getElementById("openExplainerBtn").addEventListener("click", openExplainerWindow);
    document.getElementById("openExplainerInlineBtn").addEventListener("click", openExplainerWindow);
    document.getElementById("endChapterBtn").addEventListener("click", endChapter);
    document.getElementById("resetChapterBtn").addEventListener("click", resetCurrentChapter);
    courseSelectEl.addEventListener("change", (event) => selectCourse(event.target.value));
    confidenceLevelEl.addEventListener("input", syncSignalLabels);
    focusLevelEl.addEventListener("input", syncSignalLabels);
    studentIdEl.addEventListener("change", () => {
      if (state.activeCourse && !state.sessionStartedAt) {
        state.sessionId = buildSessionId(studentIdEl.value, state.activeCourse.chapter_id);
      }
    });
    window.addEventListener("online", flushPendingExitQueue);
    window.addEventListener("offline", () => {
      if (!hasOpenSession()) return;
      upsertPendingExitPayload(buildStudentSessionPayload(true));
      state.sessionClosed = true;
      stopTimer();
      setStatus("Network disconnected. The session was closed as exited midway and queued for retry.", "error");
    });
    window.addEventListener("pagehide", () => {
      if (hasOpenSession()) {
        deliverExitSession({ useBeacon: true, silent: true });
      }
    });

    syncSignalLabels();
    flushPendingExitQueue();
    loadCourses();
  </script>
</body>
</html>
"""
