# plana gore opsiyonel kisimlar

- bulut llm gemini yerine baska llm apisi de olabilir. o mecburi degil.
- local llm'i de deneyerek uygun olani bulup karar verecegiz. ollama veya orada yazanlardan baska biri olmasi mecburi degil.
- chunklari okuyup duzenleme yapacak olan llm modelini iyi secelim. cok hafif bir modelle calisip da kalitesiz cikti almayalim. bi kere yapacagiz zaten, duzgun bi modelle calisalim. bunu claude yapabilirse zaten guzel olabilir ama onu da cok para etmeyecek sekilde secmek lazim.


# TO DO

- biz bu proje icin yahsi bati filmini ve gerek olursa internetten elde edecegimiz bilgileri kullanacagiz. yani hocalara sunulacak olan kisim sadece yahsi batiyi kapsiyor. ama aslinda proje kapsami yahsi bati ile sinirli degil aslinda. bu proje llm'in cem yilmaz'la baglantili mizahi anlayabilmesi icin planlaniyor, o yuzden adi cmyllmz. yani cem yilmazin baska filmleri, gosterileri, karikaturleri, konuk oldugu programlarda yaptigi sakalari vs. cem yilmaz kulliyatini icerecek zamanla. bu sayede cem yilmaz'in mizahini bilen bir rag sistemi olacak. her turlu llm ile calisabilir hale gelecek.
- rag anything ile belki filmin gorsellerini, sesini de rag'a dahil edebiliriz sonra?
- derslerin sunumu icin bizden arayuz tasarlamamiz isteniyor, o sebeple streamlit kullanip arayuz tasarlayacagiz. yoksa bu projeyi (rag sistemini) kullanmak icin bir arayuze gerek yoktur diye tahmin ediyorum. local llm icin de bulut llm icin de bu rag sistemini kullanmanin best practice'i her ne ise, proje sunumlarini yaptiktan sonra ona gecebiliriz.
- bu proje llm'lerin mizahi dogru yorumlayabilmesini, saka yapabilmesini, sakalari anlayabilmesini, sakalarin devamini getirebilmesini vs. saglamak amaciyla yapiliyor. bu yuzden eger cem yilmaz ozelinde bunu basarabilirsek, baska komedyenler, mizah kisilikleri icin de boyle rag sistemleri kurulabilir, bu rag sistemleri birlestirilerek llm'lerin global sekilde mizahi anlayabilmesi saglanabilir.

# ne yapiyoruz

bir yapay zeka ile oturup bir film izledigini dusun.
bizim gordugumuzu gorecek
duydugumuzu duyacak
anladigimizi anlayacak olsa ve 
tum bunlari bizim gibi ayni anda yapacak olsa, bu su an icin mumkun degilm, ama mumkun olsaydi nasil olurdu?

hem kor hem duymayan birine nasil anlatirsin? ya da bu kulturde yetismemis baska dilde konusan bir yabanciya nasil anlatirsin? ben filmi yapay zekaya iste bu sekilde anlatarak veri olarak sagladim. bu veriyle de rag sistemi kurdum.

# verilerimiz hakkinda bilgiler

- replik ici alintilarda " kullandik.
- -XX- seklinde karakterleri kodladik.
- [] bloklariyla notlar aldik.
- filmdeki guldurucu etkisi olan her seyi "komik" kelimesi ile isaretledik.
- gondermeleri "gonderme kelimesi ile isaretledik. 
- notlarda AZ VE LE karakteri bazen "ikili" kelimesini kullanarak kisalttik. 

# anlamadigim sakalar:

0497
528,529,530
1215
1607

# yapacagimiz arayuzdeki agent nasil konussun:

bilmedigi sey olursa izledim ama onu hatirlamiyorum, tekrar izlesem hatirlarim falan desin.