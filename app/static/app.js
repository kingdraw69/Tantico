const API_PREFIX = "/api/v1";

const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const messages = document.getElementById("messages");
const sendButton = document.getElementById("sendButton");
const avatarImage = document.getElementById("avatarImage");
const stateBubble = document.getElementById("stateBubble");
const avatarState = document.getElementById("avatarState");
const emotionLabel = document.getElementById("emotionLabel");
const riskLabel = document.getElementById("riskLabel");
const voiceToggle = document.getElementById("voiceToggle");
const allowHistory = document.getElementById("allowHistory");
const panicButton = document.getElementById("panicButton");
const guidedExercisePanel = document.getElementById("guidedExercisePanel");

let voiceEnabled = true;
let conversationHistory = [];
let activeExerciseSession = null;
const avatarStates = {
  idle: {
    src: "/static/avatars/ana-idle.png",
    label: "Neutral / Idle",
    bubble: "Hola, soy Ana 💚",
    alt: "Avatar Ana en estado neutral"
  },
  listening: {
    src: "/static/avatars/ana-listening.png",
    label: "Listening",
    bubble: "Te escucho con calma",
    alt: "Avatar Ana escuchando"
  },
  thinking: {
    src: "/static/avatars/ana-thinking.png",
    label: "Thinking",
    bubble: "Estoy pensando contigo",
    alt: "Avatar Ana pensando"
  },
  speaking: {
    src: "/static/avatars/ana-speaking.png",
    label: "Speaking",
    bubble: "Te respondo despacito",
    alt: "Avatar Ana hablando"
  },
  supportive: {
    src: "/static/avatars/ana-supportive.png",
    label: "Supportive / Empathetic",
    bubble: "Vamos paso a paso",
    alt: "Avatar Ana apoyando emocionalmente"
  },
  crisis: {
    src: "/static/avatars/ana-crisis.png",
    label: "Alert / Crisis Support",
    bubble: "Busquemos apoyo seguro",
    alt: "Avatar Ana en estado de alerta o crisis"
  }
};

const emotionNames = {
  neutral: "Conversación normal",
  ansiedad: "Ansiedad",
  estres_academico: "Estrés académico",
  tristeza: "Tristeza",
  enojo: "Enojo",
  confusion: "Conversación normal",
  crisis: "Crisis"
};

const hiddenActions = [
  "conversacion-normal",
  "normal_conversation",
  "ninguna",
  "none",
  "null",
  "",
  "undefined"
];

function setAvatarState(state) {
  const selectedState = avatarStates[state] ? state : "idle";
  const config = avatarStates[selectedState];

  if (!avatarImage) return;

  avatarImage.classList.add("is-changing");

  setTimeout(() => {
    avatarImage.src = config.src;
    avatarImage.alt = config.alt;

    if (avatarState) {
      avatarState.textContent = config.label;
    }

    if (stateBubble) {
      stateBubble.textContent = config.bubble;
    }

    avatarImage.classList.remove("is-changing");
  }, 120);
}

function addMessage(role, title, text) {
  const box = document.createElement("div");
  box.className = `message ${role}`;
  box.innerHTML = `<strong>${escapeHtml(title)}</strong><p>${escapeHtml(text)}</p>`;
  messages.appendChild(box);
  messages.scrollTop = messages.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = String(text ?? "");
  return div.innerHTML;
}

async function getGuestToken() {
  const current = localStorage.getItem("tantico_token");

  if (current) {
    return current;
  }

  const response = await fetch(`${API_PREFIX}/auth/guest`, {
    method: "POST"
  });

  if (!response.ok) {
    throw new Error("No se pudo crear la sesión invitada.");
  }

  const data = await response.json();

  localStorage.setItem("tantico_token", data.access_token);
  localStorage.setItem("tantico_user_id", data.user_id);

  return data.access_token;
}

function mapAvatarState(data) {
  const risk = String(data.risk_level || "").toLowerCase();
  const emotion = String(data.emotion || "").toLowerCase();
  const backendState = String(data.avatar_state || "").toLowerCase();
  const suggestedAction = String(data.suggested_action || "").toLowerCase();

  if (avatarStates[backendState]) {
    return backendState;
  }

  if (risk === "alto" || emotion.includes("crisis")) {
    return "crisis";
  }

  const hiddenActions = [
    "conversacion-normal",
    "normal_conversation",
    "ninguna",
    "none",
    "null",
    "",
    "undefined"
  ];

  const hasRealExercise = suggestedAction && !hiddenActions.includes(suggestedAction);

  if (
    hasRealExercise ||
    emotion.includes("ansiedad") ||
    emotion.includes("tristeza") ||
    emotion.includes("estres") ||
    emotion.includes("estrés") ||
    emotion.includes("estres_academico")
  ) {
    return "supportive";
  }

  return "speaking";
}

function speak(text, finalState = "idle") {
  if (!voiceEnabled || !("speechSynthesis" in window)) {
    setAvatarState(finalState);
    return;
  }

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "es-CO";
  utterance.rate = 0.94;
  utterance.pitch = 1.05;
  utterance.volume = 1;

  utterance.onstart = () => setAvatarState("speaking");
  utterance.onend = () => setAvatarState(finalState);
  utterance.onerror = () => setAvatarState(finalState);

  window.speechSynthesis.speak(utterance);
}

function clearGuidedExerciseIfNormal(suggestedAction) {
  const normalizedAction = String(suggestedAction || "").toLowerCase();

  if (!guidedExercisePanel) return;

  if (!suggestedAction || hiddenActions.includes(normalizedAction)) {
    guidedExercisePanel.innerHTML = "";
    guidedExercisePanel.style.display = "none";
  }
}

if (voiceToggle) {
  voiceToggle.addEventListener("click", () => {
    voiceEnabled = !voiceEnabled;
    voiceToggle.textContent = voiceEnabled ? "🔊 Voz activada" : "🔇 Voz desactivada";

    if (!voiceEnabled && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
  });
}

if (input) {
  input.addEventListener("focus", () => setAvatarState("listening"));
  input.addEventListener("input", () => setAvatarState("listening"));
}

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();

    if (form.requestSubmit) {
      form.requestSubmit();
    } else {
      sendButton.click();
    }
  }
});

if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = input.value.trim();

    if (!message) return;

    addMessage("user", "Tú", message);

    conversationHistory.push({
      role: "user",
      content: message
    });

    conversationHistory = conversationHistory.slice(-12);

    input.value = "";
    sendButton.disabled = true;
    setAvatarState("thinking");

    try {
      const token = await getGuestToken();

      const response = await fetch(`${API_PREFIX}/chat/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          message,
          context: {
            source: "web_avatar_ana",
            minutes_available: 10,
            allow_history: allowHistory.checked,
            conversation_history: conversationHistory
          }
        })
      });

      if (response.status === 404) {
        throw new Error("El endpoint /api/v1/chat/message no está registrado todavía.");
      }

      if (response.status === 401 || response.status === 403) {
        localStorage.removeItem("tantico_token");
        throw new Error("La sesión expiró. Intenta enviar el mensaje otra vez.");
      }

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(`Error del backend: ${detail}`);
      }

      const data = await response.json();

      emotionLabel.textContent = emotionNames[data.emotion] || "Conversación normal";
      riskLabel.textContent = data.risk_level || "No evaluado";

      const reply = data.reply || "Estoy aquí contigo.";
      const nextState = mapAvatarState(data);

      addMessage("bot", "Ana", reply);

      conversationHistory.push({
        role: "assistant",
        content: reply
      });

      conversationHistory = conversationHistory.slice(-12);

      const suggestedAction = String(data.suggested_action || "").toLowerCase();

      if (data.suggested_action && !hiddenActions.includes(suggestedAction)) {
        await loadGuidedExercise(data.suggested_action);
      } else {
        clearGuidedExerciseIfNormal(data.suggested_action);
      }

      speak(reply, nextState);
    } catch (error) {
      console.error(error);
      setAvatarState("crisis");
      addMessage("system", "Aviso", error.message);
    } finally {
      sendButton.disabled = false;
      input.focus();
    }
  });
}

if (panicButton) {
  panicButton.addEventListener("click", (event) => {
    event.preventDefault();
    activatePanicButton();
  });
}

async function activatePanicButton() {
  console.log("Botón de pánico presionado");

  setAvatarState("crisis");

  if (panicButton) {
    panicButton.disabled = true;
    panicButton.textContent = "Activando apoyo...";
  }

  try {
    const token = await getGuestToken();

    const response = await fetch(`${API_PREFIX}/support/panic`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      }
    });

    if (response.status === 404) {
      throw new Error("El endpoint /api/v1/support/panic no está registrado en el backend.");
    }

    if (response.status === 401 || response.status === 403) {
      localStorage.removeItem("tantico_token");
      throw new Error("La sesión expiró. Intenta activar el botón otra vez.");
    }

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(`No se pudo activar el botón de pánico: ${detail}`);
    }

    const data = await response.json();

    addMessage(
      "bot",
      "Ana",
      data.message || "Estoy contigo. Vamos a hacer una pausa segura primero."
    );

    if (data.motivational_phrase) {
      addMessage("system", "Frase de apoyo", data.motivational_phrase);
    }

    if (data.tcc_prompt) {
      addMessage("system", "Guía TCC", data.tcc_prompt);
    }

    if (data.exercises && data.exercises.length > 0) {
      renderPanicExercises(data.exercises);
    } else {
      renderPanicExercises([
        {
          title: "Respiración 4-4-4",
          category: "respiración",
          duration_minutes: 2,
          description: "Ejercicio breve para volver al presente.",
          steps: [
            "Inhala lentamente contando hasta 4.",
            "Mantén el aire contando hasta 4.",
            "Exhala despacio contando hasta 4.",
            "Repite el ciclo tres veces."
          ]
        },
        {
          title: "Guía TCC breve",
          category: "TCC",
          duration_minutes: 3,
          description: "Ejercicio para revisar un pensamiento difícil.",
          steps: [
            "Identifica el pensamiento que más pesa ahora.",
            "Pregúntate si es un hecho o una interpretación.",
            "Busca una evidencia a favor y una en contra.",
            "Crea una versión más equilibrada del pensamiento."
          ]
        }
      ]);
    }

    speak(
      data.message || "Estoy contigo. Vamos a hacer una pausa segura primero.",
      "crisis"
    );
  } catch (error) {
    console.error(error);

    addMessage(
      "system",
      "Aviso",
      error.message || "No pude cargar la guía completa, pero intenta respirar despacio y busca apoyo humano si sientes que estás en peligro."
    );
  } finally {
    if (panicButton) {
      panicButton.disabled = false;
      panicButton.textContent = "Botón de pánico";
    }
  }
}

async function loadGuidedExercise(slug) {
  try {
    const token = await getGuestToken();

    const response = await fetch(`${API_PREFIX}/support/tools/${slug}`, {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) {
      console.warn("No se encontró el ejercicio:", slug);
      return;
    }

    const exercise = await response.json();
    renderGuidedExercise(exercise);
  } catch (error) {
    console.error("Error cargando ejercicio guiado:", error);
  }
}

function stopActiveExercise() {
  if (activeExerciseSession && typeof activeExerciseSession.stop === "function") {
    activeExerciseSession.stop();
  }

  activeExerciseSession = null;
}

function renderGuidedExercise(exercise) {
  stopActiveExercise();

  const slug = String(exercise.slug || "").toLowerCase();
  const category = String(exercise.category || "").toLowerCase();
  const title = String(exercise.title || "").toLowerCase();

  if (
    slug.includes("respiracion") ||
    title.includes("respiración") ||
    title.includes("respiracion") ||
    category.includes("respiracion")
  ) {
    renderBreathingExercise(exercise);
    return;
  }

  if (
    slug.includes("54321") ||
    slug.includes("conexion-tierra") ||
    title.includes("presente") ||
    title.includes("pánico") ||
    title.includes("panico")
  ) {
    renderGroundingExercise(exercise);
    return;
  }

  if (
    slug.includes("reestructuracion") ||
    slug.includes("tcc") ||
    category.includes("tcc") ||
    title.includes("tcc")
  ) {
    renderTccExercise(exercise);
    return;
  }

  if (
    slug.includes("frase") ||
    category.includes("motivacion") ||
    title.includes("ánimo") ||
    title.includes("animo")
  ) {
    renderMotivationalExercise(exercise);
    return;
  }

  renderStepByStepExercise(exercise);
}

function getExerciseSteps(exercise) {
  return Array.isArray(exercise.steps) && exercise.steps.length > 0
    ? exercise.steps
    : ["Respira un momento.", "Lee con calma.", "Avanza paso a paso."];
}

function openExercisePanel(html) {
  const panel = guidedExercisePanel;

  if (!panel) return;

  panel.innerHTML = html;
  panel.style.display = "block";
  panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function closeExercisePanel() {
  stopActiveExercise();

  if (!guidedExercisePanel) return;

  guidedExercisePanel.innerHTML = "";
  guidedExercisePanel.style.display = "none";
  setAvatarState("idle");
}

function guideVoice(text, finalState = "supportive") {
  if (typeof speak === "function") {
    speak(text, finalState);
  } else {
    setAvatarState(finalState);
  }
}

function renderBreathingExercise(exercise) {
  const roundsTotal = 3;

  openExercisePanel(`
    <div class="exercise-card interactive-exercise breathing-exercise">
      <div class="exercise-header">
        <span class="exercise-category">${escapeHtml(exercise.category || "respiración")}</span>
        <span class="exercise-time">${escapeHtml(exercise.duration_minutes || "2")} min</span>
      </div>

      <h3>${escapeHtml(exercise.title || "Respiración guiada")}</h3>
      <p>${escapeHtml(exercise.description || "Vamos a respirar juntos por unos segundos.")}</p>

      <div class="breathing-stage">
        <div id="breathingCircle" class="breathing-circle">
          <span id="breathingCounter">4</span>
        </div>

        <h4 id="breathingPhase">Inhala</h4>
        <p id="breathingInstruction">Cuando estés listo, presiona iniciar.</p>
        <p class="exercise-progress" id="breathingRound">Ronda 1 de ${roundsTotal}</p>
      </div>

      <div class="exercise-actions">
        <button type="button" id="startBreathingBtn">Iniciar</button>
        <button type="button" id="resetBreathingBtn" class="secondary-action">Reiniciar</button>
        <button type="button" id="closeExerciseBtn" class="secondary-action">Cerrar</button>
      </div>
    </div>
  `);

  setAvatarState("supportive");

  const phases = [
    {
      name: "Inhala",
      className: "inhale",
      seconds: 4,
      instruction: "Inhala suavemente por la nariz conmigo."
    },
    {
      name: "Sostén",
      className: "hold",
      seconds: 4,
      instruction: "Mantén el aire con calma, sin forzarte."
    },
    {
      name: "Exhala",
      className: "exhale",
      seconds: 4,
      instruction: "Suelta el aire despacio por la boca."
    }
  ];

  let round = 1;
  let phaseIndex = 0;
  let remaining = phases[phaseIndex].seconds;
  let timer = null;
  let running = false;

  const circle = document.getElementById("breathingCircle");
  const counter = document.getElementById("breathingCounter");
  const phaseText = document.getElementById("breathingPhase");
  const instruction = document.getElementById("breathingInstruction");
  const roundText = document.getElementById("breathingRound");
  const startBtn = document.getElementById("startBreathingBtn");
  const resetBtn = document.getElementById("resetBreathingBtn");
  const closeBtn = document.getElementById("closeExerciseBtn");

  function updateBreathingUI(read = false) {
    const phase = phases[phaseIndex];

    circle.className = `breathing-circle ${phase.className}`;
    counter.textContent = remaining;
    phaseText.textContent = phase.name;
    instruction.textContent = phase.instruction;
    roundText.textContent = `Ronda ${round} de ${roundsTotal}`;

    if (read) {
      guideVoice(`${phase.name}. ${phase.instruction}`, "supportive");
    }
  }

  function completeBreathing() {
    clearInterval(timer);
    timer = null;
    running = false;

    circle.className = "breathing-circle completed";
    counter.textContent = "✓";
    phaseText.textContent = "Muy bien";
    instruction.textContent = "Terminamos la respiración. Quédate un momento notando cómo está tu cuerpo.";
    roundText.textContent = "Ejercicio completado";
    startBtn.textContent = "Iniciar de nuevo";

    guideVoice("Muy bien. Terminamos la respiración. Quédate un momento notando cómo está tu cuerpo.", "supportive");
  }

  function nextPhase() {
    phaseIndex += 1;

    if (phaseIndex >= phases.length) {
      phaseIndex = 0;
      round += 1;
    }

    if (round > roundsTotal) {
      completeBreathing();
      return;
    }

    remaining = phases[phaseIndex].seconds;
    updateBreathingUI(true);
  }

  function tick() {
    remaining -= 1;

    if (remaining <= 0) {
      nextPhase();
      return;
    }

    counter.textContent = remaining;
  }

  function startBreathing() {
    if (running) {
      clearInterval(timer);
      timer = null;
      running = false;
      startBtn.textContent = "Continuar";
      setAvatarState("supportive");
      return;
    }

    if (round > roundsTotal) {
      round = 1;
      phaseIndex = 0;
      remaining = phases[phaseIndex].seconds;
    }

    running = true;
    startBtn.textContent = "Pausar";
    updateBreathingUI(true);
    timer = setInterval(tick, 1000);
  }

  function resetBreathing() {
    clearInterval(timer);
    timer = null;
    running = false;
    round = 1;
    phaseIndex = 0;
    remaining = phases[phaseIndex].seconds;
    startBtn.textContent = "Iniciar";
    updateBreathingUI(false);
    setAvatarState("supportive");
  }

  startBtn.addEventListener("click", startBreathing);
  resetBtn.addEventListener("click", resetBreathing);
  closeBtn.addEventListener("click", closeExercisePanel);

  activeExerciseSession = {
    stop() {
      clearInterval(timer);
    }
  };

  updateBreathingUI(false);
}

function renderGroundingExercise(exercise) {
  const prompts = [
    {
      title: "5 cosas que puedes ver",
      helper: "Mira a tu alrededor y escribe cinco cosas que puedas ver."
    },
    {
      title: "4 cosas que puedes tocar",
      helper: "Toca cuatro cosas cercanas o nota cuatro sensaciones físicas."
    },
    {
      title: "3 sonidos que puedes escuchar",
      helper: "Haz una pausa y escribe tres sonidos que puedas notar."
    },
    {
      title: "2 cosas que puedes oler",
      helper: "Identifica dos olores. Si no encuentras, escribe dos olores que recuerdes."
    },
    {
      title: "1 cosa que puedes saborear o notar",
      helper: "Nota un sabor o simplemente escribe cómo se siente tu respiración ahora."
    }
  ];

  let currentStep = 0;
  const answers = [];

  function renderStep() {
    const prompt = prompts[currentStep];

    openExercisePanel(`
      <div class="exercise-card interactive-exercise grounding-exercise">
        <div class="exercise-header">
          <span class="exercise-category">conexión a tierra</span>
          <span class="exercise-time">Paso ${currentStep + 1} de ${prompts.length}</span>
        </div>

        <h3>${escapeHtml(exercise.title || "Volver al presente")}</h3>

        <div class="step-progress-bar">
          <div style="width: ${((currentStep + 1) / prompts.length) * 100}%"></div>
        </div>

        <h4>${escapeHtml(prompt.title)}</h4>
        <p>${escapeHtml(prompt.helper)}</p>

        <textarea
          id="groundingAnswer"
          class="exercise-textarea"
          rows="3"
          placeholder="Escribe aquí con calma..."
        ></textarea>

        <p class="privacy-mini-note">Esto solo se usa en pantalla. No se envía al backend.</p>

        <div class="exercise-actions">
          <button type="button" id="groundingNextBtn">
            ${currentStep === prompts.length - 1 ? "Finalizar" : "Siguiente"}
          </button>
          <button type="button" id="groundingSkipBtn" class="secondary-action">Saltar</button>
          <button type="button" id="closeExerciseBtn" class="secondary-action">Cerrar</button>
        </div>
      </div>
    `);

    setAvatarState("listening");
    guideVoice(prompt.helper, "listening");

    const answerInput = document.getElementById("groundingAnswer");
    const nextBtn = document.getElementById("groundingNextBtn");
    const skipBtn = document.getElementById("groundingSkipBtn");
    const closeBtn = document.getElementById("closeExerciseBtn");

    nextBtn.addEventListener("click", () => {
      answers[currentStep] = answerInput.value.trim();

      if (currentStep >= prompts.length - 1) {
        renderGroundingSummary(prompts, answers);
        return;
      }

      currentStep += 1;
      renderStep();
    });

    skipBtn.addEventListener("click", () => {
      answers[currentStep] = "";

      if (currentStep >= prompts.length - 1) {
        renderGroundingSummary(prompts, answers);
        return;
      }

      currentStep += 1;
      renderStep();
    });

    closeBtn.addEventListener("click", closeExercisePanel);
  }

  renderStep();
}

function renderGroundingSummary(prompts, answers) {
  openExercisePanel(`
    <div class="exercise-card interactive-exercise completed-exercise">
      <div class="exercise-header">
        <span class="exercise-category">ejercicio completado</span>
        <span class="exercise-time">✓</span>
      </div>

      <h3>Volviste al presente</h3>
      <p>Muy bien. Fuiste paso a paso y usaste tus sentidos para anclarte al momento actual.</p>

      <div class="exercise-summary">
        ${prompts.map((prompt, index) => `
          <div>
            <strong>${escapeHtml(prompt.title)}</strong>
            <p>${escapeHtml(answers[index] || "Sin respuesta escrita")}</p>
          </div>
        `).join("")}
      </div>

      <div class="exercise-closing">
        No tienes que resolver todo ahora. Este momento ya fue un paso de cuidado.
      </div>

      <div class="exercise-actions">
        <button type="button" id="closeExerciseBtn">Terminar</button>
      </div>
    </div>
  `);

  setAvatarState("supportive");
  guideVoice("Muy bien. Volviste al presente paso a paso.", "supportive");

  document.getElementById("closeExerciseBtn").addEventListener("click", closeExercisePanel);
}

function renderTccExercise(exercise) {
  const questions = [
    {
      title: "Pensamiento principal",
      helper: "¿Qué pensamiento te está pesando ahora?"
    },
    {
      title: "Hecho o interpretación",
      helper: "¿Ese pensamiento es un hecho confirmado, una interpretación o no estás seguro?"
    },
    {
      title: "Evidencia a favor",
      helper: "¿Qué cosas te hacen pensar que ese pensamiento podría ser cierto?"
    },
    {
      title: "Evidencia en contra",
      helper: "¿Qué cosas muestran que tal vez no es completamente cierto?"
    },
    {
      title: "Pensamiento más equilibrado",
      helper: "Escribe una versión más calmada, realista o amable de ese pensamiento."
    },
    {
      title: "Siguiente paso pequeño",
      helper: "¿Qué acción pequeña puedes hacer hoy para cuidarte o avanzar?"
    }
  ];

  let currentQuestion = 0;
  const answers = [];

  function renderQuestion() {
    const question = questions[currentQuestion];

    openExercisePanel(`
      <div class="exercise-card interactive-exercise tcc-exercise">
        <div class="exercise-header">
          <span class="exercise-category">guía TCC</span>
          <span class="exercise-time">Pregunta ${currentQuestion + 1} de ${questions.length}</span>
        </div>

        <h3>${escapeHtml(exercise.title || "Guía TCC breve")}</h3>

        <div class="step-progress-bar">
          <div style="width: ${((currentQuestion + 1) / questions.length) * 100}%"></div>
        </div>

        <h4>${escapeHtml(question.title)}</h4>
        <p>${escapeHtml(question.helper)}</p>

        <textarea
          id="tccAnswer"
          class="exercise-textarea"
          rows="4"
          placeholder="Escribe con calma. No tiene que ser perfecto..."
        ></textarea>

        <p class="privacy-mini-note">Esta reflexión no se guarda automáticamente.</p>

        <div class="exercise-actions">
          <button type="button" id="tccNextBtn">
            ${currentQuestion === questions.length - 1 ? "Ver resumen" : "Siguiente"}
          </button>
          <button type="button" id="tccSkipBtn" class="secondary-action">Saltar</button>
          <button type="button" id="closeExerciseBtn" class="secondary-action">Cerrar</button>
        </div>
      </div>
    `);

    setAvatarState("listening");
    guideVoice(question.helper, "listening");

    const answerInput = document.getElementById("tccAnswer");
    const nextBtn = document.getElementById("tccNextBtn");
    const skipBtn = document.getElementById("tccSkipBtn");
    const closeBtn = document.getElementById("closeExerciseBtn");

    nextBtn.addEventListener("click", () => {
      answers[currentQuestion] = answerInput.value.trim();

      if (currentQuestion >= questions.length - 1) {
        renderTccSummary(questions, answers);
        return;
      }

      currentQuestion += 1;
      renderQuestion();
    });

    skipBtn.addEventListener("click", () => {
      answers[currentQuestion] = "";

      if (currentQuestion >= questions.length - 1) {
        renderTccSummary(questions, answers);
        return;
      }

      currentQuestion += 1;
      renderQuestion();
    });

    closeBtn.addEventListener("click", closeExercisePanel);
  }

  renderQuestion();
}

function renderTccSummary(questions, answers) {
  openExercisePanel(`
    <div class="exercise-card interactive-exercise completed-exercise">
      <div class="exercise-header">
        <span class="exercise-category">reflexión completada</span>
        <span class="exercise-time">✓</span>
      </div>

      <h3>Resumen de tu guía TCC</h3>
      <p>Hoy tomaste un pensamiento difícil y lo miraste con más calma.</p>

      <div class="exercise-summary">
        ${questions.map((question, index) => `
          <div>
            <strong>${escapeHtml(question.title)}</strong>
            <p>${escapeHtml(answers[index] || "Sin respuesta escrita")}</p>
          </div>
        `).join("")}
      </div>

      <div class="exercise-closing">
        Un pensamiento puede sentirse fuerte, pero no siempre cuenta toda la verdad. Puedes volver a mirarlo paso a paso.
      </div>

      <div class="exercise-actions">
        <button type="button" id="closeExerciseBtn">Terminar</button>
      </div>
    </div>
  `);

  setAvatarState("supportive");
  guideVoice("Muy bien. Miraste ese pensamiento con más calma y eso ya es un avance.", "supportive");

  document.getElementById("closeExerciseBtn").addEventListener("click", closeExercisePanel);
}

function renderMotivationalExercise(exercise) {
  const defaultPhrases = [
    "No tienes que resolver todo en este momento.",
    "Puedes ir paso a paso, incluso si hoy el paso es pequeño.",
    "Sentirte mal no significa que estés fallando.",
    "Respira. Este momento difícil también puede pasar.",
    "No estás solo. Buscar apoyo también es una forma de valentía."
  ];

  const phrases = getExerciseSteps(exercise).length > 0
    ? getExerciseSteps(exercise)
    : defaultPhrases;

  let currentPhrase = 0;

  function renderPhrase() {
    const phrase = phrases[currentPhrase] || defaultPhrases[0];

    openExercisePanel(`
      <div class="exercise-card interactive-exercise motivational-exercise">
        <div class="exercise-header">
          <span class="exercise-category">frase de apoyo</span>
          <span class="exercise-time">${currentPhrase + 1} de ${phrases.length}</span>
        </div>

        <h3>${escapeHtml(exercise.title || "Frase para acompañarte")}</h3>

        <div class="phrase-card">
          “${escapeHtml(phrase)}”
        </div>

        <p>Elige si quieres escucharla, cambiarla o repetirla un momento contigo.</p>

        <div class="exercise-actions">
          <button type="button" id="readPhraseBtn">Leer en voz alta</button>
          <button type="button" id="nextPhraseBtn" class="secondary-action">Otra frase</button>
          <button type="button" id="closeExerciseBtn" class="secondary-action">Cerrar</button>
        </div>
      </div>
    `);

    setAvatarState("supportive");

    document.getElementById("readPhraseBtn").addEventListener("click", () => {
      guideVoice(phrase, "supportive");
    });

    document.getElementById("nextPhraseBtn").addEventListener("click", () => {
      currentPhrase = (currentPhrase + 1) % phrases.length;
      renderPhrase();
    });

    document.getElementById("closeExerciseBtn").addEventListener("click", closeExercisePanel);
  }

  renderPhrase();
}

function renderStepByStepExercise(exercise) {
  const steps = getExerciseSteps(exercise);
  let currentStep = 0;

  function renderStep() {
    const step = steps[currentStep];

    openExercisePanel(`
      <div class="exercise-card interactive-exercise step-exercise">
        <div class="exercise-header">
          <span class="exercise-category">${escapeHtml(exercise.category || "apoyo")}</span>
          <span class="exercise-time">Paso ${currentStep + 1} de ${steps.length}</span>
        </div>

        <h3>${escapeHtml(exercise.title || "Ejercicio guiado")}</h3>

        <div class="step-progress-bar">
          <div style="width: ${((currentStep + 1) / steps.length) * 100}%"></div>
        </div>

        <div class="guided-step">
          ${escapeHtml(step)}
        </div>

        <div class="exercise-actions">
          <button type="button" id="prevStepBtn" class="secondary-action" ${currentStep === 0 ? "disabled" : ""}>Anterior</button>
          <button type="button" id="nextStepBtn">
            ${currentStep === steps.length - 1 ? "Finalizar" : "Siguiente"}
          </button>
          <button type="button" id="closeExerciseBtn" class="secondary-action">Cerrar</button>
        </div>
      </div>
    `);

    setAvatarState("supportive");
    guideVoice(step, "supportive");

    document.getElementById("prevStepBtn").addEventListener("click", () => {
      if (currentStep > 0) {
        currentStep -= 1;
        renderStep();
      }
    });

    document.getElementById("nextStepBtn").addEventListener("click", () => {
      if (currentStep >= steps.length - 1) {
        openExercisePanel(`
          <div class="exercise-card interactive-exercise completed-exercise">
            <div class="exercise-header">
              <span class="exercise-category">completado</span>
              <span class="exercise-time">✓</span>
            </div>

            <h3>Ejercicio terminado</h3>
            <p>Muy bien. Lo hiciste paso a paso.</p>

            <div class="exercise-closing">
              Quédate un momento con esta calma antes de volver al chat.
            </div>

            <div class="exercise-actions">
              <button type="button" id="closeExerciseBtn">Terminar</button>
            </div>
          </div>
        `);

        setAvatarState("supportive");
        guideVoice("Muy bien. Lo hiciste paso a paso.", "supportive");
        document.getElementById("closeExerciseBtn").addEventListener("click", closeExercisePanel);
        return;
      }

      currentStep += 1;
      renderStep();
    });

    document.getElementById("closeExerciseBtn").addEventListener("click", closeExercisePanel);
  }

  renderStep();
}

function renderPanicExercises(exercises) {
  const panel = guidedExercisePanel;

  if (!panel) return;

  panel.innerHTML = `
    <div class="exercise-card panic-card">
      <h3>Apoyo inmediato</h3>
      <p>Elige una guía para empezar ahora mismo:</p>

      <div class="panic-exercise-list">
        ${exercises.map((exercise, index) => `
          <button class="exercise-option" type="button" data-index="${index}">
            ${escapeHtml(exercise.title || "Ejercicio")} · ${escapeHtml(exercise.duration_minutes || "1")} min
          </button>
        `).join("")}
      </div>
    </div>
  `;

  panel.style.display = "block";
  panel.scrollIntoView({ behavior: "smooth", block: "nearest" });

  const buttons = panel.querySelectorAll(".exercise-option");

  buttons.forEach(button => {
    button.addEventListener("click", () => {
      const index = Number(button.dataset.index);
      renderGuidedExercise(exercises[index]);
    });
  });
}

setAvatarState("idle");

getGuestToken().catch(() => {
  addMessage("system", "Aviso", "No se pudo iniciar sesión invitada automáticamente.");
});