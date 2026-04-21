# Karakterler (eski)

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

# film hakkinda notlar

- Greenland Vadisi - 27 Nisan 1881
- serif lloyd koylu ali sen agizina benzer bir agizla konusuyor.
- zeki ve ramazan pek tanismiyor gibi yapiyorlar. aslinda birlikte dolandirmaya calisiyorlar.
- Cannonball Town
- Rose Hills, WC (kizilderililerin koyu)
- Kırkpınar Güreşleri Gösteri Alanı 18 Haziran 1881.
- Beyaz Saray, Washington (Kolombiya Bölgesi)

# plana gore opsiyonel kisimlar

- bulut llm gemini yerine baska llm apisi de olabilir. o mecburi degil.
- local llm'i de deneyerek uygun olani bulup karar verecegiz. ollama veya orada yazanlardan baska biri olmasi mecburi degil.
- chunklari okuyup duzenleme yapacak olan llm modelini iyi secelim. cok hafif bir modelle calisip da kalitesiz cikti almayalim. bi kere yapacagiz zaten, duzgun bi modelle calisalim. bunu claude yapabilirse zaten guzel olabilir ama onu da cok para etmeyecek sekilde secmek lazim.


# TO DO

- biz bu proje icin yahsi bati filmini ve gerek olursa internetten elde edecegimiz bilgileri kullanacagiz. yani hocalara sunulacak olan kisim sadece yahsi batiyi kapsiyor. ama aslinda proje kapsami yahsi bati ile sinirli degil aslinda. bu proje llm'in cem yilmaz'la baglantili mizahi anlayabilmesi icin planlaniyor, o yuzden adi cmyllmz. yani cem yilmazin baska filmleri, gosterileri, karikaturleri, konuk oldugu programlarda yaptigi sakalari vs. cem yilmaz kulliyatini icerecek zamanla. bu sayede cem yilmaz'in mizahini bilen bir rag sistemi olacak. her turlu llm ile calisabilir hale gelecek.
- rag anything ile belki filmin gorsellerini, sesini de rag'a dahil edebiliriz sonra?
- derslerin sunumu icin bizden arayuz tasarlamamiz isteniyor, o sebeple streamlit kullanip arayuz tasarlayacagiz. yoksa bu projeyi (rag sistemini) kullanmak icin bir arayuze gerek yoktur diye tahmin ediyorum. local llm icin de bulut llm icin de bu rag sistemini kullanmanin best practice'i her ne ise, proje sunumlarini yaptiktan sonra ona gecebiliriz.
- bu proje llm'lerin mizahi dogru yorumlayabilmesini, saka yapabilmesini, sakalari anlayabilmesini, sakalarin devamini getirebilmesini vs. saglamak amaciyla yapiliyor. bu yuzden eger cem yilmaz ozelinde bunu basarabilirsek, baska komedyenler, mizah kisilikleri icin de boyle rag sistemleri kurulabilir, bu rag sistemleri birlestirilerek llm'lerin global sekilde mizahi anlayabilmesi saglanabilir.


Dikkat Edilmesi Gerekenler

- Chunk boyutu stratejisi belirsiz. Sahne bazlı bölüyorsun ama bir sahne 30 saniye de olabilir 5 dakika da. Retrieval kalitesi için chunk'ların çok uzun olmaması önemli — genel kural 200-500 token civarı. Uzun sahneleri bölmeyi düşün.
- NLP ön işleme ile embedding çakışması var. Stop-word çıkarımı ve stemming yapıp sonra neural embedding kullanmak biraz çelişkili. Sentence-transformers zaten kendi içinde bu işi yapıyor, ham metinden daha iyi sonuç veriyor. NLP ön işlemeyi ders gereksinimi için yapıyorsun, ama RAG pipeline'ında embedding'e ham (ya da sadece normalize edilmiş) metin ver.
- Retrieval'ı test etme mekanizman zayıf kalabilir. 20-30 test sorusu iyi bir başlangıç, ama hangi chunk'ın gelmesi gerektiğini de önceden işaretlersen (ground truth retrieval) metrikler çok daha anlamlı olur.



karakterler hakkinda aciklama girilmeli. ekstra olarak biliniyorsa oyuncularin adlari da verilmeli. yani film icin bir wiki olusturmak lazim rag icinde.

ai duzelttirme islerini adim adim ayri ayri yapalim. her seyi tekte yapmasin?


-AZ- oncesi [bla bla] -AZ- devam
seklinde repligi de bolebilirsin. sonuc olarak ses ve goruntuyu replige aktariyoruz. boyle bi kisinin replikleri arasinda da bolunmeler olur.

replik icindeki alintilari nasil yapalim? " mi yoksa ' mi yoksa '' mi kullanalim?

.... oldugu icin ... oldu. simdi bu yuzden .... diyecek/ olacak. seklinde ileri ve gerideki repliklere referans verilebilir.

az ama cok dolu chunk mi daha kotu yoksa cok ama ici daha az chunk mi? ona gore kucultelim chunklari ve cogaltalim.