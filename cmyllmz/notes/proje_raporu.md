# cmyLLMz — Proje Raporu

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

---

## Sistemin Çalışma Mantığı

```
Kullanıcı sorusu
       │
       ▼
Soru → Embedding vektörü
       │
       ▼
ChromaDB'den en benzer 3-5 chunk getirilir
       │
       ▼
[chunk metinleri + soru] → Prompt
       │
       ▼
LLM (Ollama local veya Gemini API)
       │
       ▼
Cevap (+ kaynak sahneler gösterilir)
```

**Örnek:**
> Kullanıcı: "Filmde anakronizm örnekleri neler?"
> → System: "Google'a girmek" gibi modern referansların Osmanlı/1881 bağlamında kullanıldığı sahneleri bulur, mizah mekanizmasını açıklar.

---

## Veri Seti: Nasıl Hazırlanıyor?

Bu projenin özgün katkısı, filmden **elle hazırlanmış, zenginleştirilmiş chunk veri setidir**.

### Pipeline (7 Faz)

```
Faz 1 ✅  SRT → Ham Block'lar (srt_parser.py)
          1653 altyazı birimi, zaman damgalı

Faz 2 ✅  Ham block'lardan referans dosyası oluştur (block_referans.md)
          Format: "0001 [00:00:14] -AL- Şimdi kadın, ince uzun da olur..."

Faz 3 🔄  Film izlerken manuel düzenleme (block_referans.md)
          - Chunk sınırı: === (tek satır)
          - Karakter değişimi: -KOD- (örn. -AZ-, -LE-)
          Hedef: 60-80 chunk

Faz 4     chunk_merger.py → base_chunks.json
          === sınırlarını okur, block'ları birleştirir, [NNNN] markerları ekler

Faz 5     Manuel annotation (base_chunks.json üzerinde)
          location, scene_description, humor_note alanları

Faz 6     LLM zenginleştirme (enricher.py + Gemini API)
          humor_analysis ve summary alanları otomatik doldurulur

Faz 7     Gözden geçirme + related_chunks → final_chunks.json
```

### Chunk Örneği

```json
{
  "id": "yb_001",
  "start": "00:00:14",
  "end": "00:00:49",
  "duration_sec": 35.0,
  "block_range": "0001-0012",
  "text": "[0001] -AL- Şimdi kadın, ince uzun da olur... [0005] -RA- Ustaya bak!",
  "characters": ["Alpay", "Ramazan", "Vedat", "Zeki"],
  "location": "Rakı masası",
  "scene_description": "Alpay masada zıbık hakkında komik bir hikaye anlatıyor.",
  "humor_note": "Marangoz ustasının tepkisi ve 'zıbık' kelimesinin günlük konuşmaya sokulması.",
  "humor_analysis": {
    "techniques": ["anecdote", "wordplay"],
    "why_funny": "...",
    "cultural_context": "...",
    "comedic_timing": "..."
  },
  "summary": "Alpay'ın zıbık hikayesi ve masadaki tepkiler."
}
```

**Kim ne doldurur:**

| Alan | Kaynak |
|------|--------|
| `id`, `start`, `end`, `duration_sec`, `block_range` | Otomatik (script) |
| `text` içindeki `-KOD-` etiketleri | Manuel (izlerken) |
| `characters` | Otomatik (`-KOD-` etiketlerinden) |
| `location`, `scene_description`, `humor_note` | Manuel (annotation) |
| `humor_analysis`, `summary` | LLM (Gemini) |
| `entities` | Otomatik (spaCy NER) |

---

## Teknoloji Stack'i

| Bileşen | Teknoloji |
|---------|-----------|
| Embedding | `paraphrase-multilingual-MiniLM-L12-v2` (384 boyut, Türkçe destekli) |
| Vektör DB | ChromaDB (cosine similarity) |
| Local LLM | Ollama — Gemma 3 4B (GTX 1650 Ti 4GB için uygun) |
| Bulut LLM | Gemini API (Gemini 2.5 Flash) |
| NLP | NLTK / spaCy (`xx_ent_wiki_sm`) |
| Arayüz | Streamlit |

**Embedding için birleştirilen metin:**
Sadece diyalog değil; `text + scene_description + humor_note + summary + humor_analysis` birlikte embed edilir. Bu sayede "anakronizm içeren sahneler" gibi sorular doğrudan analiz alanlarıyla eşleşir.

---

## Başarı Metrikleri

### 1. Hallucination Oranı
20-30 olgusal soru sorulur (RAG'lı vs RAG'sız). RAG'sız LLM'in uydurmaya karşı RAG'lı sistemin doğruluk oranı karşılaştırılır.

### 2. Retrieval Precision
Her soru için getirilen 3 chunk'tan kaçı gerçekten ilgili? `ilgili / toplam` oranı.

### 3. Cevap Kalitesi (LLM-as-a-Judge)
RAG'lı sistem vs düz LLM cevapları, üçüncü bir LLM tarafından doğruluk / detay / tutarlılık kriterleriyle 1-5 arası puanlanır.

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
│   ├── block_referans.md    (izlerken düzenliyorsun)
│   ├── karakterler.txt      (karakter kodu → tam isim)
│   └── cmyllmz_proje_plani.md
│
├── src/
│   ├── data_prep/     srt_parser.py, chunk_merger.py, enricher.py, ner_extractor.py
│   ├── rag/           embedder.py, vector_store.py, retriever.py
│   ├── llm/           ollama_client.py, gemini_client.py, prompt_templates.py
│   ├── evaluation/    hallucination_test.py, retrieval_test.py, quality_test.py
│   └── app.py         (Streamlit)
│
└── chroma_db/         (otomatik oluşur)
```

---

## Şu Anki Durum

- **Tamamlandı:** Faz 1-2 (SRT → ham_chunks.json, block_referans.md)
- **Devam ediyor:** Faz 3 — film izlerken chunk sınırları ve karakter kodları ekleniyor
- **Sırada:** Faz 4 → chunk_merger.py çalıştır → base_chunks.json, ardından Faz 5 annotation
