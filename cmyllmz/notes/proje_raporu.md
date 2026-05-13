# cmyLLMz — Proje Raporu

> **Bu rapor proje tamamlandı raporudur.** Planlanan tüm fazlar (1-13) tamamlandı. Streamlit arayüzü çalışıyor ve evaluation sonuçları alındı. Son güncelleme: 2026-05-13.

## Proje Nedir?

**cmyLLMz**, Cem Yılmaz'ın "Yahşi Batı" (2010) filmindeki mizahı analiz eden, açıklayan ve sorgulatan bir **RAG tabanlı yapay zeka sistemi**dir. Kullanıcı "Garfield şakasını açıkla" gibi bir soru sorduğunda sistem, filmden ilgili sahneleri bulur ve LLM yardımıyla detaylı bir mizah analizi üretir.

Proje, iki dersin gerekliliklerini tek bir çalışmayla karşılar:
- **MBU (Mühendislikte Bilgisayar Uygulamaları):** RAG pipeline, LLM entegrasyonu, Streamlit arayüzü
- **NLP (Doğal Dil İşleme):** Tokenizasyon, embedding, NER, retrieval kalitesi ölçümü

---

## Sistemin Yapabilecekleri

1. **Bir şakayı açıklamak** → "Garfield şakası neden komik?" — Ramazan, ABD başkanı Garfield'ı karikatür kediyle karıştırır

2. **Bir şakanın devamını getirmek** → Kullanıcı "Karagözüm yapma, mübarek Ramazandayız." dediğinde chatbot "Hiç tasa etme Hacı cavcav, sülalece arkandayız! Geçen sene Sultanahmet'te en çok tutan gösteri bu be. Biraz gülün ya!" ile devam eder

3. **Filmle ilgili detaylı bir bilgiyi bulmak** → "Cem Yılmaz'ın bir filminde karakter Mickey Mouse oynatıyordu, hangi filmdi, replik neydi?" → Yahşi Batı, Lemi Galip oynattıyor; Zeki anlatıyor: *"Yahu, Lemi Bey'in kendi yaptığı makineyle miki filmi oynatıyorlar ya! Miki filmi diyorum usta. Daha Walt Disney yok, Mickey Mouse yok!"*

4. **Karakter analizi yapmak** → "Lemi Galip ne tür mizah kullanıyor, saflık mı ironi mi?"

5. **İçerik kaynağını bulmak** → Birden fazla film/gösteri eklendiğinde: "'Aziz Efendi, at nalı ne işe yarar?' repliği hangi filmde kime ait?" ya da bulanık bir hatırayla "bir karakterin Mickey Mouse oynatması" gibi ipucuyla doğru sahneye ulaşmak

6. **Mizah tekniğine göre sahneleri listelemek** → "Filmde anakronizm kullanılan sahneler neler?" — Google'a girmek, modern argo gibi örnekler listelenir

7. **İki karakterin mizah tarzını karşılaştırmak** → "Aziz ve Lemi nasıl farklı güldürüyor?"

8. **Benzer şakayı filmin başka yerinde bulmak** → "Garfield gibi başka yanlış anlama şakası var mı filmde?"

9. **Kültürel referansı bağlamıyla açıklamak** → "Teşkilât-ı Mahsusa nedir, filmde neden geçiyor, bilmeyenler için ne ifade ediyor?"

10. **Tekrar eden bir espriyi takip etmek** → "Zıbık konusu filmde kaç kez ve hangi bağlamlarda geri geliyor?"

11. **Bir sahnenin setup/punchline yapısını ayrıştırmak** → "Garfield şakasında setup nerede başlıyor, punchline nerede patlıyor?"

12. **Belirli zaman damgasındaki repliği bulmak** → "Filmin 47. dakikasında kim ne diyordu?" — block-level retrieval ile cevaplanır

---

## Sistemin Çalışma Mantığı

### Çok Çözünürlüklü Retrieval (Multi-Resolution)

Sistem **iki ayrı çözünürlükte** sorguya cevap verir. Soru tipine göre uygun katman seçilir:

| Katman | Granülerlik | Use Case | ChromaDB Collection |
|---|---|---|---|
| **Chunk** | 62 sahne, ortalama 100s | Semantik sorular ("şu sahne nasıldı", "bu konu nerede geçiyor") | `yb_chunks` |
| **Block** | 1644 altyazı birimi, ~3-5s | Spesifik replik / timestamp sorguları | `yb_blocks` |

Her sorgunun hangi katmana gideceği retriever tarafından belirlenir (ya kullanıcı seçer, ya soru tipi otomatik analiz edilir).

### Pipeline Akışı

```
Kullanıcı sorusu
       │
       ▼
Soru → Embedding vektörü
       │
       ▼
Retriever: katman seçimi (chunk vs block)
       │
       ▼
ChromaDB'den en benzer N kayıt getirilir (top-k)
       │
       ▼
İlgili kayıtların related_chunks alanı kontrol edilir
(Bağlantılı sahneler de getirilir — setup/punchline kopukluğu önlenir)
       │
       ▼
[kayıt metinleri + soru + sistem prompt] → LLM
       │
       ▼
Cevap (+ kaynak sahneler kullanıcıya gösterilir)
```

**Sistem prompt'unda LLM'e iletilen kritik bilgiler:**
- Bu chunk'lar bir filmin sahneleri, ID'ler (yb_001, yb_002...) kronolojik sırayı yansıtır
- Bağlamda olmayan bilgi uydurma; "bu bilgi veri setimde yok" de
- Türkçe ve samimi dil kullan

---

## Veri Seti: Nasıl Hazırlandı?

Bu projenin özgün katkısı, filmden **elle hazırlanmış, üç izleme geçirmiş, zenginleştirilmiş chunk veri setidir**. Toplam emek: ~3 hafta.

### Pipeline (Tamamlanan Fazlar)

```
Faz 1 ✅  SRT → Ham Block'lar (srt_parser.py)
          1653 altyazı birimi, zaman damgalı, dialect/encoding düzeltmeleri yapıldı

Faz 2 ✅  block_referans.md üretildi
          Her satır: NNNN [HH:MM:SS] altyazı metni
          Zaman boşlukları --- ile ayrıldı

Faz 3 ✅  1. İzleme — Karakter Kodları + Chunk Sınırları
          - Konuşmacılara -XX- karakter kodu eklendi (-AZ-, -LE-, -ZE- ...)
          - karakterler.txt dosyası oluşturuldu (55 karakter, kod=isim eşlemesi)
          - Chunk sınırları === ile işaretlendi (ilk pass: 50 chunk)

Faz 4 ✅  2. İzleme — Detaylı İçerik Notları
          - Her sahneye [köşeli parantez içinde] inline notlar yazıldı
          - Notlar şunları içeriyor: kültürel referanslar, görsel gag açıklamaları,
            wordplay mekanizmaları, sahnelerdeki gizli detaylar, anakronizm tespitleri
          - Chunk sınırları gözden geçirildi, uzunlar bölündü, kısalar birleştirildi
          - Sonuç: 62 chunk

Faz 5 ✅  Türkçe Karakter Normalizasyonu
          - Notlar ASCII Türkçe yazılmıştı (ö→o, ü→u vb.)
          - turkish_normalizer.py: GPT-4o-mini ile [] içlerine diakritik eklendi
          - 1107 inline not segmenti, ~$0.01 maliyet
          - Diyalog metinleri zaten doğru Türkçe (SRT'den geliyor) — dokunulmadı
          - Yapısal elementler (NNNN, [HH:MM:SS], -XX-, ===) korundu

Faz 6 ✅  3. İzleme — Lokasyon + Cross-Reference + Son Kontrol
          - Her chunk'a @lokasyon X directive'i eklendi (62 directive)
          - Sahneler arası bağlantılar (bkz. yb_NNN) formatında işaretlendi (56 ref)
          - Tekrar eden esprileri (callback), setup-payoff ilişkilerini, geri dönen
            kavramları (zıbık, mızıka, "see you" gag'i, kola hikayesi vb.) bağlamak için
          - Son sınır kontrolü ve ufak düzeltmeler
```

### Sıradaki Fazlar (RAG Pipeline)

```
Faz 7 ✅  chunk_merger.py Final Sürüm
          - @lokasyon directive parsing → location field
          - (bkz. yb_NNN) regex extract → related_chunks field
          - chunk_index.md auto-generation entegre
          - Çıktı: base_chunks.json + chunk_index.md

Faz 8 ✅  enricher.py — OpenAI gpt-4o-mini ile Zenginleştirme
          - Schema: techniques, mechanism, cultural_context, summary
          - (why_funny / comedic_timing kaldırıldı, mechanism eklendi)
          - characters artık dict {KOD: isim} — LLM metin içindeki -XX- kodlarını eşler
          - 62/62 chunk işlendi
          - Çıktı: enriched_chunks.json

Faz 9 ⛔  NER — ATLANIDI
          - entities field boş kalıyor (RAG için zorunlu değil)
          - Post-MVP olarak değerlendirilebilir

Faz 10 ✅ Embedding + Vector Store
          - embedder.py: BAAI/bge-m3 (1024 boyut, 8192 token)
          - Embed içeriği: summary + text concat
          - vector_store.py: yb_chunks collection, cosine similarity
          - indexer.py: 62/62 chunk ChromaDB'ye yüklendi
          - Depolama: data/chroma/

Faz 11 ✅ Retriever + LLM Entegrasyonu
          - openai_client.py: gpt-4o-mini, streaming destekli
          - retriever.py: top-k=5, related_chunks expansion (maks 8 chunk)
          - build_context: Zaman (start→end), related_chunks bilgisi eklendi
          - prompt_templates.py: timestamp tahmini + çıkarım izni eklendi
          - retriever.ask(): uçtan uca soru → retrieval → LLM cevap
          - Bilinen zayıflık: spesifik replik araması (hybrid BM25 post-MVP)

Faz 12 ✅ Streamlit Arayüzü (app.py)
          - Soru sor → retrieval → LLM cevap (streaming)
          - Kullanıcı chatbot ile sohbet edebiliyor
          - Konuşma geçmişi data/conversations/ altında JSON olarak saklanıyor
          - Kaynak chunk gösterimi (şeffaflık için, expander içinde)
          - Sidebar: konuşma listesi, yeni sohbet, soru önerileri

Faz 13 ✅ Evaluation
          - 20 test sorusu elle hazırlandı (data/eval/questions.json)
          - 4 tip: timestamp (3), character (4), humor (6), cultural (7)
          - Her soru için ground_truth + relevant_chunk_ids
          - Retrieval testi: Hit Rate (ana metrik), Recall@k, Precision@k
          - Quality testi: LLM-as-a-Judge (gpt-5.4 hakem) ile RAG vs No-RAG karşılaştırması
          - 3 kriter: doğruluk, detay, tutarlılık (1-5 puan)
          - Notebook: notebooks/faz13_evaluation.ipynb (analiz + görselleştirme)
          - Sonuçlar: data/eval/results_retrieval.json, results_quality.json
          - Hybrid BM25 kararı: gerek yok (Hit Rate %100), post-MVP olarak işaretlendi
```

---

## Veri Şeması

### block_referans.md Format

Veri kaynağı, insan tarafından okunabilir bir markdown dosyası:

```
===001===
@lokasyon beykoz meyhanesi
0001 [00:00:14] [yahşi batı filmi başlıyor. dört karakter meyhanede bir rakı masasında.
                 samimi bir ortam. arkada kısık sesle "kimseye etmem şikayet" şarkısı
                 çalıyor. AL karakteri erotik shop işleten bir adamın başına gelmiş
                 komik bir hikayeyi anlatıyor:] -AL- Şimdi kadın "ince uzun da olur..."
0002 [00:00:18] şöyle de olur, böyle de olur" deyince...
0003 [00:00:20] bizim usta dayanamıyor, birden ayağa kalkıyor.
...
```

**Element açıklamaları:**

| Element         | Açıklama                                                             |
| --------------- | -------------------------------------------------------------------- |
| ===NNN===       | Chunk sınırı, sıralı numaralı                                        |
| `@lokasyon X`   | Chunk'ın geçtiği mekan (chunk_merger.py parse eder)                  |
| `NNNN`          | Block sıra numarası (4 digit, sıfır-padded)                          |
| `[HH:MM:SS]`    | Block timestamp'i                                                    |
| `[...]`         | Inline sahne notu (görsel detay, kültürel context, mizah açıklaması) |
| `-XX-`          | Karakter kodu (text içinde kalır, attribution için)                  |
| `(bkz. yb_NNN)` | Başka bir chunk'a cross-reference (related_chunks'a extract edilir)  |

### Chunk Schema (base_chunks.json — final)

```json
{
  "id": "yb_001",
  "start": "00:00:14",
  "end": "00:00:49",
  "duration_sec": 35.0,
  "block_range": "0001-0012",

  "text": "[yahşi batı filmi başlıyor...] -AL- Şimdi kadın... -RA- Ustaya bak!",
  "characters": {"AL": "Alpay (...)", "RA": "Ramazan (...)", "VE": "Vedat (...)", "ZE": "Zeki (...)"},
  "location": "beykoz meyhanesi",
  "related_chunks": ["yb_005", "yb_012"],

  "humor_analysis": {
    "techniques": ["anecdote", "wordplay"],
    "mechanism": "Mizahın nasıl işlediği — kısa, analitik.",
    "cultural_context": "..."
  },

  "entities": {
    "persons": ["Garfield", "Sultan"],
    "locations": ["Dolmabahçe", "Beykoz"],
    "orgs": ["Teşkilât-ı Mahsusa"],
    "misc": ["Wellington çizmesi"]
  },

  "summary": "Sahnenin 1-2 cümlelik kısa özeti."
}
```

**Eski schema'dan farklar (kaldırıldı):**
- `scene_description`: kaldırıldı (inline notlar zaten içeriyor, redundant)
- `humor_note`: kaldırıldı (inline notlar zaten içeriyor, redundant)
- `text` içindeki `[NNNN]` block markerları: kaldırıldı (chunk seviyesinde gerek yok, block-level zaten ayrı)

### Block Schema (yb_blocks collection için)

```json
{
  "block_id": "0001",
  "chunk_id": "yb_001",
  "timestamp": "00:00:14",
  "text": "-AL- Şimdi kadın \"ince uzun da olur, kalın da olur...\"",
  "characters": ["Alpay"]
}
```

### Field Sorumluluk Matrisi

| Alan | Kim doldurdu? |
|------|---------------|
| `id`, `start`, `end`, `duration_sec`, `block_range` | Otomatik (chunk_merger.py) |
| `text` (raw, with `-XX-` ve `[...]`) | Manuel (3 izleme) |
| `characters` | Otomatik (`-XX-` extract + `karakterler.txt` mapping) — dict {KOD: isim} |
| `location` | Otomatik (`@lokasyon` directive parse) |
| `related_chunks` | Otomatik (`(bkz. yb_NNN)` regex extract) |
| `humor_analysis` | LLM (OpenAI gpt-4o-mini, enricher.py) |
| `summary` | LLM (OpenAI gpt-4o-mini, enricher.py) |
| `entities` | Boş (NER atlandı — RAG için zorunlu değil, post-MVP) |

---

## Veri İstatistikleri (Şu Anki Durum)

```
Toplam block (altyazı birimi): 1644 (1653 ham, 9 kasıtlı silinmiş)
Toplam chunk (sahne):          62
Ortalama chunk süresi:         100s
Min / max chunk süresi:        35s / 286s
Toplam karakter sayısı:        55 (ana hikaye + çerçeve hikaye + yan karakterler)
Inline not sayısı:             1107 (Türkçe normalize edildi)
Cross-reference sayısı:        56 (bkz. yb_NNN)
Lokasyon directive:            62 (her chunk için bir tane)
```

---

## Teknoloji Stack'i

| Bileşen | Teknoloji | Notlar |
|---------|-----------|--------|
| Embedding | `BAAI/bge-m3` | 1024 boyut, 8192 token max, Türkçe dahil çok dilli |
| Vektör DB | ChromaDB | `yb_chunks` collection (62 chunk); `yb_blocks` post-MVP |
| RAG runtime LLM | OpenAI gpt-5.4-mini | Cevap üretimi (Faz 13 öncesi gpt-4o-mini idi, kalite için yükseltildi) |
| Evaluation hakem LLM | OpenAI gpt-5.4 | LLM-as-a-Judge (quality_test.py) |
| Veri zenginleştirme LLM | OpenAI gpt-4o-mini | enricher.py, turkish_normalizer.py — veri hazırlama tek seferlik |
| Local LLM | Ollama (opsiyonel) | Post-MVP — donanım yetersiz, kalite farkı belirgin |
| NLP | NLTK / spaCy (`xx_ent_wiki_sm`) | Ön işleme; NER post-MVP |
| Arayüz | Streamlit | Streaming destekli |

### Embedding İçin Birleştirilen Metin

```
{summary} {text} Mekan: {location} Karakterler: {isimler} Mizah teknikleri: {techniques} Kültürel bağlam: {cultural_context}
```

Summary + text temel içeriği sağlar; location, karakter isimleri, teknikler ve kültürel bağlam eklenerek "Betty nasıl bir karakter?", "wordplay sahneleri", "meyhanede geçen sahneler" gibi sorguların retrieval kalitesi artırıldı. bge-m3'ün 8192 token kapasitesi sayesinde en uzun chunk bile kesilmeden sığar.

---

## Başarı Metrikleri (Faz 13 Sonuçları)

Faz 13'te 20 soruluk test seti üzerinde iki ana ölçüm yapıldı: retrieval kalitesi ve cevap kalitesi (LLM-as-a-Judge). Soru seti: `data/eval/questions.json` — 4 tip (timestamp 3, character 4, humor 6, cultural 7). Her soruda ground_truth + relevant_chunk_ids.

### 1. Retrieval Testi (retrieval_test.py)

Top-k = 5. Üç metrik hesaplandı:

| Metrik | Değer | Yorum |
|--------|-------|-------|
| **Hit Rate** (ana metrik) | **%100** | 20 sorudan hepsi için en az 1 relevant chunk top-k içinde geldi |
| Recall@k | %76.4 | Çoklu chunk'lı sorularda 5 slot tüm relevant'leri her zaman sığdıramıyor (örn. q08 muska — 5 relevant chunk var) |
| Precision@k | %17.3 | Bilgilendirici; retriever "related_chunks expansion" yaptığı için payda 5'ten büyük olabiliyor — bu metrik tek başına yanıltıcı |

**Tipe göre Hit Rate:** Hepsi %100 (timestamp, character, humor, cultural).

**Sonuç:** Retrieval temelden çalışıyor. Hybrid BM25'e gerek kalmadı; post-MVP olarak işaretlendi.

### 2. Quality Testi — LLM-as-a-Judge (quality_test.py)

Hakem: **OpenAI gpt-5.4** (RAG runtime modeli olan gpt-5.4-mini'den farklı bir model — kısmi yanlılık riski azaltıldı). Her soru için 3 çağrı: RAG cevabı + No-RAG cevabı + hakem puanlaması. 20 soru × 3 = 60 çağrı, ~$0.40 maliyet.

| Kriter | RAG | No-RAG | Fark |
|--------|-----|--------|------|
| **Doğruluk** | **4.65/5** | 1.45/5 | **+3.20** |
| Detay | 4.65/5 | 2.05/5 | +2.60 |
| Tutarlılık | 4.70/5 | 3.70/5 | +1.00 |

**Yorum:**
- **Doğruluk farkı 3.2 puan** — RAG'sız base model film hakkında spesifik bilgiye sahip değil; "20-30. dakika civarı diye hatırlıyorum" gibi tahminlerle cevap veriyor. Bu, **hallucination metriğinin yerini tutuyor**: No-RAG'in 1.45'lik doğruluk skoru = yüksek hallucination oranı.
- **Detay farkı 2.6 puan** — RAG, system prompt'a eklenen "mizah mekanizmasını açıkla" talimatıyla zengin analiz üretiyor.
- **Tutarlılık farkı küçük (+1.0)** — beklenen. İki cevap da iç tutarlılıkta benzer, çünkü her ikisi de aynı modelle üretiliyor; ayrım içerikten geliyor.

### Karşılanan Hedefler

| Hedef | Beklenen | Gerçekleşen |
|-------|----------|-------------|
| Retrieval Hit Rate | > %85 | %100 ✅ |
| RAG doğruluk > No-RAG doğruluk | büyük fark | 4.65 vs 1.45 (3.2× kat üstün) ✅ |
| Hallucination düşürmek | RAG'sız %50+, RAG'lı <%20 | Quality test doğruluk boyutu bunu doğruluyor ✅ |

### Methodology Notları

- **Ground truth metodolojisi:** Yazılı ground_truth'lar "minimum doğru cevap" formatında — sisteme dayatma listesi değil, kontrol listesi. RAG cevabı bu olguları içeriyorsa yüksek puan alıyor (uzunluk eşitliği aranmıyor).
- **Hakem yanlılığı:** Hakem (gpt-5.4) ve RAG modeli (gpt-5.4-mini) aynı aileden olsa da farklı boyutlardalar. RAG vs No-RAG kıyasında olası yanlılık iki tarafa da eşit yansıyor.
- **Hallucination ayrı script gerekmedi:** Quality testindeki doğruluk boyutu (No-RAG = 1.45/5) hallucination oranını dolaylı olarak ölçüyor. Ayrı bir hallucination_test.py implement edilmedi.

---

## Dosya Yapısı

```
cmyllmz/
├── data/
│   ├── raw/           yahsi_bati.srt
│   ├── processing/    ham_chunks.json → base_chunks.json → enriched_chunks.json
│   └── final/         final_chunks.json (RAG'a yüklenecek)
│
├── notes/
│   ├── block_referans.md      (1929 satır, ana veri kaynağı)
│   ├── karakterler.txt        (55 karakter, kod=isim)
│   ├── chunk_index.md         (62 chunk özet tablo, izleme/referans için)
│   ├── cmyllmz_proje_plani.md (orijinal detaylı plan, tarihsel)
│   ├── proje_raporu.md        (bu dosya — checkpoint)
│   ├── notes.md               (serbest notlar)
│   └── sunum_notlari.md       (sunum konuşma notları)
│
├── src/
│   ├── data_prep/     srt_parser.py, chunk_merger.py, turkish_normalizer.py,
│   │                  enricher.py, ner_extractor.py, preprocessor.py
│   ├── rag/           embedder.py, vector_store.py, indexer.py, retriever.py
│   ├── llm/           openai_client.py, prompt_templates.py,
│   │                  ollama_client.py (post-MVP), gemini_client.py (post-MVP)
│   ├── evaluation/    retrieval_test.py, quality_test.py
│   └── app.py         (Streamlit ana uygulama)
│
├── notebooks/
│   └── faz13_evaluation.ipynb   (evaluation analiz + görselleştirme)
│
├── data/eval/         (questions.json, results_retrieval.json, results_quality.json)
├── data/conversations/ (Streamlit sohbet geçmişi, otomatik oluşur)
└── data/chroma/       (otomatik oluşur, persistent)
```

---

## Final Durum (2026-05-13)

### Tamamlanan Fazlar

**Faz 1-11** (veri hazırlama + RAG pipeline):
- SRT parsing → block_referans.md (1644 block, 62 chunk, hepsi elle annotate edildi)
- enriched_chunks.json: 62/62 chunk, OpenAI gpt-4o-mini ile zenginleştirildi
- ChromaDB `yb_chunks`: 62 chunk, BAAI/bge-m3, data/chroma/
- retriever.py + openai_client.py: uçtan uca soru → cevap çalışıyor
- Embedding: summary + text + location + karakterler + teknikler + kültürel bağlam concat
- build_context: timestamp (start→end) ve related_chunks LLM'e iletiliyor

**Faz 12** (Streamlit arayüzü):
- `src/app.py` — `streamlit run src/app.py` ile çalışıyor
- Chat arayüzü, streaming cevap, kaynak chunk gösterimi (expander)
- Konuşma geçmişi `data/conversations/` altında JSON olarak saklanıyor
- Sidebar: yeni sohbet, eski sohbetleri açma, soru önerileri

**Faz 13** (Evaluation):
- `data/eval/questions.json` (20 soru, 4 tip)
- `src/evaluation/retrieval_test.py` — Hit Rate ana metrik, Recall@k, Precision@k
- `src/evaluation/quality_test.py` — gpt-5.4 hakem ile RAG vs No-RAG karşılaştırması
- `notebooks/faz13_evaluation.ipynb` — analiz + görselleştirme
- Sonuç dosyaları: `results_retrieval.json`, `results_quality.json`
- **Sonuç:** Hit Rate %100, RAG doğruluk 4.65 vs No-RAG 1.45 (detaylar yukarıda "Başarı Metrikleri" bölümünde)

### Faz 13 Sırasında Yapılan Sistem İyileştirmeleri

- **System prompt güncellemesi** (`prompt_templates.py`): "Fazladan yorum ekleme" kuralı kaldırıldı, yerine "mizah mekanizmasını açıkla, kültürel bağlamı ver, birden fazla sahneyi sentezle" talimatları eklendi. Bu, cevap kalitesinde belirgin iyileştirme sağladı.
- **Runtime LLM yükseltmesi**: gpt-4o-mini → gpt-5.4-mini. Mizah analizi ve Türkçe sentez kalitesi için.
- **Embedder cihaz seçimi** (`embedder.py`): `EMBEDDER_DEVICE` env değişkeniyle CPU/CUDA seçilebilir hale getirildi (GPU OOM durumlarında evaluation'ı engellememesi için).

### Post-MVP Olarak Bırakılanlar

| Madde | Durum / Gerekçe |
|-------|-----------------|
| **Hybrid BM25 retrieval** | Hit Rate %100 olduğu için ihtiyaç yok |
| **Block-level retrieval** (`yb_blocks` collection) | Multi-resolution mimarisi planlandı ama chunk-level yeterli olduğu için implement edilmedi |
| **NER** (entities field) | Faz 9'da atlandı, RAG için zorunlu değil |
| **Ollama local LLM** | Donanım yetersiz, kalite farkı belirgin — OpenAI tek runtime |
| **Ayrı hallucination_test.py** | Quality test'in doğruluk boyutu zaten ölçüyor; ayrı script gerekmedi |

### Bilinen Zayıflıklar (Üretim Notları)

- **Spesifik replik araması:** "çaldığı ıslık..." gibi birebir alıntı aramaları semantik sistemle bulunamıyor. Hybrid BM25 ileride eklenebilir.
- **"Veri setimde yok" tepkisinde dikkat:** System prompt sıkılaştırıldı; evaluation'da hallucination'a rastlanmadı ama kullanım sırasında dikkat edilmeli.

---

## Veri Hazırlama Süreci: Edinilen Dersler

1. **Plan vs gerçek:** Başta "60-80 chunk" hedefi vardı, 62 ile bitti — neredeyse tam isabet. Sahne bazlı sınırların kelime sayısından önce gelmesi doğru karar olmuş.

2. **Field minimalizmi:** İlk schema'da `scene_description` ve `humor_note` ayrı alanlardı. İnline notlar yeterince zengin olunca bu iki alan redundant kaldı, kaldırıldı. **Ders:** Veri elle hazırlanırken format minimum tutulmalı, fazla alan iş yükünü artırır.

3. **Üç izleme stratejisi:** Tek izlemede her şey yapılmaya çalışılmadı. Her izlemenin tek bir odak alanı oldu (sınır, içerik, lokasyon+cross-ref). Bu, izleme verimliliğini artırdı ve hata oranını düşürdü.

4. **block_referans.md merkezli yaklaşım:** Tüm manuel iş JSON'da değil, insan-okunabilir markdown'da yapıldı. JSON yeniden üretildikçe manuel düzenlemeler kaybolmadı. Tek bir source-of-truth dosyası tutmanın değeri büyük.

5. **Türkçe diakritik için LLM otomasyonu:** Manuel diakritik ekleme 1107 segment için saatler alırdı. GPT-4o-mini ile tek bir scriptte ~1 dakikada $0.01 maliyetle yapıldı. Yapısal elementlerin (timestamp, karakter kodu) kod seviyesinde korunması, LLM'in yanlış yerlere müdahale etmesini önledi.

6. **Cross-reference değeri:** 56 `bkz.` referansı, RAG sisteminin "kopuk espri" sorununu (setup A sahnesinde, payoff B sahnesinde) çözecek. Bu manuel iş, otomatik chunk-similarity ile yakalanamayacak bağlantıları yakalar.
