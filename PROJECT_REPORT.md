# RoadSight Pro: Advanced Vehicle Tracking & Counting
### Proje Raporu

---

## 1. Proje Özeti

| Alan | Bilgi |
|---|---|
| **Proje Adı** | RoadSight Pro |
| **Amaç** | Production-kalitesinde araç tespit, sınıflandırma, takip ve sayım CLI aracı |
| **Model** | YOLO11 (Ultralytics) — kullanıcı tarafından değiştirilebilir |
| **Takip Algoritması** | ByteTrack (persist=True) |
| **Çalışma Ortamı** | CLI — yerel, sunucu, Colab (headless) |
| **Dil / Kütüphaneler** | Python 3.9+, Ultralytics, OpenCV, tqdm (opsiyonel) |
| **Lisans** | MIT |

**Kısa açıklama (repo description için):**
> Production-ready CLI tool for real-time vehicle detection, classification, tracking, and per-class counting using YOLO11 and ByteTrack, with class-flicker reconciliation and headless mode support.

---

## 2. GitHub Repository Ayarları

### 2.1 Repo İsmi
- `roadsight-pro`
- `vehicle-tracker-cli`
- `advanced-vehicle-counting`

### 2.2 Repo Açıklaması
```
Production-ready CLI tool for real-time vehicle detection, classification, and counting using YOLO11 + ByteTrack.
```

### 2.3 Topics
```
object-detection, object-tracking, yolo11, vehicle-counting,
computer-vision, bytetrack, opencv, python, cli-tool
```

### 2.4 Görünürlük
Public.

### 2.5 Lisans
MIT License.

### 2.6 .gitignore
```
# Model ağırlıkları
*.pt

# Video girdi/çıktı dosyaları (büyük, repoya koymayın)
*.mp4
*.avi
!assets/*.gif

# Export edilen sonuçlar
results/

# Python
__pycache__/
*.pyc
.venv/
venv/

# Jupyter (varsa)
.ipynb_checkpoints/
```

---

## 3. Klasör / Dosya Yapısı

```
roadsight-pro/
├── vehicle_tracker.py        # Ana script
├── README.md                  # Proje tanıtımı
├── PROJECT_REPORT.md          # Bu rapor
├── requirements.txt           # Bağımlılıklar
├── LICENSE                    # MIT
├── .gitignore
├── results/                   # JSON/CSV export çıktıları (gitignore'da)
└── assets/                    # Demo görselleri
```

---

## 4. Mimari ve Tasarım Kararları

### 4.1 Sınıf Yapısı
```
VehicleTracker
├── _load_model()       → model yükleme + hata yönetimi
├── _open_video()        → video açma + doğrulama
├── _build_writer()       → codec fallback'li video yazıcı
├── _reconcile_class()    → sınıf flickering düzeltmesi (ÇEKİRDEK MANTIK)
├── _passes_threshold()   → sınıf bazlı eşik kontrolü
├── _draw_frame()          → çizim + sayım güncelleme
└── run()                  → ana işleme döngüsü
```

### 4.2 Neden Sınıf Tabanlı Tasarım?
Orijinal script'teki global değişkenler (`object_paths`, `object_colors`, `vehicle_counts`) fonksiyon dışında paylaşılan durum (shared state) oluşturuyordu — test edilebilirliği ve yeniden kullanılabilirliği zorlaştırıyordu. `VehicleTracker` sınıfı bu durumu kapsülleyerek (encapsulation) birden fazla video/oturum için bağımsız örnekler oluşturmayı mümkün kılıyor.

### 4.3 Sınıf Flickering Problemi (Kritik Tasarım Kararı)
**Problem:** YOLO, aynı fiziksel nesneyi ardışık karelerde farklı sınıflandırabilir (ör. bir van bazen "car" bazen "truck" olarak tespit edilir).

**Naif çözüm (yanlış):** Her tespitte sayacı artırmak → aynı araç birden fazla kez, farklı sınıflarda sayılır → toplam sayı gerçek araç sayısından fazla çıkar.

**Uygulanan çözüm:** Her `track_id` için "mevcut sınıf" hafızada tutulur. Sınıf değişirse:
```python
vehicle_counts[eski_sınıf] -= 1
vehicle_counts[yeni_sınıf] += 1
```
Bu, toplam benzersiz araç sayısını her zaman doğru tutar (ID sayısı = toplam araç sayısı).

### 4.4 Bellek Yönetimi
`deque(maxlen=40)` kullanımı, uzun videolarda (ör. 1 saatlik trafik kamerası kaydı) her nesnenin iz geçmişinin sınırsız büyümesini engeller. 40 nokta, görsel olarak yeterli bir "kuyruk" efekti sağlarken belleği sabit tutar.

### 4.5 Headless Mod
`cv2.imshow()` GUI gerektirir ve Colab/Docker/sunucu ortamlarında hata fırlatır. `--headless` bayrağı bu çağrıyı atlayarak scriptin CI/CD pipeline'larında veya bulut ortamlarında sorunsuz çalışmasını sağlar.

---

## 5. Kullanım Senaryoları

| Senaryo | Komut |
|---|---|
| Yerel test | `python vehicle_tracker.py --video test.mp4` |
| Colab/sunucu | `python vehicle_tracker.py --video test.mp4 --headless` |
| GPU zorlama | `python vehicle_tracker.py --video test.mp4 --device cuda:0` |
| CSV export | `python vehicle_tracker.py --video test.mp4 --export-format csv` |
| Özel model | `python vehicle_tracker.py --video test.mp4 --model yolo11m.pt` |

---

## 6. requirements.txt

```
ultralytics>=8.3.0
opencv-python>=4.9.0
numpy>=1.26.0
tqdm>=4.66.0
```

---

## 7. Bilinen Sınırlamalar

- Tek video dosyası işler; canlı RTSP stream desteği henüz yok (roadmap'te)
- Şerit/bölge bazlı sayım (belirli bir çizgiyi geçen araçları sayma) henüz eklenmedi
- Birim testleri henüz yazılmadı

---

## 8. Sonraki Geliştirme Adımları

- [ ] Zone-based / line-crossing counting
- [ ] Hız tahmini (komşu kareler arası piksel deplasmanından)
- [ ] RTSP/canlı kamera desteği
- [ ] `pytest` ile birim testleri (özellikle `_reconcile_class` için)
- [ ] Docker imajı + `docker-compose.yml`
- [ ] GitHub Actions CI (lint + test)

---

## 9. Referanslar

- Ultralytics YOLO11 Documentation — docs.ultralytics.com/models/yolo11
- Zhang, Y. et al. *ByteTrack: Multi-Object Tracking by Associating Every Detection Box*, 2022.
