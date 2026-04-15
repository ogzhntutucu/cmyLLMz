# Karakterler

- zeki, vedat, alpay, ramazan
- aziz vefa, lemi galip
- jack, bayan 1
- haydut 1, johnny lesh, haydut 2
- kizilderili 1, kizilderili 2, kenan, richard thomas
- ulak, redkit
- Silah Saticisi, Bayanlar, Zorba, Esnaflar
- Serif 1, Serif Cheko
- Peder, Şerif Murphy, Trenci Jack, Gardiyan, Deli
- Suzan Van Dyke
- serif lloyd, Macaulay, Betty

# opsiyonel kisimlar

- bulut llm gemini yerine baska llm apisi de olabilir. o mecburi degil.
- local llm'i de deneyerek uygun olani bulup karar verecegiz. ollama veya orada yazanlardan baska biri olmasi mecburi degil.
- chunklari okuyup duzenleme yapacak olan llm modelini iyi secelim. cok hafif bir modelle calisip da kalitesiz cikti almayalim. bi kere yapacagiz zaten, duzgun bi modelle calisalim. bunu claude yapabilirse zaten guzel olabilir ama onu da cok para etmeyecek sekilde secmek lazim.


# TO DO

- biz bu proje icin yahsi bati filmini ve gerek olursa internetten elde edecegimiz bilgileri kullanacagiz. yani hocalara sunulacak olan kisim sadece yahsi batiyi kapsiyor. ama aslinda proje kapsami yahsi bati ile sinirli degil aslinda. bu proje llm'in cem yilmaz'la baglantili mizahi anlayabilmesi icin planlaniyor, o yuzden adi cmyllmz. yani cem yilmazin baska filmleri, gosterileri, karikaturleri, konuk oldugu programlarda yaptigi sakalari vs. cem yilmaz kulliyatini icerecek zamanla. bu sayede cem yilmaz'in mizahini bilen bir rag sistemi olacak. her turlu llm ile calisabilir hale gelecek.
- rag anything ile belki filmin gorsellerini, sesini de rag'a dahil edebiliriz sonra?
- derslerin sunumu icin bizden arayuz tasarlamamiz isteniyor, o sebeple streamlit kullanip arayuz tasarlayacagiz. yoksa bu projeyi (rag sistemini) kullanmak icin bir arayuze gerek yoktur diye tahmin ediyorum. local llm icin de bulut llm icin de bu rag sistemini kullanmanin best practice'i her ne ise, proje sunumlarini yaptiktan sonra ona gecebiliriz.
- bu proje llm'lerin mizahi dogru yorumlayabilmesini, saka yapabilmesini, sakalari anlayabilmesini, sakalarin devamini getirebilmesini vs. saglamak amaciyla yapiliyor. bu yuzden eger cem yilmaz ozelinde bunu basarabilirsek, baska komedyenler, mizah kisilikleri icin de boyle rag sistemleri kurulabilir, bu rag sistemleri birlestirilerek llm'lerin global sekilde mizahi anlayabilmesi saglanabilir.

---

## 🎬 Filmi izlerken doldurman gereken 4 alan

### 1. `note` — Sahne notu (1-3 cümle)

Sahnenin ne anlattığını, komik olan şeyi, dikkat çeken detayı kısa yaz. LLM bu notu okuyarak mizah analizi yapacak, bu yüzden **espriyi açıklayan** notlar çok değerli.

**İyi not örnekleri** (senin yazdıkların):
```
yb_002: "alpay 'istersen sey yapalim' diyerek zekiyi tesvik ediyor. 
zeki karakteri posetteki cizmeyi cikariyor. cizmenin hikayesini 
ortama anlatmaya basliyor."

yb_012: "haydutlardan birisi ingilizce bir ifade kullaniyor. tam bu 
sirada filmdeki flashback bozuluyor ve hikayeyi anlatan zeki 
karakterinin tarihine donuyoruz. ramazan ingilizce kismini 
anlamadigini soyluyor. zeki filmi ingilizceden turkceye aliyor."
```

**Boş olan bir chunk için örnek** — `yb_082` (text: *"Ayağın biri arızalı olunca tabii... Buyrun. Öyle ahım şahım bir kilise değil..."*):
```json
"note": "lemi ve aziz kasabaya ulastiktan sonra kiliseye gidiyorlar. 
peder onlari karsilarken lemi'nin topallayarak yurudugunu gorup 
espri yapiyor."
```

---

### 2. `characters` — Sahnede konuşan karakterler

Sahnede **konuşan** (veya aktif rol alan) karakterlerin listesi. `hatalar.md` dosyandaki karakter listesini referans al.

```json
"characters": ["Aziz Vefa", "Lemi Galip", "Peder"]
```

> **Dikkat:** İsim tutarlılığı önemli. Her yerde aynı ismi kullan. Örneğin "Şerif Lloyd" mı, "serif lloyd" mı? Büyük/küçük harf biçimini standartlaştır.

---

### 3. `scene_type` — Sahne türü

5 seçenekten birini yaz:

| Değer | Ne zaman? | Örnek |
|---|---|---|
| `frame_story` | Rakı masası sahneleri (günümüz) | Zeki'nin hikaye anlattığı kısımlar |
| `flashback` | Osmanlı/Vahşi Batı canlandırmaları | Ana hikaye — Aziz ve Lemi'nin maceraları |
| `action` | Kavga, kaçış, silahlı çatışma | Haydut baskını, kızılderili karşılaşması |
| `transition` | Yolculuk, sahne geçişi, bekleme | Harita üzerinde rota gösterimi |
| `emotional` | Ciddi/duygusal anlar | Karakterlerin ciddi konuşmaları |

**Şu an sadece 12 chunk `frame_story` olarak işaretli**, geri kalan 160 chunk boş. Büyük çoğunluğu `flashback` olacak çünkü filmin ana hikayesi flashback.

**Örnek:**
```json
// yb_006 — Lemi ve Jack'in arabada sohbeti
"scene_type": "flashback"

// yb_010 — Haydut baskınında Aziz herkesi sakinleştirmeye çalışıyor  
"scene_type": "action"

// yb_004 — Dünya haritasında rota + film introsu
"scene_type": "transition"
```

---

### 4. `location` — Sahnenin geçtiği mekan

Kısa, tutarlı mekan adları yaz. Aynı mekanı farklı chunk'larda aynı isimle yaz.

**Önerilen mekan isimleri** (filmi sen daha iyi biliyorsun ama genel hatlarıyla):

```
"Rakı masası"            — Çerçeve hikaye sahneleri
"Posta arabası"          — Yolculuk sahneleri
"Kasaba meydanı"         — Kasaba sahneleri  
"Kilise"                 — Peder'in kilisesi
"Şerif ofisi"            — Şerif'in bürosu
"Salon (bar)"            — Western bar
"Çöl yolu"               — Dış mekan yolculuk
"Kızılderili kampı"      — Kızılderili sahneleri
"Saray"                  — Sultan sahnesi (flashback içi flashback)
```

**Örnek:**
```json
// yb_001 — Alpay hikaye anlatıyor, rakı içiliyor
"location": "Rakı masası"

// yb_006 — Lemi, Aziz, Jack ve bayan arabada
"location": "Posta arabası"

// yb_026 — Kızılderili Richard Thomas kendini tanıtıyor
"location": "Çöl yolu"
```

---

### 5. `text` düzeltmeleri

Text alanının çoğu zaten düzeltilmiş (87 chunk'ta `-` işaretleri eklenmiş). Ama izlerken şunlara dikkat et:

- **Yanlış bölünmüş chunk'lar**: Bir espri iki chunk'a bölünmüşse → birleştir
- **Eksik replikler**: SRT'den kaçan diyalog varsa → ekle
- **Karışmış diyaloglar**: Kim ne dedi belli değilse → `- ` işaretleriyle ayır

---

## ⏸️ Şimdilik DOKUNMA — Sonraya bırakılacak alanlar

| Alan | Neden? |
|---|---|
| `related_chunks` | Tüm chunk'lar hazır olduktan sonra ikinci geçişle doldurulacak |
| `humor_analysis` | LLM (Gemini) otomatik dolduracak |
| `entities` | NER scripti otomatik dolduracak |
| `summary` | LLM otomatik dolduracak |

---

## 🎯 Pratik iş akışı önerisi

1. **Filmi aç**, JSON dosyasını yanında tut
2. **yb_082'den başla** (note'ları burada bırakmışsın)
3. Her sahne için hızlıca doldur:
   - `note`: 1-2 cümle, ne oluyor + komik olan ne
   - `characters`: kim konuşuyor
   - `scene_type`: 5 değerden biri
   - `location`: kısa mekan adı
4. Bir yandan da `characters` ve `scene_type` boş olan **eski chunk'ları** (yb_001–yb_081 arası) tamamla — özellikle `scene_type` ve `location`

Çalışma hızın: chunk başına 1-2 dakika yeterli. 97 boş note = ~2-3 saat film izleme. Zaten doldurulmuş 75 chunk'a `scene_type` ve `location` eklemek ~30-40 dakika.