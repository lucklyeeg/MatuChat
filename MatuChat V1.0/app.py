# MatuChat - Flask web sunucusu ve HTTP uclari
# Copyright (C) 2026 lucklyeeg
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Turkce ozet (resmi gecerliligi yoktur, yalnizca kolaylik icindir):
# Bu program ozgur yazilimdir; GNU Genel Kamu Lisansi'nin 3. ya da daha
# sonraki bir surumu kapsaminda dagitabilir ve degistirebilirsiniz.
# Hicbir garanti verilmez. Baglayici metin yukaridaki Ingilizce
# bildirimdir; tam lisans icin LICENSE dosyasina bakiniz.

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
    room.whisper(str(data.get("agent_id", "")), str(data.get("text", "")))
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
    # Tarayiciyi burada aciyoruz: port mesgulse pick_port baska bir tane secer,
    # baslatma betigi sabit adresi bilemez.
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
