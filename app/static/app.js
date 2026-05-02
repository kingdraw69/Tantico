const API_PREFIX = "/api/v1";

const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const messages = document.getElementById("messages");
const sendButton = document.getElementById("sendButton");
const avatar = document.getElementById("anaAvatar");
const stateBubble = document.getElementById("stateBubble");
const avatarState = document.getElementById("avatarState");
const emotionLabel = document.getElementById("emotionLabel");
const riskLabel = document.getElementById("riskLabel");
const voiceToggle = document.getElementById("voiceToggle");
const allowHistory = document.getElementById("allowHistory");

let voiceEnabled = true;

let conversationHistory = [];

const stateText = {
  idle: "Neutral / Idle",
  listening: "Listening",
  thinking: "Thinking",
  speaking: "Speaking",
  supportive: "Supportive / Empathetic",
  crisis: "Alert / Crisis Support"
};

const bubbleText = {
  idle: "Hola, soy Ana 💚",
  listening: "Te escucho con calma",
  thinking: "Estoy pensando contigo",
  speaking: "Te respondo despacito",
  supportive: "Vamos paso a paso",
  crisis: "Busquemos apoyo seguro"
};

function setAvatarState(state) {
  avatar.className = `ana-avatar ${state}`;
  avatarState.textContent = stateText[state] || state;
  stateBubble.textContent = bubbleText[state] || "Estoy aquí";
}

function addMessage(role, title, text) {
  const box = document.createElement("div");
  box.className = `message ${role}`;
  box.innerHTML = `<strong>${title}</strong><p>${escapeHtml(text)}</p>`;
  messages.appendChild(box);
  messages.scrollTop = messages.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

async function getGuestToken() {
  const current = localStorage.getItem("tantico_token");
  if (current) return current;

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

  if (backendState) return backendState;
  if (risk === "alto" || emotion.includes("crisis")) return "crisis";
  if (["ansiedad", "tristeza", "estres", "estrés", "estres_academico"].some(e => emotion.includes(e))) {
    return "supportive";
  }

  return "speaking";
}

function speak(text, finalState = "supportive") {
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

voiceToggle.addEventListener("click", () => {
  voiceEnabled = !voiceEnabled;
  voiceToggle.textContent = voiceEnabled ? "🔊 Voz activada" : "🔇 Voz desactivada";
  if (!voiceEnabled && "speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }
});

input.addEventListener("focus", () => setAvatarState("listening"));
input.addEventListener("input", () => setAvatarState("listening"));

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

    const emotionNames = {
      neutral: "Conversación normal",
      ansiedad: "Ansiedad",
      estres_academico: "Estrés académico",
      tristeza: "Tristeza",
      enojo: "Enojo",
      confusion: "Conversación normal",
      crisis: "Crisis"
    };

    emotionLabel.textContent = emotionNames[data.emotion] || "Conversación normal";
    riskLabel.textContent = data.risk_level || "No evaluado";

    const reply = data.reply || "Estoy aquí contigo. Probemos una pausa breve para respirar.";
    const nextState = mapAvatarState(data);

    addMessage("bot", "Ana", reply);
    conversationHistory.push({
      role: "assistant",
      content: reply
    });

    conversationHistory = conversationHistory.slice(-12);

    const hiddenActions = [
      "conversacion-normal",
      "normal_conversation",
      "ninguna",
      "none",
      "null"
    ];

    const suggestedAction = String(data.suggested_action || "").toLowerCase();

    if (data.suggested_action && !hiddenActions.includes(suggestedAction)) {
      addMessage("system", "Acción sugerida", `Puedes intentar: ${data.suggested_action}`);
    }

    speak(reply, nextState);
  } catch (error) {
    setAvatarState("crisis");
    addMessage("system", "Aviso", error.message);
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
});

setAvatarState("idle");
getGuestToken().catch(() => {
  addMessage("system", "Aviso", "No se pudo iniciar sesión invitada automáticamente.");
});