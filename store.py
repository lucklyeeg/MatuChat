import json
import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "ayarlar.json")

AGENT_FIELDS = ("provider", "model", "base_url", "personality", "api_key", "enabled")
ROOM_FIELDS = ("auto", "tempo", "drama", "web")


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
    try:
        fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".ayarlar-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2)
            _lock_down(tmp)
            os.replace(tmp, PATH)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
    except (IOError, OSError, ValueError, TypeError):
        return False
    return True


def _lock_down(path):
    try:
        os.chmod(path, 0o600)
    except (OSError, NotImplementedError):
        pass
