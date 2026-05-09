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
    sessionState: document.getElementById("sessionState"),
    taskAudio: document.getElementById("taskAudio"),
    audioBox: document.getElementById("audioBox"),
    audioHint: document.getElementById("audioHint"),
    taskState: document.getElementById("taskState"),
    taskSpeed: document.getElementById("taskSpeed"),
    taskSnr: document.getElementById("taskSnr"),
    taskNoise: document.getElementById("taskNoise"),
    taskId: document.getElementById("taskId"),
    textHash: document.getElementById("textHash"),
    targetText: document.getElementById("targetText"),
    userInput: document.getElementById("userInput"),
    submitAnswerBtn: document.getElementById("submitAnswerBtn"),
    answerState: document.getElementById("answerState"),
    answerCorrect: document.getElementById("answerCorrect"),
    answerScore: document.getElementById("answerScore"),
    answerDifficulty: document.getElementById("answerDifficulty"),
    answerMessage: document.getElementById("answerMessage"),
    progressState: document.getElementById("progressState"),
    accuracyValue: document.getElementById("accuracyValue"),
    totalAnswers: document.getElementById("totalAnswers"),
    correctCount: document.getElementById("correctCount"),
    progressDifficulty: document.getElementById("progressDifficulty"),
    apiStatus: document.getElementById("apiStatus"),
    apiStatusDot: document.getElementById("apiStatusDot"),
    apiState: document.getElementById("apiState"),
    errorText: document.getElementById("errorText"),
    lastRequest: document.getElementById("lastRequest"),
    lastResponse: document.getElementById("lastResponse"),
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
      icon.textContent = isDark ? "Light" : "Dark";
    }
  }

  function setPill(element, text, mode) {
    if (!element) {
      return;
    }
    element.textContent = text;
    element.classList.remove("empty", "loading", "success", "error");
    element.classList.add(mode || "empty");
  }

  function setAudioState(mode) {
    els.audioBox.classList.remove("is-empty", "is-loading", "is-ready", "is-error");
    els.audioBox.classList.add(`is-${mode}`);
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
    setPill(els.apiState, mode === "loading" ? "Loading" : mode === "error" ? "Error" : "Ready", mode === "error" ? "error" : mode === "loading" ? "loading" : "success");

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

  function writeDebug(kind, data) {
    const target = kind === "request" ? els.lastRequest : els.lastResponse;
    if (!target) {
      return;
    }
    if (typeof data === "string") {
      target.textContent = data;
      return;
    }
    target.textContent = JSON.stringify(data, null, 2);
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
    setPill(els.sessionState, session ? "Active" : "Not started", session ? "success" : "empty");
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
      els.audioHint.textContent = state.session ? "Session is active. Request the next task to generate audio." : "Create a session, then request the next task.";
      els.taskAudio.removeAttribute("src");
      els.taskAudio.load();
      setPill(els.taskState, "Empty", "empty");
      setAudioState("empty");
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
    setPill(els.taskState, "Loaded", "success");
    setPill(els.answerState, "Ready", "success");
    setAudioState("ready");
  }

  function updateAnswerView(answer) {
    if (!answer) {
      els.answerCorrect.textContent = "None";
      els.answerScore.textContent = "None";
      els.answerDifficulty.textContent = "None";
      els.answerMessage.textContent = "Waiting for answer";
      setPill(els.answerState, state.task ? "Ready" : "Waiting", state.task ? "success" : "empty");
      return;
    }
    els.answerCorrect.textContent = answer.correct ? "Yes" : "No";
    els.answerScore.textContent = Number(answer.score).toFixed(2);
    els.answerDifficulty.textContent = formatDifficulty(answer.new_difficulty);
    els.answerMessage.textContent = answer.message;
    setPill(els.answerState, answer.correct ? "Correct" : "Submitted", answer.correct ? "success" : "loading");
  }

  function updateProgressView(progress) {
    const accuracy = Math.round(Number(progress.accuracy) * 100);
    els.accuracyValue.textContent = `${accuracy}%`;
    els.totalAnswers.textContent = progress.total_answers;
    els.correctCount.textContent = progress.correct_count;
    els.progressDifficulty.textContent = formatDifficulty(progress.current_difficulty);
    setPill(els.progressState, Number(progress.total_answers) > 0 ? "Updated" : "Empty", Number(progress.total_answers) > 0 ? "success" : "empty");
  }

  async function requestJson(url, options, endpointKey) {
    const method = (options && options.method) || "GET";
    writeDebug("request", {
      method,
      url,
      body: options && options.body ? JSON.parse(options.body) : null,
    });

    const response = await fetch(url, options);
    let payload = null;
    try {
      payload = await response.json();
    } catch (error) {
      payload = null;
    }

    writeDebug("response", {
      status: response.status,
      ok: response.ok,
      endpoint: endpointKey || null,
      body: payload,
    });

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
    setPill(els.sessionState, "Creating", "loading");
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
      }, "sessions");
      state.session = session;
      state.task = null;
      updateSessionView();
      updateTaskView();
      updateAnswerView(null);
      setStatus("Session created. Request the next task.", "ok", "sessions");
      await refreshProgress();
    } catch (error) {
      setPill(els.sessionState, "Error", "error");
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
    setPill(els.taskState, "Loading", "loading");
    setAudioState("loading");
    els.audioHint.textContent = "Requesting task and generating audio...";
    setStatus("Requesting next task and audio...", "loading", "task");
    try {
      const params = new URLSearchParams({ session_id: state.session.session_id });
      const task = await requestJson(`/api/v1/tasks/next?${params.toString()}`, undefined, "task");
      state.task = task;
      updateTaskView();
      updateAnswerView(null);
      setStatus("Task loaded. Audio is ready when the browser can fetch it.", "ok", "task");
    } catch (error) {
      state.task = null;
      updateTaskView();
      setPill(els.taskState, "Error", "error");
      setAudioState("error");
      els.audioHint.textContent = "Audio could not be generated. This often means edge-tts or network access failed; keep the session and retry when TTS is available.";
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
    setPill(els.answerState, "Submitting", "loading");
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
      }, "answer");
      updateAnswerView(answer);
      setStatus("Answer submitted. Progress refreshed.", "ok", "answer");
      await refreshProgress();
    } catch (error) {
      setPill(els.answerState, "Error", "error");
      showError("Answer request failed", error);
    } finally {
      setBusy(false);
    }
  }

  async function refreshProgress() {
    const userId = (state.session && state.session.user_id) || els.userId.value.trim() || "demo_user";
    clearError();
    setPill(els.progressState, "Loading", "loading");
    setStatus("Refreshing progress...", "loading", "progress");
    try {
      const progress = await requestJson(`/api/v1/users/${encodeURIComponent(userId)}/progress`, undefined, "progress");
      updateProgressView(progress);
      setStatus("Progress is up to date.", "ok", "progress");
    } catch (error) {
      setPill(els.progressState, "Error", "error");
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
  els.noiseProfile.addEventListener("change", updateSessionView);
  els.taskAudio.addEventListener("error", function () {
    if (state.task) {
      setAudioState("error");
      setPill(els.taskState, "Audio error", "error");
      showError("Audio playback failed", new Error("The returned audio_url could not be loaded by the browser."));
    }
  });

  updateSessionView();
  updateTaskView();
  updateAnswerView(null);
  refreshProgress();
})();
