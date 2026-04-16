# cmyLLMz — Proje Planı

## Proje Özeti

**Proje adı:** cmyLLMz
**Amaç:** Cem Yılmaz'ın "Yahşi Batı" filminin altyazı verisini kullanarak, mizahı analiz eden, açıklayan ve sorgulatan bir RAG (Retrieval-Augmented Generation) tabanlı yapay zeka sistemi kurmak.
**Kapsam:** Bu tek proje, iki ayrı dersin proje gerekliliklerini karşılayacak şekilde tasarlanmıştır.

### Hangi Dersin Neresini Karşılıyor?

**Ders 1 — Mühendislikte Bilgisayar Uygulamaları (MBU):**

- RAG pipeline'ı (veri toplama → chunking → embedding → vektör DB → retrieval → generation)
- Local LLM desteği (Ollama)
- Bulut LLM desteği (Gemini API)
- Streamlit web arayüzü

**Ders 2 — Doğal Dil İşleme (NLP):**

- NLP ön işleme adımları (tokenizasyon, stop-word çıkarımı, normalizasyon)
- Özellik çıkarımı / vektörleştirme (embedding)
- Özgün veri seti (elle hazırlanmış Yahşi Batı chunk'ları)
- Kullanıcı arayüzü (Streamlit)
- Başarı ölçümü: hallucination oranı, retrieval doğruluğu, cevap kalitesi skoru
- RAG destekli sistem vs düz LLM kıyaslaması

---

## Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                        KULLANICI                            │
│                     (Streamlit UI)                           │
│         "Yahşi Batı'da Garfield şakası neydi?"              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   SORGULAMA KATMANI                          │
│                                                             │
│  1. Kullanıcı sorusu embedding'e çevrilir                   │
│  2. ChromaDB'den en benzer chunk'lar getirilir (top-k)      │
│  3. Chunk'lar + soru → prompt oluşturulur                   │
│  4. Prompt → LLM'e gönderilir                               │
│  5. LLM cevap üretir                                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
┌──────────────────────┐  ┌──────────────────────┐
│     LOCAL LLM        │  │     BULUT LLM        │
│  Ollama              │  │  Gemini API           │
│  (Gemma 3 4B veya    │  │  (Google AI Studio)   │
│   Phi-4 Mini)        │  │                       │
└──────────────────────┘  └──────────────────────┘
              ▲                         ▲
              │                         │
┌─────────────┴─────────────────────────┴─────────────────────┐
│                      RAG KATMANI                             │
│                                                              │
│  ChromaDB (vektör veritabanı)                                │
│  ├── Embedding modeli: paraphrase-multilingual-MiniLM-L12-v2 │
│  ├── Similarity: cosine                                      │
│  └── Her chunk metadata ile birlikte saklanır                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     VERİ KATMANI                             │
│                                                              │
│  Yahşi Batı chunk'ları (JSON)                                │
│  ├── Altyazıdan sahne bazlı chunk'lar                        │
│  ├── Karakter bilgileri                                      │
│  ├── Elle alınmış notlar                                     │
│  └── LLM ile üretilmiş mizah analizleri                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Teknoloji Stack'i

| Bileşen | Teknoloji | Neden? |
|---|---|---|
| Programlama dili | Python 3.10+ | Tüm kütüphanelerle uyumlu |
| Local LLM | Ollama (Gemma 3 4B veya Phi-4 Mini) | GTX 1650 Ti 4GB VRAM ile çalışır |
| Bulut LLM | Gemini API (Google AI Studio) | Ücretsiz API kotası, ders notlarıyla uyumlu |
| Embedding | sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2) | Türkçe destekli, 384 boyutlu vektör, hafif |
| Vektör DB | ChromaDB | Kolay kurulum, ders notlarıyla uyumlu, cosine similarity |
| NLP ön işleme | NLTK veya spaCy | Tokenizasyon, stop-word, stemming/lemmatizasyon |
| Arayüz | Streamlit | Python ile hızlı web UI, temel Python bilgisiyle yeterli |
| Veri formatı | JSON | Chunk'lar ve metadata için |

### Donanım

- **GPU:** NVIDIA GTX 1650 Ti Mobile (4GB VRAM)
- **CPU:** Intel Core i5-10300H @ 2.50GHz × 4
- **İşletim sistemi:** Linux Mint Cinnamon

### Ollama Kurulumu

```bash
# Ollama'yı kur
curl -fsSL https://ollama.ai/install.sh | sh

# Model indir (4GB VRAM için önerilen seçenekler, birini seç)
ollama pull gemma3:4b         # ~3GB VRAM, Türkçe makul, multimodal, 128K context
# veya
ollama pull phi4-mini          # ~3GB VRAM, reasoning odaklı, hızlı

# Test et
ollama run gemma3:4b "Merhaba, nasılsın?"
```

**Not:** GTX 1650 Ti'de 4GB VRAM sınırı var. 3-4B parametre modeller (Q4 quantization ile) rahat çalışır. Her iki modeli de dene, Türkçe cevap kalitesine göre birini seç. Gemma 3 4B önerilir çünkü Google'ın modeli olarak Türkçe desteği daha iyi olabilir ve multimodal özelliği var. RAG ile desteklediğimiz için modelin kendi bilgisi çok kritik değil — önemli olan verilen bağlamı doğru kullanması.

---

## Veri Seti Hazırlama

Bu, projenin en kritik ve en çok emek gerektiren kısmı. Veri setinin kalitesi projenin kalitesini belirler.

### Kaynak Veri

- Yahşi Batı filmi (.srt altyazı dosyası)
- Senin film izleme notların

### Chunk Yapısı (JSON Şeması)

Her chunk şu alanlara sahip olacak:

```json
{
  "id": "yb_001",
  "start": "00:00:14",
  "end": "00:00:49",
  "duration_sec": 35.0,
  "block_range": "0001-0012",
  "text": "[0001] -AL- Şimdi kadın, ince uzun da olur... [0005] -RA- Ustaya bak! [0006] -VE- Tabii canım...",

  "characters": ["Alpay", "Ramazan", "Vedat", "Zeki"],
  "location": "Rakı masası",

  "scene_description": "Alpay masada zıbık hakkında komik bir hikaye anlatıyor, herkes gülüyor.",
  "humor_note": "Marangoz ustasının tepkisi ve 'zıbık' kelimesinin günlük konuşmaya sokulması espriyi oluşturuyor.",

  "related_chunks": ["yb_005", "yb_012"],

  "humor_analysis": {
    "techniques": ["anecdote", "irony", "cultural_reference"],
    "why_funny": "Bu sahnenin neden komik olduğunun açıklaması",
    "cultural_context": "Anlaşılması için gereken kültürel bağlam",
    "comedic_timing": "Zamanlamanın komikliğe etkisi"
  },

  "entities": {
    "persons": ["Garfield"],
    "locations": ["Dolmabahçe"],
    "orgs": ["Teşkilât-ı Mahsusa"],
    "misc": ["Wellington çizmesi"]
  },

  "summary": "Sahnenin kısa özeti"
}
```

**`text` alanı formatı:**
- Her block'un başına `[NNNN]` sıra numarası eklenir (chunk_merger.py otomatik yapar)
- Karakter değişimlerinde `-KOD-` eklenir (sen eklersin, örn: `-AL-`, `-ZE-`)
- Karakter kodları `notes/karakterler.txt`'te tanımlı; `characters` alanı bu kodlardan otomatik çıkarılır

### Alan Açıklamaları

| Alan | Kim dolduracak? | Açıklama |
|---|---|---|
| `id` | Otomatik (script) | `yb_001`, `yb_002`... formatında sıralı ID |
| `start`, `end` | Otomatik (script) | Ham block'lardan alınan zaman damgaları |
| `duration_sec` | Otomatik (script) | start ve end'den hesaplanır |
| `block_range` | Otomatik (script) | Chunk'a dahil edilen block'ların aralığı (örn: `"0001-0012"`) |
| `text` | Sen (izlerken) + script | `block_referans.md`'deki karakter kodlu diyaloglar; `[NNNN]` block markerleri script tarafından eklenir. Anlamsız blok numaralarını annotation sırasında temizleyebilirsin. |
| `characters` | Otomatik (script) | `text` içindeki `-KOD-` etiketlerinden çıkarılır; `karakterler.txt`'teki eşlemeden tam isimlere dönüştürülür |
| `location` | Sen (annotation sırasında) | Sahnenin geçtiği mekan. Tutarlı isimler kullan |
| `scene_description` | Sen (annotation sırasında) | 1-2 cümle. Ne oluyor, nerede, kim ne yapıyor |
| `humor_note` | Sen (annotation sırasında) | 1-2 cümle. Esprinin mekanizması, neden komik, nüans nerede. Komik olmayan sahnelerde boş bırakılabilir |
| `related_chunks` | Sen (son geçişte) | Bağlantılı chunk ID'leri. Tüm chunk'lar hazır olunca doldur |
| `humor_analysis` | LLM (otomatik) | `scene_description` + `humor_note` + `text` girdi alarak Gemini üretir. Sen gözden geçirirsin |
| `entities` | Otomatik (NER scripti) | spaCy + regex ile kişi, yer, kurum isimleri |
| `summary` | LLM (otomatik) | Sahnenin 1-2 cümlelik özeti |

### Veri Hazırlama İş Akışı

```
Faz 1: SRT → Ham Block'lar (Otomatik — tamamlandı)
─────────────────────────────────────────────────────
srt_parser.py ile SRT okunur, temizlenir.
İngilizce orijinal/Türkçe çeviri çakışmaları çözülür.
Çıktı: ham_chunks.json (1653 block, her biri birkaç saniyelik altyazı birimi)

Faz 2: Referans Dosyası (Otomatik — tamamlandı)
─────────────────────────────────────────────────────
ham_chunks.json'dan block_referans.md oluşturuldu.
Her satır: 0001 [00:00:14] altyazı metni
Zaman boşlukları --- ile gösterilmiş.
Dosyalar: notes/block_referans.md, notes/karakterler.txt

Faz 3: Chunk Sınırları + Karakter Kodları (Manuel — devam ediyor)
─────────────────────────────────────────────────────
Filmi izlerken block_referans.md üzerinde çalış:
- Chunk sınırına === yaz (tek başına satır)
- Karakter değişimlerinde -KOD- yaz (örn: -AL-, -ZE-, -H1-)
- Yeni karakter ekleyince karakterler.txt'e de ekle
Hedef: 60-80 chunk

Faz 4: Base Chunk'lar Oluştur (Otomatik)
─────────────────────────────────────────────────────
chunk_merger.py çalıştır:
- block_referans.md'deki === sınırlarını okur
- Blokları birleştirir, [NNNN] block markerlerini ekler
- characters alanını -KOD- etiketlerinden otomatik doldurur
Çıktı: base_chunks.json

Faz 5: Annotation (Manuel)
─────────────────────────────────────────────────────
base_chunks.json üzerinde her chunk için doldur:
- location: sahne mekanı
- scene_description: ne oluyor (1-2 cümle)
- humor_note: esprinin mekanizması (1-2 cümle, boş bırakılabilir)
- text temizliği: anlamsız [NNNN] markerlarını sil, işine yarayanları bırak
Aynı izlemede test sorularını da not al (metrik ölçümü için)

Faz 6: LLM ile Zenginleştir (Yarı-otomatik)
─────────────────────────────────────────────────────
enricher.py ile her chunk'ı Gemini'ye gönder.
Girdi: text + scene_description + humor_note + characters + location
LLM, humor_analysis ve summary alanlarını doldursun.
Çıktı: enriched_chunks.json

Faz 7: Gözden Geçir + related_chunks (Manuel)
─────────────────────────────────────────────────────
LLM çıktılarını kontrol et, yanlışları düzelt.
related_chunks alanlarını doldur (tüm chunk ID'leri artık belli).
Çıktı: final_chunks.json (RAG'a yüklenecek)
```

### Faz 6 İçin LLM Prompt Örneği

```
Sen bir mizah analisti ve film eleştirmenisin. Sana Cem Yılmaz'ın "Yahşi Batı" filminden
bir sahne vereceğim. Bu sahneyi mizah açısından analiz etmeni istiyorum.

Sahne bilgileri:
- Karakterler: {characters}
- Mekan: {location}
- Sahne açıklaması: {scene_description}
- Mizah notu: {humor_note}

Diyaloglar:
{text}

Lütfen aşağıdaki JSON formatında cevap ver (sadece JSON, başka bir şey yazma):

{
  "humor_analysis": {
    "techniques": ["kullanılan mizah teknikleri listesi — şunlardan seç: irony, sarcasm, wordplay, exaggeration, anachronism, cultural_reference, slapstick, absurd, anecdote, character_contrast, breaking_fourth_wall, callback, misunderstanding, deadpan, timing"],
    "why_funny": "Bu sahne neden komik? 2-3 cümle ile açıkla.",
    "cultural_context": "Bu espriyi anlamak için hangi kültürel bilgiye ihtiyaç var? Türk kültürüne, popüler kültüre veya tarihsel bilgiye referans varsa belirt.",
    "comedic_timing": "Zamanlamanın veya beklenmedik tepkilerin komikliğe etkisini açıkla. Yoksa boş bırak."
  },
  "summary": "Sahnenin 1-2 cümlelik kısa özeti."
}
```

### Mizah Teknikleri Referansı

| Teknik                 | Açıklama                                                     | Yahşi Batı Örneği                             |
| ---------------------- | ------------------------------------------------------------ | --------------------------------------------- |
| `irony`                | Söylenenin tam tersinin kastedilmesi                         | —                                             |
| `sarcasm`              | İğneleme, alaycı konuşma                                     | —                                             |
| `wordplay`             | Kelime oyunu, çift anlamlılık                                | —                                             |
| `exaggeration`         | Abartı                                                       | —                                             |
| `anachronism`          | Zamana aykırılık (modern şeylerin eski dönemde kullanılması) | Google'a girmek, modern Türkçe argo kullanımı |
| `cultural_reference`   | Kültürel gönderme                                            | Garfield kedisi ile ABD Başkanı karışıklığı   |
| `slapstick`            | Fiziksel komedi                                              | —                                             |
| `absurd`               | Saçmalık, mantık dışılık                                     | —                                             |
| `anecdote`             | Hikaye anlatma yoluyla komedi                                | Alpay'ın usta hikayesi                        |
| `character_contrast`   | Karakter çelişkisi                                           | —                                             |
| `breaking_fourth_wall` | Dördüncü duvarı kırma                                        | —                                             |
| `callback`             | Daha önceki bir espriye geri dönüş                           | —                                             |
| `misunderstanding`     | Yanlış anlama                                                | Garfield kedi mi başkan mı                    |
| `deadpan`              | Düz yüzle komiklik                                           | —                                             |
| `timing`               | Zamanlama ile gelen komiklik                                 | —                                             |

**Not:** Yahşi Batı örnek sütununu film izlerken doldurabilirsin. Bu referans tablosu, etiketleme yaparken sana rehber olacak. Her sahne için birden fazla teknik seçilebilir.

---

## RAG Pipeline Detayları

### 1. NLP Ön İşleme

Bu adımlar hem chunk'ları ChromaDB'ye yüklemeden önce uygulanacak, hem de raporlama için önemli (Proje 2'nin NLP gerekliliklerini karşılar).

```python
# Uygulanacak ön işleme adımları:

# 1. Metin temizleme
#    - HTML taglarını kaldır (<i>, {\a6} gibi)
#    - Birden fazla boşluğu tek boşluğa indir
#    - Satır başı/sonu boşlukları temizle

# 2. Tokenizasyon
#    - Metni kelime bazında token'lara ayır
#    - NLTK veya spaCy kullanılabilir

# 3. Stop-word çıkarımı
#    - Türkçe stop-word listesi kullan
#    - "bir", "ve", "ile", "da", "de" gibi kelimeler

# 4. Normalizasyon
#    - Küçük harfe çevirme
#    - Türkçe stemming veya lemmatizasyon (Zeyrek kütüphanesi Türkçe için iyi çalışır)

# NOT: ÖNEMLİ TEKNİK DETAY
# SentenceTransformer gibi modern embedding modelleri kendi tokenizer'larına sahiptir.
# Bu modeller bağlamı anlayarak çalışır — stop-word'ler ve ekler bağlam için önemlidir.
# Bu yüzden:
#
# - Embedding'e VERİLECEK metin: temizlenmiş ama stem'lenmemiş/stop-word'süz orijinal metin
# - ChromaDB "documents" alanı: aynı temiz orijinal metin (LLM'e gönderilecek)
# - Ön işlenmiş versiyon (stop-word çıkarılmış, stem'lenmiş): SADECE raporlama ve
#   NLP süreçlerini göstermek için kullanılır. Raporda "bu adımları uyguladık,
#   token sayısı şu kadar azaldı, kök bulma sonuçları şöyle oldu" diye gösterilir.
#
# ÖZET: Ön işleme adımlarını uygula ve sonuçlarını kaydet (rapor için),
# ama embedding ve retrieval için orijinal temiz metni kullan.
```

### 1.5. NER — Named Entity Recognition (İsimli Varlık Tanıma)

MBU ders notlarında RAG pipeline'ının zorunlu adımlarından biri olarak NER geçiyor (Hafta 4, madde 4). Chunk'lardan otomatik olarak kişi, yer, kurum gibi varlıkları çıkarmak retrieval kalitesini artırır ve metadata'yı zenginleştirir.

```python
# spaCy ile NER (çok dilli model Türkçe'yi destekler)
# Model: xx_ent_wiki_sm (çok dilli; PER, ORG, LOC, MISC)
#
# Her chunk üzerinde NER çalıştırılır.
# Çıkan entity'ler chunk'ın metadata'sına eklenir.
# Bu sayede ChromaDB'de metadata filtreleme yapılabilir.
#
# Ek olarak: Türkçe'ye özel regex pattern'ler kullanılabilir
# (ders notlarında "iki katmanlı sistem: spaCy + Türkçe regex" önerisi var)
# Örnek: "Paşa", "Sultan", "Abi" gibi Türkçe hitap kalıpları
# veya "Teşkilât-ı Mahsusa" gibi tarihsel kurum isimleri

# Çıktı: chunk metadata'sına "entities" alanı eklenir
# Örnek: {"persons": ["Zeki", "Alpay"], "locations": ["Dolmabahçe"], "orgs": ["Teşkilât-ı Mahsusa"]}
```

**NOT:** Karakter isimlerini sen zaten elle dolduruyorsun. NER'in buradaki ek değeri, sözle geçen ama karakter olmayan varlıkları (yer adları, kurum adları, tarihsel figürler) otomatik çıkarmak. Raporlamada da "NER uyguladık" diyebilmek önemli çünkü ders notlarında beklenen bir adım.

### 2. Embedding ve ChromaDB'ye Yükleme

```python
# Embedding modeli
# Model: paraphrase-multilingual-MiniLM-L12-v2
# Çıktı: 384 boyutlu vektör
# Türkçe dahil 50+ dil destekler

# ChromaDB koleksiyonu oluşturma
# Collection adı: "yahsi_bati"
# Metadata: her chunk'ın tüm alanları (characters, scene_type, humor_analysis vs.)
# Distance metric: cosine similarity

# Her chunk için ChromaDB'ye yüklenecek veriler:
# - id: chunk ID'si (yb_001, yb_002...)
# - documents: chunk'ın text + scene_description + summary + humor_analysis birleştirilmiş hali
#   (Bu, retrieval sırasında daha zengin eşleştirme sağlar)
# - embeddings: yukarıdaki birleştirilmiş metnin embedding'i
# - metadatas: tüm chunk alanları — characters, location, block_range vs. (filtreleme için)
```

**ÖNEMLİ — Embedding için birleştirilecek metin:**
Sadece `text` alanını embed etmek yeterli olmayabilir çünkü diyaloglar tek başına "bu neden komik" sorusuna cevap vermez. Bu yüzden embedding için şu alanları birleştir:

```
{text}

Sahne: {scene_description}
Mizah notu: {humor_note}
Özet: {summary}
Mizah teknikleri: {humor_analysis.techniques}
Neden komik: {humor_analysis.why_funny}
Kültürel bağlam: {humor_analysis.cultural_context}
```

Bu sayede kullanıcı "anakronizm içeren sahneler" diye sorduğunda, `humor_analysis.techniques` alanında "anachronism" yazan chunk'lar yüksek benzerlik skoru alır.

**Opsiyonel Bonus — Ablation Study (vaktin kalırsa):**
İlk aşamada sadece text + summary ile embed et ve retrieval kalitesini test et. İkinci aşamada humor_analysis'i de ekleyip retrieval kalitesinin artıp artmadığını karşılaştır. Bu karşılaştırma raporun için güzel bir "ablation study" olur ve hocanın gözünde projenin bilimsel değerini artırır. Ama bu zorunlu değil, sadece bonus.

### 3. Retrieval (Sorgulama)

```python
# Kullanıcı sorusu geldiğinde:
# 1. Soruyu aynı embedding modeli ile vektöre çevir
# 2. ChromaDB'den en benzer k chunk'ı getir (k=3 veya k=5)
#    - Eğer kullanıcı arayüzden karakter/sahne türü filtresi seçtiyse,
#      ChromaDB'nin where parametresi ile metadata filtreleme uygula
#      Örnek: collection.query(..., where={"characters": {"$contains": "Zeki"}})
# 3. Getirilen chunk'ların related_chunks alanını kontrol et
#    - Eğer related_chunks varsa, o chunk'ları da getir (bağlam bütünlüğü için)
#    - Bu sayede setup bir sahnede, punchline başka sahnede olan espriler kopuk kalmaz
# 4. Tüm chunk'ların text, summary, humor_analysis bilgilerini al
# 5. Bunları bir prompt template'ine yerleştir
# 6. Prompt'u seçilen LLM'e (local veya bulut) gönder
```

### 4. Generation (Cevap Üretme)

```python
# Prompt template örneği:

SYSTEM_PROMPT = """
Sen cmyLLMz adlı bir mizah analiz asistanısın. 
Cem Yılmaz'ın "Yahşi Batı" filmi hakkında sorulara cevap veriyorsun.

Sana verilen bağlam bilgilerini kullanarak cevap ver.
Bağlamda olmayan bilgileri UYDURMA. 
Eğer bağlamda cevap yoksa "Bu bilgi veri setimde bulunmuyor" de.

Cevaplarında:
- Sahne detaylarını ve diyalogları doğru aktar
- Mizah tekniklerini açıkla
- Kültürel bağlamı belirt
- Türkçe ve samimi bir dil kullan
"""

USER_PROMPT = """
Bağlam bilgileri:
---
{retrieved_chunks}
---

Kullanıcının sorusu: {user_question}
"""
```

### 5. LLM Entegrasyonu

**Local LLM (Ollama):**
```python
# Ollama Python kütüphanesi ile:
# pip install ollama
import ollama

response = ollama.chat(
    model="gemma3:4b",  # veya phi4-mini
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ]
)
```

**Bulut LLM (Gemini):**
```python
# Google AI Studio API ile:
# pip install google-generativeai
import google.generativeai as genai

genai.configure(api_key="SENIN_API_ANAHTARIN")
model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content(
    SYSTEM_PROMPT + "\n\n" + USER_PROMPT
)
```

---

## Streamlit Arayüzü

### Tasarım

```
┌─────────────────────────────────────────────────────┐
│                    cmyLLMz                          │
│         Yahşi Batı Mizah Analiz Sistemi             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  LLM Seçimi: [○ Local (Ollama)] [● Bulut (Gemini)] │
│                                                     │
│  ┌─────────────────────────────────────────────┐    │
│  │ Sorunuzu yazın...                           │    │
│  └─────────────────────────────────────────────┘    │
│                                    [Sor]            │
│                                                     │
│  ── Cevap ──────────────────────────────────────    │
│  │ LLM'in ürettiği cevap burada görünür.       │    │
│  │ Sahne detayları, mizah analizi vs.           │    │
│  └──────────────────────────────────────────────    │
│                                                     │
│  ── Kaynak Chunk'lar ───────────────────────────    │
│  │ Retrieval ile getirilen chunk'lar burada     │    │
│  │ gösterilir. Hangi sahnelerden bilgi          │    │
│  │ getirildiği şeffaf olur.                     │    │
│  └──────────────────────────────────────────────    │
│                                                     │
│  ── Metrikler (opsiyonel sekme) ────────────────    │
│  │ Hallucination testi sonuçları               │    │
│  │ Retrieval doğruluğu                         │    │
│  │ Cevap kalitesi karşılaştırması              │    │
│  └──────────────────────────────────────────────    │
└─────────────────────────────────────────────────────┘
```

### Arayüz Özellikleri

- LLM seçimi (local/bulut) radio button ile
- Soru girişi text input
- **Opsiyonel filtreler (sidebar):** Karakter seçimi dropdown, mekan seçimi dropdown. Kullanıcı bunları seçerse ChromaDB'de metadata filtreleme uygulanır. Seçmezse tüm chunk'lar arasında aranır.
- Cevap alanı (markdown formatında, **streaming destekli** — kelimeler daktilo gibi tek tek ekrana düşer)
- Kaynak chunk'lar expander içinde (şeffaflık için)
- Metrikler sekmesi (bar chart'lar ile)

**Streaming Neden Önemli:** GTX 1650 Ti ile local LLM kullanırken, RAG prompt'undaki chunk'lar context'i büyütür ve ilk token'ın üretilmesi 5-15 saniye sürebilir. Streaming olmadan kullanıcı (veya sunum izleyicisi) ekranın donduğunu sanır. Ollama ve Gemini API ikisi de streaming destekler.

---

## Metrik Ölçümü

Projenin başarısını kanıtlamak için üç metrik kullanılacak. Bu metrikler hocanın slaytındaki "Üretken/RAG Projeleri İçin" bölümünü karşılar.

### Metrik 1: Hallucination Oranı

**Amaç:** RAG'ın LLM'in uydurmasını ne kadar azalttığını kanıtlamak.

**Yöntem:**
1. 20-30 adet test sorusu hazırla (filmin içeriğiyle ilgili olgusal sorular).
2. Her soruyu iki şekilde sor:
   - **RAG'sız:** LLM'e direkt sor (chunk vermeden). LLM kendi bilgisiyle cevap versin.
   - **RAG'lı:** Aynı soruyu RAG pipeline'ı üzerinden sor (chunk'lar verilmiş).
3. Her cevabı doğru/yanlış/uydurma olarak değerlendir.
4. Hallucination oranını hesapla: `uydurma_cevap_sayısı / toplam_soru_sayısı`

**Örnek test soruları:**
- "Yahşi Batı'da çizmeyi kim satmaya çalışıyor?" (Doğru cevap: Zeki)
- "Filmde Garfield şakasını kim yapıyor?" (Doğru cevap: Ramazan)
- "Çizmenin tarihi ne kadar eski?" (Doğru cevap: 130-140 yıllık)

**Beklenen sonuç:** RAG'sız LLM birçok detayı uydururken, RAG'lı sistem doğru cevap verecek.

**Gösterim:** Bar chart — RAG'lı vs RAG'sız hallucination oranları yan yana.

### Metrik 2: Retrieval Doğruluğu (Retrieval Precision)

**Amaç:** RAG sistemi doğru chunk'ları getiriyor mu?

**Yöntem:**
1. Aynı 20-30 test sorusunu kullan.
2. Her soru için RAG'ın getirdiği chunk'ları (top-3) incele.
3. Her chunk'ı "ilgili" veya "ilgisiz" olarak etiketle.
4. Precision hesapla: `ilgili_chunk_sayısı / toplam_getirilen_chunk_sayısı`

**Örnek:**
- Soru: "Garfield şakası neydi?"
- Getirilen chunk'lar: [yb_002 (ilgili), yb_005 (ilgisiz), yb_003 (ilgili)]
- Precision: 2/3 = %66.7

**Gösterim:** Ortalama retrieval precision yüzdelik olarak ve soru bazlı detaylı tablo.

### Metrik 3: Cevap Kalitesi Skoru (RAG'lı Sistem vs Düz LLM) — LLM-as-a-Judge

**Amaç:** Hocanın istediği "senin sistemin vs LLM" kıyaslamasını yapmak.

**Yöntem (LLM-as-a-Judge):**
Puanlamayı sen yapman yerine, bir LLM'e (Gemini) yaptırıyoruz. Bu daha objektif ve raporlanabilir.

1. 20-30 test sorusunu hem RAG'lı sisteme hem düz LLM'e (Gemini, RAG'sız) sor.
2. Her soru için iki cevabı ve doğru cevabı (ground truth) bir "hakem" LLM'e ver.
3. Hakem LLM şu prompt ile değerlendirir:

```
Sen bir cevap kalitesi değerlendirmecisisin. Sana bir soru, doğru cevap ve iki aday cevap vereceğim.
Her aday cevabı şu 3 kriter üzerinden 1-5 arası puanla:
- Doğruluk: Cevap olgusal olarak doğru mu? Doğru cevapla ne kadar örtüşüyor?
- Detay: Cevap yeterince detaylı ve bilgilendirici mi?
- Tutarlılık: Cevap kendi içinde tutarlı mı, çelişki var mı?

Sadece JSON formatında cevap ver:
{"cevap_a": {"dogruluk": X, "detay": X, "tutarlilik": X}, "cevap_b": {"dogruluk": X, "detay": X, "tutarlilik": X}}
```

4. Ortalama puanları karşılaştır.

**Neden LLM-as-a-Judge?** Puanlamayı projeyi yapan kişi (sen) yaparsa "taraflı metrik" eleştirisi alırsın. LLM ile otomatik değerlendirme hem daha objektif hem de tekrarlanabilir. Bu, akademide kabul gören bir yöntem.

**Olası bias ve limitation:** Eğer aynı LLM'i (Gemini) hem veri zenginleştirmede hem hakemlikte kullanırsan, model kendi üslubuna yatkınlık gösterebilir. Raporda bunu "limitation" olarak belirt. İdeal olan zenginleştirmede ve hakemlikte farklı modeller kullanmak ama bu zorunlu değil — farkında olduğunu göstermek yeterli.

**Gösterim:** Grouped bar chart — her kriter için RAG'lı vs RAG'sız puanlar yan yana. Her bir metrik için ayrı bar, iki renk (RAG'lı ve RAG'sız).

### Metrik Gösterim Örneği (Streamlit)

```
Metrikler sekmesinde üç grafik yan yana:

[Hallucination Oranı]     [Retrieval Precision]    [Cevap Kalitesi]
 RAG'sız: ████████ %70     Ortalama: ████████ %82    Doğruluk:  RAG ████ 4.2
 RAG'lı:  ██ %15                                                LLM ██ 2.1
                                                     Detay:     RAG ████ 3.8
                                                                LLM ███ 3.5
                                                     Tutarlılık:RAG ████ 4.5
                                                                LLM ██ 2.8
```

---

## Proje Dosya Yapısı

```
cmyllmz/
├── data/
│   ├── raw/
│   │   └── yahsi_bati.srt              # Orijinal altyazı dosyası
│   ├── processing/
│   │   ├── ham_chunks.json             # Faz 1 çıktısı — 1653 ham block (değiştirilmez)
│   │   ├── base_chunks.json            # Faz 4 çıktısı — chunk_merger.py ile oluşturulur
│   │   └── enriched_chunks.json        # Faz 6 çıktısı — LLM zenginleştirdi
│   └── final/
│       └── final_chunks.json           # Faz 7 çıktısı — RAG'a yüklenecek son hali
│
├── notes/
│   ├── block_referans.md              # Faz 3'te düzenliyorsun (=== ve -KOD-)
│   ├── karakterler.txt                # Karakter kodu → tam isim eşlemesi
│   ├── cmyllmz_proje_plani.md         # Bu dosya
│   └── notes.md                       # Serbest notlar
│
├── src/
│   ├── data_prep/
│   │   ├── srt_parser.py              # SRT → ham_chunks.json
│   │   ├── chunk_merger.py            # block_referans.md → base_chunks.json
│   │   ├── enricher.py                # LLM ile zenginleştirme scripti
│   │   ├── ner_extractor.py           # NER ile entity çıkarma
│   │   └── preprocessor.py            # NLP ön işleme (tokenizasyon, stop-word vs.)
│   │
│   ├── rag/
│   │   ├── embedder.py                # Embedding oluşturma
│   │   ├── vector_store.py            # ChromaDB işlemleri (yükleme, sorgulama)
│   │   └── retriever.py               # Retrieval mantığı
│   │
│   ├── llm/
│   │   ├── ollama_client.py           # Local LLM bağlantısı
│   │   ├── gemini_client.py           # Gemini API bağlantısı
│   │   └── prompt_templates.py        # System prompt ve user prompt şablonları
│   │
│   ├── evaluation/
│   │   ├── test_questions.json        # 20-30 test sorusu ve doğru cevapları
│   │   ├── hallucination_test.py      # Hallucination ölçümü
│   │   ├── retrieval_test.py          # Retrieval precision ölçümü
│   │   └── quality_test.py            # Cevap kalitesi ölçümü
│   │
│   └── app.py                         # Streamlit ana uygulaması
│
├── chroma_db/                         # ChromaDB veritabanı dosyaları (otomatik oluşur)
│
├── requirements.txt                   # Python bağımlılıkları
├── .env                               # API anahtarları (Gemini)
└── README.md                          # Proje açıklaması
```

### requirements.txt

```
streamlit
chromadb
sentence-transformers
ollama
google-generativeai
nltk
spacy
zeyrek
python-dotenv
matplotlib
```

Kurulum sonrası spaCy modelini de indir:
```bash
python -m spacy download xx_ent_wiki_sm
```

---

## Adım Adım Uygulama Planı

### Hafta 1: Altyapı Kurulumu + Veri Hazırlama (Tam Hafta)

**Gün 1: Ortam kurulumu**
- Python sanal ortamı oluştur
- requirements.txt'teki tüm kütüphaneleri kur
- Ollama'yı kur, model indir ve test et
- Gemini API anahtarını al (Google AI Studio'dan ücretsiz)
- Proje dosya yapısını oluştur

**Gün 1-2: SRT → Ham Block'lar (tamamlandı)**
- srt_parser.py ile ham_chunks.json oluşturuldu (1653 block)
- block_referans.md referans dosyası hazırlandı
- karakterler.txt karakter kodu listesi oluşturuldu

**Gün 2-7: Film İzle — Chunk Sınırları + Karakter Kodları (Faz 3, devam ediyor)**
- block_referans.md'i açık tut, filmi izle
- Chunk sınırlarına === yaz, karakter değişimlerinde -KOD- ekle
- Yeni karakterleri karakterler.txt'e ekle
- İzlerken aklına gelen test sorularını ayrı bir yere not al
- Bitince chunk_merger.py çalıştır → base_chunks.json
- Ardından base_chunks.json'da location / scene_description / humor_note doldur (Faz 5)
- NOT: related_chunks alanını bu aşamada boş bırak

### Hafta 2: Zenginleştirme + RAG Sistemi + Arayüz

**Gün 8-10: LLM ile Zenginleştirme + Gözden Geçirme (Faz 6-7)**
- base_chunks.json'daki her chunk'ı enricher.py ile Gemini'ye gönder
- Girdi: text + scene_description + humor_note + characters + location
- humor_analysis ve summary alanlarını doldurt → enriched_chunks.json
- Gözden geçirme (kritik!): her chunk'ın analizini oku, yanlış/saçma olanları düzelt
- related_chunks alanlarını doldur (tüm chunk ID'leri artık belli)
- final_chunks.json oluştur

**Gün 11-12: NLP Ön İşleme + NER + Embedding + ChromaDB**
- preprocessor.py: tokenizasyon, stop-word, normalizasyon
- ner_extractor.py: chunk'lardan entity çıkarma (spaCy + regex)
- embedder.py: chunk'ları embedding'e çevir
- vector_store.py: ChromaDB'ye yükle
- Basit bir sorgu ile test et

**Gün 13-14: LLM Entegrasyonu + Retrieval + Streamlit**
- ollama_client.py ve gemini_client.py: LLM bağlantıları
- retriever.py: soru → embedding → ChromaDB sorgu → chunk getir → prompt oluştur → LLM'e gönder
- app.py: Streamlit arayüzü (LLM seçimi, filtreler, streaming, kaynak chunk gösterimi)
- Uçtan uca test et

### Hafta 3: Metrikler + Raporlama + Son Düzeltmeler

**Gün 15-17: Test Soruları ve Metrik Ölçümü**
- test_questions.json: 20-30 soru + doğru cevaplar
- Hallucination testi çalıştır
- Retrieval precision hesapla
- LLM-as-a-Judge ile cevap kalitesi puanlama
- Bar chart'ları oluştur ve arayüze ekle

**Gün 18-21: Raporlama ve Son Düzeltmeler**
- Proje 1 raporu (RAG odaklı)
- Proje 2 raporu (NLP odaklı)
- Son testler, bug fix'ler
- Sunum hazırlığı (sunum için Gemini API kullanmayı düşün — local LLM sunum sırasında yavaş kalabilir)

---

## Raporlama Stratejisi

Aynı projeyi iki farklı açıdan raporlayacaksın.

### Proje 1 Raporu (MBU — Mühendislikte Bilgisayar Uygulamaları)

Odak: RAG pipeline'ı ve sistem mimarisi.

Anlatım sırası:
1. Problem tanımı (yapay zekanın mizah konusundaki eksikliği)
2. Veri kaynakları ve veri elde etme yöntemi (SRT dosyası, elle annotation)
3. Chunking stratejisi (sahne bazlı, heading-aware benzeri yaklaşım)
4. NER — Named Entity Recognition (spaCy ile kişi/yer/kurum çıkarma)
5. Embedding ve vektör veritabanı (SentenceTransformer + ChromaDB)
6. Retrieval mekanizması (cosine similarity ile top-k chunk getirme)
7. LLM entegrasyonu (local Ollama + bulut Gemini)
8. Arayüz (Streamlit)
9. Sonuçlar ve örnek soru-cevaplar

### Proje 2 Raporu (NLP — Doğal Dil İşleme)

Odak: NLP süreçleri, ön işleme, vektörleştirme, ölçüm.

Anlatım sırası:
1. Problem tanımı ve motivasyon
2. Özgün veri seti (Yahşi Batı chunk'ları, elle etiketlenmiş)
3. NLP ön işleme adımları (tokenizasyon, stop-word, normalizasyon — ders notlarındaki kavramlarla açıkla)
4. Özellik çıkarımı / vektörleştirme (embedding — Word2Vec'ten modern embedding'lere geçişi anlat)
5. RAG pipeline'ı (retrieval + generation)
6. Kullanıcı arayüzü
7. Başarı ölçümü:
   - Hallucination oranı (RAG'lı vs RAG'sız)
   - Retrieval doğruluğu
   - Cevap kalitesi (RAG destekli sistem vs düz LLM)
   - Bar chart'lar ile görselleştirme
8. RAG destekli sistemin düz LLM'den üstünlüğünün tartışması

---

## Kritik Uyarılar ve Dikkat Edilecekler

1. **API anahtarını asla GitHub'a yükleme.** `.env` dosyasını `.gitignore`'a ekle.

2. **Ollama modelini önceden test et.** Türkçe performansı düşükse farklı model dene. RAG ile desteklediğin için modelin Türkçe bilgisi çok kritik değil — önemli olan verilen bağlamı doğru kullanması.

3. **Veri seti kalitesi her şeyden önemli (Yankı Odası Riski).** LLM ile üretilen humor_analysis verileri yanlış olabilir. Bu yanlışları veri tabanına kaydedersen, RAG sistemi yanlış bilgiyi "doğruymuş gibi" kullanıcıya sunar. Adım 4'teki gözden geçirmeyi kesinlikle atlama — her chunk'ın analizini oku, saçma olanları düzelt. Bu projenin ölüm kalım noktası.

4. **Embedding için birleştirilmiş metin kullan.** Sadece diyalog metnini embed etme — summary ve humor_analysis bilgilerini de birleştir. Bu, retrieval kalitesini önemli ölçüde artırır.

5. **Test sorularını veri hazırlarken ayrı yaz.** Filmi izlerken aklına gelen soruları not al. Bunlar metrik ölçümünde kullanılacak.

6. **ChromaDB'yi her çalıştırmada sıfırdan oluşturma.** Persistent storage kullan ki her seferinde embed etmek zorunda kalma.

7. **Gemini API'nin ücretsiz kotasını kontrol et.** Google AI Studio'dan ücretsiz API anahtarı alabilirsin. Gemini 2.5 Flash ücretsiz tier'da kullanılabilir ancak rate limit'ler var. Zenginleştirme ve test sırasında buna dikkat et, gerekirse araya bekleme koy. Güncel limit'leri AI Studio'daki rate limit sayfasından kontrol et.

8. **SRT ön işleme çıktısını mutlaka gözden geçir.** SRT dosyaları beklenenden kirlidir: `[GÜLÜŞMELER]`, `(At kişnemesi)`, `{\a6}`, bozuk HTML tagları, üst üste binen diyaloglar. AI agent'ların yazacağı regex bunların hepsini temizleyemeyebilir. Ön işleme scriptinin çıktısını ham metin olarak gözünle kontrol et.

9. **Chunk bölmede mizahın bağlamını kırma.** Bazı espriler birden fazla sahneye yayılır (setup 10. dakikada, punchline 45. dakikada). Filmi izlerken chunk'ları düzeltirken, gerekirse bazılarını 1-2 dakikalık uzun sahnelere dönüştürmekten çekinme. Ayrıca `related_chunks` alanını kullanarak birbiriyle bağlantılı sahneleri işaretle.

10. **NER'de spaCy'den çok regex'e güven.** spaCy'nin çok dilli modeli Osmanlıca kelimeleri, film-spesifik isimleri ve uydurma terimleri tanımayacaktır. "Paşa", "Efendi", "Teşkilât-ı Mahsusa", "Aziz Vefa" gibi yapıları Türkçe regex pattern'lerle yakalamak daha güvenilir.

---

## Örnek Kullanım Senaryoları

Projenin çalışır halinde nasıl görüneceğine dair örnekler:

**Senaryo 1:**
Kullanıcı: "Garfield şakasını açıkla"
Sistem: yb_002 chunk'ını getirir. Cevap: "Zeki, çizmenin hikayesini anlatırken ABD Başkanı Garfield'den bahseder. Ramazan 'o kedi olan mı?' diye sorar. Burada mizah tekniği 'misunderstanding' ve 'cultural_reference' — Garfield ismi Türk popüler kültüründe karikatür kediyle özdeşleşmiştir, tarihsel figür bilinmez."

**Senaryo 2:**
Kullanıcı: "Filmde anakronizm örnekleri neler?"
Sistem: anachronism tekniği içeren tüm chunk'ları getirir. "Google'a girmek" gibi modern referansların Osmanlı/Vahşi Batı bağlamında kullanılmasını açıklar.

**Senaryo 3:**
Kullanıcı: "Alpay karakteri nasıl bir mizah tarzı kullanıyor?"
Sistem: Alpay'ın geçtiği chunk'ları getirir, karakter bazlı mizah analizi yapar.
