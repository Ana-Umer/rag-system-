/* ─── State ─────────────────────────────────────────────────────── */
let docCount   = 0;
let chunkCount = 0;
let isLoading  = false;

/* ─── Auto-resize textarea ──────────────────────────────────────── */
function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 140) + 'px';
}

/* ─── Toast ─────────────────────────────────────────────────────── */
function showToast(msg, type = 'success') {
  const t = document.getElementById('toast');
  const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
  t.innerHTML = `<span>${icon}</span><span>${msg}</span>`;
  t.className = `show ${type}`;
  clearTimeout(t._t);
  t._t = setTimeout(() => { t.className = ''; }, 3500);
}

/* ─── Update stats ──────────────────────────────────────────────── */
function updateStats(newChunks = 0) {
  docCount++;
  chunkCount += newChunks;
  document.getElementById('doc-count').textContent   = docCount;
  document.getElementById('chunk-count').textContent = chunkCount;
}

/* ─── Ingest plain text ─────────────────────────────────────────── */
async function ingestText() {
  const text   = document.getElementById('paste-text').value.trim();
  const source = document.getElementById('source-name').value.trim() || 'user_input';
  if (!text) { showToast('Please paste some text first.', 'error'); return; }

  const btn = document.getElementById('ingest-text-btn');
  btn.disabled    = true;
  btn.textContent = '⏳ Ingesting…';

  try {
    const res  = await fetch('/ingest/text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, source }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Ingestion failed');
    updateStats(data.chunks_added);
    document.getElementById('paste-text').value  = '';
    document.getElementById('source-name').value = '';
    showToast(`Added ${data.chunks_added} chunks from "${source}".`);
  } catch (e) {
    showToast(e.message, 'error');
  } finally {
    btn.disabled    = false;
    btn.textContent = '➕ Add to Knowledge Base';
  }
}

/* ─── File upload (drop zone) ───────────────────────────────────── */
function initDropZone() {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');

  dropZone.addEventListener('dragover', e => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) uploadFile(file);
  });
  dropZone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) uploadFile(fileInput.files[0]);
  });
}

async function uploadFile(file) {
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!['.txt', '.pdf'].includes(ext)) {
    showToast('Only .txt and .pdf files are supported.', 'error');
    return;
  }

  document.querySelector('#drop-zone .dz-title').textContent = '⏳ Uploading…';
  const fd = new FormData();
  fd.append('file', file);

  try {
    const res  = await fetch('/ingest/file', { method: 'POST', body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Upload failed');
    updateStats(data.chunks_added);
    const statusEl = document.getElementById('file-status');
    document.getElementById('file-status-text').textContent =
      `"${file.name}" — ${data.chunks_added} chunks added`;
    statusEl.style.display = 'flex';
    showToast(`"${file.name}" ingested (${data.chunks_added} chunks).`);
  } catch (e) {
    showToast(e.message, 'error');
  } finally {
    document.querySelector('#drop-zone .dz-title').textContent = 'Drop file here';
    document.getElementById('file-input').value = '';
  }
}

/* ─── Reset knowledge base ──────────────────────────────────────── */
async function resetKB() {
  if (!confirm('This will permanently delete all ingested documents. Continue?')) return;
  try {
    const res = await fetch('/reset', { method: 'POST' });
    if (!res.ok) throw new Error('Reset failed');
    docCount = 0; chunkCount = 0;
    document.getElementById('doc-count').textContent   = '0';
    document.getElementById('chunk-count').textContent = '0';
    document.getElementById('file-status').style.display = 'none';
    showToast('Knowledge base cleared.', 'info');
  } catch (e) {
    showToast(e.message, 'error');
  }
}

/* ─── Chat helpers ──────────────────────────────────────────────── */
function setQuestion(q) {
  const inp = document.getElementById('question-input');
  inp.value = q;
  autoResize(inp);
  inp.focus();
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendQuestion();
  }
}

function hideWelcome() {
  const w = document.getElementById('welcome-screen');
  if (w) w.remove();
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>');
}

function toggleChunks(el) {
  const box  = el.nextElementSibling;
  const open = box.style.display === 'block';
  box.style.display = open ? 'none' : 'block';
  el.textContent = el.textContent.replace(
    open ? '▼' : '▶',
    open ? '▶' : '▼'
  ).replace(
    open ? 'Hide' : 'Show',
    open ? 'Show' : 'Hide'
  );
}

function appendMessage(role, content, sources = [], chunks = []) {
  hideWelcome();
  const container = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = `message ${role}`;

  const avatarEmoji = role === 'ai' ? '🧠' : '👤';
  const avatarClass = role === 'ai' ? 'ai' : 'user';

  const sourcesHtml = sources.length
    ? `<div class="sources">${sources.map(s => `<span class="source-tag">📎 ${s}</span>`).join('')}</div>`
    : '';

  const chunksHtml = chunks.length
    ? `<div class="chunks-toggle" onclick="toggleChunks(this)">▶ Show retrieved context (${chunks.length} chunks)</div>
       <div class="chunks-box">${escapeHtml(chunks.map((c, i) => `[Chunk ${i + 1}]\n${c}`).join('\n\n'))}</div>`
    : '';

  div.innerHTML = `
    <div class="avatar ${avatarClass}">${avatarEmoji}</div>
    <div>
      <div class="bubble">${escapeHtml(content)}${sourcesHtml}</div>
      ${chunksHtml}
    </div>`;

  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function appendTyping() {
  hideWelcome();
  const container = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'message ai';
  div.id = 'typing-bubble';
  div.innerHTML = `
    <div class="avatar ai">🧠</div>
    <div class="bubble">
      <div class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    </div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

/* ─── Send question ─────────────────────────────────────────────── */
async function sendQuestion() {
  if (isLoading) return;
  const input    = document.getElementById('question-input');
  const question = input.value.trim();
  if (!question) return;

  input.value = '';
  autoResize(input);
  isLoading = true;
  document.getElementById('send-btn').disabled          = true;
  document.getElementById('header-status').textContent  = 'Thinking…';

  appendMessage('user', question);
  const typingBubble = appendTyping();

  try {
    const res  = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    typingBubble.remove();
    if (!res.ok) throw new Error(data.detail || 'Request failed');
    appendMessage('ai', data.answer, data.sources || [], data.chunks || []);
  } catch (e) {
    typingBubble.remove();
    appendMessage('ai', `⚠️ Error: ${e.message}`);
  } finally {
    isLoading = false;
    document.getElementById('send-btn').disabled         = false;
    document.getElementById('header-status').textContent = 'Ready';
  }
}

/* ─── Init ──────────────────────────────────────────────────────── */
window.addEventListener('load', async () => {
  initDropZone();

  try {
    const res  = await fetch('/health');
    const data = await res.json();
    if (data.has_documents) {
      showToast('Existing knowledge base loaded.', 'info');
      document.getElementById('doc-count').textContent   = '?';
      document.getElementById('chunk-count').textContent = '?';
    }
  } catch (_) {}
});
