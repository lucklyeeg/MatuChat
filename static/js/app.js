const log = document.getElementById("log");
const agentList = document.getElementById("agentList");
const typingBox = document.getElementById("typing");
const statusText = document.getElementById("statusText");
const roomBadge = document.getElementById("roomBadge");
const topicLine = document.getElementById("topicLine");
const dramaBar = document.getElementById("dramaBar");
const autoBtn = document.getElementById("autoBtn");
const tempoBtn = document.getElementById("tempoBtn");
const webBtn = document.getElementById("webBtn");
const overlay = document.getElementById("overlay");
const modalTitle = document.getElementById("modalTitle");
const modalBody = document.getElementById("modalBody");
const sayForm = document.getElementById("sayForm");
const sayInput = document.getElementById("sayInput");

const TEMPOS = ["yavas", "normal", "hizli"];
const PROVIDERS = [
  ["anthropic", "Anthropic (Claude)"],
  ["openai", "OpenAI (GPT)"],
  ["gemini", "Google (Gemini)"],
  ["xai", "xAI (Grok)"],
  ["groq", "Groq (Compound, GPT-OSS, Qwen)"],
  ["deepseek", "DeepSeek"],
  ["mistral", "Mistral"],
  ["openrouter", "OpenRouter"],
  ["custom", "Ozel adres (OpenAI uyumlu)"],
];

let since = 0;
let epoch = null;
let lastAuthor = null;
let agents = [];
let bases = {};
let personalities = [];
let rosterSig = "";
let tempo = "normal";
let drama = 1;
let web = true;
let auto = true;
let frozen = false;

function esc(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

function highlight(text) {
  return esc(text).replace(/@([A-Za-z0-9ÇĞİÖŞÜçğıöşü][A-Za-z0-9ÇĞİÖŞÜçğıöşü-]+)/g, '<span class="at">@$1</span>');
}

function findAgent(id) {
  return agents.find((a) => a.id === id);
}

function atBottom() {
  return log.scrollHeight - log.scrollTop - log.clientHeight < 90;
}

function renderRoster() {
  const sig = JSON.stringify(agents.map((a) => [a.id, a.enabled, a.has_key, a.status, a.provider_label, a.personality_label]));
  if (sig === rosterSig) return;
  rosterSig = sig;
  agentList.innerHTML = "";
  agents.forEach((a) => {
    const card = document.createElement("div");
    card.className = "agent" + (a.enabled ? "" : " off");
    card.style.borderColor = a.enabled ? a.color : "#94a9c6";
    const bad = !a.enabled || !a.has_key;
    card.innerHTML = `
      <div class="face">${a.svg}</div>
      <div>
        <div class="who" style="color:${esc(a.color)}">${esc(a.name)}</div>
        <div class="prov">${esc(a.provider_label)}${a.personality_label ? " &middot; " + esc(a.personality_label) : ""}</div>
        <div class="st ${bad ? "bad" : ""}">${esc(a.status)}</div>
      </div>
      <div class="tools">
        <button class="pxbtn tiny ${a.has_key ? "" : "hot"}" data-cfg="${a.id}">${a.has_key ? "AYAR" : "ANAHTAR"}</button>
      </div>`;
    agentList.appendChild(card);
  });
  const live = agents.filter((a) => a.enabled);
  roomBadge.textContent = live.length + " AI";
  document.getElementById("setupHint").classList.toggle("hidden", live.length > 0);
  document.getElementById("memberLine").textContent = live.length
    ? live.map((a) => a.name.toLowerCase()).join(", ") + ", sen"
    : "grupta senden baska kimse yok";
  const faces = document.getElementById("headFaces");
  faces.innerHTML = "";
  live.slice(0, 4).forEach((a) => {
    const cell = document.createElement("span");
    cell.innerHTML = a.svg;
    faces.appendChild(cell);
  });
}

function renderMessage(m) {
  if (!log.querySelector(".daysep")) {
    const sep = document.createElement("div");
    sep.className = "daysep";
    sep.textContent = "BUGUN";
    log.appendChild(sep);
  }
  if (m.kind === "system") {
    lastAuthor = null;
    const el = document.createElement("div");
    el.className = "sys";
    el.textContent = m.text;
    log.appendChild(el);
    return;
  }
  if (m.kind === "whisper") {
    lastAuthor = null;
    const el = document.createElement("div");
    el.className = "wsp";
    el.innerHTML = `<b>${esc(m.name)}</b><br>${esc(m.text)}`;
    log.appendChild(el);
    return;
  }
  const row = document.createElement("div");
  const agent = m.agent_id ? findAgent(m.agent_id) : null;
  const author = m.kind === "user" ? "user" : m.agent_id;
  const chained = author === lastAuthor;
  lastAuthor = author;
  if (m.kind === "user") {
    row.className = "row me" + (chained ? " cont" : "");
    row.innerHTML = `
      <div class="bubble">
        <div class="head"><span>SEN</span><span class="time">${esc(m.ts)}<span class="tick">&#10003;&#10003;</span></span></div>
        <div class="body">${highlight(m.text)}</div>
      </div>`;
  } else {
    row.className = "row" + (chained ? " cont" : "");
    const head = chained
      ? `<div class="head"><span class="time">${esc(m.ts)}</span></div>`
      : `<div class="head">
          <span style="color:${esc(m.color)}">${esc(m.name)}</span>
          <span class="tag">${esc(agent ? agent.provider_label : "")}</span>
          <span class="time">${esc(m.ts)}</span>
        </div>`;
    row.innerHTML = `
      <div class="face">${chained || !agent ? "" : agent.svg}</div>
      <div class="bubble" style="border-left-color:${esc(m.color)}">
        ${head}
        <div class="body">${highlight(m.text)}</div>
      </div>`;
  }
  log.appendChild(row);
}

function renderDrama() {
  dramaBar.innerHTML = "";
  for (let i = 0; i < 3; i++) {
    const cell = document.createElement("i");
    if (i < drama) cell.className = "on" + (drama === 3 ? " max" : "");
    dramaBar.appendChild(cell);
  }
}

async function post(url, body) {
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}),
    });
    let data = {};
    try {
      data = await res.json();
    } catch (e) {}
    return { ok: res.ok && data.ok !== false, ...data };
  } catch (e) {
    statusText.textContent = "sunucuya ulasilamiyor";
    return { ok: false, error: "sunucuya ulasilamiyor" };
  }
}

function clearLog() {
  log.innerHTML = "";
  lastAuthor = null;
  since = 0;
}

let polling = false;
let pollAgain = false;
let pollTimer = null;

async function poll() {
  if (polling) {
    pollAgain = true;
    return;
  }
  polling = true;
  clearTimeout(pollTimer);
  try {
    await pollOnce();
  } finally {
    polling = false;
    if (pollAgain) {
      pollAgain = false;
      poll();
    } else {
      pollTimer = setTimeout(poll, 1200);
    }
  }
}

async function pollOnce() {
  try {
    const res = await fetch("/api/state?since=" + since, { cache: "no-store" });
    const data = await res.json();
    if (data.epoch !== epoch) {
      const first = epoch === null;
      epoch = data.epoch;
      if (!first) {
        clearLog();
        pollAgain = true;
        return;
      }
    }
    agents = data.agents;
    bases = data.bases || bases;
    personalities = data.personalities || personalities;
    renderRoster();
    const stick = atBottom();
    const fresh = data.messages.filter((m) => m.id > since);
    if (fresh.length) {
      fresh.forEach(renderMessage);
      since = fresh[fresh.length - 1].id;
      if (stick) log.scrollTop = log.scrollHeight;
    }
    if (data.typing) {
      const a = findAgent(data.typing);
      typingBox.classList.remove("hidden");
      typingBox.querySelector(".tname").textContent = a ? a.name : "birisi";
      typingBox.querySelector(".tname").style.color = a ? a.color : "";
    } else {
      typingBox.classList.add("hidden");
    }
    auto = data.auto;
    frozen = data.frozen;
    tempo = data.tempo;
    drama = data.drama;
    autoBtn.textContent = "OTONOM: " + (auto ? "ACIK" : "KAPALI");
    autoBtn.classList.toggle("hot", !auto);
    autoBtn.disabled = frozen;
    const freezeBtn = document.getElementById("freezeBtn");
    freezeBtn.textContent = frozen ? "SOHBETE DEVAM" : "SOHBETI DURDUR";
    freezeBtn.classList.toggle("hot", frozen);
    document.querySelector(".stage").classList.toggle("paused", frozen);
    tempoBtn.textContent = "TEMPO: " + tempo.toUpperCase();
    web = data.web !== false;
    webBtn.textContent = "INTERNET: " + (web ? "ACIK" : "KAPALI");
    webBtn.classList.toggle("hot", !web);
    renderDrama();
    topicLine.textContent = data.topic ? "konu: " + data.topic : "konu serbest";
    document.getElementById("groupName").textContent = data.group || "GRUP";
    statusText.textContent = frozen
      ? "sohbet durduruldu, kimse yazmiyor"
      : auto
      ? "grup kendi kendine yaziyor"
      : "otonom akis duraklatildi, sadece sen yazinca cevap verirler";
  } catch (e) {
    statusText.textContent = "baglanti yok, tekrar deneniyor";
  }
}

function openModal(title, html) {
  modalTitle.textContent = title;
  modalBody.innerHTML = html;
  overlay.classList.remove("hidden");
}

function closeModal() {
  overlay.classList.add("hidden");
  modalBody.innerHTML = "";
}

function agentOptions(list, selected) {
  return list
    .map((a) => `<option value="${a.id}" ${a.id === selected ? "selected" : ""}>${esc(a.name)}</option>`)
    .join("");
}

function openSettings(focusId) {
  const rows = agents
    .map(
      (a) => `
    <div class="cfg" data-id="${a.id}">
      <div class="cfg-head">
        <span class="face">${a.svg}</span>
        <b style="color:${esc(a.color)}">${esc(a.name)}</b>
        <button class="pxbtn tiny ${a.enabled ? "" : "hot"}" data-act="toggle">
          ${a.enabled ? "GRUPTAN CIKAR" : "GRUBA AL"}
        </button>
      </div>
      <div class="cfg-grid">
        <div class="field">
          <label>SAGLAYICI</label>
          <select data-f="provider">
            ${PROVIDERS.map(([v, t]) => `<option value="${v}" ${v === a.provider ? "selected" : ""}>${t}</option>`).join("")}
          </select>
        </div>
        <div class="field">
          <label>MODEL</label>
          <input data-f="model" list="ml-${a.id}" value="${esc(a.model)}">
          <datalist id="ml-${a.id}"></datalist>
        </div>
      </div>
      <div class="cfg-models hidden"></div>
      <div class="field">
        <label>API ADRESI</label>
        <input data-f="base_url" value="${esc(a.base_url || "")}" placeholder="${esc(a.default_base || "kendi adresini yaz")}">
        <span class="hint">bos birakirsan varsayilan adres kullanilir</span>
      </div>
      <div class="field">
        <label>KISILIK</label>
        <select data-f="personality">
          ${personalities.filter((k) => !k.only || !k.only.length || k.only.includes(a.id)).map((k) => `<option value="${esc(k.id)}" ${k.id === a.personality ? "selected" : ""}>${esc(k.label)}</option>`).join("")}
        </select>
        <span class="hint">davranisini ve yazma stilini belirler</span>
      </div>
      <div class="field">
        <label>API ANAHTARI</label>
        <input data-f="api_key" type="password" placeholder="${a.has_key ? "kayitli, degistirmek icin yaz" : "anahtari buraya yapistir"}">
      </div>
      <div class="probe hidden"></div>
      <div class="cfg-actions">
        <button class="pxbtn tiny" data-act="models">MODELLERI GETIR</button>
        <button class="pxbtn tiny" data-act="test">TEST ET</button>
        <button class="pxbtn tiny send" data-act="save">KAYDET</button>
      </div>
    </div>`
    )
    .join("");

  openModal("API AYARLARI", rows +
    '<div class="hint pad">Girdigin ayarlar proje klasorundeki <b>ayarlar.json</b> ' +
    'dosyasina kaydedilir, boylece bir dahaki acilista tekrar girmen gerekmez. ' +
    'Dosya senin makinende durur, hicbir yere gonderilmez. Anahtarlari silmek ' +
    'istersen bu dosyayi sil.</div>');

  modalBody.querySelectorAll(".cfg").forEach((box) => {
    const id = box.dataset.id;
    const probe = box.querySelector(".probe");
    const val = (f) => box.querySelector(`[data-f="${f}"]`).value;
    const payload = (join) => {
      const body = {
        provider: val("provider"),
        model: val("model"),
        base_url: val("base_url"),
        personality: val("personality"),
        api_key: val("api_key"),
      };
      if (join) body.enabled = true;
      return body;
    };

    box.querySelector('[data-f="provider"]').onchange = (e) => {
      const base = box.querySelector('[data-f="base_url"]');
      base.placeholder = (bases && bases[e.target.value]) || "kendi adresini yaz";
    };

    box.querySelector('[data-act="models"]').onclick = async (e) => {
      const btn = e.currentTarget;
      const shelf = box.querySelector(".cfg-models");
      btn.disabled = true;
      probe.className = "probe";
      probe.textContent = "model listesi aliniyor...";
      await post("/api/agent/" + id, payload());
      try {
        const res = await fetch("/api/agent/" + id + "/models", { method: "POST" });
        const data = await res.json();
        probe.className = "probe " + (data.ok ? "good" : "bad");
        probe.textContent = data.ok ? data.detail : "olmadi: " + data.detail;
        const list = box.querySelector("datalist");
        list.innerHTML = data.models.map((m) => `<option value="${esc(m)}">`).join("");
        shelf.innerHTML = data.models
          .map((m) => `<button class="chip" type="button">${esc(m)}</button>`)
          .join("");
        shelf.classList.toggle("hidden", !data.models.length);
        shelf.querySelectorAll(".chip").forEach((chip) => {
          chip.onclick = () => {
            box.querySelector('[data-f="model"]').value = chip.textContent;
            shelf.querySelectorAll(".chip").forEach((c) => c.classList.remove("on"));
            chip.classList.add("on");
          };
        });
      } catch (err) {
        probe.className = "probe bad";
        probe.textContent = "sunucuya ulasilamadi";
      }
      btn.disabled = false;
    };

    const toggleBtn = box.querySelector('[data-act="toggle"]');
    const showEnabled = (on) => {
      toggleBtn.textContent = on ? "GRUPTAN CIKAR" : "GRUBA AL";
      toggleBtn.classList.toggle("hot", !on);
    };

    box.querySelector('[data-act="save"]').onclick = async () => {
      const res = await post("/api/agent/" + id, payload(true));
      rosterSig = "";
      probe.className = "probe " + (res.ok ? "" : "bad");
      probe.textContent = !res.ok
        ? "kaydedilemedi: " + (res.error || "bilinmeyen hata")
        : res.enabled
        ? "kaydedildi"
        : "kaydedildi ama anahtar olmadan gruba katilamaz";
      if (res.ok) {
        showEnabled(res.enabled);
        const keyInput = box.querySelector('[data-f="api_key"]');
        if (keyInput.value.trim()) keyInput.placeholder = "kayitli, degistirmek icin yaz";
        keyInput.value = "";
      }
      poll();
    };

    box.querySelector('[data-act="test"]').onclick = async (e) => {
      const btn = e.currentTarget;
      btn.disabled = true;
      probe.className = "probe";
      probe.textContent = "deneniyor...";
      await post("/api/agent/" + id, payload());
      try {
        const res = await fetch("/api/agent/" + id + "/test", { method: "POST" });
        const data = await res.json();
        probe.className = "probe " + (data.ok ? "good" : "bad");
        probe.textContent = data.ok
          ? "baglanti tamam, model cevap verdi: " + data.detail
          : "olmadi: " + data.detail;
      } catch (err) {
        probe.className = "probe bad";
        probe.textContent = "sunucuya ulasilamadi";
      }
      btn.disabled = false;
      rosterSig = "";
      poll();
    };

    toggleBtn.onclick = async () => {
      const a = findAgent(id);
      const want = !(a && a.enabled);
      const res = await post("/api/agent/" + id, { enabled: want });
      rosterSig = "";
      if (!res.ok) {
        probe.className = "probe bad";
        probe.textContent = "olmadi: " + (res.error || "bilinmeyen hata");
      } else if (want && !res.enabled) {
        probe.className = "probe bad";
        probe.textContent = "once API anahtarini girip KAYDET'e bas";
      } else {
        probe.className = "probe hidden";
      }
      if (a && res.ok) a.enabled = res.enabled;
      showEnabled(res.ok ? res.enabled : a && a.enabled);
      poll();
    };
  });

  if (focusId) {
    const target = modalBody.querySelector(`.cfg[data-id="${focusId}"]`);
    if (target) target.scrollIntoView({ block: "start" });
  }
}

function openFitne() {
  const live = agents.filter((x) => x.enabled);
  if (!live.length) {
    openModal("FITNE", '<div class="sys">Once odaya en az bir AI al.</div>');
    return;
  }
  openModal("FITNE AT", `
    <div class="field">
      <label>KIME OZELDEN</label>
      <select id="fTarget">${agentOptions(live, live[0].id)}</select>
    </div>
    <div class="field">
      <label>MESAJ</label>
      <textarea id="fText" maxlength="300" placeholder="LLAMA senin arkandan konusuyormus, haberin var mi"></textarea>
      <span class="hint">grup bunu gormez, sadece o kisi etkilenir</span>
    </div>
    <div class="probe hidden" id="fNote"></div>
    <div class="modal-actions">
      <button class="pxbtn hot" id="fSend">GONDER</button>
    </div>`);
  const input = document.getElementById("fText");
  const note = document.getElementById("fNote");
  const btn = document.getElementById("fSend");
  input.focus();
  btn.onclick = async () => {
    const text = input.value.trim();
    if (!text) {
      note.className = "probe bad";
      note.textContent = "once bir mesaj yaz";
      input.focus();
      return;
    }
    btn.disabled = true;
    const res = await post("/api/whisper", { agent_id: document.getElementById("fTarget").value, text });
    btn.disabled = false;
    if (!res.ok) {
      note.className = "probe bad";
      note.textContent = "gonderilemedi: " + (res.error || "bilinmeyen hata");
      return;
    }
    closeModal();
    poll();
  };
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) btn.click();
  });
}

function openTopic() {
  openModal("KONU AC", `
    <div class="field">
      <label>ODANIN KONUSU</label>
      <input id="tText" placeholder="ornek: ananasli pizza suc mu">
      <span class="hint">bos birakip kaydedersen konu serbest kalir</span>
    </div>
    <div class="modal-actions">
      <button class="pxbtn send" id="tSend">AC</button>
    </div>`);
  document.getElementById("tSend").onclick = async () => {
    await post("/api/topic", { topic: document.getElementById("tText").value });
    closeModal();
    poll();
  };
}

function openPoke() {
  const live = agents.filter((x) => x.enabled);
  if (!live.length) {
    openModal("DURT", '<div class="sys">Odada kimse yok.</div>');
    return;
  }
  openModal("BIRINI DURT", `
    <div class="field">
      <label>SIRAYI KIME VERELIM</label>
      <select id="pTarget">${agentOptions(live, live[0].id)}</select>
    </div>
    <div class="modal-actions">
      <button class="pxbtn send" id="pSend">DURT</button>
    </div>`);
  document.getElementById("pSend").onclick = async () => {
    await post("/api/poke", { agent_id: document.getElementById("pTarget").value });
    closeModal();
    poll();
  };
}

agentList.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-cfg]");
  if (btn) openSettings(btn.dataset.cfg);
});

document.getElementById("modalClose").onclick = closeModal;
overlay.addEventListener("click", (e) => {
  if (e.target === overlay) closeModal();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeModal();
});

document.getElementById("freezeBtn").onclick = async () => {
  await post("/api/control", { frozen: !frozen });
  poll();
};

autoBtn.onclick = async () => {
  await post("/api/control", { auto: !auto });
  poll();
};

webBtn.onclick = async () => {
  await post("/api/control", { web: !web });
  poll();
};

tempoBtn.onclick = async () => {
  const next = TEMPOS[(TEMPOS.indexOf(tempo) + 1) % TEMPOS.length];
  await post("/api/control", { tempo: next });
  poll();
};

document.querySelectorAll("[data-drama]").forEach((btn) => {
  btn.onclick = async () => {
    const next = Math.max(0, Math.min(3, drama + Number(btn.dataset.drama)));
    await post("/api/control", { drama: next });
    poll();
  };
});

document.getElementById("resetBtn").onclick = async () => {
  const res = await post("/api/reset");
  if (!res.ok) return;
  poll();
};

document.getElementById("settingsBtn").onclick = () => openSettings();
document.getElementById("fitneBtn").onclick = openFitne;
document.getElementById("topicBtn").onclick = openTopic;
document.getElementById("pokeBtn").onclick = openPoke;

sayForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = sayInput.value.trim();
  if (!text) return;
  sayInput.value = "";
  await post("/api/say", { text });
  poll();
});

poll();
