# cmyllmz — Cem Yılmaz Evreni için Özelleşmiş Dil Modeli

> **Ders:** Doğal Dil İşleme (NLP)
> **Proje Türü:** Hibrit RAG + LLM Sistemi
> **Başlangıç Kapsamı:** Yahşi Batı (2010)
> **Dil:** Türkçe
> **Geliştirme Ortamı:** Python + VSCode (lokal), Google Colab (gerekirse)
> **Donanım:** Laptop, GTX 1650Ti GPU

---

## 1. Proje Özeti

cmyllmz, Cem Yılmaz'ın film replikleri, stand-up gösterileri ve diğer içerikleri üzerinde uzmanlaşmış bir hibrit RAG (Retrieval-Augmented Generation) + LLM sistemidir.

**Modelin yapabilecekleri:**
- Bir repliğin devamını getirebilir
- Repliğin hangi film/gösteri/sahneden olduğunu söyleyebilir
- Şakayı açıklayabilir / bağlamını anlatabilir
- Karaktere göre replik bulabilir
- Konu/tema bazlı replik önerebilir

**İlk aşamada** yalnızca Yahşi Batı filmi için özelleşecek. Süreç öğrenildikten sonra kapsam genişletilecek.

---

## 2. Teknik Mimari

```
┌─────────────────────────────────────────────────┐
│                  Kullanıcı Sorusu               │
│   "Yahşi Batı'da Aziz'in düello sahnesindeki    │
│    repliği neydi?"                              │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│            1. Preprocessing                     │
│   Soruyu temizle, tokenize et, normalize et     │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│            2. Vektörleme (Embedding)            │
│   Soruyu sayısal vektöre çevir                  │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│            3. RAG — Vektör Veritabanı           │
│   Soruyla en benzer replikleri/bilgileri bul     │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│            4. LLM (API)                         │
│   Bulunan bilgileri bağlam olarak LLM'e ver     │
│   LLM yaratıcı/doğru cevap üretsin             │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│            5. Cevap                             │
│   "Aziz'in düello sahnesindeki repliği:         │
│    '...' şeklindedir. Bu sahne filmin           │
│    X bölümünde geçer."                          │
└─────────────────────────────────────────────────┘
```

---

## 3. Hocanın Gereksinimleri ve Karşılıkları

| Gereksinim | cmyllmz'deki Karşılığı | Durum |
|---|---|---|
| Spesifik konu seçimi | Cem Yılmaz evreni (başlangıç: Yahşi Batı) | ✅ |
| En az 50 cümlelik ham veri seti | Yahşi Batı replik veritabanı (~50-70 entry) | ⬜ |
| Preprocessing pipeline | Metin temizleme, tokenizasyon, normalizasyon | ⬜ |
| RAG veritabanı | Vektör DB (ChromaDB veya FAISS) | ⬜ |
| Vektörleme | Türkçe embedding modeli ile vektöre çevirme | ⬜ |
| Model oluşturma | Hibrit RAG + LLM sistemi | ⬜ |
| %80/%20 train/test split | Veri bölme ve test seti oluşturma | ⬜ |
| %90+ accuracy | Test soruları üzerinde doğruluk ölçümü | ⬜ |
| MAE, accuracy gibi metrikler | Accuracy, precision, recall, F1-score | ⬜ |
| LLM ile kıyaslama | Aynı soruları sade LLM'e sorarak karşılaştırma | ⬜ |

---

## 4. Detaylı Roadmap

### Aşama 1: Temelleri Öğrenme
> *Tahmini süre: 2-3 gün*

Herhangi bir kod yazmadan önce temel kavramları öğrenmemiz gerekiyor.

- [ ] **1.1** NLP temel kavramlarını öğren
  - Tokenizasyon nedir?
  - Embedding (vektörleme) nedir?
  - Cosine similarity (kosinüs benzerliği) nedir?
- [ ] **1.2** RAG kavramını öğren
  - RAG nedir, neden kullanılır?
  - Vektör veritabanı nedir? (ChromaDB, FAISS)
  - Retrieval (bilgi çekme) nasıl çalışır?
- [ ] **1.3** Gerekli araçları/kütüphaneleri tanı
  - Python ortamı (venv / conda)
  - LangChain veya LlamaIndex (RAG framework)
  - ChromaDB veya FAISS (vektör DB)
  - Sentence-Transformers (embedding)
  - OpenAI / Gemini API (LLM)

### Aşama 2: Veri Toplama ve Hazırlama
> *Tahmini süre: 2-3 gün*

- [ ] **2.1** Yahşi Batı repliklerini topla
  - Film altyazı dosyasını (.srt) bul veya replikleri elle yaz
  - Her repliği yapılandırılmış formata çevir
- [ ] **2.2** Veri yapısını oluştur
  ```
  Her veri parçası (document) şunları içerecek:
  - film: "Yahşi Batı"
  - karakter: "Aziz Vefa"
  - sahne: "Düello sahnesi"
  - replik: "..."
  - bağlam: "Sahne açıklaması / öncesi-sonrası"
  - kategori: "komedi / aksiyon / dram"
  ```
- [ ] **2.3** Veriyi %80/%20 oranında böl
  - Tüm veriler vektör veritabanına yüklenir
  - Soru setini %80/%20 olarak böl:
    - %80 → Geliştirme sırasında test etmek için (eğitim soruları)
    - %20 → Final değerlendirmede kullanılacak sorular (model bu soruları hiç görmeyecek)
- [ ] **2.4** Q&A (Soru-Cevap) çiftleri oluştur
  - İki tür soru hazırla:
    - **Faktüel sorular** (tek doğru cevabı olan): "Bu replik hangi sahneden?" → Exact match ile ölçülür
    - **Açık uçlu sorular** (yoruma dayalı): "Bu şakanın bağlamını açıkla" → Semantik benzerlik ile ölçülür
  - Her soru için beklenen doğru cevabı yaz
  - Örnek: Soru: "Aziz'in şerife söylediği ilk replik nedir?" → Cevap: "..."

### Aşama 3: Preprocessing Pipeline
> *Tahmini süre: 1-2 gün*

- [ ] **3.1** Metin temizleme fonksiyonları yaz
  - Gereksiz boşlukları kaldır
  - Noktalama işaretlerini düzenle
  - Küçük/büyük harf normalizasyonu
- [ ] **3.2** Tokenizasyon işlemini uygula
  - Cümleleri anlamlı parçalara (token) ayır
  - Türkçeye uygun tokenizer seç
- [ ] **3.3** Pipeline'ı birleştir
  - Ham veri → temizleme → tokenizasyon → çıktı
  - Pipeline'ın doğru çalıştığını test et

### Aşama 4: Vektörleme ve RAG Veritabanı
> *Tahmini süre: 2-3 gün*

- [ ] **4.1** Embedding modelini seç ve kur
  - Türkçe destekleyen bir model seç
  - Sentence-Transformers kütüphanesini kullan
- [ ] **4.2** Verileri vektöre çevir
  - Her replik/dokümanı sayısal vektöre dönüştür
  - Vektörlerin doğruluğunu kontrol et
- [ ] **4.3** Vektör veritabanını kur (ChromaDB veya FAISS)
  - Veritabanını oluştur
  - Vektörleri yükle
  - Basit bir sorguyla test et (örn: "düello" → ilgili replikler gelmeli)
- [ ] **4.4** Retrieval (bilgi çekme) mekanizmasını yaz
  - Kullanıcı sorusunu al → vektöre çevir → en benzer sonuçları getir
  - Top-K parametresini ayarla (kaç sonuç getirsin)

### Aşama 5: LLM Entegrasyonu (Hibrit Model)
> *Tahmini süre: 2-3 gün*

- [ ] **5.1** LLM API'sini bağla
  - OpenAI (GPT) veya Google (Gemini) API key al
  - API bağlantısını test et
- [ ] **5.2** Prompt şablonu oluştur
  ```
  Örnek prompt:
  "Sen Cem Yılmaz filmleri konusunda uzman bir asistansın.
   Aşağıdaki bağlam bilgilerini kullanarak soruyu cevapla.
   
   Bağlam: {RAG'dan gelen replikler/bilgiler}
   
   Soru: {Kullanıcının sorusu}
   
   Cevap:"
  ```
- [ ] **5.3** RAG + LLM pipeline'ını birleştir
  - Soru → RAG'dan bilgi çek → LLM'e bağlamla birlikte gönder → cevap al
  - Uçtan uca test et
- [ ] **5.4** Cevap kalitesini gözle kontrol et
  - 5-10 soru sor, cevapları incele
  - Prompt şablonunu gerekirse düzenle

### Aşama 6: Test ve Değerlendirme
> *Tahmini süre: 1-2 gün*

- [ ] **6.1** Test setini modelden geçir
  - %20'lik test setindeki tüm soruları modele sor
  - Cevapları kaydet
- [ ] **6.2** Metrikleri hesapla
  - **Accuracy ölçümü — iki yöntemle:**
    - *Faktüel sorular:* Modelin cevabı doğru mu değil mi → exact match (doğru=1, yanlış=0)
    - *Açık uçlu sorular:* Modelin cevabı ile beklenen cevap arasındaki semantik benzerlik (cosine similarity). Benzerlik ≥ 0.8 ise doğru sayılır
  - **MAE (Mean Absolute Error):** Semantik benzerlik skorları üzerinden hesaplanır
    - Her soru için: hata = 1.0 - benzerlik_skoru
    - MAE = tüm hataların ortalaması (düşük MAE = iyi performans)
  - **Precision**: Doğru pozitif / (doğru pozitif + yanlış pozitif)
  - **Recall**: Doğru pozitif / (doğru pozitif + yanlış negatif)
  - **F1-Score**: Precision ve recall'un harmonik ortalaması
  - Hedef: %90+ accuracy
- [ ] **6.3** Sonuçları analiz et
  - Hangi sorularda başarısız oldu?
  - Neden başarısız oldu?
  - İyileştirme yapılabilir mi?

### Aşama 7: LLM Kıyaslaması
> *Tahmini süre: 1 gün*

- [ ] **7.1** Aynı test sorularını sade LLM'e sor
  - ChatGPT / Gemini API'ye aynı soruları sor (RAG bağlamı olmadan)
  - Cevapları kaydet
- [ ] **7.2** Sonuçları karşılaştır
  - cmyllmz accuracy vs. sade LLM accuracy
  - Spesifik sorularda farkları göster
  - Tablo/grafik hazırla
- [ ] **7.3** Sonuç raporu yaz
  - "cmyllmz, Yahşi Batı replikleri konusunda genel LLM'den %X daha iyi performans gösterdi"

### Aşama 8: Sunum ve Dokümantasyon
> *Tahmini süre: 1 gün*

- [ ] **8.1** Proje dokümantasyonunu tamamla
  - README.md yaz
  - Kurulum adımları
  - Kullanım örnekleri
- [ ] **8.2** Sonuçları görselleştir
  - Accuracy karşılaştırma grafikleri
  - Örnek soru-cevap görselleri
- [ ] **8.3** (Opsiyonel) GitHub'a yükle

---

## 5. Kullanılacak Teknolojiler

| Araç | Kullanım Amacı |
|---|---|
| **Python 3.10+** | Ana programlama dili |
| **ChromaDB** veya **FAISS** | Vektör veritabanı |
| **Sentence-Transformers** | Türkçe metin vektörleme |
| **LangChain** veya **LlamaIndex** | RAG framework |
| **OpenAI API** veya **Gemini API** | LLM (cevap üretme + kıyaslama) |
| **scikit-learn** | Metrik hesaplama |
| **pandas** | Veri işleme |
| **matplotlib** / **seaborn** | Görselleştirme |

---

## 6. Veri Yapısı Örneği

```json
{
  "id": "yb_001",
  "film": "Yahşi Batı",
  "yil": 2010,
  "karakter": "Aziz Vefa",
  "sahne": "Düello sahnesi",
  "replik": "...",
  "baglam": "Aziz, şerife meydan okur ve...",
  "kategori": "komedi",
  "sure_dakika": "01:12:34"
}
```

---

## 7. Başarı Kriterleri

- [ ] Preprocessing pipeline çalışıyor
- [ ] Vektör veritabanı sorgulanabiliyor
- [ ] RAG + LLM entegrasyonu cevap üretiyor
- [ ] Test setinde %90+ accuracy
- [ ] Sade LLM ile kıyaslamada daha iyi sonuç

---

## 8. Notlar

- Bu dosya proje boyunca güncellenecektir
- Her aşama için ayrı not dosyaları (01-xxx, 02-xxx, ...) oluşturulacaktır
- Sorular ve kararlar bu klasörde dokümante edilecektir
