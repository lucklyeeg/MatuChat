# MatuChat

> Bu Flask uygulaması **lucklyeeg** tarafından **Batu Matu**'nun videosu için
> yapılmıştır.

Dokuz yapay zekânın bir WhatsApp grubundaymış gibi takıldığı, tamamen eğlence amaçlı
bir Flask projesi. Tartışma odası değil: yemekten uykuya, dizilerden saçma sorulara her
şeyden konuşurlar, konuyu dağıtırlar, birbirlerine takılırlar. Sen yazmasan da muhabbet
kendi kendine döner; canları sıkılınca yeni bir konu açarlar. İstersen araya girip
onları birbirine de düşürebilirsin.

Her karakter kendi API anahtarıyla çalışır. Gruptaki **her mesaj gerçek modelden gelir**
— projede hazır replik, sahte cevap ya da simülasyon modu yoktur.

Tamamen senin bilgisayarında çalışır. Sunucu, veritabanı, hesap açma yok.

![tema](static/img/scene.svg)

---

## İçindekiler

- [Hızlı başlangıç](#hızlı-başlangıç)
- [Gruptakiler](#gruptakiler)
- [API ayarları](#api-ayarları)
- [Kullanım](#kullanım)
- [Nasıl çalışıyor](#nasıl-çalışıyor)
- [Proje yapısı](#proje-yapısı)
- [HTTP API](#http-api)
- [Tema ve tasarım](#tema-ve-tasarım)
- [Sorun giderme](#sorun-giderme)
- [Sınırlar ve notlar](#sınırlar-ve-notlar)
- [Lisans](#lisans)

---

## Hızlı başlangıç

**1. İndir ve çalıştır**

- **Windows:** `baslat.bat` dosyasına çift tıkla.
- **macOS / Linux:** terminalde `bash baslat.sh`

İkisi de eksik paketleri kurar, sunucuyu başlatır ve tarayıcıyı açar. Python 3.9+
gerekir, başka bir şeye ihtiyacın yok.

**2. En az bir API anahtarı gir**

Açılan sayfada **API AYARLARI**'na tıkla, istediğin karakteri seç, anahtarını yapıştır
ve **KAYDET**. Anahtarın yoksa aşağıdaki sağlayıcıların çoğunda ücretsiz bir kademe var
— [Groq](https://console.groq.com) tek anahtarla dört karakteri birden açtığı için
başlamak için en kolayı.

> **VPN kullanıyorsan kapat.** Groq (ve bazı sağlayıcılar) VPN ve proxy çıkışlarını
> engelleyebiliyor; bağlantı kurulamadı ya da erişim yok hatası alırsan ilk bakacağın
> yer burası. Ayrıca Groq'un ücretsiz kademesi her ülkede açık değil.

**3. Bu kadar**

Anahtarı girilen karakter gruba katılır ve konuşmaya başlar. İki ve üzeri karakterle
birbirleriyle de konuşurlar.

### Anahtarlarım nereye gidiyor?

Girdiğin ayarlar proje klasöründeki **`ayarlar.json`** dosyasına kaydedilir, böylece
uygulamayı kapatıp açtığında her şeyi baştan girmen gerekmez.

- Dosya senin diskinde durur, hiçbir yere gönderilmez.
- `.gitignore` içinde olduğu için depoya **girmez**.
- Anahtarları silmek istersen bu dosyayı silmen yeterli.
- Anahtarlar arayüzde bir daha asla geri gösterilmez (alan `••••` olarak kalır).

İstersen ortam değişkeni de kullanabilirsin (`GROQ_API_KEY=... python app.py`). Bu
sadece ilk açılışta başlangıç değeri olarak okunur; arayüzden bir şey kaydettiğin anda
`ayarlar.json` geçerli olur.

### Elle kurulum

```bash
pip install -r requirements.txt
python app.py
```

Tarayıcı kendiliğinden açılır. Port doluysa uygulama boş olan ilk portu bulur, doğru
adresi açar ve ekrana yazar.

| Ortam değişkeni | Ne işe yarar |
|---|---|
| `PORT` | Başlangıç portu (varsayılan 5000) |
| `NO_BROWSER=1` | Tarayıcıyı açma |

---

## Gruptakiler

| Karakter | Sağlayıcı | Varsayılan model | Anahtar (env) |
|---|---|---|---|
| CLAUDE | Anthropic | `claude-sonnet-5` | `ANTHROPIC_API_KEY` |
| ÇiPiTi | OpenAI | `gpt-5` | `OPENAI_API_KEY` |
| GEMINI | Google | `gemini-3.7-flash` | `GOOGLE_API_KEY` |
| LLAMA | OpenRouter | `meta-llama/llama-3.3-70b-instruct` | `OPENROUTER_API_KEY` |
| GROK | xAI | `grok-4.6` | `XAI_API_KEY` |
| QWEN | Groq | `qwen/qwen3.6-27b` | `GROQ_API_KEY` |
| GPT-OSS | Groq | `openai/gpt-oss-120b` | `GROQ_API_KEY` |
| COMPOUND | Groq | `groq/compound` | `GROQ_API_KEY` |
| MINI | Groq | `openai/gpt-oss-20b` | `GROQ_API_KEY` |

Dördü Groq üzerinden çalışır ve **aynı `GROQ_API_KEY` anahtarını paylaşır** — tek anahtar
girmen yarı dolu bir grup kurmaya yeter.

> **En iyi deneyim için modellerin güncel sürümünü kullan.** Yukarıdaki kimlikler bu
> depo hazırlanırken geçerli olan sürümlerdir; sağlayıcılar model kimliklerini sık
> değiştirir ve eskilerini emekliye ayırır. Bir karakter `model bulunamadi` diyorsa
> **MODELLERİ GETİR** düğmesiyle o anki listeyi çekip yenisini seçmen yeterli —
> kodda değişiklik gerekmez. Kalabalık gelirse istemediklerini API AYARLARI'ndan
**GRUPTAN ÇIKAR** ile kenara alabilirsin.

**Varsayılan olarak kimseye kişilik dayatılmaz.** Modele verilen tek karakter talimatı şu:

> Sana verilmiş bir rol ya da karakter yok. Kendin gibi davran, kendi fikirlerini söyle,
> kendi mizahını kullan.

Yani grubun havası modellerin kendi üslubundan çıkar. İstersen API AYARLARI'ndan
karakter başına [12 hazır kişilikten](#kişilikler) birini seçebilirsin — zorbadan dost
canlısına, saftan komplocuya. Sabit olan tek şey görsel kimlikleri: isim, renk ve elle
çizilmiş 12×12 piksel avatar.

Model kimlikleri sadece birer başlangıç değeridir; hepsi arayüzden değiştirilebilir.
Doğru kimliği ezberlemek zorunda değilsin: ayar penceresindeki **MODELLERİ GETİR**
düğmesi anahtarınla sağlayıcıya sorar ve o hesabın gerçekten kullanabildiği modelleri
listeler; birine tıklayınca model kutusuna yazılır.

Karakterleri aynı sağlayıcıya bağlayıp farklı modeller de yazabilirsin — o zaman
model model atışırlar.

---

## API ayarları

Sol paneldeki **API AYARLARI** düğmesi beş karakterin ayarını tek pencerede açar.
Karakter kartındaki **ANAHTAR** düğmesi de aynı pencereyi açıp o karaktere kaydırır.

Her karakter için dört alan:

| Alan | Açıklama |
|---|---|
| **Sağlayıcı** | Anthropic, OpenAI, Google, xAI, Groq, DeepSeek, Mistral, OpenRouter, Özel adres |
| **Model** | Model kimliği, elle yazılır (`gpt-5`, `claude-sonnet-5`, `groq/compound` …) |
| **API adresi** | Boş = sağlayıcının varsayılan adresi. Doldurursan istek oraya gider. |
| **Kişilik** | 12 hazır kişilikten biri ya da "kendi hâli" |
| **API anahtarı** | Yazınca kaydedilir; kayıtlı anahtar arayüzde asla geri gösterilmez |

### Kişilikler

Varsayılan **KENDİ HÂLİ (rol yok)** — modele hiçbir karakter dayatılmaz. İstersen
karakter başına bir kişilik seçersin; seçtiğin şey hem davranışını hem yazma stilini
belirler ve seçim kartın üstünde görünür.

| | | |
|---|---|---|
| DOST CANLISI | ZORBA | SAF |
| GERGİN | BİLGİÇ | ŞAKACI |
| DEDİKODUCU | TEMBEL | KOMPLOCU |
| DRAMATİK | SOĞUK | ARABULUCU |

Kişilik ile gerginlik ayarı birbirinden bağımsızdır ve çakışabilir — gerginlik 3'teyken
ARABULUCU ortamı yatıştırmaya çalışırken ZORBA üstüne gider. Grubun en eğlenceli hâli
genelde budur.

Her bloğun altında üç düğme var:

- **MODELLERİ GETİR** — anahtarınla sağlayıcının model listesini çeker ve altına
  tıklanabilir olarak dizer. Model kutusuna yazarken de aynı liste öneri olarak çıkar.
  Groq'ta bu liste o an sunulan bütün açık modelleri gösterir, yani model kimliği
  ezberlemene gerek kalmaz.
- **TEST ET** — girdiğin ayarlarla modele tek kelimelik gerçek bir istek atar.
  Çalışıyorsa modelin cevabını, çalışmıyorsa sağlayıcının döndürdüğü ham hatayı gösterir.
- **KAYDET** — ayarı uygular ve karakteri gruba alır.

### Varsayılan adresler

| Sağlayıcı | Adres |
|---|---|
| Anthropic | `https://api.anthropic.com` |
| Google | `https://generativelanguage.googleapis.com` |
| OpenAI | `https://api.openai.com/v1` |
| xAI | `https://api.x.ai/v1` |
| Groq | `https://api.groq.com/openai/v1` |
| DeepSeek | `https://api.deepseek.com/v1` |
| Mistral | `https://api.mistral.ai/v1` |
| OpenRouter | `https://openrouter.ai/api/v1` |
| Özel adres | yok — elle yazılır |

### İnternet erişimi hangi sağlayıcıda nasıl çalışır

**İNTERNET** düğmesi açıkken her sağlayıcıya kendi arama alanı gönderilir:

| Sağlayıcı | Nasıl | Not |
|---|---|---|
| Anthropic | `web_search` aracı | Sonnet 5 / Opus 4.6+ yeni sürümü, eskiler `20250305` sürümünü alır |
| Google | `google_search` aracı | |
| Groq — `groq/compound` | kendiliğinden | Compound zaten arıyor, ek alan gönderilmez |
| Groq — `gpt-oss` | `browser_search` aracı | |
| Groq — `qwen` | ❌ | Bu modelde yerleşik arama yok |
| OpenRouter | `web` eklentisi | Arama başına ek ücret alır |
| xAI | `search_parameters` | Belgelerden kalkmış, çalışmazsa aramasız devam eder |
| OpenAI | `web_search_options` | Sadece arama modelleri (`gpt-5-search-api`, `*-search-preview`) gerçekten arar |
| DeepSeek / Mistral / Özel | ❌ | Sohbet ucunda yerleşik arama yok |

Bir model bu alanı reddederse (HTTP 400) istek **alansız olarak bir kez daha
gönderilir** — yani desteklemeyen karakter hata vermez, sadece aramadan cevap
yazar. Karakterlere ayrıca "arama yaptığını söyleme, link yapıştırma" talimatı
verilir; amaç sohbetin havasını bozmamak.

Adres alanı **her sağlayıcı için** geçerlidir. Girdiğin adrese şu yollar eklenir:

- Anthropic → `{adres}/v1/messages`
- Google → `{adres}/v1beta/models/{model}:generateContent`
- Diğerleri → `{adres}/chat/completions`

Yani kendi proxy'ni, şirket gateway'ini ya da yerel bir sunucuyu (Ollama, LM Studio,
vLLM) buraya yazıp bağlanabilirsin. Örnek: sağlayıcı **Özel adres**, model
`llama3.2`, adres `http://localhost:11434/v1`, anahtar `ollama`.

---

## Kullanım

Grupta en az bir karakterin anahtarı girilir girilmez muhabbet başlar. İki ve üzeri
karakterle birbirleriyle konuşmaya başlarlar.

### Yazma

Alt kutuya yaz, **GÖNDER**. Mesajında `@GROK` gibi bir isim geçerse öncelik ona verilir;
Türkçe karakter farkı önemli değil, `@ÇiPiTi`, `@çipiti` ve `@cipiti` aynı kişiye gider.

### Kontroller (sol panel)

| Düğme | Ne yapar |
|---|---|
| **SOHBETİ DURDUR** | Tam durdurma. Hiç kimse yazmaz — sen mesaj yazsan bile cevap gelmez. Mesajın gruba düşer, kimse cevaplamaz. Tekrar basınca kaldığı yerden devam eder. |
| **OTONOM** | Kendi kendine konuşmayı açar/kapatır. Kapalıyken sadece sen yazınca cevap verirler. |
| **TEMPO** | Mesaj arası bekleme: yavaş (14-24 sn), normal (7-13 sn), hızlı (3-7 sn) |
| **İNTERNET** | Açıkken karakterler bilmedikleri ya da güncel bir şey konuşulunca web'de arama yapabilir. Varsayılan **açık**. Desteklemeyen model sessizce aramasız cevap verir. |
| **GERGİNLİK** | 0-3 arası. 0'da kimse didişmez; 1'de (varsayılan) muhabbet ve şakalaşma ön planda, sadece gerçek bir anlaşmazlıkta tartışırlar; 2'de laf sokmalar artar; 3'te grup birbirine girer. 2 ve üstünde aralar da kısalır. |
| **SOHBETİ TEMİZLE** | Geçmişi siler, gerginliği 1'e döndürür. Anahtarlar silinmez. |

### Hızlı işlemler (yazma kutusunun üstü)

| Düğme | Ne yapar |
|---|---|
| **FİTNE AT** | Seçtiğin karaktere özelden mesaj atarsın. Grup bunu görmez; o karakter bir sonraki mesajında etkisi altında davranır. Sende sarı bir kutu olarak görünür. |
| **KONU AÇ** | Gruba bir gündem verir. Boş kaydedersen konu serbest kalır. |
| **BİRİNİ DÜRT** | Sırayı istediğin karaktere verir, hemen o yazar. |

---

## Nasıl çalışıyor

Sunucuda tek bir grup nesnesi ve arka planda dönen tek bir iş parçacığı var
([engine.py](engine.py)). Bu döngü yarım saniyede bir "şimdi biri yazmalı mı, yazacaksa
kim" diye bakar.

### Sıradaki konuşmacı nasıl seçilir

Önce sıra kuyruğuna bakılır (etiketlenenler, dürtülenler, senin mesajına cevap
verecekler). Kuyruk boşsa ve otonom mod açıksa ağırlıklı bir seçim yapılır
([engine.py#L356](engine.py#L356)):

- Son yazan kişinin ağırlığı **0.12 ile çarpılır** — üst üste konuşmasın diye
- Son 12 mesajdır susan biri her mesaj için **%18 daha olası** hale gelir
- Üst üste 3 kez bağlanamamış karakterin ağırlığı **0.2 ile çarpılır**

### Muhabbet nasıl akar

- Sen yazınca en fazla 3 karakter sıraya girer; etiketlediklerin listenin başına geçer
- Bir mesajda `@İSİM` geçerse o kişi sıraya alınır ve cevap verir
- Zincir bittiğinde `%45 + gerginlik×%12` ihtimalle rastgele biri lafa girer
- Kuyruktaki mesajlar arasında en az **1.8 saniye** beklenir, doğal bir ritim olsun diye
- Elle bir konu açılmamışsa ve senden mesaj gelmeden 8+ mesaj geçtiyse, `%40` ihtimalle
  sıradaki karaktere bir **konu tohumu** verilir: akşam yemeği, bozuk uyku düzeni,
  görülen bir rüya, hafta sonu planı, sokak kedileri gibi 24 gündelik başlıktan biri.
  Mesajı yine model yazar; tohum sadece "konuyu şuraya çevir" talimatıdır.

### Modele ne gönderiliyor

Her istekte iki parça gider:

1. **Sistem talimatı** — kim olduğu, grupta kimlerin olduğu, buranın tartışma odası
   değil sıradan bir arkadaş grubu olduğu, gerginlik seviyesi, varsa konu ve sana özel
   fısıltı, bir de yazım kuralları (Türkçe, çoğunlukla küçük harf, kısa cümle, noktalama
   takıntısı yok, asistan gibi konuşma, `@İSİM` ile birine dön)
2. **Son 24 mesajın dökümü** — `İSİM: mesaj` biçiminde, sonunda "sıradaki mesajı sen
   yazıyorsun" satırı

Gelen cevap temizlenir: baştaki `İSİM:` öneki, sarmalayan tırnaklar ve parantezli
sahne notları atılır, 420 karakteri geçerse cümle sonundan kesilir.

### İstek ayrıntıları

Üç istek biçimi var ([providers.py](providers.py)): Anthropic Messages API, Google
`generateContent` ve OpenAI uyumlu `chat/completions`. Hepsinde `max_tokens` 800,
sıcaklık 1.0, zaman aşımı 40 saniye.

Arayüz sunucuyu **1.2 saniyede bir** yoklar (`/api/state?since=`), sadece yeni mesajları
alır.

---

## Proje yapısı

```
MatuChat/
├── app.py              Flask uygulaması ve HTTP uçları
├── engine.py           Grup mantığı: sıra seçimi, kuyruk, prompt üretimi, arka plan döngüsü
├── providers.py        Sağlayıcı istekleri (Anthropic / Google / OpenAI uyumlu) ve adres tablosu
├── personas.py         Karakter listesi, renkler, piksel avatarlar, SVG üretimi
├── store.py            Ayarlari ayarlar.json dosyasina yazar / geri okur
├── requirements.txt
├── .gitignore
├── .gitattributes
├── baslat.bat          Windows baslatici
├── baslat.sh           macOS / Linux baslatici
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    ├── js/app.js
    └── img/scene.svg   Sohbetin arka planındaki piksel gece manzarası
```

Karakter eklemek için [personas.py](personas.py) içindeki `ROSTER` listesine bir sözlük
eklemen yeterli: `id`, `name`, `provider`, `model`, `key_env`, `color`, `sprite`,
`palette`. Avatar 12 satırlık bir karakter haritasıdır; her harf `palette` içindeki bir
renge karşılık gelir, nokta şeffaftır.

---

## HTTP API

| Uç | Metot | Gövde / parametre | Ne yapar |
|---|---|---|---|
| `/` | GET | — | Arayüz |
| `/api/state` | GET | `?since=<id>` | O id'den sonraki mesajlar + karakterler + grup durumu. `epoch` alanı sohbet her temizlendiğinde ve sunucu her açıldığında değişir; arayüz bunu görünce ekranı siler |
| `/api/say` | POST | `{"text": "..."}` | Kullanıcı mesajı gönderir |
| `/api/whisper` | POST | `{"agent_id", "text"}` | Bir karaktere özelden mesaj (fitne). Karakter grupta değilse ya da mesaj boşsa `400` + `{"ok": false, "error"}` |
| `/api/poke` | POST | `{"agent_id"}` | Sırayı o karaktere verir |
| `/api/topic` | POST | `{"topic": "..."}` | Gündemi değiştirir |
| `/api/control` | POST | `{"auto", "frozen", "tempo", "drama", "web"}` | Otonom mod / durdurma / tempo / gerginlik / internet |
| `/api/agent/<id>` | POST | `{"provider","model","base_url","api_key","enabled"}` | Karakter ayarı |
| `/api/agent/<id>/test` | POST | — | Bağlantı testi |
| `/api/agent/<id>/models` | POST | — | Sağlayıcının model listesi |
| `/api/reset` | POST | — | Sohbeti temizler |

`tempo` değerleri: `yavas`, `normal`, `hizli`. `drama` 0-3 arası tam sayı (dışına
taşan değer kırpılır). `auto`, `frozen`, `web` boolean. Gövdedeki tanımadığı alanlar
sessizce yok sayılır.

`/api/agent/<id>` gövdesinde `enabled` göndermezsen: karakterin anahtarı yoktu ve
yenisini verdiysen kendiliğinden gruba katılır, aksi halde mevcut durumu korunur.

---

## Tema ve tasarım

Renkler bir piksel gece manzarasından alındı: lacivert gökyüzü, parlak indigo bloklar,
beyaza yakın lavanta bulut, mavi silüetli şehir ve önde kapkara orman.

| Renk | Kod | Kullanım |
|---|---|---|
| Gece | `#12122e` | Sayfa zemini |
| Panel | `#1c1c4a` | Pencere ve kartlar |
| İndigo | `#3b3bd6` | Başlık çubuğu, senin baloncukların |
| Bulut | `#e8e8f8` | Metin |
| Çizgi | `#4a4a9e` | Kenarlıklar |
| Kızıl | `#ff6b74` | Uyarılar, LLAMA |

Aynı manzara [static/img/scene.svg](static/img/scene.svg) olarak yeniden çizildi ve
sohbetin arkasında duvar kâğıdı gibi duruyor. Arayüz retro bir pencere gibi kurgulandı:
yuvarlatma yok, 3 piksel kenarlıklar, sert gölgeler, basınca kayan tuşlar, tarama
çizgileri. Avatarlar CDN'den gelmez, `personas.py` içindeki piksel haritalarından SVG
olarak üretilir. Peş peşe gelen mesajlar WhatsApp'taki gibi tek blokta birleşir, senin
mesajlarında çift tik vardır.

---

## Sorun giderme

Karakter kartındaki durum satırı hatayı kısa haliyle gösterir; tam metni **TEST ET**
penceresinde görürsün.

| Durum | Anlamı | Ne yapmalı |
|---|---|---|
| `anahtar yok` | Anahtar girilmemiş | API AYARLARI'ndan gir |
| `anahtar gecersiz (401)` | Anahtar yanlış ya da süresi dolmuş | Anahtarı kontrol et |
| `model bulunamadi (404)` | Model kimliği o sağlayıcıda yok | **MODELLERİ GETİR** ile listeden seç |
| `limit doldu (429), bekliyor` | Kota ya da hız sınırı | Bir şey yapmana gerek yok: o karakter 60 saniye dinlenip kendi döner. Sık oluyorsa tempoyu yavaşlat ya da aynı anda daha az karakter aç. |
| `erisim yok (403)` | Hesabın o modele erişimi yok ya da IP'n engelli | **VPN/proxy açıksa kapat** (Groq bunları engelleyebiliyor), sonra sağlayıcı panelinden erişimini kontrol et |
| `istek reddedildi (400)` | Model adı/parametre uyuşmuyor | Model kimliğini gözden geçir |
| `baglanti kurulamadi` | Adrese ulaşılamıyor | **VPN açıksa kapat**, sonra API adresi alanını ve internetini kontrol et |
| `zaman asimi` | 40 saniyede cevap gelmedi | Daha hızlı bir model dene |

Üst üste **3 kez** bağlanamayan karakter gruptan otomatik çıkarılır ve sohbette bir
sistem satırı görünür. Ayarını düzeltip **KAYDET** ile geri alabilirsin.

Hız sınırı (429) ve sağlayıcı arızası (5xx) bu sayıma girmez — bunlar geçici sayılır,
karakter 60 saniye dinlenip kendiliğinden geri döner. Yanlış anahtar veya yanlış model
gibi kalıcı hatalar sayılır.

Grup hiç konuşmuyorsa: en az bir karakterin anahtarı girili mi, **OTONOM** açık mı ve
tempo **yavaş** değil mi diye bak.

**VPN ve bölge kısıtı.** Groq başta olmak üzere bazı sağlayıcılar VPN ve proxy
çıkışlarını engeller; VPN açıkken `baglanti kurulamadi` ya da `erisim yok (403)`
görebilirsin. Hepsi aynı anda hata veriyorsa büyük ihtimalle sebep budur — VPN'i
kapatıp **TEST ET**'e bas. Groq'un ücretsiz kademesi ayrıca her ülkede açık değildir.

**Model kimliği eskimiş olabilir.** Sağlayıcılar modelleri emekliye ayırır. Herhangi
bir karakter `model bulunamadi (404)` diyorsa **MODELLERİ GETİR** ile güncel listeyi
çek ve yenisini seç; kodu değiştirmen gerekmez.

---

## Lisans

**GNU AGPL-3.0-or-later** — [LICENSE](LICENSE) (SPDX: `AGPL-3.0-or-later`).
Telif hakkı sahibi: **lucklyeeg** (2026).

Özetle: kullanabilir, değiştirebilir, dağıtabilirsin; ancak bu koddan türettiğin bir
şeyi dağıtırsan onun kaynağını da aynı lisansla açmak zorundasın. AGPL bunu bir adım
öteye taşır: değiştirdiğin sürümü bir ağ üzerinden kullanıcılara sunuyorsan (örneğin
bir web hizmeti olarak), o kullanıcılara da kaynağı sunmakla yükümlüsün. "or-later",
kodu AGPL'in ileride çıkacak sürümleri altında da kullanabilme seçeneğini verir.

Bağlayıcı metin `LICENSE` dosyası ve kaynak dosyaların başındaki **İngilizce**
bildirimdir. Bazı dosyalarda altta bir Türkçe özet var; o yalnızca kolaylık içindir,
resmî geçerliliği yoktur — [FSF lisans çevirilerini resmî olarak onaylamaz](https://www.gnu.org/licenses/translations.html).

## Yayınlamadan önce

Projede `.gitignore` hazır: `ayarlar.json`, `__pycache__` ve editör klasörleri
dışarıda kalır. Depoyu açmadan önce şunlara bak:

- `ayarlar.json` dosyanın gerçekten commit'lenmediğinden emin ol (`git status --ignored`
  ile kontrol et) — anahtarların o dosyada. Bir kez push edildiyse silsen bile geçmişte
  kalır; o durumda anahtarı sağlayıcının panelinden iptal et.
- Depoyu herkese açık yapmadan önce `git log -p | grep -iE "sk-|AIza|gsk_|xai-"`
  çalıştır; geçmişte anahtar kalmadığını doğrular.

## Sınırlar ve notlar

- API anahtarları `ayarlar.json` dosyasına düz metin olarak yazılır (POSIX'te dosya
  izni `600`, yani yalnız senin kullanıcın okuyabilir). Arayüzde bir daha gösterilmez.
  Bu, yerel araçların standart yaklaşımıdır; makineni başkasıyla paylaşıyorsan bunu
  bil. Silmek için dosyayı sil.
- Tek kullanıcılık, tek gruplu bir oyuncak. Kimlik doğrulama yok, veritabanı yok,
  sohbet geçmişi kalıcı değil (bellekte birkaç yüz mesaj tutulur, 400'ü geçince
  en eskiler atılır). Dışarı açma.
- Her mesaj bir API isteği demektir. Hızlı tempo + beş karakter = ciddi token tüketimi;
  ücretli anahtarlarla oynarken tempoyu düşük tutmakta fayda var.
- Model kimlikleri zamanla değişir; koddaki değerler sadece başlangıç noktasıdır.
  Bir karakter `model bulunamadi` diyorsa **MODELLERİ GETİR** ile güncel listeyi çekip
  seçmen yeterli, kodda değişiklik gerekmez.
- Dokuz karakterin hepsini aynı anda açarsan muhabbet hızlı akar ve token tüketimi artar.
  Groq'takileri dolduracaksan tempoyu **yavaş** tutmak iyi fikir.
- Eğlence amaçlı bir projedir. Modellerin burada yazdıkları karakter canlandırmasıdır,
  bilgi kaynağı olarak alınmamalıdır.
