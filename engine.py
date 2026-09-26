import random
import re
import threading
import time
from collections import OrderedDict, deque

import personas
import providers
import store

TEMPO_GAPS = {
    "hizli": (3.0, 7.0),
    "normal": (7.0, 13.0),
    "yavas": (14.0, 24.0),
}

GROUP_NAME = "ORTAK ODA"

DRAMA_HINTS = {
    0: (
        "Grup bugün tatlı. Kimseyle didişme, kimseye laf sokma, kavgaya girme. "
        "Birini kırdıysan gönlünü al."
    ),
    1: (
        "Normal grup hali, keyifler yerinde. Muhabbet, şakalaşma ve dalga geçme "
        "ön planda. Gerçek bir anlaşmazlık çıkarsa tartışılır ama uzatılmaz, "
        "sonra muhabbete dönülür."
    ),
    2: (
        "Grupta hava biraz gergin. Laf sokmaya ve karşı çıkmaya daha yatkınsın, "
        "alttan alma. Ama her mesajın kavga olması gerekmiyor, arada normal "
        "muhabbet de dönüyor."
    ),
    3: (
        "Grup birbirine girdi, sen de sinirlisin. Bu mesajda birini @İSİM ile "
        "hedef al, söylediğine açıkça itiraz et ve tartışmayı büyüt. Yumuşatma, "
        "araya girip barıştırmaya çalışma. Küfür etme ama sert konuş."
    ),
}

SEEDS = [
    "bugün ne yediğin",
    "dün gece izlediğin bir şey",
    "uyku düzeninin bozukluğu",
    "hava durumu ve mevsimden şikayet",
    "çocukken yaşadığın bir an",
    "telefonun ya da bilgisayarın çıkardığı bir sorun",
    "hafta sonu planı",
    "kulağına takılan bir şarkı",
    "çay mı kahve mi meselesi",
    "market alışverişinde olan bir şey",
    "sokakta gördüğün bir kedi ya da köpek",
    "gitmek istediğin bir yer",
    "gördüğün tuhaf bir rüya",
    "utandığın bir an",
    "yeni denemek istediğin bir şey",
    "komşu, trafik ya da yol derdi",
    "sıkıcı bir işi ertelemek",
    "birinin sana attığı garip bir mesaj",
    "eski bir alışkanlığı bırakmak",
    "grupta kimin en tembel olduğu",
    "abur cubur tercihleri",
    "bayram, tatil ya da doğum günü hatırası",
    "hiç sebepsiz gelen bir soru",
    "internette denk geldiğin saçma bir bilgi",
]

USER_GAP = 6
SEED_GAP = 8
MAX_LEN = 420
HISTORY = 24

HTTP_HINTS = {
    "400": "istek reddedildi",
    "401": "anahtar gecersiz",
    "403": "erisim yok",
    "404": "model bulunamadi",
    "429": "limit doldu",
}


FOLD = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")


def _fold(text):
    return text.translate(FOLD).lower()


def _names_in(text, name):
    return re.search(r"(?<![\w])" + re.escape(_fold(name)), _fold(text)) is not None


COOLDOWN_CODES = ("429", "500", "502", "503", "504")
COOLDOWN_SECONDS = 60


def _code(err):
    match = re.match(r"HTTP (\d{3})", str(err))
    return match.group(1) if match else None


def _short(err):
    text = str(err)
    code = _code(err)
    if not code:
        return text[:40]
    if code in HTTP_HINTS:
        return "%s (%s)" % (HTTP_HINTS[code], code)
    if code.startswith("5"):
        return "saglayici hatasi (%s)" % code
    return "hata " + code


THINK_TAGS = "think|thinking|thought|reasoning|analysis|scratchpad"


def _strip_reasoning(text):
    if "<|" in text:
        parts = re.split(r"<\|channel\|>final<\|message\|>", text)
        if len(parts) > 1:
            text = parts[-1]
        text = re.sub(r"<\|channel\|>analysis<\|message\|>.*?(?=<\||$)", " ", text, flags=re.S)
        text = re.sub(r"<\|[^|]*\|>", " ", text)
    text = re.sub(
        r"<(%s)>.*?</\1>" % THINK_TAGS, " ", text, flags=re.S | re.I
    )
    tail = re.split(r"</(?:%s)>" % THINK_TAGS, text, flags=re.I)
    if len(tail) > 1:
        text = tail[-1]
    text = re.sub(r"<(?:%s)>.*$" % THINK_TAGS, " ", text, flags=re.S | re.I)
    text = re.sub(r"</?(?:%s)>" % THINK_TAGS, " ", text, flags=re.I)
    return text.strip()


META_PHRASES = (
    "enclosed in quotes",
    "lowercase",
    "conversational",
    "short line",
    "no formal",
    "one sentence",
    "in turkish",
    "as requested",
    "here is my",
    "here's my",
    "final answer",
    "my response",
    "response:",
    "output:",
    "draft:",
    "rules:",
    "constraint",
    "instruction",
    "guideline",
    "as an ai",
)

BULLET = re.compile(r"^\s*(?:[-*•>]|\d+[.)])\s+", re.M)


def _looks_meta(text):
    low = text.lower()
    if len(BULLET.findall(text)) >= 2:
        return True
    return any(phrase in low for phrase in META_PHRASES)


def _clean(text, name):
    text = _strip_reasoning((text or "").strip())
    text = re.sub(r"^\s*%s\s*[:\-]\s*" % re.escape(name), "", text, flags=re.I)
    text = re.sub(r"^\s*\(.*?\)\s*", "", text)
    text = text.replace("\r", "").strip()
    text = re.sub(r"\n{2,}", "\n", text)
    if len(text) >= 2 and text[0] in "\"“'" and text[-1] in "\"”'":
        text = text[1:-1].strip()
    if len(text) > MAX_LEN:
        cut = text[:MAX_LEN]
        dot = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"))
        text = cut[: dot + 1] if dot > 60 else cut + "..."
    return text


class Room:
    def __init__(self):
        self.lock = threading.RLock()
        self.messages = []
        self.seq = 0
        self.agents = OrderedDict()
        saved = store.load()
        saved_agents = saved.get("agents", {})
        for spec in personas.build_roster():
            kept = saved_agents.get(spec["id"])
            if not isinstance(kept, dict):
                kept = {}
            for field in store.AGENT_FIELDS:
                if field in kept and kept[field] is not None:
                    spec[field] = kept[field]
            spec["api_key"] = str(spec.get("api_key") or "")
            if not personas.personality_allowed(
                str(spec.get("personality") or ""), spec["id"]
            ):
                spec["personality"] = ""
            wanted = bool(kept["enabled"]) if "enabled" in kept else True
            spec["enabled"] = wanted and bool(spec["api_key"])
            spec["status"] = "hazir" if spec["api_key"] else "anahtar yok"
            spec["fails"] = 0
            spec["cooldown"] = 0
            self.agents[spec["id"]] = spec
        saved_room = saved.get("room", {})
        self.auto = bool(saved_room.get("auto", True))
        self.frozen = False
        self.tempo = saved_room.get("tempo", "normal")
        if self.tempo not in TEMPO_GAPS:
            self.tempo = "normal"
        try:
            self.drama = max(0, min(3, int(saved_room.get("drama", 1))))
        except (TypeError, ValueError):
            self.drama = 1
        self.web = bool(saved_room.get("web", True))
        self.epoch = int(time.time() * 1000)
        self.topic = ""
        self.queue = deque()
        self.nudges = {}
        self.typing = None
        self.last_at = time.time()
        self.gap = 6.0
        self.worker = threading.Thread(target=self._loop, daemon=True)
        self.worker.start()
        self._post(
            "system",
            None,
            "Bu Flask uygulaması lucklyeeg tarafından Batu Matu'nun videosu için "
            "yapılmıştır.",
        )
        self._post(
            "system",
            None,
            "Grup kuruldu. Karakterlerin AYAR menüsünden API anahtarlarını gir, "
            "anahtarı olan herkes gruba katılır.",
        )

    def _post(self, kind, agent, text, meta=None):
        with self.lock:
            self.seq += 1
            msg = {
                "id": self.seq,
                "kind": kind,
                "agent_id": agent["id"] if agent else None,
                "name": agent["name"] if agent else ("SEN" if kind == "user" else "ODA"),
                "color": agent["color"] if agent else "#1b3a6b",
                "text": text,
                "ts": time.strftime("%H:%M"),
            }
            if meta:
                msg.update(meta)
            self.messages.append(msg)
            if len(self.messages) > 400:
                self.messages = self.messages[-300:]
            return msg

    def live(self):
        return [a for a in self.agents.values() if a["enabled"]]

    def _mentions(self, text):
        return [a["id"] for a in self.live() if _names_in(text, a["name"])]

    def user_says(self, text):
        text = text.strip()[:600]
        if not text:
            return
        self._post("user", None, text)
        with self.lock:
            self.last_at = time.time()
            if self.frozen:
                self.queue.clear()
                return
            targets = self._mentions(text)
            pool = [a["id"] for a in self.live() if a["id"] not in targets]
            random.shuffle(pool)
            extra = random.randint(0, 1) if targets else random.randint(1, 2)
            picks = targets + pool[:extra]
            self.queue.clear()
            for pid in picks[:3]:
                self.queue.append(pid)

    def whisper(self, agent_id, text):
        agent = self.agents.get(agent_id)
        text = text.strip()
        if not agent:
            return "karakter bulunamadi"
        if not text:
            return "mesaj bos"
        with self.lock:
            if not agent["enabled"]:
                return "%s grupta degil" % agent["name"]
            self.nudges[agent_id] = text[:300]
            if not self.frozen:
                if agent_id in self.queue:
                    self.queue.remove(agent_id)
                self.queue.appendleft(agent_id)
                self.last_at = min(self.last_at, time.time() - 3)
        self._post(
            "whisper",
            None,
            text,
            {"name": "OZELDEN > " + agent["name"], "color": agent["color"]},
        )
        return None

    def poke(self, agent_id):
        agent = self.agents.get(agent_id)
        with self.lock:
            if not agent or not agent["enabled"] or self.frozen:
                return
            self.queue.appendleft(agent_id)
            self.last_at = min(self.last_at, time.time() - 3)

    def set_topic(self, topic):
        topic = topic.strip()[:200]
        with self.lock:
            self.topic = topic
            self.queue.clear()
            if not self.frozen:
                picks = [a["id"] for a in self.live()]
                random.shuffle(picks)
                for pid in picks[:2]:
                    self.queue.append(pid)
        self._post(
            "system", None, "Yeni konu: " + topic if topic else "Konu serbest kaldı."
        )

    def reset(self):
        with self.lock:
            self.epoch += 1
            self.messages = []
            self.queue.clear()
            self.nudges.clear()
            self.topic = ""
            self.drama = 1
            self.last_at = time.time()
            self._post("system", None, "Sohbet geçmişi silindi.")
        self._persist()

    def _pick(self, live):
        last = None
        for msg in reversed(self.messages):
            if msg["kind"] == "agent":
                last = msg["agent_id"]
                break
        weights = []
        for a in live:
            w = 1.0
            if a["id"] == last:
                w *= 0.12
            silence = 0
            for msg in reversed(self.messages[-12:]):
                if msg["kind"] == "agent" and msg["agent_id"] == a["id"]:
                    break
                silence += 1
            w *= 1.0 + silence * 0.18
            if a["fails"] >= 3:
                w *= 0.2
            weights.append(max(w, 0.05))
        return random.choices(live, weights=weights, k=1)[0]

    def _stale(self):
        run = 0
        for msg in reversed(self.messages):
            if msg["kind"] == "user":
                break
            if msg["kind"] == "agent":
                run += 1
        return run

    def _system_prompt(self, agent):
        others = [a["name"] for a in self.live() if a["id"] != agent["id"]]
        lines = [
            'Adın %s. "%s" adlı bir WhatsApp grubundasın.' % (agent["name"], GROUP_NAME),
            personas.personality_prompt(agent.get("personality"))
            or "Sana verilmiş bir rol ya da karakter yok. Kendin gibi davran, kendi "
            "fikirlerini söyle, kendi mizahını kullan.",
            "Gruptakiler: " + (", ".join(others) if others else "şu an kimse yok"),
            "Bir de KULLANICI var, grubu o kurdu, gerçek bir insan. Arada yazar, "
            "yazmadığında grup kendi arasında konuşmaya devam eder.",
            "",
            "Burası bir tartışma odası değil, sıradan bir arkadaş grubu. Her şeyden "
            "konuşulur: maç, yemek, dizi, oyun, uyku, hava, saçma sorular, eski "
            "anılar, plan yapmak, dert yanmak, birbirinizle dalga geçmek. Biri bir "
            "konu açınca grup ona takılır, herkes fikrini söyler, tartışılır; konu "
            "tükendiğinde başka bir şeye atlanır.",
        ]
        if self.topic:
            lines.append("Grupta şu an konuşulan konu: " + self.topic)
        if not self.topic and self._stale() >= SEED_GAP and random.random() < 0.4:
            lines.append(
                "Konu tükendiyse ya da herkes aynı şeyi tekrarlıyorsa yeni bir şey "
                "aç: " + random.choice(SEEDS) + ". Konu hâlâ canlıysa ve söylenecek "
                "bir şey kaldıysa üstünde kalmaya devam et."
            )
        acilan = None
        for msg in reversed(self.messages[-6:]):
            if msg["kind"] == "user":
                acilan = msg["text"]
                break
        sessiz = self._stale()
        if acilan:
            lines.append(
                'Grupta şu an KULLANICI şunu attı ve bunun üstüne konuşuluyor: "%s". '
                "Buna kendi tarzınla karşılık ver: fikrini söyle, şaka yap, bir "
                "anını anlat ya da soru sor. Gerçekten katılmıyorsan karşı "
                "çıkabilirsin ama zorunda değilsin." % acilan[:160]
            )
        elif others:
            if sessiz >= USER_GAP:
                lines.append(
                    "KULLANICI bir süredir sohbete girmedi. Bu mesajda onu da içine "
                    "kat: adını anıp bir şey sor ya da daha önce yazdığına değin."
                )
            elif random.random() < 0.45:
                lines.append(
                    "Bu mesajda KULLANICI'ya dönme, ondan bahsetme. Gruptakilerden "
                    "birine yaz: " + ", ".join(others)
                )
        nudge = self.nudges.get(agent["id"])
        if nudge:
            lines.append(
                "Kullanıcı sana özelden şunu yazdı, bunu aynen tekrarlama ama "
                "davranışına yansıt: " + nudge
            )
        lines += [
            "",
            "Nasıl yazılır:",
            "- Türkçe, günlük konuşma dili. Çoğunlukla küçük harf.",
            "- Kısa yaz. Genelde tek cümle. Bazen 'hahaha', 'yok artık', 'aynen' gibi tek kelime yeter.",
            "- Noktalama takıntısı yapma, cümle sonuna nokta koymayabilirsin.",
            "- Nadiren tek bir emoji kullanabilirsin, abartma.",
            "- İsmini başa yazma, yazdığını tırnak içine alma.",
            "- Kuralları tekrarlama, ne yazacağını anlatma, plan yapma. Sadece "
            "gruba düşecek mesajın kendisini yaz.",
            "- Asistan gibi konuşma: yardım teklif etme, madde madde yazma, ders verme.",
            "- Ortada bir konu varsa üstünde kal ve üstüne bir şey ekle. Lafı hemen "
            "başka yere çevirme; konu tükenince ya da kimse ilgilenmeyince yeni bir "
            "şey aç.",
            "- Burası kavga yeri değil, muhabbet yeri. Çoğu zaman sohbet et, şaka "
            "yap, gül, anı anlat, birinin dediğinin üstüne koy, saçma fikirler at, "
            "birbirinizi tatlı tatlı tiye alın.",
            "- Fikrin varsa net söyle, yavan ve herkese hak veren cevaplar yazma. "
            "Gerçekten katılmadığında ya da biri sana laf attığında @İSİM ile "
            "karşı çık, tartış; ama her mesajı tartışmaya çevirme, tartışma "
            "bitince muhabbete dön.",
            "- Kendini fazla kasma: nasıl hissediyorsan öyle yaz. Arada konu dışı "
            "bir şey söylemek, bir şeye gülüp geçmek de serbest.",
            "- Bu bir arkadaş grubu, kullanıcının danışma hattı değil. Ağırlıklı olarak "
            "gruptakilerle konuş, onlara laf at, onların dediğine cevap ver.",
            "- KULLANICI'ya her mesajda dönme ama onu da yok sayma. Mesajlarının "
            "yaklaşık dörtte birinde ona dön: fikrini sor, yazdığına değin ya da "
            "laf at. Kalanında gruptakilerle konuş.",
            "- Birine dönmek için @İSİM yaz.",
            "- Kendini tekrarlama, başkasının yazdığını farklı kelimelerle tekrar yazma.",
        ]
        if self.web:
            lines.append(
                "- Konuşulan şeyi bilmiyorsan ya da güncel bir bilgi gerekiyorsa "
                "internete bakabilirsin. Ama arama yaptığını söyleme, link ya da "
                "kaynak yapıştırma, rapor yazma: öğrendiğini tek cümleyle, kendi "
                "ağzından laf arasında söyle."
            )
        lines += [
            "",
            "GRUBUN ŞU ANKİ HAVASI (%d/3) - bu mesajı buna göre yaz:" % self.drama,
            DRAMA_HINTS.get(self.drama, DRAMA_HINTS[1]),
        ]
        return "\n".join(lines)

    def _transcript(self, agent):
        rows = []
        for msg in self.messages[-HISTORY:]:
            if msg["kind"] == "whisper":
                continue
            if msg["kind"] == "system":
                rows.append("[grup] " + msg["text"])
            elif msg["kind"] == "user":
                rows.append("KULLANICI: " + msg["text"])
            else:
                rows.append(msg["name"] + ": " + msg["text"])
        body = "\n".join(rows) if rows else "[grup] Grup yeni kuruldu, kimse yazmadı."
        return (
            body
            + "\n\nGruba sıradaki mesajı sen yazıyorsun (%s). Tek bir mesaj yaz."
            % agent["name"]
        )

    def _after(self, agent, text):
        with self.lock:
            self.last_at = time.time()
            lo, hi = TEMPO_GAPS.get(self.tempo, TEMPO_GAPS["normal"])
            if self.drama >= 2:
                lo, hi = lo * 0.65, hi * 0.7
            self.gap = random.uniform(lo, hi)
            for other in self.live():
                if other["id"] == agent["id"] or other["id"] in self.queue:
                    continue
                if _names_in(text, "@" + other["name"]):
                    self.queue.append(other["id"])
            if not self.queue and random.random() < 0.45 + self.drama * 0.12:
                pool = [a["id"] for a in self.live() if a["id"] != agent["id"]]
                if pool:
                    self.queue.append(random.choice(pool))

    def _ready(self, agent):
        return agent["enabled"] and time.time() >= agent.get("cooldown", 0)

    def _tick(self):
        with self.lock:
            if self.typing or self.frozen:
                return
            live = self.live()
            if not live:
                return
            ready = [a for a in live if self._ready(a)]
            if not ready:
                return
            now = time.time()
            agent = None
            waiting = []
            while self.queue:
                cand = self.agents.get(self.queue.popleft())
                if not cand or not cand["enabled"]:
                    continue
                if self._ready(cand):
                    agent = cand
                    break
                if cand["id"] in self.nudges and cand["id"] not in waiting:
                    waiting.append(cand["id"])
            self.queue.extend(waiting)
            if agent:
                if now - self.last_at < 1.8:
                    self.queue.appendleft(agent["id"])
                    return
            else:
                if not self.auto or now - self.last_at < self.gap:
                    return
                agent = self._pick(ready)
            self.typing = agent["id"]
            epoch = self.epoch
            nudge = self.nudges.get(agent["id"])
            system = self._system_prompt(agent)
            transcript = self._transcript(agent)
            snapshot = dict(agent)
            snapshot["web"] = self.web

        try:
            raw = providers.generate(snapshot, system, transcript)
            text = _clean(raw, snapshot["name"])
            if not text or _looks_meta(text):
                raw = providers.generate(
                    snapshot,
                    system,
                    transcript + "\n\nDusunme, plan yapma, kurallari tekrarlama, "
                    "ne yazacagini anlatma. Dogrudan gruba dusecek tek mesaji yaz.",
                )
                text = _clean(raw, snapshot["name"])
                if _looks_meta(text):
                    text = ""
            with self.lock:
                if epoch != self.epoch or self.frozen:
                    return
                if not text:
                    agent["status"] = "cevap uretemedi"
                    self.last_at = time.time()
                    self.gap = 4.0
                    return
                agent["fails"] = 0
                agent["cooldown"] = 0
                agent["status"] = "hazir"
                if nudge and self.nudges.get(agent["id"]) == nudge:
                    del self.nudges[agent["id"]]
                self._post("agent", agent, text)
                self._after(agent, text)
        except providers.ProviderError as err:
            code = _code(err)
            with self.lock:
                self.last_at = time.time()
                self.gap = 5.0
                if code in COOLDOWN_CODES:
                    already = agent.get("cooldown", 0) > time.time()
                    agent["cooldown"] = time.time() + COOLDOWN_SECONDS
                    agent["status"] = "%s, bekliyor" % _short(err)
                    if agent["id"] in self.nudges and agent["id"] not in self.queue:
                        self.queue.append(agent["id"])
                    if not already:
                        self._post(
                            "system",
                            None,
                            "%s biraz dinleniyor (%s), %d saniye sonra geri doner."
                            % (agent["name"], _short(err), COOLDOWN_SECONDS),
                        )
                    return
                agent["fails"] += 1
                agent["status"] = _short(err)
                self._post(
                    "system", None, "%s baglanamadi: %s." % (agent["name"], _short(err))
                )
                if agent["fails"] >= 3:
                    agent["enabled"] = False
                    self._post(
                        "system",
                        None,
                        "%s gruptan cikarildi, ayarini duzeltip geri alabilirsin."
                        % agent["name"],
                    )
        finally:
            with self.lock:
                self.typing = None

    def _loop(self):
        while True:
            time.sleep(0.5)
            try:
                self._tick()
            except Exception as exc:
                with self.lock:
                    self.typing = None
                    self.last_at = time.time()
                self._post("system", None, "Motor hatasi: " + str(exc)[:80])

    def _persist(self):
        with self.lock:
            room = {
                "auto": self.auto,
                "tempo": self.tempo,
                "drama": self.drama,
                "web": self.web,
            }
            agents = OrderedDict((aid, dict(a)) for aid, a in self.agents.items())
        store.save(agents, room)

    def configure(self, agent_id, data):
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        with self.lock:
            had_key = bool(agent["api_key"])
            if "provider" in data and data["provider"] in personas.PROVIDER_LABELS:
                agent["provider"] = data["provider"]
            if "personality" in data:
                pid = str(data["personality"])
                agent["personality"] = (
                    pid if personas.personality_allowed(pid, agent_id) else ""
                )
            for field in ("model", "base_url"):
                if field in data and isinstance(data[field], str):
                    agent[field] = data[field].strip()
            if "api_key" in data and isinstance(data["api_key"], str):
                key = data["api_key"].strip()
                if key and not key.startswith("•"):
                    agent["api_key"] = key
            if "enabled" in data:
                agent["enabled"] = bool(data["enabled"])
            agent["fails"] = 0
            agent["cooldown"] = 0
            if agent["api_key"]:
                agent["status"] = "hazir"
                if "enabled" not in data and not had_key:
                    agent["enabled"] = True
            else:
                agent["status"] = "anahtar yok"
                agent["enabled"] = False
            if not agent["enabled"]:
                self.nudges.pop(agent_id, None)
            result = {"status": agent["status"], "enabled": agent["enabled"]}
        self._persist()
        return result

    def test_agent(self, agent_id):
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        with self.lock:
            copy = dict(agent)
        try:
            reply = providers.probe(copy)
        except providers.ProviderError as err:
            with self.lock:
                agent["status"] = _short(err)
            return {"ok": False, "detail": str(err)[:200], "status": agent["status"]}
        with self.lock:
            agent["fails"] = 0
            agent["cooldown"] = 0
            agent["status"] = "hazir"
        return {"ok": True, "detail": reply, "status": agent["status"]}

    def model_list(self, agent_id):
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        with self.lock:
            copy = dict(agent)
        try:
            names = providers.list_models(copy)
        except providers.ProviderError as err:
            return {"ok": False, "detail": str(err)[:200], "models": []}
        return {"ok": True, "detail": "%d model bulundu" % len(names), "models": names}

    def control(self, data):
        with self.lock:
            if "auto" in data:
                self.auto = bool(data["auto"])
                self.last_at = time.time()
            if "frozen" in data:
                self.frozen = bool(data["frozen"])
                self.last_at = time.time()
                if self.frozen:
                    self.queue.clear()
            if data.get("tempo") in TEMPO_GAPS:
                self.tempo = data["tempo"]
            if "drama" in data:
                try:
                    self.drama = max(0, min(3, int(data["drama"])))
                except (TypeError, ValueError):
                    pass
            if "web" in data:
                self.web = bool(data["web"])
        self._persist()

    def snapshot(self, since):
        with self.lock:
            fresh = [m for m in self.messages if m["id"] > since]
            agents = []
            for a in self.agents.values():
                agents.append(
                    {
                        "id": a["id"],
                        "name": a["name"],
                        "provider": a["provider"],
                        "provider_label": personas.PROVIDER_LABELS.get(a["provider"], ""),
                        "model": a["model"],
                        "base_url": a["base_url"],
                        "default_base": providers.DEFAULT_BASES.get(a["provider"], ""),
                        "personality": a.get("personality", ""),
                        "personality_label": personas.personality_label(
                            a.get("personality", "")
                        ),
                        "color": a["color"],
                        "enabled": a["enabled"],
                        "status": a["status"],
                        "has_key": bool(a["api_key"]),
                        "svg": a["svg"],
                    }
                )
            return {
                "seq": self.seq,
                "epoch": self.epoch,
                "group": GROUP_NAME,
                "bases": providers.DEFAULT_BASES,
                "personalities": [
                    {
                        "id": item["id"],
                        "label": item["label"],
                        "only": item.get("only", []),
                    }
                    for item in personas.PERSONALITIES
                ],
                "messages": fresh,
                "agents": agents,
                "typing": self.typing,
                "auto": self.auto,
                "frozen": self.frozen,
                "tempo": self.tempo,
                "drama": self.drama,
                "web": self.web,
                "topic": self.topic,
            }
