# 🎬 Film İzleme Rehberi — Yahşi Batı

> Enricher tamamlandı ve LLM her chunk için karakter + sahne tahmini yaptı.  
> Şimdi sıra sende: Filmi izlerken `enriched_chunks.json` dosyasını kontrol edeceksin.

## Ne Zaman İzleyeceksin?

**Şimdi.** Bu, aşama 2'nin son adımı. Sen filmi izleyip kontrol ettikten sonra `final_data.json` oluşturulacak ve vektör veritabanına geçeceğiz.

---

## Nasıl İzleyeceksin?

İki ekran yan yana açacaksın:
- **Sol:** Filmi oynat (04:10 → sonuna kadar asıl hikaye)
- **Sağ:** `enriched_chunks.json` dosyası VS Code'da açık

Her sahne geçerken ilgili chunk'ı bulup kontrol et.

---

## Nelere Dikkat Edeceksin?

### 1. Karakter Hataları (EN ÖNEMLİSİ)
LLM **96 chunk'ta** karakter yazamadı — `"characters": []` boş bıraktı.  
Bunlar genellikle:
- Tek kelimelik replikler ("Haydı!", "Dur!")
- İki kişi konuşurken hangisinin söylediği belirsiz
- Sesleme sahneleri

**Yapılacak:**
- O chunk'taki metni izlerken kimin söylediğini tespit et
- `characters` alanına yaz

### 2. Karakter Tahmin Hataları
LLM bazen yanlış karakter yazabilir. Örneğin:
- "Şerif Murphy" → aslında "Şerif Lloyd"
- "Betty" → aslında "Suzan Van Dyke"

**Dikkat:** LLM filmdeki bazı yan karakterleri bilmiyor veya karıştırıyor.

### 3. Chunk Sınırı Hataları
Bazı durumlarda iki farklı sahne aynı chunk'a girmiş olabilir (3 saniye gap kuralı mükemmel değil).

**Örnek hatalı durum:**
```
Bir sahne bitiyor... [4 saniye sessizlik içi sahne geçişi] ...yeni sahne başlıyor
```
Eğer bunlar aynı chunk'taysa not et.

---

## Nasıl Not Alacaksın?

Hataları aşağıdaki basit formatta bir `.txt` veya mesaj olarak bana ilet:

```
yb_010 | characters: Aziz Vefa, Lemi Galip
yb_025 | characters: Lemi Galip | scene: Lemi haydutlardan kaçıyor
yb_052 | HATALI CHUNK SINIRI — sahne geçişi yanlış birleştirilmiş
```

Sonra ben `enriched_chunks.json` dosyasını toplu olarak düzeltirim.

---

## Chunk Listesi — Hangileri Boş?

LLM'in karakter yazamadığı 96 chunk bunlar (öncelikli bak):

```
yb_005  yb_008  yb_010  yb_011  yb_012  yb_013  yb_014  yb_015
yb_016  yb_017  yb_018  yb_019  yb_020  yb_021  yb_022  yb_023
yb_024  yb_026  yb_027  yb_028  yb_029  yb_030  yb_031  yb_033
yb_034  yb_035  yb_036  yb_037  yb_038  yb_039  yb_041  yb_042
yb_044  yb_047  yb_048  yb_049  yb_050  yb_052  yb_053  yb_054
yb_057  yb_059  yb_060  yb_062  yb_063  yb_064  yb_065  yb_066
yb_067  yb_071  yb_072  yb_073  yb_074  yb_078  yb_085  yb_086
yb_088  yb_091  yb_092  yb_094  yb_096  yb_097  yb_098  yb_100
yb_101  yb_103  yb_104  yb_108  yb_113  yb_114  yb_116  yb_118
yb_119  yb_121  yb_131  yb_132  yb_133  yb_139  yb_146  yb_148
yb_151  yb_153  yb_155  yb_160  yb_161  yb_162  yb_172  yb_173
yb_176  yb_177
```

> Hepsini doldurmak zorunda değilsin. Zamanın yoksa önce büyük önemli chunk'lara bak.

---

## Tamamlayınca

Düzeltmelerini bana iletince:
1. `final_data.json` oluşturuyoruz
2. ChromaDB vektör veritabanına yüklüyoruz
3. İlk RAG sorgusunu test ediyoruz 🚀


---

# Hatalar

Karakterler
- zeki, vedat