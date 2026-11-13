import json
import os
import sys
import tempfile

if getattr(sys, "frozen", False):
    HERE = os.path.join(
        os.environ.get("APPDATA") or os.path.expanduser("~"),
        "MatuChat",
    )
    try:
        os.makedirs(HERE, exist_ok=True)
    except OSError:
        pass
else:
    HERE = os.path.dirname(os.path.abspath(__file__))

PATH = os.path.join(HERE, "ayarlar.json")
HIST_PATH = os.path.join(HERE, "gecmis.json")

AGENT_FIELDS = (
    "provider",
    "model",
    "base_url",
    "personality",
    "custom_prompt",
    "api_key",
    "enabled",
)
ROOM_FIELDS = ("auto", "tempo", "drama", "web", "sound", "group_name", "user_name")
MSG_FIELDS = (
    "id",
    "kind",
    "agent_id",
    "name",
    "color",
    "text",
    "ts",
    "reply_to",
    "reactions",
    "options",
)


def _write_json(target, prefix, payload):
    try:
        fd, tmp = tempfile.mkstemp(dir=HERE, prefix=prefix, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2)
            _lock_down(tmp)
            os.replace(tmp, target)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
    except (IOError, OSError, ValueError, TypeError):
        return False
    return True


def load():
    try:
        with open(PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (IOError, OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    agents = data.get("agents")
    room = data.get("room")
    return {
        "agents": agents if isinstance(agents, dict) else {},
        "room": room if isinstance(room, dict) else {},
    }


def save(agents, room):
    payload = {
        "agents": {
            aid: {f: a[f] for f in AGENT_FIELDS if f in a}
            for aid, a in agents.items()
        },
        "room": {f: room[f] for f in ROOM_FIELDS if f in room},
    }
    return _write_json(PATH, ".ayarlar-", payload)


def load_history():
    try:
        with open(HIST_PATH, "r", encoding="utf-8") as fh:
            rows = json.load(fh)
    except (IOError, OSError, ValueError):
        return []
    if not isinstance(rows, list):
        return []
    out = []
    for item in rows[-120:]:
        if isinstance(item, dict) and isinstance(item.get("id"), int) and item.get("kind"):
            out.append(item)
    return out


def save_history(messages):
    trimmed = []
    for msg in messages[-120:]:
        row = {f: msg[f] for f in MSG_FIELDS if f in msg}
        if msg.get("image") and not row.get("text"):
            row["text"] = "[fotoğraf]"
        trimmed.append(row)
    return _write_json(HIST_PATH, ".gecmis-", trimmed)


def _lock_down(path):
    try:
        os.chmod(path, 0o600)
    except (OSError, NotImplementedError):
        pass
