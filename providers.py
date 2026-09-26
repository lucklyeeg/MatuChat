import requests

TIMEOUT = 40

OPENAI_BASES = {
    "openai": "https://api.openai.com/v1",
    "xai": "https://api.x.ai/v1",
    "groq": "https://api.groq.com/openai/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "mistral": "https://api.mistral.ai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
}

DEFAULT_BASES = dict(OPENAI_BASES)
DEFAULT_BASES["anthropic"] = "https://api.anthropic.com"
DEFAULT_BASES["gemini"] = "https://generativelanguage.googleapis.com"
DEFAULT_BASES["custom"] = ""


def base_for(agent):
    given = (agent.get("base_url") or "").strip().rstrip("/")
    return given or DEFAULT_BASES.get(agent.get("provider"), "")


class ProviderError(Exception):
    pass


def _post(url, headers, payload):
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
    except requests.Timeout:
        raise ProviderError("zaman asimi")
    except requests.RequestException:
        raise ProviderError("baglanti kurulamadi")
    if resp.status_code >= 400:
        snippet = " ".join(resp.text.split())[:140]
        raise ProviderError("HTTP %d %s" % (resp.status_code, snippet))
    try:
        return resp.json()
    except ValueError:
        raise ProviderError("yanit okunamadi")


NOT_CHAT = (
    "whisper",
    "tts",
    "orpheus",
    "guard",
    "embed",
    "rerank",
    "moderation",
    "image",
    "vision-preview",
    "dall-e",
    "sora",
    "playai",
    "aqa",
)


def _chat_only(names):
    kept = [n for n in names if not any(bad in n.lower() for bad in NOT_CHAT)]
    return kept or names


def _get(url, headers):
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
    except requests.Timeout:
        raise ProviderError("zaman asimi")
    except requests.RequestException:
        raise ProviderError("baglanti kurulamadi")
    if resp.status_code >= 400:
        snippet = " ".join(resp.text.split())[:140]
        raise ProviderError("HTTP %d %s" % (resp.status_code, snippet))
    try:
        return resp.json()
    except ValueError:
        raise ProviderError("yanit okunamadi")


def list_models(agent):
    if not agent.get("api_key"):
        raise ProviderError("API anahtari yok")
    base = base_for(agent)
    if not base:
        raise ProviderError("API adresi bos")
    provider = agent["provider"]
    if provider == "anthropic":
        data = _get(
            base + "/v1/models",
            {"x-api-key": agent["api_key"], "anthropic-version": "2023-06-01"},
        )
        names = [m.get("id", "") for m in data.get("data") or []]
    elif provider == "gemini":
        data = _get(base + "/v1beta/models?key=" + agent["api_key"], {})
        names = []
        for m in data.get("models") or []:
            methods = m.get("supportedGenerationMethods")
            if methods and "generateContent" not in methods:
                continue
            names.append(m.get("name", "").split("/")[-1])
    else:
        data = _get(base + "/models", {"Authorization": "Bearer " + agent["api_key"]})
        rows = data.get("data")
        if not isinstance(rows, list):
            rows = data.get("models") or []
        names = [(m.get("id") or m.get("name") or "") if isinstance(m, dict) else str(m) for m in rows]
    names = sorted({n for n in names if n})
    if not names:
        raise ProviderError("liste bos dondu")
    return _chat_only(names)


def _anthropic(agent, system, user_text, base):
    url = base + "/v1/messages"
    headers = {
        "x-api-key": agent["api_key"],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    tools = _anthropic_web_tools(agent["model"]) if agent.get("web") else []
    messages = [{"role": "user", "content": user_text}]
    chunks = []
    for _ in range(4):
        payload = {
            "model": agent["model"],
            "max_tokens": 800,
            "temperature": agent["temperature"],
            "system": system,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools
        try:
            data = _post(url, headers, payload)
        except ProviderError as err:
            if not tools or "HTTP 400" not in str(err):
                raise
            tools = []
            continue
        blocks = data.get("content", [])
        chunks += [b.get("text", "") for b in blocks if b.get("type") == "text"]
        if data.get("stop_reason") != "pause_turn":
            break
        messages = messages + [{"role": "assistant", "content": blocks}]
    return "".join(chunks)


ANTHROPIC_WEB_NEW = (
    "opus-5", "opus-4-8", "opus-4-7", "opus-4-6",
    "sonnet-5", "sonnet-4-6", "fable-5", "mythos-5",
)


def _anthropic_web_tools(model):
    low = (model or "").lower()
    fresh = any(tag in low for tag in ANTHROPIC_WEB_NEW)
    kind = "web_search_20260209" if fresh else "web_search_20250305"
    return [{"type": kind, "name": "web_search"}]


def _web_fields(agent):
    provider = agent.get("provider")
    model = (agent.get("model") or "").lower()
    if provider == "groq":
        if model.startswith("groq/compound"):
            return {}
        if "gpt-oss" in model:
            return {"tools": [{"type": "browser_search"}]}
        return {}
    if provider == "openrouter":
        return {"plugins": [{"id": "web"}]}
    if provider == "xai":
        return {"search_parameters": {"mode": "auto"}}
    if provider == "openai":
        return {"web_search_options": {}}
    return {}


NEW_OPENAI = ("gpt-5", "o1", "o3", "o4")


def _wants_completion_tokens(agent):
    if agent.get("provider") != "openai":
        return False
    low = (agent.get("model") or "").lower()
    return any(low.startswith(tag) for tag in NEW_OPENAI)


REASONERS = ("qwen", "deepseek", "gpt-oss", "-r1", "reason", "thinking")


def _is_reasoner(model):
    low = (model or "").lower()
    return any(tag in low for tag in REASONERS)


def _openai_compatible(agent, system, user_text, base):
    url = base.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": "Bearer " + agent["api_key"],
        "Content-Type": "application/json",
    }
    payload = {
        "model": agent["model"],
        "temperature": agent["temperature"],
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_text},
        ],
    }
    if _wants_completion_tokens(agent):
        payload["max_completion_tokens"] = 800
    else:
        payload["max_tokens"] = 800

    extras = []
    if agent["provider"] == "groq" and _is_reasoner(agent["model"]):
        payload["reasoning_format"] = "hidden"
        extras.append("reasoning_format")
    if agent.get("web"):
        for key, value in _web_fields(agent).items():
            payload[key] = value
            extras.append(key)

    def swap_tokens():
        if "max_tokens" not in payload:
            return False
        payload["max_completion_tokens"] = payload.pop("max_tokens")
        return True

    def drop_extras():
        hit = False
        for key in extras:
            hit = payload.pop(key, None) is not None or hit
        return hit

    data = None
    while True:
        try:
            data = _post(url, headers, payload)
            break
        except ProviderError as err:
            note = str(err)
            if "HTTP 400" not in note:
                raise
            if "max_tokens" in note and swap_tokens():
                continue
            if drop_extras():
                continue
            if swap_tokens():
                continue
            raise
    choices = data.get("choices") or []
    if not choices:
        raise ProviderError("bos yanit")
    return choices[0].get("message", {}).get("content", "") or ""


def _gemini(agent, system, user_text, base):
    url = "%s/v1beta/models/%s:generateContent?key=%s" % (
        base,
        agent["model"],
        agent["api_key"],
    )
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "generationConfig": {
            "temperature": agent["temperature"],
            "maxOutputTokens": 800,
        },
    }
    if agent.get("web"):
        payload["tools"] = [{"google_search": {}}]
    try:
        data = _post(url, {"Content-Type": "application/json"}, payload)
    except ProviderError as err:
        if "tools" not in payload or "HTTP 400" not in str(err):
            raise
        payload.pop("tools")
        data = _post(url, {"Content-Type": "application/json"}, payload)
    cands = data.get("candidates") or []
    if not cands:
        raise ProviderError("bos yanit")
    parts = cands[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts if not p.get("thought"))


def generate(agent, system, user_text):
    provider = agent["provider"]
    if not agent.get("api_key"):
        raise ProviderError("API anahtari yok")
    base = base_for(agent)
    if not base:
        raise ProviderError("API adresi bos")
    if provider == "anthropic":
        return _anthropic(agent, system, user_text, base)
    if provider == "gemini":
        return _gemini(agent, system, user_text, base)
    if provider in OPENAI_BASES or provider == "custom":
        return _openai_compatible(agent, system, user_text, base)
    raise ProviderError("bilinmeyen saglayici")


def probe(agent):
    text = generate(
        agent,
        "Tek kelimelik bir baglanti testine cevap veriyorsun.",
        "Sadece TAMAM yaz.",
    )
    return " ".join((text or "").split())[:40] or "bos yanit"
