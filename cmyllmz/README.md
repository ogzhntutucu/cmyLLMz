# cmyLLMz

Cem Yılmaz'ın "Yahşi Batı" filminin altyazı verisini kullanarak, mizahı analiz eden, açıklayan ve sorgulatan bir **RAG (Retrieval-Augmented Generation)** tabanlı yapay zeka sistemi.

## Özellikler

- 🎬 Yahşi Batı filminden elle etiketlenmiş 172 sahne chunk'ı
- 🔍 ChromaDB ile vektör tabanlı benzerlik araması
- 🤖 Çift LLM desteği: Local (Ollama/Gemma 3 4B) + Bulut (Gemini API)
- 📊 Mizah analizi: teknik, kültürel bağlam, komedi zamanlaması
- 📈 Metrik ölçümü: hallucination oranı, retrieval precision, cevap kalitesi
- 🌐 Streamlit web arayüzü (streaming destekli)

## Kurulum

```bash
# Sanal ortam oluştur ve aktif et
python -m venv venv
source venv/bin/activate

# Bağımlılıkları kur
pip install -r requirements.txt

# spaCy modelini indir
python -m spacy download xx_ent_wiki_sm

# .env dosyasına Gemini API anahtarını ekle
echo "GEMINI_API_KEY=senin_anahtarin" > .env
```

## Kullanım

```bash
# Streamlit arayüzünü başlat
streamlit run src/app.py
```

## Proje Yapısı

```
cmyllmz/
├── data/
│   ├── raw/              # Orijinal kaynak dosyalar
│   ├── processing/       # Ara işlem dosyaları
│   └── final/            # Son çıktı (RAG'a yüklenecek)
├── src/
│   ├── data_prep/        # Veri hazırlama (SRT parser, enricher, NER, ön işleme)
│   ├── rag/              # RAG pipeline (embedding, ChromaDB, retrieval)
│   ├── llm/              # LLM entegrasyonu (Ollama, Gemini, prompt şablonları)
│   ├── evaluation/       # Metrik ölçümü (hallucination, retrieval, kalite)
│   └── app.py            # Streamlit ana uygulaması
├── chroma_db/            # ChromaDB veritabanı (otomatik oluşur)
├── requirements.txt
└── .env                  # API anahtarları
```

## Teknoloji Stack'i

| Bileşen | Teknoloji |
|---|---|
| Embedding | paraphrase-multilingual-MiniLM-L12-v2 |
| Vektör DB | ChromaDB (cosine similarity) |
| Local LLM | Ollama (Gemma 3 4B) |
| Bulut LLM | Gemini API |
| NLP | NLTK, spaCy, Zeyrek |
| Arayüz | Streamlit |
