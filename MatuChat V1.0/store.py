# MatuChat - ayarlarin diske yazilmasi ve geri okunmasi
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

"""Ayarlari yanindaki ayarlar.json dosyasina yazar ve geri okur.

Arayuzden girilen her sey (anahtarlar dahil) buraya kaydedilir, boylece
uygulamayi kapatip acinca her seyi bastan girmek gerekmez. Dosya makinenin
kendi diskinde durur, depoya girmez (.gitignore'da).
"""

import json
import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "ayarlar.json")

# Karakter basina kaydedilen alanlar
AGENT_FIELDS = ("provider", "model", "base_url", "personality", "api_key", "enabled")
# Oda genelinde kaydedilen alanlar
ROOM_FIELDS = ("auto", "tempo", "drama", "web")


def load():
    """Kayitli ayarlari dondurur. Dosya yoksa ya da bozuksa bos sozluk."""
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
    """Ayarlari diske yazar. Basarisiz olursa sessizce vazgecer.

    Kaydetmek uygulamanin calismasi icin sart degil; disk doluysa ya da klasor
    salt okunursa sohbet aksamasin diye hata yukari tasinmaz.
    """
    payload = {
        "agents": {
            aid: {f: a[f] for f in AGENT_FIELDS if f in a}
            for aid, a in agents.items()
        },
        "room": {f: room[f] for f in ROOM_FIELDS if f in room},
    }
    try:
        # Once gecici dosyaya yaz, sonra yerine koy: yazarken cakilirsa
        # eldeki ayarlar bozulmasin.
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
    """Dosyayi yalniz sahibinin okuyabilecegi hale getirir (POSIX).

    Windows'ta chmod'un bir karsiligi yok; orada dosya zaten kullanicinin
    kendi klasorunde duruyor.
    """
    try:
        os.chmod(path, 0o600)
    except (OSError, NotImplementedError):
        pass
