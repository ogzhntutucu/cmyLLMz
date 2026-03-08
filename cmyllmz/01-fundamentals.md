# Aşama 1: Temel Kavramlar

> Bu dosya, cmyllmz projesine başlamadan önce anlaşılması gereken temel NLP kavramlarını kapsar.
> Her kavram, projeyle doğrudan ilişkilendirilerek açıklanmıştır.

---

## İçindekiler

1. [NLP Nedir?](#1-nlp-nedir)
2. [Tokenizasyon](#2-tokenizasyon)
3. [Embedding (Vektörleme)](#3-embedding-vektörleme)
4. [Cosine Similarity (Kosinüs Benzerliği)](#4-cosine-similarity-kosinüs-benzerliği)
5. [RAG (Retrieval-Augmented Generation)](#5-rag-retrieval-augmented-generation)
6. [Vektör Veritabanı](#6-vektör-veritabanı)
7. [LLM Nedir, Biz Neden Sıfırdan Yapmıyoruz?](#7-llm-nedir-biz-neden-sıfırdan-yapmıyoruz)
8. [Kullanacağımız Araçlar](#8-kullanacağımız-araçlar)
9. [cmyllmz'in Tüm Akışı — Bir Bütün Olarak](#9-cmyllmzin-tüm-akışı--bir-bütün-olarak)

---

## 1. NLP Nedir?

**NLP (Natural Language Processing / Doğal Dil İşleme)**, bilgisayarların insan dilini anlayıp işleyebilmesini sağlayan yapay zeka dalıdır.

Bilgisayarlar sayılarla çalışır. Ama sen "Yahşi Batı'da Aziz ne diyor?" diye sorduğunda, bu bir metin. Bilgisayar bu metni direkt anlayamaz. NLP, bu metni bilgisayarın işleyebileceği biçime dönüştürmenin yöntemidir.

### Günlük Hayattan NLP Örnekleri

| Uygulama | NLP Görevi |
|---|---|
| Google Çeviri | Makine çevirisi |
| Siri / Google Asistan | Konuşma tanıma + anlam çıkarma |
| Gmail spam filtresi | Metin sınıflandırma |
| ChatGPT | Metin üretme |
| **cmyllmz** | **Replik arama + cevap üretme** |

### cmyllmz ile Bağlantısı

Biz NLP'yi şu amaçlarla kullanacağız:
- Kullanıcının sorusunu anlayıp en ilgili Cem Yılmaz repliklerini bulmak
- Bulunan replikleri bir LLM'e bağlam olarak verip anlamlı cevap üretmek

---

## 2. Tokenizasyon

### Tokenizasyon Nedir?

**Token** = bir metnin en küçük anlamlı birimi.
**Tokenizasyon** = bir metni bu küçük parçalara bölme işlemi.

Düşün ki bir cümleyi kelimelerine ayırıyorsun. İşte bu, tokenizasyonun en basit hali.

### Örnek

```
Cümle: "Aziz Vefa, şerife meydan okudu."

Kelime bazlı tokenizasyon:
["Aziz", "Vefa", ",", "şerife", "meydan", "okudu", "."]

Alt-kelime bazlı tokenizasyon (modern modeller böyle yapar):
["Az", "iz", "Vefa", ",", "şer", "ife", "meydan", "oku", "du", "."]
```

### Neden Alt-Kelime?

Türkçe eklemeli bir dil. "Okumak" → "okuyor", "okudum", "okuyacak", "okutulmuş" gibi onlarca form alabilir. Alt-kelime tokenizasyon bu morfolojik zenginliği daha iyi yakalar çünkü ekleri ayrı token olarak işler.

### Modern Embedding Modellerinde Tokenizasyon

Biz `sentence-transformers` kütüphanesi kullanacağız. Bu kütüphane tokenizasyonu **kendi içinde otomatik yapıyor**. Yani biz "Aziz Vefa, şerife meydan okudu." diye metin veriyoruz, model kendi tokenize ediyor.

> **Önemli:** Bu yüzden biz preprocessing aşamasında noktalama kaldırmıyoruz.
> `"Lanet olsun!"` ile `"lanet olsun"` modelin gözünde farklı anlam taşıyabilir.

### cmyllmz ile Bağlantısı

Yahşi Batı repliklerini veritabanına eklerken her replik şöyle işlenecek:

```
Ham replik: "— Dur bakalım, nereye bu kadar acele?"

Sentence-Transformer bu cümleyi kendi içinde tokenize eder
ve doğrudan bir vektöre (sayı dizisine) dönüştürür.
Biz buna müdahale etmiyoruz.
```

---

## 3. Embedding (Vektörleme)

Bu kavram projenin kalbidir. İyi anlamak lazım.

### Problem: Bilgisayar Metni Anlayamaz

Bilgisayar şunu anlayamaz:
```
"Aziz elini çekti."
```

Ama şunu anlayabilir:
```
[0.23, -0.87, 0.41, 0.12, -0.55, ...]  ← sayı dizisi
```

**Embedding**, bir metni bu tür sayı dizilerine (vektörlere) dönüştürme işlemidir.

### Sihirli Özellik: Anlam = Konum

Embedding modellerinin harika yanı şu: **anlamca yakın metinler, sayı uzayında da birbirine yakın olur.**

```
"Dur bakalım!"          → [0.21, 0.85, -0.12, ...]
"Bekle bir dakika!"     → [0.19, 0.83, -0.14, ...]   ← yakın!
"İki kilo domates."     → [0.91, -0.44, 0.67, ...]   ← uzak!
```

Bu iki cümle anlam bakımından benzer, vektörleri de birbirine yakın çıkıyor.

### Görsel Olarak Düşün

Bir düşün ki her metin 2 boyutlu bir haritaya nokta olarak işleniyor:

```
        ↑
        |  "bekle"   "dur"
        |      •       •        ← Emirler grubu
        |
        |
        |
        |                "domates"
        |                    •  ← Tamamen alakasız
        +---------------------------→
```

Gerçekte vektörler 768 veya 1024 boyutlu — ama fikir bu.

### Embedding Modeli Ne Yapar?

Eğitilmiş bir sinir ağıdır. Milyonlarca cümleyi gördükten sonra "hangi cümleler birbirine benzer" ilişkisini öğrenmiştir. Biz bu hazır modeli kullanacağız.

```python
# Örnek kullanım (henüz kod yazmıyoruz, fikir için):
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

cumle = "Dur bakalım, nereye bu kadar acele?"
vektor = model.encode(cumle)  # → [0.23, -0.87, 0.41, ...]
print(vektor.shape)  # (384,) → 384 boyutlu vektör
```

### cmyllmz ile Bağlantısı

Yahşi Batı'daki her repliği bu şekilde vektöre çevireceğiz:

```
"— İki akıllı adam aynı şeyi düşünürmüş."  → [0.12, 0.89, -0.34, ...]
"— Ben zaten bunu düşünüyordum."            → [0.44, -0.21, 0.78, ...]
"— Kovboylar Batı'da yaşar."                → [0.91, 0.03, -0.55, ...]
```

Kullanıcı "Aziz ne diyordu?" diye sorduğunda, bu soru da vektöre çevrilir ve en yakın repliklere bakılır.

---

## 4. Cosine Similarity (Kosinüs Benzerliği)

### İki Vektör Arasındaki Benzerliği Nasıl Ölçürüz?

Embedding'den sonra elimizde sayı dizileri var. Peki iki sayı dizisi ne kadar birbirine benziyor?

**Cosine Similarity** bunu ölçer. Sonuç her zaman **-1 ile 1 arasında** çıkar:

| Sonuç | Anlam |
|---|---|
| **1.0** | Tamamen aynı anlam |
| **~0.8** | Çok benzer |
| **~0.5** | Orta derecede benzer |
| **~0.0** | İlgisiz |
| **-1.0** | Zıt anlam |

### Neden "Cosine"?

Vektörler arasındaki **açıya** bakılır. Paralel iki vektörün arası 0 derece → cos(0) = 1 → tamamen benzer.
Dik iki vektörün arası 90 derece → cos(90) = 0 → ilgisiz.

Bunu bilmen yeterli. Formülü ezberlemeye gerek yok.

### Math (Anlamak İçin)

```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
```

Burada:
- `A · B` = A ve B vektörlerinin iç çarpımı
- `||A||` = A vektörünün uzunluğu (büyüklüğü)

### Somut Örnek

```
Kullanıcı sorusu: "Aziz ne yapıyordu?"
  → vektör: [0.3, 0.7, -0.2, ...]

Replik 1: "Aziz elini silahına attı."
  → vektör: [0.28, 0.69, -0.18, ...]
  → benzerlik: 0.97 ✅ çok yakın

Replik 2: "Yemeği kim yapacak?"
  → vektör: [0.85, -0.4, 0.6, ...]
  → benzerlik: 0.12 ❌ alakasız
```

Sistem Replik 1'i getirir çünkü çok daha benzer.

### cmyllmz ile Bağlantısı

Kullanıcı bir soru sorduğunda:
1. Soru vektöre çevrilir
2. Veritabanındaki TÜM repliklerle cosine similarity hesaplanır
3. En yüksek skoru alanlar (Top-K) seçilir
4. Bu replikler LLM'e bağlam olarak verilir

---

## 5. RAG (Retrieval-Augmented Generation)

### RAG Neden İcat Edildi?

Bir LLM'nin iki temel problemi var:

**Problem 1: Halüsinasyon**
LLM bilmediği şeyleri uyduruyor.
> "Yahşi Batı'da Aziz ne diyor?" → ChatGPT mantıklı görünen ama tamamen uydurulmuş bir replik söyleyebilir.

**Problem 2: Güncellik / Özellik**
LLM eğitildiği kadar biliyor. Senin spesifik verine erişimi yok.

**RAG'ın Çözümü:**
> "Cevap üretmeden önce, güvenilir bir kaynaktan (kendi veritabanımız) ilgili bilgiyi çek. Sonra LLM bu bilgiyi kullanarak cevap üretsin."

### RAG'ın 3 Adımı

```
1. INDEX (Veritabanı Oluşturma — bir kez yapılır):
   Tüm replikler → embedding → vektör veritabanı

2. RETRIEVE (Bilgi Çekme — her soru için):
   Kullanıcı sorusu → embedding → veritabanında benzer replikler ara

3. GENERATE (Cevap Üretme — her soru için):
   [Bulunan replikler + Kullanıcı sorusu] → LLM → Cevap
```

### "Augmented" Ne Demek?

"Augmented Generation" = "zenginleştirilmiş üretim". LLM cevabı yoktan üretmiyor; senin sağladığın bağlamla **zenginleştirilerek** üretiyor.

Bağlam (context) olmadan:
```
Soru: "Aziz'in şerife söylediği replik nedir?"
LLM: "Aziz şerife: 'Bu kasabada ikimize yer var.' dedi." ← UYDURMA
```

RAG ile:
```
Bağlam: [Veritabanından çekilen 3 replik]
Soru: "Aziz'in şerife söylediği replik nedir?"
LLM: "Veritabanındaki bilgilere göre Aziz şerife şunu söyledi: '...'" ← DOĞRU
```

### RAG vs Fine-tuning

Neden RAG yapıyoruz, modeli fine-tune etmiyoruz?

| | RAG | Fine-tuning |
|---|---|---|
| **Veri gerekliliği** | Az veri yeterli | Çok büyük veri seti lazım |
| **Güncelleme** | Veritabanını güncelle yeter | Modeli yeniden eğitmek lazım |
| **Halüsinasyon** | Düşük (gerçek veriye dayanıyor) | Hâlâ olabilir |
| **Maliyet** | Düşük | Çok yüksek (GPU, süre) |
| **cmyllmz için** | ✅ İdeal | ❌ Gereksiz karmaşık |

### cmyllmz RAG Akışı — Somut

```
[INDEX aşaması — bir kez:]
Yahşi Batı replikleri → embedding → ChromaDB'ye yükle

[RETRIEVE aşaması — her soru için:]
Kullanıcı: "Aziz düelloda ne dedi?"
  ↓
Soru embedding'e çevrilir: [0.34, -0.12, 0.89, ...]
  ↓
ChromaDB'de en benzer 3-5 repliği bul:
  - "Silahımı çekiyorum!" [benzerlik: 0.94]
  - "Batı'da bu böyle olur." [benzerlik: 0.87]
  - "Hazır mısın?" [benzerlik: 0.81]

[GENERATE aşaması — her soru için:]
LLM'e şu prompt gönderilir:
"Sen Yahşi Batı filmi konusunda uzmansın.
 Aşağıdaki bağlam bilgilerini kullan:
 - 'Silahımı çekiyorum!'
 - 'Batı'da bu böyle olur.'
 - 'Hazır mısın?'
 
 Soru: Aziz düelloda ne dedi?
 Cevap:"
  ↓
LLM: "Yahşi Batı'daki düello sahnesinde Aziz şunları söyledi: ..."
```

---

## 6. Vektör Veritabanı

### Normal Veritabanından Farkı Nedir?

Normal bir veritabanında (SQL gibi) şöyle arama yaparsın:
```sql
SELECT * FROM replikler WHERE karakter = 'Aziz';
```
Bu **tam eşleşme** arar. "Aziz" ile tam eşleşmeyen hiçbir şeyi getirmez.

Vektör veritabanında şöyle arama yaparsın:
```
"Silahını çeken adam" → [vektör] → en benzer replikleri getir
```
Bu **anlam benzerliğine** göre arar. "Silahını çeken adam" ile "Kovboy düellosu" birbirine yakın gelir.

### Nasıl Çalışır?

```
1. Her metin bir vektöre dönüştürülür ve veritabanına kaydedilir:
   "Dur bakalım!" → [0.23, 0.41, -0.12, ...] → kaydedildi

2. Sorgu geldiğinde:
   "Ne dedi?" → [0.21, 0.39, -0.10, ...]
   
3. Bu sorgu vektörü ile tüm vektörler arasında cosine similarity hesaplanır

4. En yakın olanlar döndürülür
```

### ChromaDB mi FAISS mi?

İkisi de vektör veritabanı, ama farklı yapılar:

| | ChromaDB | FAISS |
|---|---|---|
| **Kurulum** | Çok kolay | Biraz daha teknik |
| **Kullanım** | Python ile rahat | Düşük seviyeli kontrol |
| **Persistans** | Diske kaydeder | Hafızada çalışır (ekstra adım lazım) |
| **Metadata** | Tam destek (film, karakter, sahne) | Sınırlı |
| **cmyllmz için** | ✅ Tercih edilen | Şimdilik gerek yok |

**Biz ChromaDB kullanacağız.** Sebep: kurulumu basit, metadata desteği iyi (film adı, karakter adı gibi filtreler yapabileceğiz), Python ile çalışması kolay.

### ChromaDB'de Metadata Filtreleme

ChromaDB'nin güzel özelliği şu: vektör aramanın yanında geleneksel filtreler de uygulayabilirsin:

```python
# Sadece Aziz Vefa'nın repliklerinde ara:
results = collection.query(
    query_texts=["düello sahnesi"],
    n_results=3,
    where={"karakter": "Aziz Vefa"}  # ← metadata filtresi
)
```

---

## 7. LLM Nedir, Biz Neden Sıfırdan Yapmıyoruz?

### LLM (Large Language Model) Nedir?

**LLM**, milyarlarca parametreye sahip, trilyonlarca kelimelik veriyle eğitilmiş büyük bir sinir ağıdır. GPT-4, Gemini, Claude bunlara örnektir.

Bu modeller metin okuyup **bir sonraki token'ı tahmin etmeyi** öğrenerek gelişir. Milyonlarca sayfayı "bir sonraki kelime nedir?" sorusunu yanıtlayarak okuduktan sonra, sanki her şeyi anlıyormuş gibi cevap üretebilir hale gelir.

### Neden Sıfırdan LLM Yapmıyoruz?

```
GPT-3:
- Parametre sayısı: 175 milyar
- Eğitim verisi: 570 GB metin
- Eğitim süresi: Aylarca, binlerce GPU
- Maliyet: ~4.6 milyon dolar

cmyllmz için elimizde:
- Parametre sayısı: —
- Eğitim verisi: 100-150 replik (~5 KB)
- Eğitim süresi: Yok
- Maliyet: API ücreti
```

Bu karşılaştırma bile fazlasıyla açıklıyor. Sıfırdan LLM yapmak imkansız değil ama anlamsız — özellikle bu proje için.

### Biz LLM'i Nasıl Kullanıyoruz?

Sıfırdan yapmıyoruz ama kullanıyoruz:
- OpenAI'nin GPT modelini veya Google'ın Gemini modelini **API üzerinden** kullanacağız
- Biz sorguyu + bağlamı (RAG'dan gelen replikler) gönderiyoruz
- LLM cevabı üretiyor

Bu ayırt edici nokta: LLM bizim modelimizin **parçası** ama **kendisi değil**.

### Fine-tuning Ne Olurdu?

Fine-tuning'de var olan bir modeli alıp kendi verinle ek eğitime tabi tutarsın. Mesela GPT'yi alıp 100 Cem Yılmaz repliğiyle eğitirsin. Bu da bir seçenek ama:
- Çok pahalı
- Hoca RAG istiyor
- Gereksiz karmaşık

---

## 8. Kullanacağımız Araçlar

### Python Ortamı

**Python 3.10+** kullanacağız. Tüm NLP kütüphaneleri Python için mevcut.

**Virtual Environment (venv)**: Proje bağımlılıklarını izole etmek için:
```bash
# Proje klasöründe:
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate   # Windows

# Kütüphaneleri yükle:
pip install sentence-transformers chromadb langchain openai pandas
```

Neden venv? Farklı projeler farklı kütüphane versiyonları gerektirebilir. venv bunları birbirinden ayırır.

---

### Sentence-Transformers

**Görev:** Metni vektöre çevirme (embedding)

HuggingFace'in kütüphanesi. Yüzlerce hazır embedding modeli barındırır.

**cmyllmz için kullanacağımız model:**
```
paraphrase-multilingual-MiniLM-L12-v2
```
- Türkçe dahil 50+ dili destekler
- Hızlı ve hafif (384 boyutlu vektör)
- Anlamsal benzerlikte çok iyi

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Tek cümle:
replik = "Dur bakalım, nereye bu kadar acele?"
vektor = model.encode(replik)
# vektor.shape → (384,)

# Toplu işlem (verimli):
replikler = ["Dur bakalım!", "İkimize yer var.", "Silahını çek!"]
vektorler = model.encode(replikler)
# vektorler.shape → (3, 384)
```

---

### ChromaDB

**Görev:** Vektörleri saklama ve benzerlik araması

```python
import chromadb

# Veritabanı oluştur (diske kaydeder):
client = chromadb.PersistentClient(path="./cmyllmz_db")

# Koleksiyon oluştur:
collection = client.create_collection("yahsi_bati")

# Veri ekle:
collection.add(
    documents=["Dur bakalım!", "İkimize yer var."],
    metadatas=[
        {"karakter": "Aziz", "sahne": "Giriş"},
        {"karakter": "Aziz", "sahne": "Düello"}
    ],
    ids=["yb_001", "yb_002"]
)

# Sorgula:
results = collection.query(
    query_texts=["Aziz ne dedi?"],
    n_results=2
)
```

---

### LangChain

**Görev:** RAG pipeline'ını düzenlemek

LangChain, RAG gibi karmaşık akışları kolayca bir araya getirmek için tasarlanmış bir framework.

Olmadan:
```
Soru al → Embedding model çağır → ChromaDB'ye sor →
Sonuçları formatla → LLM'e gönder → Cevap al → Döndür
```

Her adımı ayrı ayrı kod yazman lazım.

LangChain ile bu adımların çoğu hazır bileşenler olarak geliyor, sen sadece bunları birleştiriyorsun.

```python
# Kavramsal örnek (detayları Aşama 5'te):
from langchain.chains import RetrievalQA

chain = RetrievalQA(
    llm=llm,
    retriever=vectorstore.as_retriever()
)

cevap = chain.run("Aziz düelloda ne dedi?")
```

---

### OpenAI / Gemini API

**Görev:** Cevap üretme + kıyaslama

Biz iki farklı amaçla LLM API kullanacağız:

1. **cmyllmz'in içinde:** RAG bağlamıyla birlikte cevap üretmek
2. **Kıyaslamada:** Aynı soruları RAG olmadan sormak (sade LLM)

**API Key:**
- OpenAI: [platform.openai.com](https://platform.openai.com) → API keys
- Gemini: [aistudio.google.com](https://aistudio.google.com) → API keys (ücretsiz tier var)

Hangisini seçeceğimize Aşama 5'te karar vereceğiz.

---

### scikit-learn, pandas, matplotlib

**scikit-learn:** Accuracy, precision, recall, F1-score gibi metrikleri hesaplamak için.

```python
from sklearn.metrics import accuracy_score, f1_score

gercek  = [1, 1, 0, 1, 0]
tahmin  = [1, 0, 0, 1, 0]
print(accuracy_score(gercek, tahmin))  # 0.8
```

**pandas:** Veri setimizi tablo olarak yönetmek için. JSON/CSV okuma/yazma.

**matplotlib:** Sonuçları grafik olarak görselleştirmek için.

---

## 9. cmyllmz'in Tüm Akışı — Bir Bütün Olarak

Şimdi tüm kavramları bir araya getirelim. cmyllmz'e "Aziz düelloda ne söylüyor?" diye sorulduğunda ne olur?

```
┌──────────────────────────────────────────────────────────────────┐
│  HAZIRLIK (bir kez yapılır):                                     │
│                                                                  │
│  Yahşi Batı replikleri (JSON)                                    │
│         ↓                                                        │
│  Hafif temizlik (boşluklar, HTML — orijinal metin korunur)       │
│         ↓                                                        │
│  sentence-transformers → her replik 384 boyutlu vektöre çevrilir │
│         ↓                                                        │
│  ChromaDB'ye yüklenir (replik + vektör + metadata birlikte)      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  KULLANIMI (her soruda):                                         │
│                                                                  │
│  Kullanıcı: "Aziz düelloda ne söylüyor?"                         │
│         ↓                                                        │
│  Soru da vektöre çevrilir: [0.34, -0.12, 0.89, ...]             │
│         ↓                                                        │
│  ChromaDB'de cosine similarity ile en benzer 3-5 replik bulunur  │
│         ↓                                                        │
│  LLM'e şu gönderilir:                                           │
│    "Bağlam: [bulunan replikler]                                  │
│     Soru: Aziz düelloda ne söylüyor?"                            │
│         ↓                                                        │
│  LLM cevap üretir (halüsinasyon yok, bağlama dayalı)             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  DEĞERLENDİRME:                                                  │
│                                                                  │
│  Aynı soruları sade LLM'e sor (RAG olmadan)                      │
│         ↓                                                        │
│  cmyllmz accuracy vs sade LLM accuracy karşılaştır              │
│         ↓                                                        │
│  Sonuç: cmyllmz daha iyi! (çünkü gerçek veriyle destekleniyor)  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Özet: Temel Kavramlar

| Kavram | Kısaca Tanım | cmyllmz'deki Rolü |
|---|---|---|
| **Tokenizasyon** | Metni küçük parçalara bölme | Embedding modeli içinde otomatik |
| **Embedding** | Metni sayı dizisine çevirme | Her repliği vektöre çevirmek |
| **Cosine Similarity** | İki vektör arasındaki benzerlik | İlgili replikleri bulmak |
| **RAG** | Veritabanından bilgi çekip LLM ile üretme | Projenin tüm mimarisi |
| **Vektör DB** | Vektörleri saklayan ve sorgulayan veritabanı | ChromaDB ile Yahşi Batı replikleri |
| **LLM API** | Hazır büyük dil modeli servisi | Cevap üretme + kıyaslama |

---

> **Sonraki Adım:** [02-data-collection.md] — Yahşi Batı repliklerini toplayıp JSON formatına dönüştürme
