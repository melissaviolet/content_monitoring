// =============================================
// FlagWatch — Floating AI Chat Widget (RAG-powered)
// Drop this ONE script tag into every page, right before </body>:
//     <script src="static/js/chat-widget.js"></script>
// The widget builds itself — no HTML needed on the page.
// Talks to: POST /api/chatbot/  -> calls ask_rag_chatbot() in Django
// =============================================

const CHATBOT_API = '/api/chatbot/';

let panelOpen = false;

// =============================================
// Build and inject the widget HTML + CSS once
// =============================================
function buildChatWidget() {
  const wrapper = document.createElement('div');
  wrapper.id = 'fw-widget-root';
  wrapper.innerHTML = `
    <style>
      #fw-widget-root * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }

      #fw-dot {
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 46px;
        height: 46px;
        border-radius: 50%;
        background: #0F1923;
        border: 2px solid #F5A623;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 9998;
        box-shadow: 0 3px 14px rgba(0,0,0,0.2);
        transition: transform 0.15s ease;
        font-size: 19px;
      }

      #fw-dot:hover { transform: scale(1.1); }

      #fw-tooltip {
        position: fixed;
        bottom: 35px;
        right: 80px;
        background: #0F1923;
        color: #fff;
        font-size: 12px;
        font-weight: 500;
        padding: 7px 12px;
        border-radius: 7px;
        z-index: 9998;
        opacity: 0;
        transform: translateX(6px);
        pointer-events: none;
        transition: opacity 0.15s, transform 0.15s;
        white-space: nowrap;
      }

      #fw-tooltip.show {
        opacity: 1;
        transform: translateX(0);
      }

      #fw-tooltip::after {
        content: '';
        position: absolute;
        right: -5px;
        top: 50%;
        transform: translateY(-50%);
        border-left: 5px solid #0F1923;
        border-top: 5px solid transparent;
        border-bottom: 5px solid transparent;
      }

      #fw-panel {
        position: fixed;
        bottom: 84px;
        right: 24px;
        width: 340px;
        height: 460px;
        background: #fff;
        border-radius: 14px;
        box-shadow: 0 10px 36px rgba(0,0,0,0.18);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        z-index: 9999;
        opacity: 0;
        transform: translateY(12px) scale(0.97);
        pointer-events: none;
        transition: opacity 0.18s ease, transform 0.18s ease;
      }

      #fw-panel.open {
        opacity: 1;
        transform: translateY(0) scale(1);
        pointer-events: all;
      }

      #fw-panel-header {
        background: #0F1923;
        padding: 14px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-shrink: 0;
      }

      .fw-header-info p:first-child {
        color: #fff;
        font-size: 13px;
        font-weight: 700;
      }

      .fw-header-info p:last-child {
        color: #5A7A9A;
        font-size: 11px;
        margin-top: 1px;
      }

      #fw-panel-close {
        background: none;
        border: none;
        color: #5A7A9A;
        font-size: 18px;
        cursor: pointer;
        line-height: 1;
      }

      #fw-panel-close:hover { color: #fff; }

      #fw-msgs {
        flex: 1;
        overflow-y: auto;
        padding: 14px;
        background: #F7F8FA;
        display: flex;
        flex-direction: column;
        gap: 10px;
      }

      .fw-bubble {
        max-width: 85%;
        padding: 9px 13px;
        border-radius: 11px;
        font-size: 13px;
        line-height: 1.5;
      }

      .fw-bubble.user {
        background: #0F1923;
        color: #fff;
        align-self: flex-end;
        border-bottom-right-radius: 4px;
      }

      .fw-bubble.bot {
        background: #fff;
        color: #1A1A2E;
        border: 1px solid #E5E7EB;
        align-self: flex-start;
        border-bottom-left-radius: 4px;
      }

      .fw-bubble.thinking {
        color: #6B7280;
        font-style: italic;
      }

      #fw-input-row {
        display: flex;
        gap: 8px;
        padding: 10px;
        border-top: 1px solid #E5E7EB;
        flex-shrink: 0;
      }

      #fw-text-input {
        flex: 1;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 8px 14px;
        font-size: 13px;
        outline: none;
        background: #F7F8FA;
      }

      #fw-text-input:focus { border-color: #F5A623; background: #fff; }

      #fw-send {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: #F5A623;
        border: none;
        color: #0F1923;
        cursor: pointer;
        flex-shrink: 0;
        font-size: 14px;
      }

      #fw-send:disabled { opacity: 0.5; }
    </style>

    <div id="fw-dot">💬</div>
    <div id="fw-tooltip">AI assistant</div>

    <div id="fw-panel">
      <div id="fw-panel-header">
        <div class="fw-header-info">
          <p>FlagWatch Assistant</p>
          <p>RAG search · Ollama</p>
        </div>
        <button id="fw-panel-close">✕</button>
      </div>

      <div id="fw-msgs">
        <div class="fw-bubble bot">
          Hi! Ask me about your articles, flags, or keywords — I search your actual content to answer.
        </div>
      </div>

      <div id="fw-input-row">
        <input type="text" id="fw-text-input" placeholder="Ask something..." />
        <button id="fw-send">➤</button>
      </div>
    </div>
  `;

  document.body.appendChild(wrapper);
  attachEvents();
}

// =============================================
// Wire up all the interactions
// =============================================
function attachEvents() {
  const dot     = document.getElementById('fw-dot');
  const tooltip = document.getElementById('fw-tooltip');
  const panel   = document.getElementById('fw-panel');
  const closeBtn= document.getElementById('fw-panel-close');
  const input   = document.getElementById('fw-text-input');
  const sendBtn = document.getElementById('fw-send');

  // Hover shows the tooltip — only while the panel is closed
  dot.addEventListener('mouseenter', () => {
    if (!panelOpen) tooltip.classList.add('show');
  });
  dot.addEventListener('mouseleave', () => {
    tooltip.classList.remove('show');
  });

  // Click toggles the panel open/closed
  dot.addEventListener('click', () => {
    panelOpen = !panelOpen;
    panel.classList.toggle('open', panelOpen);
    tooltip.classList.remove('show');
    if (panelOpen) input.focus();
  });

  closeBtn.addEventListener('click', () => {
    panelOpen = false;
    panel.classList.remove('open');
  });

  sendBtn.addEventListener('click', sendChatMessage);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendChatMessage();
  });
}

// =============================================
// Send a message to the RAG backend
// =============================================
async function sendChatMessage() {
  const input = document.getElementById('fw-text-input');
  const question = input.value.trim();
  if (!question) return;

  input.value = '';
  addBubble(question, 'user');

  const thinkingBubble = addBubble('Thinking…', 'bot thinking');
  document.getElementById('fw-send').disabled = true;

  try {
    const res = await fetch(CHATBOT_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });

    const data = await res.json();
    thinkingBubble.remove();
    addBubble(data.answer || "I couldn't get an answer right now.", 'bot');

  } catch (e) {
    thinkingBubble.remove();
    addBubble('The chatbot is unavailable right now. Is Django running?', 'bot');
  } finally {
    document.getElementById('fw-send').disabled = false;
  }
}

// =============================================
// Add a message bubble, return it (so we can
// remove it later, e.g. the "Thinking…" one)
// =============================================
function addBubble(text, type) {
  const msgs = document.getElementById('fw-msgs');
  const bubble = document.createElement('div');
  bubble.className = `fw-bubble ${type}`;
  bubble.textContent = text;
  msgs.appendChild(bubble);
  msgs.scrollTop = msgs.scrollHeight;
  return bubble;
}

// =============================================
// Kick it off
// =============================================
buildChatWidget();