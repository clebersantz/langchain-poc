/**
 * chat.js — Session management, API calls, and DOM updates for the CRM chat UI.
 */

const API_BASE = "";  // Same origin; change if running frontend separately

// ── Session management ──────────────────────────────────────────────────────

function getOrCreateSessionId() {
  let sessionId = localStorage.getItem("crm_session_id");
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem("crm_session_id", sessionId);
  }
  return sessionId;
}

const SESSION_ID = getOrCreateSessionId();
document.getElementById("session-display").textContent = `Session: ${SESSION_ID.slice(0, 8)}…`;

// ── DOM helpers ──────────────────────────────────────────────────────────────

const messagesEl = document.getElementById("messages");
const inputEl    = document.getElementById("user-input");
const sendBtn    = document.getElementById("send-btn");
const sendIcon   = document.getElementById("send-icon");
const spinner    = document.getElementById("spinner");

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setLoading(loading) {
  sendBtn.disabled = loading;
  inputEl.disabled = loading;
  sendIcon.classList.toggle("hidden", loading);
  spinner.classList.toggle("hidden", !loading);
}

/**
 * Append a chat bubble to the messages container.
 * @param {"user"|"assistant"} role
 * @param {string} text  Raw text or Markdown for assistant messages
 * @param {string} [agentUsed]  Optional agent badge for assistant messages
 */
function appendMessage(role, text, agentUsed) {
  const wrapper = document.createElement("div");
  wrapper.className = `message-wrapper ${role}`;

  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;

  if (role === "assistant") {
    bubble.innerHTML = marked.parse(text);
    if (agentUsed) {
      const badge = document.createElement("span");
      badge.className = "agent-badge";
      badge.textContent = `🤖 ${agentUsed.replace(/_/g, " ")}`;
      wrapper.appendChild(badge);
    }
  } else {
    bubble.textContent = text;
  }

  wrapper.appendChild(bubble);
  messagesEl.appendChild(wrapper);
  scrollToBottom();
}

function appendError(message) {
  const el = document.createElement("div");
  el.className = "error-msg";
  el.textContent = `⚠️ ${message}`;
  messagesEl.appendChild(el);
  scrollToBottom();
}

// ── API call ─────────────────────────────────────────────────────────────────

/**
 * Send a message to the /chat endpoint and render the response.
 * @param {string} message
 */
async function sendMessage(message) {
  if (!message.trim()) return;

  appendMessage("user", message);
  inputEl.value = "";
  inputEl.style.height = "auto";
  setLoading(true);

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: SESSION_ID, message }),
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(`HTTP ${res.status}: ${err}`);
    }

    const data = await res.json();
    appendMessage("assistant", data.response, data.agent_used);
  } catch (err) {
    appendError(err.message || "Failed to get a response. Please try again.");
  } finally {
    setLoading(false);
    inputEl.focus();
  }
}

// ── Event listeners ──────────────────────────────────────────────────────────

sendBtn.addEventListener("click", () => sendMessage(inputEl.value));

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage(inputEl.value);
  }
});

// Auto-resize textarea
inputEl.addEventListener("input", () => {
  inputEl.style.height = "auto";
  inputEl.style.height = `${Math.min(inputEl.scrollHeight, 160)}px`;
});

document.getElementById("btn-clear").addEventListener("click", () => {
  if (confirm("Clear chat history?")) {
    messagesEl.innerHTML = "";
    localStorage.removeItem("crm_session_id");
    location.reload();
  }
});

// ── Welcome message ──────────────────────────────────────────────────────────

appendMessage(
  "assistant",
  "👋 Hello! I'm your **Odoo 16 CRM Assistant**.\n\n" +
  "I can help you with:\n" +
  "- 📚 **CRM questions** — leads, pipeline, activities, teams\n" +
  "- 🔍 **Data queries** — search, create, and update Odoo records\n" +
  "- ⚙️ **Workflows** — lead qualification, follow-ups, onboarding\n\n" +
  "How can I help you today?",
  null
);
