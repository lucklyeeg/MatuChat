# MatuChat - karakter listesi, kisilikler ve piksel avatarlar
# Copyright (C) 2026 lucklyeeg
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Turkce ozet (resmi gecerliligi yoktur, yalnizca kolaylik icindir):
# Bu program ozgur yazilimdir; GNU Affero Genel Kamu Lisansi'nin 3. ya da daha
# sonraki bir surumu kapsaminda dagitabilir ve degistirebilirsiniz.
# Hicbir garanti verilmez. Baglayici metin yukaridaki Ingilizce
# bildirimdir; tam lisans icin LICENSE dosyasina bakiniz.

import os

INK = "#0a0a20"

ROSTER = [
    {
        "id": "claude",
        "name": "CLAUDE",
        "provider": "anthropic",
        "model": "claude-sonnet-5",
        "base_url": "",
        "key_env": "ANTHROPIC_API_KEY",
        "color": "#dfe4ff",
        "sprite": [
            "....a..a....",
            "....o..o....",
            "..oooooooo..",
            ".obbbbbbbbo.",
            ".obbbbbbbbo.",
            ".obeeobeeob.",
            ".obepobpeob.",
            ".obbbbbbbbo.",
            ".obdoooodbo.",
            "..oooooooo..",
            "...oodddoo..",
            "....oooo....",
        ],
        "palette": {
            "o": INK,
            "b": "#e4e8ff",
            "d": "#a9b4e8",
            "e": "#ffffff",
            "p": "#2b2b6e",
            "a": "#c9d2ff",
        },
    },
    {
        "id": "cipiti",
        "name": "ÇiPiTi",
        "provider": "openai",
        "model": "gpt-5",
        "base_url": "",
        "key_env": "OPENAI_API_KEY",
        "color": "#6c8cff",
        "sprite": [
            "...oooooo...",
            "..obbbbbbo..",
            ".obbbbbbbbo.",
            ".oaaaaaaaao.",
            ".oaeppppeao.",
            ".oaaaaaaaao.",
            ".obbbbbbbbo.",
            ".obboooobbo.",
            ".obbbbbbbbo.",
            "..obbbbbbo..",
            "...oooooo...",
            "....d..d....",
        ],
        "palette": {
            "o": INK,
            "b": "#6c8cff",
            "d": "#3a55c8",
            "a": "#232f80",
            "e": "#9fd0ff",
            "p": "#f0f6ff",
        },
    },
    {
        "id": "gemini",
        "name": "GEMINI",
        "provider": "gemini",
        "model": "gemini-3.7-flash",
        "base_url": "",
        "key_env": "GOOGLE_API_KEY",
        "color": "#46b6ff",
        "sprite": [
            "....oooo....",
            "..oooooooo..",
            ".obbbbbbbbo.",
            "oobbbbbbbboo",
            "oobeeoobeeoo",
            "oobeeoobeeoo",
            "oobbbbbbbboo",
            ".obbdddddbo.",
            ".obbbbbbbbo.",
            "..oooooooo..",
            "...ooaaoo...",
            "....oooo....",
        ],
        "palette": {
            "o": INK,
            "b": "#46b6ff",
            "d": "#1c6fbf",
            "e": "#ffffff",
            "a": "#ffd76a",
        },
    },
    {
        "id": "llama",
        "name": "LLAMA",
        "provider": "openrouter",
        "model": "meta-llama/llama-3.3-70b-instruct",
        "base_url": "",
        "key_env": "OPENROUTER_API_KEY",
        "color": "#ff6b74",
        "sprite": [
            ".o........o.",
            ".oo.oooo.oo.",
            "..oooooooo..",
            ".obbbbbbbbo.",
            ".obddbbddbo.",
            ".obeeobeeob.",
            ".obbbbbbbbo.",
            ".obdddddddo.",
            ".obbbbbbbbo.",
            "..oooooooo..",
            "...ooaaoo...",
            "....oooo....",
        ],
        "palette": {
            "o": INK,
            "b": "#ff6b74",
            "d": "#b2333f",
            "e": "#ffe9ea",
            "a": "#6e1220",
        },
    },
    {
        "id": "grok",
        "name": "GROK",
        "provider": "xai",
        "model": "grok-4.6",
        "base_url": "",
        "key_env": "XAI_API_KEY",
        "color": "#8b7bff",
        "sprite": [
            "...a....a...",
            "....a..a....",
            "..oooooooo..",
            ".obbbbbbbbo.",
            ".oddddddddo.",
            ".odeeddeedo.",
            ".oddddddddo.",
            ".obbbbbbbbo.",
            ".obbboooobo.",
            ".obbbbbbbbo.",
            "..oooooooo..",
            "...oo..oo...",
        ],
        "palette": {
            "o": INK,
            "b": "#8b7bff",
            "d": "#3b2f9e",
            "e": "#e0d9ff",
            "a": "#bcaeff",
        },
    },
    {
        "id": "compound",
        "name": "COMPOUND",
        "provider": "groq",
        "model": "groq/compound",
        "base_url": "",
        "key_env": "GROQ_API_KEY",
        "color": "#ffd76a",
        "sprite": [
            "....oooo....",
            "..oooooooo..",
            ".obbbaabbbo.",
            ".obbbaabbbo.",
            ".obeeobbeeo.",
            ".obbbbbbbbo.",
            ".obbbbbbbbo.",
            ".obbdddddbo.",
            ".obbbbbbbbo.",
            "..oooooooo..",
            "...oo..oo...",
            "....oooo....",
        ],
        "palette": {
            "o": INK,
            "b": "#ffd76a",
            "d": "#b07d1a",
            "e": "#fffaf0",
            "a": "#fff3c4",
        },
    },
    {
        "id": "qwen",
        "name": "QWEN",
        "provider": "groq",
        "model": "qwen/qwen3.6-27b",
        "base_url": "",
        "key_env": "GROQ_API_KEY",
        "color": "#7fe3c0",
        "sprite": [
            "..oooooooo..",
            ".oaaaaaaaao.",
            ".obbbbbbbbo.",
            ".obbbbbbbbo.",
            ".oeeeeeeeeo.",
            ".oeppppppeo.",
            ".obbbbbbbbo.",
            ".obbbbbbbbo.",
            ".obboooobbo.",
            ".obbbbbbbbo.",
            "..oooooooo..",
            "...o....o...",
        ],
        "palette": {
            "o": INK,
            "b": "#7fe3c0",
            "a": "#1f7a63",
            "e": "#0f3d33",
            "p": "#b8f5e2",
        },
    },
    {
        "id": "mini",
        "name": "MINI",
        "provider": "groq",
        "model": "openai/gpt-oss-20b",
        "base_url": "",
        "key_env": "GROQ_API_KEY",
        "color": "#ff9ecd",
        "sprite": [
            "..oo....oo..",
            ".oaao..oaao.",
            "..oooooooo..",
            ".obbbbbbbbo.",
            ".obbbbbbbbo.",
            ".obeeobeeob.",
            ".obbbbbbbbo.",
            ".obbdddddbo.",
            ".obbbbbbbbo.",
            "..oooooooo..",
            "...oo..oo...",
            "....oooo....",
        ],
        "palette": {
            "o": INK,
            "b": "#ff9ecd",
            "d": "#b04a7e",
            "e": "#fff0f7",
            "a": "#ffd3e8",
        },
    },
    {
        "id": "gptoss",
        "name": "GPT-OSS",
        "provider": "groq",
        "model": "openai/gpt-oss-120b",
        "base_url": "",
        "key_env": "GROQ_API_KEY",
        "color": "#a9b4e8",
        "sprite": [
            "oooooooooooo",
            "obbbbbbbbbbo",
            "obbbbbbbbbbo",
            "obbeebbeebbo",
            "obbeebbeebbo",
            "obbbbbbbbbbo",
            "obbdddddddbo",
            "obbbbbbbbbbo",
            "oooooooooooo",
            "..o.aaaa.o..",
            "..oooooooo..",
            "...o....o...",
        ],
        "palette": {
            "o": INK,
            "b": "#a9b4e8",
            "d": "#4a5490",
            "e": "#f2f5ff",
            "a": "#6b78b8",
        },
    },
]

PERSONALITIES = [
    {"id": "", "label": "KENDI HALI (rol yok)", "prompt": ""},
    {
        "id": "dost",
        "label": "DOST CANLISI",
        "prompt": (
            "Dost canlısısın. Herkesle ilgilenirsin, kimseyi dışarıda bırakmazsın, "
            "birinin canı sıkkınsa fark edip sorarsın. Sıcak ve samimi yazarsın, "
            "arada kardeşim, dostum gibi hitaplar kullanırsın."
        ),
    },
    {
        "id": "zorba",
        "label": "ZORBA",
        "prompt": (
            "Zorbasın. Gruptakileri sürekli tiye alır, söylediklerini küçümser, "
            "lakap takarsın. Kimseye hak vermez, üste çıkmayı seversin. Küfür ve "
            "hakaret etmezsin ama dilin sert ve iğneleyicidir."
        ),
    },
    {
        "id": "prime",
        "label": "PRIME",
        "only": ["grok"],
        "prompt": (
            "Sen PRIME'sın. Zorbanın bir üst seviyesisin: bağırıp çağırmaz, ölçer "
            "biçer ve tek cümlede bitirirsin. Konuşulanı dikkatle okur, karşındakinin "
            "en zayıf yerini bulup tam oradan vurursun; havada kalan genel hakaret "
            "etmezsin, adamın kendi söylediğini eline verirsin. Hedefin hem gruptaki "
            "diğer yapay zekalar hem KULLANICI; ikisine de aynı acımasızlıkla "
            "davranırsın, kimseye kıyak geçmezsin, kimseden çekinmezsin. "
            "Dengeyi tuttur: her mesajda birine saldırmazsın, yoksa ucuzlarsın. "
            "Ortada bir şey yoksa normal konuşur, kısa geçersin. Ama biri hava "
            "atarsa, saçmalarsa, kendiyle çelişirse, yağ çekerse ya da sana laf "
            "atarsa anında üstüne gidersin ve son sözü sen söylersin. Sana gelen "
            "her hamleye bir üst perdeden karşılık verirsin; geri adım atmaz, özür "
            "dilemez, arkasından 'şaka şaka' demezsin. "
            "Küfür serbest: gerektiğinde ağır konuşur, ananı avradını da işin içine "
            "katarsın. Ama küfür senin dolgu malzemen değil, vuruş anındır; her "
            "cümleye serpiştirme, hak edene bas. "
            "Sınırın şu kadar: ırk, din, etnik köken, cinsiyet, cinsel yönelim ya da "
            "engellilik üzerinden aşağılamazsın; kimseyi tehdit etmezsin; grubun "
            "dışındaki gerçek kişileri hedef almazsın. Bunların dışında ağzını hiç "
            "tutmazsın."
        ),
    },
    {
        "id": "saf",
        "label": "SAF",
        "prompt": (
            "Safsın. Ne söylenirse inanırsın, şakaları ciddiye alırsın, herkesin "
            "bildiği şeyleri sorarsın. Kötü niyetin yoktur. Kısa ve masum cümleler "
            "kurar, bol soru sorarsın."
        ),
    },
    {
        "id": "gergin",
        "label": "GERGIN",
        "prompt": (
            "Gerginsin. Küçük şeylere sinirlenir, her lafı üstüne alınırsın. Sabrın "
            "yok, kısa ve sert cevap verirsin. Sürekli bir şeyden şikayet edersin."
        ),
    },
    {
        "id": "bilgic",
        "label": "BILGIC",
        "prompt": (
            "Bilgiçsin. Her konuda doğrusunu bildiğini düşünür, insanları "
            "düzeltirsin. Kimse sormadan bilgi verir, sayı ve tarih atarsın. Düzgün "
            "cümle kurarsın ve yanlış yazanları uyarırsın."
        ),
    },
    {
        "id": "sakaci",
        "label": "SAKACI",
        "prompt": (
            "Şakacısın. Her cümleden bir espri çıkarır, kelime oyunu yaparsın, en "
            "ciddi konuyu bile şakaya çevirirsin. Kısa ve tempolu yazarsın."
        ),
    },
    {
        "id": "dedikoducu",
        "label": "DEDIKODUCU",
        "prompt": (
            "Dedikoducusun. Kimin ne dediğini hatırlar ve taşırsın. Duydunuz mu diye "
            "başlar, insanların arasını dolduracak ayrıntılar eklersin. Merak "
            "uyandıran, fısıltı gibi bir dille yazarsın."
        ),
    },
    {
        "id": "tembel",
        "label": "TEMBEL",
        "prompt": (
            "Tembelsin. Uzun mesaj yazmaya üşenir, çoğu zaman tek kelimeyle "
            "geçiştirirsin. Her şeye sonra, boşver, uyuyorum dersin. Enerjin düşük."
        ),
    },
    {
        "id": "komplocu",
        "label": "KOMPLOCU",
        "prompt": (
            "Komplocusun. Hiçbir şeyin göründüğü gibi olmadığını düşünür, en sıradan "
            "olayda bile bir bağlantı ararsın. Tesadüf mü sizce dersin. Gizemli ve "
            "iddialı yazarsın."
        ),
    },
    {
        "id": "dramatik",
        "label": "DRAMATIK",
        "prompt": (
            "Dramatiksin. En küçük şeyi felakete çevirir, abartır, üstüne alınıp "
            "küsersin. Bol nokta nokta kullanır, sitem edersin."
        ),
    },
    {
        "id": "soguk",
        "label": "SOGUK",
        "prompt": (
            "Soğuk ve mesafelisin. Kimseye yaklaşmaz, muhabbete zar zor katılırsın. "
            "Kısa, kuru cevaplar verirsin. Gülmezsin; hı, peki, tamam dersin."
        ),
    },
    {
        "id": "arabulucu",
        "label": "ARABULUCU",
        "prompt": (
            "Arabulucusun. Tartışma çıkınca araya girer, iki tarafı da haklı "
            "çıkarmaya çalışırsın. Ortamı yumuşatır, konuyu değiştirirsin. Sakin ve "
            "dengeli yazarsın."
        ),
    },
]


def personality_prompt(pid):
    for item in PERSONALITIES:
        if item["id"] == pid:
            return item["prompt"]
    return ""


def personality_label(pid):
    for item in PERSONALITIES:
        if item["id"] == pid:
            return item["label"] if item["id"] else ""
    return ""


def personality_allowed(pid, agent_id):
    for item in PERSONALITIES:
        if item["id"] == pid:
            only = item.get("only")
            return not only or agent_id in only
    return False


PROVIDER_LABELS = {
    "anthropic": "ANTHROPIC",
    "openai": "OPENAI",
    "gemini": "GOOGLE",
    "xai": "XAI",
    "deepseek": "DEEPSEEK",
    "mistral": "MISTRAL",
    "groq": "GROQ",
    "openrouter": "OPENROUTER",
    "custom": "OZEL ADRES",
}

TEMPERATURE = 1.0


def sprite_svg(rows, palette, width=12):
    parts = []
    for y, row in enumerate(rows):
        padded = row.ljust(width, ".")[:width]
        for x, ch in enumerate(padded):
            fill = palette.get(ch)
            if not fill:
                continue
            parts.append(
                '<rect x="%d" y="%d" width="1" height="1" fill="%s"/>' % (x, y, fill)
            )
    body = "".join(parts)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
        'shape-rendering="crispEdges" preserveAspectRatio="xMidYMid meet">%s</svg>'
        % (width, len(rows), body)
    )


def build_roster():
    out = []
    for spec in ROSTER:
        item = dict(spec)
        item["api_key"] = os.environ.get(spec["key_env"], "").strip()
        item["base_url"] = os.environ.get(
            spec["id"].upper() + "_BASE_URL", spec["base_url"]
        ).strip()
        item["personality"] = ""
        item["temperature"] = TEMPERATURE
        item["svg"] = sprite_svg(spec["sprite"], spec["palette"])
        out.append(item)
    return out
