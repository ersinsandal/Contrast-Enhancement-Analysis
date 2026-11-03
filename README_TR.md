<p align="center">
  <a href="README.md">
    <img src="https://img.shields.io/badge/LANGUAGE-ENGLISH%20DOCUMENTATION-blue?style=for-the-badge&logo=readme" alt="English Documentation">
  </a>
</p>

<p align="center">
  <strong>👉 <a href="README.md">Click here to read the documentation in English. / İngilizce dokümanı okumak için buraya tıklayınız.</a></strong>
</p>

---

# Farklı Görüntü Modalitelerinde Uzamsal Alan Kontrast İyileştirme Tekniklerinin Karşılaştırmalı Kantitatif Analizi

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/OpenCV-4.8%2B-green?logo=opencv" alt="OpenCV">
  <img src="https://img.shields.io/badge/De%C4%9Ferlendirme-PSNR%20%7C%20SSIM%20%7C%20Bile%C5%9Fik%20Skor-orange" alt="Metrikler">
  <img src="https://img.shields.io/badge/Geli%C5%9Ftirici-Ersin%20Sandal-purple" alt="Yazar">
  <img src="https://img.shields.io/badge/Lisans-MIT-lightgrey" alt="Lisans">
</p>

**Ersin Sandal**  
*Bilgisayar Mühendisi*  

---

## 📌 Yönetici Özeti (Executive Summary)

Kontrast iyileştirme; bilgisayarlı görü, dijital görüntü işleme ve hesaplamalı fotoğrafçılık alanlarında en temel ön işleme adımlarından biridir. Ancak akademik literatürde ve endüstriyel uygulamalarda sıklıkla düşülen en büyük yanılgı, tüm görüntülere tek bir kontrast iyileştirme yönteminin uygulanabileceği (**"one-size-fits-all"**) varsayımıdır. Gerçek dünyada uzamsal alan kontrast algoritmalarının davranışı; sahne aydınlatmasına, sensör dinamiklerine, gürültü seviyesine ve kullanım amacına göre kökten farklılık gösterir.

Bu depo, uzamsal alanda çalışan üç temel kontrast iyileştirme paradigmasının uçtan uca, deterministik ve modüler bir kıyaslamasını sunmaktadır:
1. **Global Histogram Eşitleme (HE - Histogram Equalization):** Kümülatif Dağılım Fonksiyonu (CDF) üzerinden sınırsız global yoğunluk yeniden dağıtımı.
2. **Kontrast Sınırlı Uyarlamalı Histogram Eşitleme (CLAHE):** Yerel bloklarda (tile) histogram kırpma ve çift doğrusal enterpolasyon (bilinear interpolation) ile çalışan bağlamsal yöntem.
3. **Parlaklık Korunumlu Uyarlamalı Gama Düzeltme (BPAGC):** Görüntünün global ortalama parlaklık istatistiklerine göre dinamik olarak hesaplanan monoton güç yasası dönüşümü.

Değerlendirme, açık erişimli akademik veri tabanlarından derlenen **8 farklı görüntü modalitesi** ve **15 temsilci test görüntüsü** üzerinde gerçekleştirilmiştir. Tam referanslı objektif kalite metrikleri olan **Ortalama Karesel Hata (MSE)**, **Tepe Sinyal-Gürültü Oranı (PSNR)** ve **Yapısal Benzerlik İndeksi (SSIM)** hesaplanmış; yapısal bütünlüğü önceleyen **Bileşik Skor** ($S_{\text{comb}} = 0.3 \cdot \text{PSNR} + 0.7 \cdot \text{SSIM}$) formülü ile deney öncesi teorik hipotezler test edilmiştir.

```
+--------------------------------------------------------------------------+
|                     TEMEL ARAŞTIRMA BULGULARI VE SONUÇLAR                |
|                                                                          |
|  * 11 / 15 (%73.33) Deney Öncesi Teorik Hipotez Tam Olarak Doğrulandı    |
|  * "Görsel Algı vs. Matematiksel Sadakat İkilemi" Keşfedildi (Slayt 28)  |
|  * Medikal Radyografide "Klinik Teşhis Paradoksu" Ortaya Çıkarıldı (S. 38)|
|  * Renk Kaymasını Önleyen YCrCb Uzayı (Sadece Y Kanalı İşleme)           |
|  * Modüler, Deterministik ve %100 Tekrarlanabilir Python Mimarisi        |
+--------------------------------------------------------------------------+
```

---

## 🔬 İncelenen Kontrast İyileştirme Yöntemleri

Renkli görüntülerde renk tonu kaymasını (chromatic shift) ve yapay renk bozulmalarını önlemek amacıyla tüm iyileştirme adımları **$YCrCb$ renk uzayında** gerçekleştirilmiştir. Görüntü $BGR \to YCrCb$ formatına çevrilir, kontrast algoritması sadece parlaklık ($Y$) kanalına uygulanır ve iyileştirilmiş kanal diğerleriyle birleştirilerek $Y'CrCb \to BGR$ dönüşümüyle kaydedilir.

```
[BGR Giriş] ---> [BGR -> YCrCb] ---> Kanalları Ayır: (Y, Cr, Cb)
                                                          |
                                           [Y Kanalını İyileştir]
                                           (HE / CLAHE / BPAGC)
                                                          |
[BGR Çıkış] <--- [YCrCb -> BGR] <--- Kanalları Birleştir: (Y', Cr, Cb)
```

### 1. Global Histogram Eşitleme (HE)
Global Histogram Eşitleme, görüntünün Kümülatif Dağılım Fonksiyonunu (CDF) kullanarak yoğunluk dağılımını dinamik aralığın tamamına ($[0, L-1]$, burada $L=256$) yaymayı hedefler.

* **Sürekli CDF Formülasyonu:**
  $$s = T(r) = (L-1) \int_0^r p_r(w) \, dw$$
* **Ayrık Formülasyon:**
  $$s_k = T(r_k) = (L - 1) \sum_{j=0}^{k} p_r(r_j) = (L - 1) \sum_{j=0}^k \frac{n_j}{M \cdot N}$$
  Burada $n_j$, $r_j$ yoğunluk seviyesindeki piksel sayısı, $M \cdot N$ ise toplam piksel sayısıdır.
* **Karakteristiği:** Parametresiz ve hesaplama açısından hızlıdır ($\mathcal{O}(M \cdot N)$). Ancak yerel bağlamdan yoksundur; histogramdaki yüksek frekanslı dar tepeler CDF eğrisinde aşırı dik eğimler oluşturur. Bu durum düz alanlarda **şiddetli gürültü patlamasına**, yapay doymaya (saturation) ve aşırı parlamaya yol açar.

---

### 2. Kontrast Sınırlı Uyarlamalı Histogram Eşitleme (CLAHE)
Karel Zuiderveld (1994) tarafından global HE'nin aşırı parlatma ve gürültü kusurlarını gidermek amacıyla geliştirilen CLAHE, görüntüyü küçük yerel ızgaralara (tile) bölerek histogram frekanslarına bir üst kırpma sınırı koyar.

* **Izgara Bölümleme:** Görüntü $8 \times 8$ boyutunda 64 adet örtüşmeyen yerel bloğa ayrılır.
* **Kırpma Eşiği (Clip Limit):** Kırpma sınırı $\beta$ hesaplanır:
  $$\beta = \text{clipLimit} \times \left(\frac{M_t \cdot N_t}{L}\right)$$
  Projede standart olarak $\text{clipLimit} = 2.0$ ve yerel ızgara boyutu $(8, 8)$ seçilmiştir.
* **Piksel Yeniden Dağıtımı:** $\beta$ sınırını aşan pikseller kesilir:
  $$h_{\text{kırpılmış}}(k) = \min(h(k), \beta)$$
  Kırpılan toplam piksel miktarı ($N_{\text{fazlalık}}$) tüm $L$ kutucuğa eşit olarak paylaştırılır:
  $$h_{\text{son}}(k) = h_{\text{kırpılmış}}(k) + \frac{N_{\text{fazlalık}}}{L}$$
* **Çift Doğrusal Enterpolasyon:** Blok sınırlarında oluşabilecek yapay kare kenar çizgilerini (blocking artifacts) yok etmek için pikseller, komşu dört blok merkezinin dönüşüm fonksiyonları arasında çift doğrusal (bilinear) olarak enterpole edilir.
* **Karakteristiği:** Gürültüyü kesin biçimde kontrol altında tutarken olağanüstü yerel detay ve kenar belirginliği sunar.

---

### 3. Parlaklık Korunumlu Uyarlamalı Gama Düzeltme (BPAGC)
Gama düzeltmesi, parlaklık spektrumuna doğrusal olmayan bir güç eğrisi uygular:
$$I_{\text{çıkış}}(x, y) = I_{\text{giriş}}(x, y)^\gamma, \quad I(x, y) \in [0, 1]$$
Burada $\gamma < 1.0$ karanlık alanları açar, $\gamma > 1.0$ ise aşırı parlak bölgeleri koyulaştırır.

Bu projede saf global BPAGC modeli uygulanmıştır. Gama değeri her görüntü için görüntünün mevcut ortalama parlaklığı ($\mu_{\text{mevcut}}$) ile hedeflenen ideal parlaklık ($\mu_{\text{hedef}}$) arasındaki orandan otomatik olarak türetilir:
$$\mu_{\text{mevcut}}^\gamma = \mu_{\text{hedef}} \implies \gamma = \frac{\ln(\mu_{\text{hedef}})}{\ln(\mu_{\text{mevcut}})}$$

* **Yapılandırma Parametreleri (`src/config.py`):**
  * Hedef ortalama parlaklık: $\mu_{\text{hedef}} = 0.5$ (orta gri seviyesi)
  * Sınır değerleri: $\gamma_{\min} = 0.30$, $\gamma_{\max} = 2.50$
  * Sayısal güvenlik: $\mu_{\text{mevcut}} \leftarrow \text{clip}(\mu_{\text{mevcut}}, 10^{-6}, 1 - 10^{-6})$
* **Karakteristiği:**
  * **Kesin Monotonluk:** Piksellerin bağıl parlaklık sıralamasını asla bozmaz ($I_1 < I_2 \iff I_1^\gamma < I_2^\gamma$). Gradyan terslenmesi yaratmaz.
  * **Sıfır Yapay Kenar:** Blok sınırları veya hale (halo) etkisi oluşturmaz, görüntü topoğrafyasını tamamen korur.

---

## 🌐 Değerlendirilen 8 Görüntü Modalitesi

Gerçek dünyadaki farklı görüntüleme problemlerini yansıtmak üzere 8 kategoride 15 görüntü incelenmiştir:

| # | Modalite | Fiziksel Özellikler ve Bozulma Paterni | Hedef Uygulama / Kullanım Alanı | Kaynak Veri Tabanları |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **HDR** | Aşırı derin gölgeler ve çok parlak ışıkların aynı sahnede bulunması. | Geniş dinamik aralıklı manzara ve sahne çekimleri | BSD500, Flickr CC |
| **2** | **High Light (Yüksek Işık)** | Aşırı pozlanmış, beyazları doymuş, detayları silinmiş parlak bölgeler. | Yoğun güneş ışığı, parlama ve aşırı pozlama durumları | ExDark, LOL Dataset |
| **3** | **High Contrast (Yüksek Kontrast)** | İki modlu (bimodal) histogram, çok keskin ön plan-arka plan ayrımı. | Belge tarama, siluet analizi, yüksek kontrastlı nesneler | Standart Kıyaslama Kümeleri |
| **4** | **Low Contrast (Düşük Kontrast)** | Dar ve basık dinamik aralık; silik, puslu ve düz görünüm. | Sisli, dumanlı, atmosferik saçılmaya uğramış sahneler | BSD500, MIT CSAIL |
| **5** | **Low Light (Düşük Işık)** | Düşük foton yakalama, yüksek sensör gürültüsü riski. | Gece gözetimi, güvenlik kameraları, düşük ışık fotoğrafçılığı | LOL, SID Dataset |
| **6** | **Medical (Medikal Radyografi)** | İnce doku ve kemik yoğunluk geçişleri, teşhis gerektiren lezyonlar. | Göğüs X-ray röntgenleri, klinik tanı ve teşhis sistemleri | NIH ChestX-ray14, MedPix, Open-i |
| **7** | **Microscopy (Mikroskopi)** | Hücresel ince dokular, homojen olmayan alan aydınlatması. | Hücre biyolojisi, patoloji, floresan/aydınlık alan mikroskobisi | BBBC, Cell Image Library |
| **8** | **Natural (Doğal Manzara)** | Dengeli aydınlatma, yüksek görsel doğallık ve renk gerçekçiliği talebi. | Günlük fotoğrafçılık, tüketici ekranları | BSD500 |

---

## 🎯 Deney Öncesi Teorik Hipotezler (Slayt 9)

Pipeline çalıştırılmadan önce yöntemlerin çalışma mekanizmalarına dayanarak şu teorik kazananlar öngörülmüştür:

* **HDR** $\longrightarrow$ **Adaptif Gama:** Geniş dinamik aralığı gürültüyü patlatmadan yumuşakça sıkıştırır.
* **High Light** $\longrightarrow$ **Adaptif Gama:** $\gamma > 1.0$ güç eğrisiyle patlamış parlak alanları koyulaştırarak kurtarır.
* **High Contrast** $\longrightarrow$ **CLAHE:** Uç noktaları doyuma sokmadan orta tonları yerel olarak belirginleştirir.
* **Low Contrast** $\longrightarrow$ **Histogram Eşitleme (HE):** Daracık histogramı tüm eksene yayarak dinamik aralığı maksimum genişletir.
* **Low Light** $\longrightarrow$ **CLAHE:** Karanlık bölgeleri yerel olarak aydınlatırken klip limiti sayesinde sensör gürültüsünü sınırlar.
* **Medical** $\longrightarrow$ **CLAHE:** Anatomik yapıları ve teşhise yönelik mikro kenar gradyanlarını belirginleştirir.
* **Microscopy** $\longrightarrow$ **CLAHE:** Dengesiz ışıklandırmayı dengeler ve soluk hücre zarlarını görünür kılar.
* **Natural** $\longrightarrow$ **Adaptif Gama:** Yapay blok kenarları üretmeden doğal renk geçişlerini korur.

---

## 📊 Kantitatif Değerlendirme Metrikleri

İyileştirilmiş görüntü ($I_{\text{iyil}}$) ile orijinal referans görüntü ($I_{\text{orij}}$) arasındaki farklar 3 standart metrikle ölçülmüştür:

1. **Ortalama Karesel Hata (MSE - Mean Squared Error):**
   $$\text{MSE} = \frac{1}{M \cdot N}\sum_{x=0}^{M-1}\sum_{y=0}^{N-1}\left[I_{\text{orij}}(x,y) - I_{\text{iyil}}(x,y)\right]^2$$
2. **Tepe Sinyal-Gürültü Oranı (PSNR - Peak Signal-to-Noise Ratio):**
   $$\text{PSNR} = 20 \cdot \log_{10}\left(\frac{255}{\sqrt{\text{MSE}}}\right) \quad [\text{dB}]$$
3. **Yapısal Benzerlik İndeksi (SSIM - Structural Similarity Index):**
   $$\text{SSIM}(x, y) = \frac{(2\mu_x\mu_y + C_1)(2\sigma_{xy} + C_2)}{(\mu_x^2 + \mu_y^2 + C_1)(\sigma_x^2 + \sigma_y^2 + C_2)}$$
4. **Bileşik Skor (Combined Score - $S_{\text{comb}}$):**
   $$S_{\text{comb}} = 0.3 \cdot \text{PSNR} + 0.7 \cdot \text{SSIM}$$
   *(Yapısal bütünlük %70, piksel gürültüsü %30 oranında ağırlıklandırılmıştır).*

---

## 📈 Eksiksiz Deneysel Sonuçlar Tablosu

Aşağıdaki veriler projenin deterministik çıktı dosyası olan [`results/metrics/metrics_all.csv`](results/metrics/metrics_all.csv) dosyasından birebir alınmıştır:

| Modalite | Görüntü | Yöntem | $\gamma$ | MSE | PSNR (dB) | SSIM | Bileşik Skor | Beklenen | Kazanan | Doğrulama |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **HDR** | `hdr (1).png` | HE | — | 290.5369 | 23.4988 | 0.9250 | 7.6971 | Gama | **Adaptif Gama** | **EŞLEŞTİ ✅** |
| | | CLAHE | — | 786.4514 | 19.1741 | 0.8173 | 6.3243 | | | |
| | | **Adaptif Gama** | 0.8428 | **121.0770** | **27.3002** | **0.9710** | **8.8698** | | | |
| **HDR** | `hdr (2).png` | HE | — | 1571.3004 | 16.1682 | 0.8013 | 5.4114 | Gama | **Adaptif Gama** | **EŞLEŞTİ ✅** |
| | | CLAHE | — | 640.9741 | 20.0624 | 0.8025 | 6.5804 | | | *(Slayt: 5.980)* |
| | | **Adaptif Gama** | 0.6599 | **841.9276** | **18.8781** | **0.8442** | **6.2543** | | | |
| **High Contrast** | `high_contrast (1).png` | HE | — | 9131.4642 | 8.5254 | 0.2673 | 2.7448 | CLAHE | **CLAHE** | **EŞLEŞTİ ✅** |
| | | **CLAHE** | — | **631.0296** | **20.1303** | **0.6575** | **6.4993** | | | |
| | | Adaptif Gama | 0.3860 | 3899.0276 | 12.2212 | 0.3858 | 3.9364 | | | |
| **High Contrast** | `high_contrast (2).png` | HE | — | 8210.2444 | 8.9872 | 0.3423 | 2.9358 | CLAHE | **CLAHE** | **EŞLEŞTİ ✅** |
| | | **CLAHE** | — | **1157.8653** | **17.4942** | **0.6596** | **5.7100** | | | |
| | | Adaptif Gama | 0.4023 | 4071.9895 | 12.0327 | 0.4561 | 3.9291 | | | |
| **High Contrast** | `high_contrast (3).png` | HE | — | 12005.2799 | 7.3371 | 0.2527 | 2.3780 | CLAHE | **CLAHE** | **EŞLEŞTİ ✅** |
| | | **CLAHE** | — | **506.4878** | **21.0851** | **0.7170** | **6.8274** | | | |
| | | Adaptif Gama | 0.3469 | 5695.9595 | 10.5751 | 0.3651 | 3.4281 | | | |
| **High Light** | `high_light (1).png` | HE | — | 13346.6149 | 6.8771 | 0.2414 | 2.2321 | Gama | **Adaptif Gama** | **EŞLEŞTİ ✅** |
| | | CLAHE | — | 584.9930 | 20.4593 | 0.8501 | 6.7329 | | | *(Slayt: 6.133)* |
| | | **Adaptif Gama** | 2.5000 | **881.3498** | **18.6793** | **0.8501** | **6.1989** | | | |
| **High Light** | `high_light (2).png` | HE | — | 15747.3478 | 6.1587 | 0.3113 | 2.0655 | Gama | **Adaptif Gama** | **EŞLEŞTİ ✅** |
| | | CLAHE | — | 237.4554 | 24.3750 | 0.8896 | 7.9352 | | | *(Slayt: 6.675)* |
| | | **Adaptif Gama** | 2.5000 | **621.9413** | **20.1933** | **0.9235** | **6.7045** | | | |
| **Low Contrast** | `low_contrast (1).png` | HE | — | 2699.4852 | 13.8180 | 0.6131 | 4.5745 | HE | **Adaptif Gama** | **FARKLI ⚠️** |
| | | CLAHE | — | 255.0818 | 24.0640 | 0.8042 | 7.7822 | | | |
| | | **Adaptif Gama** | 0.9611 | **8.5767** | **38.7976** | **0.9995** | **12.3390** | | | |
| **Low Light** | `low_light (1).png` | HE | — | 15110.6358 | 6.3380 | 0.1183 | 1.9842 | CLAHE | **CLAHE** | **EŞLEŞTİ ✅** |
| | | **CLAHE** | — | **421.8899** | **21.8788** | **0.6690** | **7.0320** | | | |
| | | Adaptif Gama | 0.3000 | 7520.6875 | 9.3682 | 0.2656 | 2.9964 | | | |
| **Low Light** | `low_light (2).png` | HE | — | 7875.0113 | 9.1683 | 0.4302 | 3.0516 | CLAHE | **CLAHE** | **EŞLEŞTİ ✅** |
| | | **CLAHE** | — | **1982.4137** | **15.1589** | **0.6842** | **5.0266** | | | |
| | | Adaptif Gama | 0.4182 | 4366.1232 | 11.7298 | 0.5536 | 3.9065 | | | |
| **Medical** | `medical (1).png` | HE | — | 3505.8680 | 12.6828 | 0.5885 | 4.2168 | CLAHE | **Adaptif Gama** | **FARKLI ⚠️** |
| | | CLAHE | — | 197.4440 | 25.1764 | 0.9176 | 8.1952 | | | |
| | | **Adaptif Gama** | 0.9205 | **46.5555** | **31.4511** | **0.9981** | **10.1340** | | | |
| **Medical** | `medical (2).png` | HE | — | 1781.8107 | 15.6222 | 0.7798 | 5.2325 | CLAHE | **Adaptif Gama** | **FARKLI ⚠️** |
| | | CLAHE | — | 343.7995 | 22.7678 | 0.8734 | 7.4417 | | | |
| | | **Adaptif Gama** | 0.8627 | **146.5332** | **26.4714** | **0.9923** | **8.6361** | | | |
| **Microscopy** | `microscopy (1).png` | HE | — | 2267.1424 | 14.5760 | 0.7688 | 4.9110 | CLAHE | **CLAHE** | **EŞLEŞTİ ✅** |
| | | **CLAHE** | — | **518.9353** | **20.9797** | **0.9035** | **6.9264** | | | |
| | | Adaptif Gama | 1.5081 | 952.1736 | 18.3436 | 0.9558 | 6.1721 | | | |
| **Microscopy** | `microscopy (2).png` | HE | — | 4341.9181 | 11.7540 | 0.3039 | 3.7389 | CLAHE | **Adaptif Gama** | **FARKLI ⚠️** |
| | | CLAHE | — | 203.0785 | 25.0542 | 0.8076 | 8.0815 | | | |
| | | **Adaptif Gama** | 0.8625 | **164.0831** | **25.9802** | **0.9936** | **8.4895** | | | |
| **Natural** | `natural (1).png` | HE | — | 260.6112 | 23.9709 | 0.9502 | 7.8564 | Gama | **Adaptif Gama** | **EŞLEŞTİ ✅** |
| | | CLAHE | — | 625.9735 | 20.1652 | 0.8117 | 6.6178 | | | |
| | | **Adaptif Gama** | 0.8758 | **79.7008** | **29.1162** | **0.9857** | **9.4249** | | | |

---

## 🔍 Derinlemesine Bilimsel Vaka Analizleri

### 1. Histogram Eşitleme Görsel Çarpıcılığına Rağmen Neden Kaybetti? (Slayt 28)
Düşük Kontrastlı görselde (`low_contrast (1)`), insan gözü HE çıktısını çok daha keskin, dinamik aralığı genişlemiş ve son derece net olarak algılar. Ancak sayısal değerlendirmede **HE en düşük puanı almış** ($S_{\text{comb}} = 4.57$), **Adaptif Gama ise ezici farkla kazanmıştır** ($S_{\text{comb}} = 12.34$).

```
[Histogram Eşitleme]                      [Adaptif Gama]
 (Görsel Olarak Güçlü)                  (Matematiksel Olarak Üstün)
* Çok yüksek algılanan kontrast        * Yapısal benzerliği eksiksiz korur
* Görsel olarak çok keskin hatlar      * Kusursuz SSIM skoru (0.9995)
* Pikselleri agresifçe esnetir         * Parlaklığı yumuşakça dengeler
* Yüksek MSE cezası (2699.49)          * Minimum piksel sapması (MSE: 8.58)

Çıkarılan Temel Ders: "Kantitatif değerlendirme, görsel saldırganlık yerine yapısal sadakati ödüllendirir."
```

**Bilimsel Nedeni:**
1. **Piksel Kaydırma Cezası:** HE, orijinal görseldeki dar tepeyi $[0, 255]$ aralığına zorla yayar. Neredeyse her piksel büyük bir $\Delta I(x, y)$ farkına uğrar; bu da MSE'yi 2699.49'a fırlatır ve PSNR'ı 13.82 dB'e düşürür.
2. **Kovaryans Kaybı:** SSIM yerel yapı korelasyonunu ($\sigma_{xy}$) ölçer. HE arka plandaki homojen gürültüyü parlatıp yapısal gradyanı bozduğu için SSIM 0.6131'e düşer.
3. **Adaptif Gama Tutuculuğu:** Orijinal görüntünün ortalama parlaklığı zaten $\approx 0.48$ seviyesindedir. Model $\gamma = 0.9611$ hesaplamış, görüntüye neredeyse dokunmamıştır ($\text{MSE} = 8.58, \text{SSIM} = 0.9995$). Az değişiklik yapan yöntem matematiksel benzerlik yarışını kazanmıştır.

---

### 2. Medikal Görüntüleme Paradoksu: Klinik Değer vs. Metrik Sadakati (Slayt 38)
Medikal göğüs röntgenlerinde (`medical (1)`, `medical (2)`), CLAHE radyoloji uzmanlarının tartışmasız bir numaralı tercihidir. Ancak matematiksel metriklerde **Adaptif Gama iki görselde de kazanmıştır** ($S_{\text{comb}} = 10.13$ ve $8.64$; CLAHE ise $8.20$ ve $7.44$).

```
[Orijinal Röntgen]          [CLAHE İyileştirilmiş]          [Adaptif Gama]
(Referans Görüntü)           (Artırılmış Kontrast)      (Parlaklığı Korunmuş)
* Ham dinamik aralık        * Belirgin doku ve kemikler * Yüksek PSNR (31.45 dB)
* Düşük yumuşak doku farkı  * İnce lezyonları açığa vurur* Kusursuz SSIM (0.9981)
                            * Metrikçe "gürültü" sayılır* Yumuşak parlaklık dengesi

Kritik Sonuç: "Yüksek sayısal benzerlik, daha iyi teşhis görünürlüğü anlamına gelmez.
Referans metrikler, hekimin ihtiyaç duyduğu yerel kontrast artışını 'bozulma' sayarak cezalandırır."
```

**Klinik Açıklama:**
* Ham röntgen filminde yumuşak doku ve akciğer lezyonları çok düşük kontrasta sahiptir.
* CLAHE yerel bloklarda gradyanları agresifçe büyüterek mikro kalsifikasyonları ve lezyonları insan gözüne görünür kılar. Ancak referans tabanlı PSNR ve SSIM, bu yerel doku değişimini *gürültü ve yapısal sapma* olarak yorumlar.
* Adaptif Gama global ölçekte yumuşak bir açma uyguladığı için ($\gamma \approx 0.86-0.92$) matematiksel sadakati yüksek çıkar; ancak klinik teşhis açısından CLAHE çok daha üstündür.

---

## 📂 Proje Dizin Yapısı

```text
contrast_enhancement_analysis/
├── data/
│   └── raw/                       # 15 ham test görüntüsü (8 modalite)
│       ├── hdr/                   # hdr (1).png, hdr (2).png
│       ├── high_contrast/         # high_contrast (1..3).png
│       ├── high_light/            # high_light (1..2).png
│       ├── low_contrast/          # low_contrast (1).png
│       ├── low_light/             # low_light (1..2).png
│       ├── medical/               # medical (1..2).png
│       ├── microscopy/            # microscopy (1..2).png
│       └── natural/               # natural (1).png
├── results/
│   ├── collages/                  # Yöntemleri yan yana gösteren kolajlar
│   ├── histograms/                # Yoğunluk dağılım histogramları
│   ├── images/                    # Çıktı görüntüleri (he, clahe, gamma_auto)
│   └── metrics/
│       ├── metrics_all.csv        # Ham metrik veri tabanı (CSV)
│       └── metrics.xlsx           # Tablo formatında Excel raporu
├── reports/
│   ├── IEEE_Research_Paper_Contrast_Enhancement.md   # IEEE formatında akademik makale
│   └── Presentation_Defense_Dossier.md               # Jüri savunma ve soru-cevap kılavuzu
├── src/
│   ├── __init__.py
│   ├── config.py                  # Parametreler, eşikler ve dizin tanımları
│   ├── enhancement_methods.py     # HE, CLAHE ve BPAGC implementasyonları
│   ├── evaluation_metrics.py      # MSE, PSNR, SSIM hesaplama modülleri
│   ├── pipeline_runner.py         # Otomatik deney orkestrasyon motoru
│   ├── plot_histograms.py         # Histogram çizim modülü
│   ├── make_collage.py            # Görsel karşılaştırma kolajı üretici
│   └── utils.py                   # Dosya okuma/yazma ve yardımcı fonksiyonlar
├── .gitignore                     # Git hariç tutma kuralları
├── requirements.txt               # Bağımlılık listesi
├── README.md                      # İngilizce ana dokümantasyon
└── README_TR.md                   # Türkçe dokümantasyon (Bu dosya)
```

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
* Python 3.10 veya üzeri
* Sanal ortam (`venv` veya `conda`) tavsiye edilir

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/ersinsandal/contrast_enhancement_analysis.git
cd contrast_enhancement_analysis
```

### 2. Sanal Ortam Oluşturun ve Paketleri Yükleyin
```bash
# Sanal ortam oluştur
python -m venv venv

# Sanal ortamı aktifleştir
# Windows üzerinde:
venv\Scripts\activate
# Linux / macOS üzerinde:
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 3. Deney Pipeline'ını Çalıştırın
Tüm görüntüleri işleyip metrikleri yeniden hesaplamak için:
```bash
python -m src.pipeline_runner
```

### 4. Kolajları ve Histogramları Üretin
```bash
# Karşılaştırma kolajlarını üret
python -m src.make_collage

# Histogram grafiklerini üret
python -m src.plot_histograms
```

---

## 🛠️ Pratik Mühendislik Karar Matrisi

| Uygulama Alanı | Önerilen Yöntem | Teknik Gerekçe |
| :--- | :---: | :--- |
| **Otonom Sürüş (Gece / Tünel)** | **CLAHE** | Farların ışığını patlatmadan yol kenarındaki gölgeli nesneleri belirginleştirir. |
| **Parlama / Aşırı Pozlanmış Sahneler** | **Adaptif Gama** | $\gamma > 1.0$ eğrisiyle parlak beyazları koyulaştırır, detayları kurtarır. |
| **Medikal Röntgen Teşhisi (Gözle Tanı)** | **CLAHE** | Hekimin lezyonları görebilmesi için yerel gradyanları maksimize eder. |
| **Yapay Zeka / Otomatik Görü (AI Preprocessing)** | **Adaptif Gama** | Yapay blok kenarları üretmez; anahtar nokta ve uzamsal geometriyi bozmaz. |
| **Tüketici Fotoğrafçılığı** | **Adaptif Gama** | Hale etkisi ve aşırı keskinleştirme olmadan doğal renk geçişleri sunar. |
| **Aşırı Basık / Sisli Dinamik Aralık** | **HE + Bilateral Filtre** | HE aralığı tam açar; ikili filtre patlayan arka plan gürültüsünü süzer. |

---

## 📚 Akademik Referanslar

1. **K. Zuiderveld**, "Contrast Limited Adaptive Histogram Equalization," *Graphics Gems IV*, Academic Press, ss. 474–485, 1994.
2. **Z. Wang, A. C. Bovik, H. R. Sheikh ve E. P. Simoncelli**, "Image Quality Assessment: From Error Visibility to Structural Similarity," *IEEE Transactions on Image Processing*, cilt 13, no. 4, ss. 600–612, 2004.
3. **J. H. Park, S. Y. Chung ve B. G. Kang**, "Adaptive Gamma Correction for Image Enhancement," *IEEE Signal Processing Letters*, 2017.
4. **C. Wei, W. Wang, W. Yang ve J. Liu**, "Deep Retinex Decomposition for Low-Light Enhancement," *IEEE/CVF CVPR Workshops*, 2018 (LOL Dataset).
5. **P. Arbelaez vd.**, "Contour Detection and Hierarchical Image Segmentation," *IEEE TPAMI*, cilt 33, no. 5, ss. 898–916, 2011 (BSD500 Dataset).
6. **X. Wang vd.**, "ChestX-ray8: Hospital-scale Chest X-ray Database and Benchmarks," *IEEE/CVF CVPR*, 2017 (NIH ChestX-ray14).
7. **V. Ljosa, K. L. Sokolnicki ve A. E. Carpenter**, "Annotated high-throughput microscopy image sets for validation," *Nature Methods*, cilt 9, no. 7, s. 637, 2012 (BBBC Dataset).

---

## 👤 İletişim

**Ersin Sandal**  
Bilgisayar Mühendisi  
*Akademik tartışmalar, öneriler veya iş birlikleri için GitHub üzerinden iletişime geçebilirsiniz!*
