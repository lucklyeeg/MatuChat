import os
import socket
import sys
import threading
import webbrowser

from flask import Flask, jsonify, render_template, request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import engine

app = Flask(__name__)
room = engine.Room()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/state")
def state():
    try:
        since = int(request.args.get("since", 0))
    except ValueError:
        since = 0
    return jsonify(room.snapshot(since))


@app.post("/api/say")
def say():
    data = request.get_json(silent=True) or {}
    room.user_says(str(data.get("text", "")))
    return jsonify({"ok": True})


@app.post("/api/whisper")
def whisper():
    data = request.get_json(silent=True) or {}
    error = room.whisper(str(data.get("agent_id", "")), str(data.get("text", "")))
    if error:
        return jsonify({"ok": False, "error": error}), 400
    return jsonify({"ok": True})


@app.post("/api/poke")
def poke():
    data = request.get_json(silent=True) or {}
    room.poke(str(data.get("agent_id", "")))
    return jsonify({"ok": True})


@app.post("/api/topic")
def topic():
    data = request.get_json(silent=True) or {}
    room.set_topic(str(data.get("topic", "")))
    return jsonify({"ok": True})


@app.post("/api/control")
def control():
    room.control(request.get_json(silent=True) or {})
    return jsonify({"ok": True})


@app.post("/api/agent/<agent_id>")
def agent(agent_id):
    updated = room.configure(agent_id, request.get_json(silent=True) or {})
    if not updated:
        return jsonify({"ok": False, "error": "bulunamadi"}), 404
    return jsonify({"ok": True, "status": updated["status"], "enabled": updated["enabled"]})


@app.after_request
def no_cache(resp):
    if request.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    return resp


@app.post("/api/agent/<agent_id>/test")
def agent_test(agent_id):
    result = room.test_agent(agent_id)
    if result is None:
        return jsonify({"ok": False, "detail": "bulunamadi"}), 404
    return jsonify(result)


@app.post("/api/agent/<agent_id>/models")
def agent_models(agent_id):
    result = room.model_list(agent_id)
    if result is None:
        return jsonify({"ok": False, "detail": "bulunamadi", "models": []}), 404
    return jsonify(result)


@app.post("/api/reset")
def reset():
    room.reset()
    return jsonify({"ok": True})


def pick_port(start):
    for candidate in range(start, start + 12):
        probe = socket.socket()
        try:
            probe.bind(("127.0.0.1", candidate))
            return candidate
        except OSError:
            continue
        finally:
            probe.close()
    return start


if __name__ == "__main__":
    port = pick_port(int(os.environ.get("PORT", 5000)))
    url = "http://127.0.0.1:%d" % port
    if os.environ.get("NO_BROWSER", "") != "1":
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    hazir = [a["name"] for a in room.agents.values() if a["enabled"]]
    print("")
    print("  Bu Flask uygulamasi lucklyeeg tarafindan")
    print("  Batu Matu'nun videosu icin yapilmistir.")
    print("")
    print("  MatuChat calisiyor ->  %s" % url)
    if hazir:
        print("  Anahtari bulunan karakterler: " + ", ".join(hazir))
    else:
        print("  Henuz anahtar yok. Tarayicida API AYARLARI'ndan gir.")
    print("  Durdurmak icin bu pencerede Ctrl+C")
    print("")
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False, threaded=True)
