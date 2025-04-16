# Restoran Rezervasyon ve Masa Yönetimi Sistemi

Bu proje, Restaurant Lezzet'in tasarım öğelerini kullanarak geliştirilen, Flask tabanlı kapsamlı bir restoran rezervasyon ve masa yönetimi sistemidir. Sistem, restoran personelinin rezervasyonları verimli bir şekilde yönetmesini, masa düzenini görselleştirmesini ve masa durumlarını gerçek zamanlı olarak takip etmesini sağlar.

## Özellikler

- **Güvenli Yönetici Girişi**: Kullanıcı adı ve şifre ile giriş sistemi
- **Dashboard**: Günlük rezervasyon ve masa durumu özeti
- **Rezervasyon Yönetimi**: Rezervasyon oluşturma, düzenleme, iptal etme ve silme
- **Masa Düzeni Görünümü**: Restoranın masa düzeninin görsel temsili
- **Masa Yönetimi**: Masaların sürükle-bırak yöntemiyle konumlandırılması, masa ekleme, silme ve birleştirme
- **Müsaitlik Çizelgesi**: Seçilen bir tarih için tüm masaların saatlik müsaitlik durumu
- **Müşteri Yönetimi**: Müşteri bilgilerinin kaydedilmesi ve takibi
- **Gelmeyen Müşteri Takibi**: Rezervasyon yaptırıp gelmeyen müşterilerin kaydedilmesi

## Kurulum

1. Projeyi klonlayın veya indirin:
```
git clone https://github.com/username/restaurant_reservation_system.git
cd restaurant_reservation_system
```

2. Sanal ortam oluşturun ve etkinleştirin:
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. Gerekli paketleri yükleyin:
```
pip install -r requirements.txt
```

4. Veritabanını oluşturun:
```
python create_database.py
```

5. Uygulamayı çalıştırın:
```
python run.py
```

6. Tarayıcınızda `http://localhost:5000` adresine gidin

## Giriş Bilgileri

- **Kullanıcı adı**: admin
- **Şifre**: admin123

## Proje Yapısı

```
restaurant_reservation_system/
├── app/                      # Ana uygulama paketi
│   ├── static/               # Statik dosyalar (CSS, JS, resimler)
│   ├── templates/            # HTML şablonları
│   ├── models/               # Veritabanı modelleri
│   ├── routes/               # Rotalar ve görünümler
│   └── __init__.py           # Uygulama fabrikası
├── database/                 # Veritabanı şeması ve ilgili dosyalar
├── instance/                 # Veritabanı dosyası (otomatik oluşturulur)
├── create_database.py        # Veritabanı oluşturma betiği
├── run.py                    # Uygulamayı çalıştırma betiği
├── requirements.txt          # Gerekli Python paketleri
└── README.md                 # Bu dosya
```

## Teknoloji Yığını

- **Backend**: Python 3.x, Flask Framework
- **Veritabanı**: SQLite 3
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Kimlik Doğrulama**: Flask-Login
- **Form Güvenliği**: Flask-WTF (CSRF Koruması için)
- **Şifreleme**: Werkzeug (Şifre hashing için)

## Tasarım

Bu uygulama, Restaurant Lezzet'in web sitesinden esinlenerek tasarlanmıştır. Kırmızı ve siyah tonları ağırlıklı renk şeması, zarif yazı tipleri ve modern düzen, Restaurant Lezzet'in görsel kimliğini yansıtmaktadır.

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakın.
