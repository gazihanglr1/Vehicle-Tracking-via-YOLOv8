<div align="center">

# 🚦 RoadSight Pro

### Advanced Real-Time Vehicle Detection, Classification, Tracking & Counting

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![YOLO](https://img.shields.io/badge/Model-YOLO11-00FFFF.svg)](https://docs.ultralytics.com/models/yolo11/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Cross--Platform-lightgrey.svg)](#)

<br>

<img src="assets/sample_tracking.png" alt="Sample Tracking Output" width="720"/>

*<sub>PLACEHOLDER — çalıştırdıktan sonra örnek çıktı ekran görüntüsü buraya gelecek</sub>*

</div>

---

## 📖 Overview

**RoadSight Pro**, video akışlarında araçları tespit eden, sınıflandıran, kareler arasında takip eden ve sınıf bazlı benzersiz sayım yapan production-kalitesinde bir komut satırı aracıdır. Temel özelliği: aynı takip ID'sinin YOLO tarafından farklı karelerde farklı sınıflandırılması (flickering) durumunda sayımı otomatik düzeltmesidir.

**Temel yetenekler:**
- 🎯 Sınıf bazlı confidence eşikleri (motosiklet gibi zor sınıflar için ayrı ayarlanabilir eşik)
- 🔄 ByteTrack tabanlı kimlik takibi + **sınıf değişimi düzeltme mantığı**
- 🧮 Sınıf bazlı benzersiz araç sayımı (çift sayım önlenir)
- 💾 Bellek-güvenli iz (trail) geçmişi — uzun videolarda RAM şişmesi yok
- 🖥️ Headless mod desteği (Colab, sunucu, Docker uyumlu)
- 📤 JSON/CSV formatında sonuç export
- 🛠️ Tamamen CLI ile yapılandırılabilir (argparse)
- 🪵 Yapılandırılmış logging + hata yönetimi

---

## 🎬 Demo

<div align="center">

| Tespit + Takip | Sayım Paneli |
|:---:|:---:|
| <img src="assets/tracking_demo.gif" width="380"/> | <img src="assets/counting_overlay.png" width="380"/> |
| *PLACEHOLDER* | *PLACEHOLDER* |

</div>

---

## 📊 Performance

| Metrik | Değer |
|---|---|
| **Ortalama FPS (GPU)** | `PLACEHOLDER` |
| **Ortalama FPS (CPU)** | `PLACEHOLDER` |
| **Test videosu süresi** | `PLACEHOLDER` |
| **Toplam tespit edilen araç** | `PLACEHOLDER` |
| **Sınıf değişimi düzeltme sayısı** | `PLACEHOLDER` *(kaç kez flickering önlendi)* |

---

## ⚙️ Configuration

Sınıf bazlı varsayılan eşikler (`vehicle_tracker.py` içinde `DEFAULT_CLASS_THRESHOLDS`):

```python
{
    "car": 0.55,
    "truck": 0.50,
    "bus": 0.50,
    "motorcycle": 0.40,
    "bicycle": 0.35,
}
```

> Neden farklı eşikler? Küçük/az temsil edilen sınıflar (motosiklet, bisiklet) modelin daha az emin olduğu durumlarda bile kaçırılmasın diye daha düşük eşikle tutuluyor; büyük/kolay sınıflar (araba) yanlış pozitifleri azaltmak için daha yüksek eşikle filtreleniyor.

---

## 🚀 Getting Started

### Prerequisites
```
Python 3.9+
CUDA-compatible GPU (opsiyonel, önerilir)
```

### Installation
```bash
git clone https://github.com/KULLANICI_ADINIZ/roadsight-pro.git
cd roadsight-pro
pip install -r requirements.txt
```

### Usage

**Temel kullanım (ekranlı, yerel bilgisayar):**
```bash
python vehicle_tracker.py --video test5.mp4 --model yolo11n.pt
```

**Headless mod (Colab / sunucu — ekran gerektirmez):**
```bash
python vehicle_tracker.py --video test5.mp4 --headless --export-format json
```

**GPU zorlama:**
```bash
python vehicle_tracker.py --video test5.mp4 --device cuda:0
```

**Tüm parametreler:**

| Argüman | Açıklama | Varsayılan |
|---|---|---|
| `--video` | Girdi video yolu (zorunlu) | — |
| `--model` | YOLO model yolu/adı | `yolo11n.pt` |
| `--output` | Çıktı video yolu | `output.mp4` |
| `--conf` | Global eşik (tüm sınıflara uygulanır) | Sınıf bazlı |
| `--headless` | Ekransız çalıştırma | `False` |
| `--device` | `cuda:0` / `cpu` | Otomatik |
| `--export-format` | `json` / `csv` / `none` | `json` |
| `--export-dir` | Export klasörü | `results` |

---

## 📁 Project Structure

```
roadsight-pro/
├── vehicle_tracker.py        # Ana script (production-ready)
├── README.md                  # Bu dosya
├── PROJECT_REPORT.md          # Detaylı teknik dokümantasyon
├── requirements.txt           # Bağımlılıklar
├── LICENSE                    # MIT
├── .gitignore
├── results/                   # Export edilen JSON/CSV çıktılar (otomatik oluşur)
└── assets/                    # Görseller ve demo çıktıları
```

---

## 🧠 Technical Highlights

<details>
<summary><b>Detayları göster</b></summary>

<br>

**Sınıf reconciliation mantığı (`_reconcile_class`)**
YOLO, aynı fiziksel nesneyi ardışık karelerde bazen farklı sınıflandırabilir (ör. bir kare "car", sonraki "truck" der). Bu script, her takip ID'sinin *mevcut* sınıfını hafızada tutar; sınıf değişirse önceki sınıfın sayacını azaltıp yeni sınıfınkini artırır — böylece final sayım şişmez.

**Bellek güvenliği**
Her nesnenin hareket izi (`trail`) `deque(maxlen=40)` ile sınırlıdır. Orijinal implementasyonda sınırsız büyüyen liste, saatlerce süren videolarda bellek sorununa yol açabilirdi.

**Codec fallback**
`mp4v` codec her sistemde çalışmayabilir; başarısız olursa otomatik olarak `avc1`'e geçer.

**Neden ByteTrack?**
Düşük güven skorlu tespitleri de değerlendirerek ID sürekliliğini artırır — yoğun trafikte araçların birbirini geçici olarak kapatması (oklüzyon) durumunda bile takip ID'sinin korunma olasılığını yükseltir.

</details>

---

## 🛣️ Roadmap

- [ ] Şerit/çizgi bazlı geçiş sayımı (zone-based counting)
- [ ] Hız tahmini modülü
- [ ] Çoklu video/RTSP stream desteği
- [ ] Docker imajı
- [ ] Web tabanlı canlı izleme paneli (Streamlit/FastAPI)
- [ ] Birim testleri (pytest)

---

## 📚 References

- [Ultralytics YOLO11 Documentation](https://docs.ultralytics.com/models/yolo11/)
- Zhang, Y. et al. *ByteTrack: Multi-Object Tracking by Associating Every Detection Box*, 2022.

---

## 📄 License

Bu proje [MIT Lisansı](LICENSE) altında yayınlanmıştır.

---

<div align="center">

**`PLACEHOLDER — Adınız / GitHub / LinkedIn`**

⭐ Projeyi faydalı bulduysanız yıldız vermeyi unutmayın!

</div>
