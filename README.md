# Marketing Dashboard

Bu proje, basit bir pazarlama dashboard iskeleti sağlar.

Dizin yapısı:

marketing_dashboard/

├── config/
│   └── settings.py          # Kolon haritaları, sabitler, ISO kodları

├── core/
│   ├── data_loader.py       # Veri okuma, temizleme ve standardize etme
│   ├── analyzer.py          # İstatistiksel hesaplamalar, KPI'lar
│   └── simulator.py         # Dummy data oluşturma ve simülasyonlar

├── visualization/
│   ├── charts.py            # Plotly grafiklerini üreten fonksiyonlar
│   └── report_generator.py  # HTML şablonu ve raporu birleştirme

└── main.py                  # Uygulamayı başlatan ana yönetici (Orchestrator)

Nasıl kullanılır:

1. Sanal ortam oluşturun ve bağımlılıkları yükleyin (örnek olarak `requirements.txt` mevcut).
2. `python main.py` çalıştırarak örnek verilerle rapor oluşturun.

Not: Bu iskelet genişletilmeye ve projeye özgü ihtiyaçlarla uyarlanmaya uygundur.
