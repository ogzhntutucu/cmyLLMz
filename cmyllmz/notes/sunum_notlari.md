# cmyLLMz — Sunum Notları

> Her aşama için: ne söyleyebilirsin, neyi gösterebilirsin, nasıl çerçeveleyebilirsin.

---

## Aşama 1 — Problem Tanımı + Veri Kaynakları

### Ne söyleyebilirsin

**Problem:**
> "Büyük dil modelleri, Türk kültürüne özgü mizahı yeterince açıklayamıyor. Cem Yılmaz gibi bir ismin sahnelerini sadece diyalog üzerinden değerlendirirsen kültürel bağlamı, fiziksel komediyi, Osmanlı-Vahşi Batı çelişkisini kaçırırsın. Peki bu bilgiyi nasıl sisteme yüklersin? Hazır bir veri seti yok — kendim oluşturdum."

**Çözüm:**
> "RAG kullanarak özgün bir film analiz veri seti oluşturdum ve bunu LLM'e bağladım. Kullanıcı bir soru sorduğunda sistem, cevabı uydurmak yerine filmden ilgili sahneyi bulup analiz ediyor."

**Veri kaynakları:**
> "İki kaynak: Yahşi Batı'nın SRT altyazı dosyası — bu ham veri. Ve benim izleyerek hazırladığım annotation katmanı — bu özgün katkı."

### Gösterebileceklerin
- `data/raw/yahsi_bati.srt` — ham kaynak
- `data/processing/ham_chunks.json` — srt_parser.py çıktısı, 1653 blok, her birinde start/end/text bilgisi
- `src/data_prep/srt_parser.py` — çalışan kod

---

## Aşama 2 — Ortam Kurulumu + Veri Toplandı mı + Chunk Stratejisi

### Ne söyleyebilirsin

**Ortam:**
> "Python ortamı kurulu. SentenceTransformers, ChromaDB, spaCy, Gemini API, Ollama, Streamlit — hepsi requirements.txt'te tanımlı ve kurulu."

**Veri toplandı mı:**
> "SRT dosyasından 1653 ham altyazı bloğu otomatik olarak çıkarıldı. Şu an filmi izleyerek bu bloklara chunk sınırları ve karakter etiketleri ekliyorum. Bu en emek yoğun adım — ama projenin kalitesi buraya bağlı."

**Chunk stratejisi — bunu güçlü anlat:**
> "Çoğu RAG projesi metni sabit kelime veya karakter sayısına göre böler. Bu yaklaşım Yahşi Batı için işe yaramaz — bir espri beş repliğe yayılabilir, ortasından keserseniz ne setup ne punchline kalır. Bu yüzden sahneleri bizzat izleyerek bölüyorum."

Sistemi somut göster:

```
0479 [00:35:52] [birlikte at sürerek ilerlerken konuşuyorlar] -LE- Aman bunu da hep söylerler.
0480 [00:35:55] -AZ- İşte matbaanın bize geç gelmesi... Falan filan... [silah sesleri]
0481 [00:36:00] Ne oluyor ya?
0483 [00:36:03] -AZ- Hoo... [atlarından inip sese doğru yürüyorlar]
0485 [00:36:28] -LE- Kadın mı bu ya? -AZ- Kadın tabii oğlum.
===
```

> "=== chunk sınırı, -XX- etiketleri konuşan karakteri, [...] köşeli parantezler görsel sahneleri gösteriyor. Bunlar diyalogla aynı satırda, zaman sırasında. Sonra chunk_merger.py bu dosyayı okuyup JSON üretiyor."

**Nihai chunk örneği:**
```json
{
  "id": "yb_012",
  "start": "00:35:52", "end": "00:36:28",
  "duration_sec": 36.0,
  "block_range": "0479-0485",
  "text": "[birlikte at sürerek ilerlerken] -LE- Aman bunu da hep söylerler. -AZ- İşte matbaanın bize geç gelmesi... [silah sesleri] Ne oluyor ya? -AZ- Hoo... [atlarından inip sese doğru yürüyorlar] Sakin... -LE- Kadın mı bu ya? -AZ- Kadın tabii oğlum.",
  "characters": ["Lemi Galip", "Aziz Vefa"]
}
```

### Gösterebileceklerin
- `notes/block_referans.md` — annotation devam eden dosya, === ve -XX- etiketleri görünür
- `src/data_prep/chunk_merger.py` — çalışan kod, block_referans.md'yi okuyup JSON üretiyor
- `notes/karakterler.txt` — karakter kodu → tam isim eşlemesi

---

## Aşama 3 — Embedding Üretildi mi + Vektör DB + Retriever

### Durumu dürüstçe çerçevele
> "Veri hazırlama tamamlanınca embedding ve vektör DB otomatik olarak oluşturulacak. Mimari ve araç seçimleri hazır, tasarım kararları alındı."

### Ne söyleyebilirsin

**Embedding modeli:**
> "paraphrase-multilingual-MiniLM-L12-v2 kullandım. 50'den fazla dil destekliyor, Türkçe dahil. 384 boyutlu vektör üretiyor — hızlı ve hafif, GTX 1650 Ti'da rahat çalışıyor."

**Kritik tasarım kararı — bunu güçlü anlat:**
> "Sadece diyalog metnini embed etmek yeterli değil. 'Bu sahne neden komik?' sorusunu sormak istiyorum ama diyaloğun kendisi bu soruyu cevaplamıyor. Bu yüzden sahne açıklaması, mizah notu ve Gemini ile üretilecek humor_analysis alanlarını da embed ediyorum. Kullanıcı 'anakronizm örnekleri neler?' diye sorduğunda, humor_analysis'te anachronism yazan chunk'lar öne çıkıyor."

Embed edilecek alan:
```
{diyalog metni ve inline notlar}
Mizah notu: {humor_note}
Özet: {summary}
Mizah teknikleri: {humor_analysis.techniques}
Neden komik: {humor_analysis.why_funny}
Kültürel bağlam: {humor_analysis.cultural_context}
```

**ChromaDB:**
> "Vektör veritabanı olarak ChromaDB kullandım. Cosine similarity ile arama yapıyor. Önemli bir özelliği: metadata filtreleme. Kullanıcı 'sadece Aziz'in sahnelerini getir' diyebiliyor — ChromaDB bunu characters alanı üzerinden filtreliyor."

**Prompt templates:**
> "Retriever'ın LLM'e gönderdiği promptlar tamamlandı."

### Gösterebileceklerin
- `src/rag/embedder.py`, `vector_store.py`, `retriever.py` — kod iskeletleri, yapı görünür
- `src/llm/prompt_templates.py` — **TAMAMLANMIŞ**, RAG sistem promptu ve hakem LLM promptu var

---

## Aşama 4 — Örnek Soru-Cevap + Arayüz Demo + Sonuç Değerlendirme

### Durumu dürüstçe çerçevele
> "Uçtan uca demo henüz hazır değil — veri hazırlama tamamlanınca embedding ve arayüz hızlıca kurulacak. Ama değerlendirme metodolojim hazır ve beklenen çıktıları somut olarak gösterebilirim."

### Ne söyleyebilirsin

**Beklenen soru-cevap örnekleri:**

*Örnek 1 — Espri açıklama:*
> Kullanıcı: "Garfield şakasını açıkla"
> Sistem: "Zeki, çizmenin geçmişini anlatırken ABD başkanı Garfield'dan bahseder. Ramazan 'o kedi olan mı?' diye sorar. Mizah tekniği: misunderstanding + cultural_reference. Türk popüler kültüründe Garfield karikatür kediyle özdeşleştiğinden tarihsel figür bilinmez."

*Örnek 2 — Bulanık hatıradan somut sahneye:*
> Kullanıcı: "Cem Yılmaz'ın bir filminde karakter Mickey Mouse oynatıyordu, hangi filmdi?"
> Sistem: "Yahşi Batı. Lemi Galip oynattıyor. Zeki anlatıyor: 'Yahu, Lemi Bey'in kendi yaptığı makineyle miki filmi oynatıyorlar ya! Daha Walt Disney yok, Mickey Mouse yok!'"

*Örnek 3 — Teknik soru:*
> Kullanıcı: "Filmde anakronizm örnekleri neler?"
> Sistem: anachronism tekniği geçen tüm chunk'ları listeler, her birini açıklar.

**Değerlendirme metodolojisi:**
> "Üç metrik kullanıyorum:"

| Metrik | Yöntem |
|--------|--------|
| Hallucination oranı | 20-30 soru, RAG'lı vs RAG'sız, olgusal doğruluk kontrolü |
| Retrieval precision | Getirilen 3 chunk'tan kaçı gerçekten ilgili? |
| Cevap kalitesi | LLM-as-a-Judge: Gemini, iki cevabı doğruluk/detay/tutarlılık üzerinden 1-5 puanlar |

> "LLM-as-a-Judge akademik çevrelerde kabul gören bir yöntem — benim manuel puanlamam taraflı olurdu."

**Arayüz:**
> "Streamlit arayüzü olacak. İki özellik önemli: birincisi streaming — local LLM ile chunk'lar context'i büyütüyor, 5-15 saniyelik gecikme var, streaming olmadan ekran donuyor gibi görünür. İkincisi kaynak gösterimi — hangi sahnelerden bilgi geldiği şeffaf olarak kullanıcıya gösterilir."

### Gösterebileceklerin
- `src/evaluation/hallucination_test.py`, `quality_test.py`, `retrieval_test.py` — yapı görünür
- `src/app.py` — iskelet, Streamlit yapısı görünür
- Proje planındaki metrik gösterim tasarımı

---

## Genel Çerçeveleme (Sunum Boyunca)

Hocaya dürüst ama güçlü söyle:

> "Veri hazırlama diğer aşamaların temelini oluşturuyor ve en emek yoğun kısım bu. Otomatik yapılabilirdi ama kalitesi düşük olurdu — mizahın bağlamını korumak için manuel yapıyorum. Mimari kararların tamamı alındı, implementasyon veri hazırlama biter bitmez hızlıca tamamlanacak."

Bu seni savunur çünkü:
- 1653 blok somut bir veri var
- Chunk stratejisi tasarlanmış ve kodlanmış
- Mimari seçimlerin her biri gerekçeli
- Metodoloji (LLM-as-a-Judge) akademik
