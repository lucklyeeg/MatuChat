import os
import socket
import sys
import threading
import time
import webbrowser

from flask import Flask, Response, jsonify, render_template, request

if getattr(sys, "frozen", False):
    BUNDLE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
else:
    BUNDLE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BUNDLE)

import engine

app = Flask(
    __name__,
    template_folder=os.path.join(BUNDLE, "templates"),
    static_folder=os.path.join(BUNDLE, "static"),
)
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
    room.user_says(
        str(data.get("text", "")),
        data.get("reply_to"),
        data.get("image"),
    )
    return jsonify({"ok": True})


@app.post("/api/react")
def react():
    data = request.get_json(silent=True) or {}
    ok = room.react(data.get("msg_id"), str(data.get("emoji", "")))
    return jsonify({"ok": ok})


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


@app.post("/api/poll")
def poll_create():
    data = request.get_json(silent=True) or {}
    error = room.create_poll(str(data.get("question", "")), data.get("options") or [])
    if error:
        return jsonify({"ok": False, "error": error}), 400
    return jsonify({"ok": True})


@app.post("/api/poll/vote")
def poll_vote():
    data = request.get_json(silent=True) or {}
    ok = room.vote_poll(data.get("poll_id"), data.get("option"))
    return jsonify({"ok": ok})


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


@app.get("/api/export")
def export_chat():
    body = room.export_text()
    return Response(
        body,
        mimetype="text/plain; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=matuchat-sohbet.txt"},
    )


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


def _open_window(url, port):
    try:
        import webview
    except ImportError:
        return False
    srv = threading.Thread(
        target=lambda: app.run(
            host="127.0.0.1",
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True,
        ),
        daemon=True,
    )
    srv.start()
    for _ in range(40):
        probe = socket.socket()
        try:
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                break
        finally:
            probe.close()
        time.sleep(0.05)
    try:
        webview.create_window(
            "MatuChat",
            url,
            width=1200,
            height=800,
            min_size=(760, 520),
            background_color="#12122e",
        )
        webview.start()
        return True
    except Exception:
        webbrowser.open(url)
        srv.join()
        return True


if __name__ == "__main__":
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    port = pick_port(int(os.environ.get("PORT", 5000)))
    url = "http://127.0.0.1:%d" % port
    if getattr(sys, "frozen", False) and os.environ.get("NO_WINDOW", "") != "1":
        if _open_window(url, port):
            sys.exit(0)
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
