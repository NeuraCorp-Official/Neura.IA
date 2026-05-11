const API = 'https://neura-api.onrender.com'; // ← troca pela URL do teu serviço no Render

const input    = document.getElementById('textInput');
const btn      = document.getElementById('btnEnviar');
const chat     = document.getElementById('chat');
const statMsgs = document.getElementById('stat-msgs');

let msgCount = 0;

// ── Teclado
input.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); enviar(); }
  if (e.key === 'Escape') input.value = '';
});

// ── Criar mensagem
function criarMsg(texto, tipo) {
  const wrap = document.createElement('div');
  wrap.className = tipo === 'user' ? 'msg-user' : tipo === 'neura' ? 'msg-neura' : 'msg-system';

  if (tipo === 'system') {
    wrap.textContent = texto;
  } else {
    wrap.innerHTML = `
      <div class="msg-label">${tipo === 'user' ? 'VOCÊ' : 'NEURA'}</div>
      <div class="msg-text">${texto}</div>
    `;
  }

  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
  return wrap;
}

function mostrarTyping() {
  const div = document.createElement('div');
  div.className = 'msg-neura';
  div.id = 'typing';
  div.innerHTML = `
    <div class="msg-label">NEURA</div>
    <div class="msg-text">
      <div class="typing-dots"><span></span><span></span><span></span></div>
    </div>
  `;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function removerTyping() {
  const el = document.getElementById('typing');
  if (el) el.remove();
}

// ── Enviar mensagem
async function enviar() {
  const texto = input.value.trim();
  if (!texto) return;

  criarMsg(texto, 'user');
  input.value = '';
  input.disabled = true;
  btn.disabled = true;

  mostrarTyping();

  try {
    const res = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mensagem: texto })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    removerTyping();
    criarMsg(data.resposta, 'neura');

    msgCount++;
    statMsgs.textContent = msgCount;

    // Atualiza memórias após cada resposta
    setTimeout(carregarMemorias, 1500);

  } catch (err) {
    removerTyping();
    criarMsg('// Neura offline ou sem conexão', 'system');
    console.error(err);

  } finally {
    input.disabled = false;
    btn.disabled = false;
    input.focus();
  }
}

// ── Limpar chat
function limparChat() {
  chat.innerHTML = '';
  criarMsg('// chat limpo · nova conversa iniciada', 'system');
  msgCount = 0;
  statMsgs.textContent = 0;
}

// ── Carregar memórias importantes da sessão atual
async function carregarMemorias() {
  try {
    const res  = await fetch(`${API}/sessions`);
    const data = await res.json();
    if (!data.length) return;

    const sessaoAtual = data[0]; // mais recente
    const resMem = await fetch(`${API}/sessions/${sessaoAtual.id}/memories`);
    const mems   = await resMem.json();

    const list = document.getElementById('memories-list');

    if (!mems.length) {
      list.innerHTML = '<p class="mem-empty">// nenhuma memória registrada ainda</p>';
      return;
    }

    list.innerHTML = mems.map(m => `
      <div class="mem-item">→ ${m.texto}</div>
    `).join('');

  } catch (err) {
    console.error('Erro ao carregar memórias:', err);
  }
}

// ── Carregar sessões recentes
async function carregarSessoes() {
  const list = document.getElementById('sessions-list');

  try {
    const res  = await fetch(`${API}/sessions`);
    const data = await res.json();

    if (!data.length) {
      list.innerHTML = '<p class="mem-empty">// nenhuma sessão anterior</p>';
      return;
    }

    list.innerHTML = data.slice(0, 5).map(s => {
      const hora = s.criado_em
        ? new Date(s.criado_em).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
        : '--:--';
      return `
        <div class="session-entry">
          <div class="session-time">${hora} · ${s.data || ''}</div>
          <div class="session-count">${s.total_msgs} mensagens</div>
        </div>
      `;
    }).join('');

  } catch (err) {
    list.innerHTML = '<p class="mem-empty">// erro ao carregar</p>';
  }
}

// ── Init
carregarSessoes();
