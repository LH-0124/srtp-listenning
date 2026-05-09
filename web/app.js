(function () {
  const root = document.documentElement;
  const toggle = document.getElementById("themeToggle");
  const label = document.getElementById("themeLabel");
  const icon = toggle ? toggle.querySelector(".theme-icon") : null;
  const storageKey = "capd-demo-theme";

  const state = {
    session: null,
    task: null,
    busy: false,
  };

  const els = {
    sessionForm: document.getElementById("sessionForm"),
    answerForm: document.getElementById("answerForm"),
    userId: document.getElementById("userId"),
    trainingMode: document.getElementById("trainingMode"),
    noiseProfile: document.getElementById("noiseProfile"),
    createSessionBtn: document.getElementById("createSessionBtn"),
    nextTaskBtn: document.getElementById("nextTaskBtn"),
    refreshProgressBtn: document.getElementById("refreshProgressBtn"),
    sessionId: document.getElementById("sessionId"),
    sessionUser: document.getElementById("sessionUser"),
    sessionMode: document.getElementById("sessionMode"),
    taskAudio: document.getElementById("taskAudio"),
    audioHint: document.getElementById("audioHint"),
    taskSpeed: document.getElementById("taskSpeed"),
    taskSnr: document.getElementById("taskSnr"),
    taskNoise: document.getElementById("taskNoise"),
    taskId: document.getElementById("taskId"),
    textHash: document.getElementById("textHash"),
    targetText: document.getElementById("targetText"),
    userInput: document.getElementById("userInput"),
    submitAnswerBtn: document.getElementById("submitAnswerBtn"),
    answerCorrect: document.getElementById("answerCorrect"),
    answerScore: document.getElementById("answerScore"),
    answerDifficulty: document.getElementById("answerDifficulty"),
    answerMessage: document.getElementById("answerMessage"),
    accuracyValue: document.getElementById("accuracyValue"),
    totalAnswers: document.getElementById("totalAnswers"),
    correctCount: document.getElementById("correctCount"),
    progressDifficulty: document.getElementById("progressDifficulty"),
    apiStatus: document.getElementById("apiStatus"),
    apiStatusDot: document.getElementById("apiStatusDot"),
    errorText: document.getElementById("errorText"),
  };

  const endpointIds = {
    sessions: "endpointSession",
    task: "endpointTask",
    answer: "endpointAnswer",
    progress: "endpointProgress",
  };

  function applyTheme(theme) {
    root.dataset.theme = theme;
    const isDark = theme === "dark";
    if (toggle) {
      toggle.setAttribute("aria-pressed", String(isDark));
    }
    if (label) {
      label.textContent = isDark ? "Light mode" : "Dark mode";
    }
    if (icon) {
      icon.textContent = isDark ? "Sun" : "Moon";
    }
  }

  function setBusy(isBusy) {
    state.busy = isBusy;
    els.createSessionBtn.disabled = isBusy;
    els.nextTaskBtn.disabled = isBusy || !state.session;
    els.refreshProgressBtn.disabled = isBusy;
    els.submitAnswerBtn.disabled = isBusy || !state.session || !state.task;
    els.userInput.disabled = isBusy || !state.task;
  }

  function setStatus(message, mode, endpointKey) {
    els.apiStatus.textContent = message;
    els.apiStatusDot.classList.toggle("loading", mode === "loading");
    els.apiStatusDot.classList.toggle("error", mode === "error");
    Object.values(endpointIds).forEach(function (id) {
      const item = document.getElementById(id);
      if (item) {
        item.classList.remove("active");
      }
    });
    if (endpointKey && endpointIds[endpointKey]) {
      document.getElementById(endpointIds[endpointKey]).classList.add("active");
    }
  }

  function clearError() {
    els.errorText.textContent = "";
  }

  function showError(prefix, error) {
    const detail = error && error.message ? error.message : String(error);
    els.errorText.textContent = `${prefix}: ${detail}`;
    setStatus(prefix, "error");
  }

  function formatDifficulty(difficulty) {
    if (!difficulty) {
      return "None";
    }
    return `${Number(difficulty.speed).toFixed(2)}x / ${Number(difficulty.snr).toFixed(0)} dB`;
  }

  function updateSessionView() {
    const session = state.session;
    els.sessionId.textContent = session ? session.session_id : "None";
    els.sessionUser.textContent = session ? session.user_id : els.userId.value.trim() || "demo_user";
    els.sessionMode.textContent = session ? session.training_mode : els.trainingMode.value;
    if (session) {
      els.taskSpeed.textContent = `${Number(session.difficulty.speed).toFixed(2)}x`;
      els.taskSnr.textContent = `${Number(session.difficulty.snr).toFixed(0)} dB`;
      els.taskNoise.textContent = els.noiseProfile.value;
    }
  }

  function updateTaskView() {
    const task = state.task;
    if (!task) {
      els.taskId.textContent = "None";
      els.textHash.textContent = "None";
      els.targetText.textContent = "Hidden until a task is loaded";
      els.audioHint.textContent = "Create a session, then request the next task.";
      els.taskAudio.removeAttribute("src");
      els.taskAudio.load();
      return;
    }

    els.taskId.textContent = task.task_id;
    els.textHash.textContent = task.text_hash;
    els.targetText.textContent = task.target_text;
    els.taskSpeed.textContent = `${Number(task.difficulty.speed).toFixed(2)}x`;
    els.taskSnr.textContent = `${Number(task.difficulty.snr).toFixed(0)} dB`;
    els.taskNoise.textContent = task.difficulty.noise_profile;
    els.taskAudio.src = task.audio_url;
    els.taskAudio.load();
    els.audioHint.textContent = "Audio loaded. Use the player controls to listen.";
    els.userInput.value = "";
  }

  function updateAnswerView(answer) {
    if (!answer) {
      els.answerCorrect.textContent = "None";
      els.answerScore.textContent = "None";
      els.answerDifficulty.textContent = "None";
      els.answerMessage.textContent = "Waiting for answer";
      return;
    }
    els.answerCorrect.textContent = answer.correct ? "Yes" : "No";
    els.answerScore.textContent = Number(answer.score).toFixed(2);
    els.answerDifficulty.textContent = formatDifficulty(answer.new_difficulty);
    els.answerMessage.textContent = answer.message;
  }

  function updateProgressView(progress) {
    els.accuracyValue.textContent = `${Math.round(Number(progress.accuracy) * 100)}%`;
    els.totalAnswers.textContent = progress.total_answers;
    els.correctCount.textContent = progress.correct_count;
    els.progressDifficulty.textContent = formatDifficulty(progress.current_difficulty);
  }

  async function requestJson(url, options) {
    const response = await fetch(url, options);
    let payload = null;
    try {
      payload = await response.json();
    } catch (error) {
      payload = null;
    }
    if (!response.ok) {
      const detail = payload && payload.detail ? payload.detail : response.statusText;
      throw new Error(`${response.status} ${detail}`);
    }
    return payload;
  }

  async function createSession(event) {
    event.preventDefault();
    clearError();
    setBusy(true);
    setStatus("Creating session...", "loading", "sessions");
    try {
      const userId = els.userId.value.trim() || "demo_user";
      const session = await requestJson("/api/v1/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          training_mode: els.trainingMode.value,
          noise_profile: els.noiseProfile.value,
        }),
      });
      state.session = session;
      state.task = null;
      updateSessionView();
      updateTaskView();
      updateAnswerView(null);
      setStatus("Session created. Request the next task.", "ok", "sessions");
      await refreshProgress();
    } catch (error) {
      showError("Session request failed", error);
    } finally {
      setBusy(false);
    }
  }

  async function fetchNextTask() {
    if (!state.session) {
      return;
    }
    clearError();
    setBusy(true);
    setStatus("Requesting next task and audio...", "loading", "task");
    try {
      const params = new URLSearchParams({ session_id: state.session.session_id });
      const task = await requestJson(`/api/v1/tasks/next?${params.toString()}`);
      state.task = task;
      updateTaskView();
      updateAnswerView(null);
      setStatus("Task loaded. Audio is ready when the browser can fetch it.", "ok", "task");
    } catch (error) {
      state.task = null;
      updateTaskView();
      els.audioHint.textContent = "Audio could not be generated. This often means edge-tts or network access failed; try again later or use noise_profile=none.";
      showError("Task request failed", error);
    } finally {
      setBusy(false);
    }
  }

  async function submitAnswer(event) {
    event.preventDefault();
    if (!state.session || !state.task) {
      return;
    }
    clearError();
    setBusy(true);
    setStatus("Submitting answer...", "loading", "answer");
    try {
      const answer = await requestJson("/api/v1/answers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: state.session.session_id,
          task_id: state.task.task_id,
          user_input: els.userInput.value,
        }),
      });
      updateAnswerView(answer);
      setStatus("Answer submitted. Progress refreshed.", "ok", "answer");
      await refreshProgress();
    } catch (error) {
      showError("Answer request failed", error);
    } finally {
      setBusy(false);
    }
  }

  async function refreshProgress() {
    const userId = (state.session && state.session.user_id) || els.userId.value.trim() || "demo_user";
    clearError();
    setStatus("Refreshing progress...", "loading", "progress");
    try {
      const progress = await requestJson(`/api/v1/users/${encodeURIComponent(userId)}/progress`);
      updateProgressView(progress);
      setStatus("Progress is up to date.", "ok", "progress");
    } catch (error) {
      showError("Progress request failed", error);
    }
  }

  const savedTheme = localStorage.getItem(storageKey);
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(savedTheme || (prefersDark ? "dark" : "light"));

  if (toggle) {
    toggle.addEventListener("click", function () {
      const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
      localStorage.setItem(storageKey, nextTheme);
      applyTheme(nextTheme);
    });
  }

  els.sessionForm.addEventListener("submit", createSession);
  els.nextTaskBtn.addEventListener("click", fetchNextTask);
  els.answerForm.addEventListener("submit", submitAnswer);
  els.refreshProgressBtn.addEventListener("click", refreshProgress);
  els.userId.addEventListener("input", updateSessionView);
  els.trainingMode.addEventListener("change", updateSessionView);
  els.taskAudio.addEventListener("error", function () {
    if (state.task) {
      showError("Audio playback failed", new Error("The returned audio_url could not be loaded by the browser."));
    }
  });

  updateSessionView();
  updateTaskView();
  updateAnswerView(null);
  refreshProgress();
})();
