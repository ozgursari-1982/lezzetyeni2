# Restoran Rezervasyon ve Masa Yönetimi Sistemi

Bu proje, Restaurant Lezzet'in tasarım öğelerini kullanarak geliştirilen, Flask tabanlı kapsamlı bir restoran rezervasyon ve masa yönetimi sistemidir. Sistem, restoran personelinin rezervasyonları verimli bir şekilde yönetmesini, masa düzenini görselleştirmesini ve masa durumlarını gerçek zamanlı olarak takip etmesini sağlar.

## Özellikler

### Temel Özellikler
- **Güvenli Yönetici Girişi**: Kullanıcı adı ve şifre ile güvenli giriş sistemi
- **Dashboard**: Günlük rezervasyon ve masa durumu özeti
- **Rezervasyon Yönetimi**: Rezervasyon oluşturma, düzenleme, iptal etme ve silme
- **Masa Düzeni Görünümü**: Restoranin masa düzeninin görsel temsili
- **Masa Yönetimi**: Masaların sürükle-bırak yöntemiyle konumlandırılması, masa ekleme, silme ve birleştirme
- **Müsaitlik Çizelgesi**: Seçilen bir tarih için tüm masaların saatlik müsaitlik durumu
- **Müşteri Yönetimi**: Müşteri bilgilerinin kaydedilmesi ve takibi
- **Gelmeyen Müşteri Takibi**: Rezervasyon yaptırıp gelmeyen müşterilerin kaydedilmesi

### Güvenlik Özellikleri (Yeni!)
- **CSRF Koruması**: Cross-Site Request Forgery saldırılarına karşı koruma
- **Rate Limiting**: Brute force saldırılarına karşı rate limiting
- **Güvenlik Headers**: XSS, clickjacking ve diğer saldırılara karşı HTTP security headers
- **Input Validation**: Kapsamlı veri doğrulama ve sanitization
- **Session Güvenliği**: Güvenli session yönetimi ve otomatik timeout
- **Logging Sistemi**: Güvenlik olayları ve sistem aktivitelerini kaydetme

### Yeni Özellikler
- **Email Bildirim Sistemi**: Rezervasyon onayı, hatırlatma ve iptal bildirimleri
- **Gelişmiş Validation**: Telefon, email, tarih ve saat doğrulama
- **API Endpoints**: Mobil uygulama entegrasyonu için RESTful API
- **Error Handling**: Kapsamlı hata yönetimi ve kullanıcı dostu hata sayfaları
- **Environment Variables**: Güvenli konfigürasyon yönetimi

## Kurulum

### Gereksinimler
- Python 3.8+
- SQLite 3
- Internet bağlantısı (email bildirimleri için)

### Adım 1: Projeyi İndirin
```bash
git clone https://github.com/ozgursari-1982/lezzetyeni2.git
cd lezzetyeni2
```

### Adım 2: Sanal Ortam Oluşturun
```bash
python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### Adım 3: Gerekli Paketleri Yükleyin
```bash
pip install -r requirements.txt
```

### Adım 4: Environment Variables'ı Ayarlayın
`.env.example` dosyasını `.env` olarak kopyalayın ve gerekli değerleri doldurun:

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin:
```env
# Güvenlik Anahtarı (Güçlü bir anahtar oluşturun)
SECRET_KEY=your-very-strong-secret-key-here

# Email Konfigürasyonu (opsiyonel)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Uygulama Modu
FLASK_ENV=development
```

### Adım 5: Veritabanını Oluşturun
```bash
python create_database.py
```

### Adım 6: Uygulamayı Çalıştırın
```bash
python run.py
```

### Adım 7: Tarayıcıda Açın
Tarayıcınızda `http://localhost:5002` adresine gidin

## Giriş Bilgileri

**Varsayılan Yönetici Hesabı:**
- **Kullanıcı adı**: admin
- **Şifre**: admin123

> **Önemli**: İlk girişten sonra şifrenizi değiştirmeyi unutmayın!

## Proje Yapısı

```
restaurant_reservation_system/
├── app/                      # Ana uygulama paketi
│   ├── models/               # Veritabanı modelleri
│   ├── routes/               # Rotalar ve görünümler
│   ├── services/             # İş mantığı servisleri
│   ├── static/               # Statik dosyalar (CSS, JS, resimler)
│   ├── templates/            # HTML şablonları
│   │   ├── auth/             # Giriş sayfaları
│   │   ├── dashboard/        # Dashboard sayfaları
│   │   ├── emails/           # Email şablonları
│   │   ├── errors/           # Hata sayfaları
│   │   ├── reservations/     # Rezervasyon sayfaları
│   │   └── tables/           # Masa yönetimi sayfaları
│   └── __init__.py           # Uygulama fabrikası
├── database/                 # Veritabanı şeması ve ilgili dosyalar
├── instance/                 # Veritabanı dosyası (otomatik oluşturulur)
├── logs/                     # Log dosyaları (otomatik oluşturulur)
├── config.py                 # Konfigürasyon ayarları
├── create_database.py        # Veritabanı oluşturma betiği
├── run.py                    # Uygulamayı çalıştırma betiği
├── requirements.txt          # Gerekli Python paketleri
├── .env.example              # Environment variables örneği
└── README.md                 # Bu dosya
```

## Teknoloji Yığını

### Backend
- **Python 3.8+**: Programlama dili
- **Flask 2.3+**: Web framework
- **SQLite 3**: Veritabanı
- **Flask-Login**: Kullanıcı kimlik doğrulama
- **Flask-WTF**: Form güvenliği ve CSRF koruması
- **Flask-Limiter**: Rate limiting
- **Flask-Talisman**: Güvenlik headers
- **Flask-Mail**: Email gönderimi
- **Werkzeug**: Şifre hashing

### Frontend
- **HTML5**: Markup
- **CSS3**: Stillendirme
- **JavaScript (ES6+)**: İnteraktivite
- **Bootstrap 4**: Responsive tasarım
- **Font Awesome**: İkonlar
- **jQuery**: DOM manipulasyonu

### Güvenlik
- **CSRF Protection**: Cross-site request forgery koruması
- **Rate Limiting**: Brute force koruması
- **Input Validation**: XSS ve injection koruması
- **Secure Headers**: Clickjacking ve diğer saldırı koruması
- **Session Security**: Güvenli session yönetimi

## API Kullanımı

### Müsaitlik Kontrolü
```
GET /reservations/api/availability?date=2025-09-23&start_time=19:00&end_time=21:00&party_size=4
```

Response:
```json
{
  "available_tables": [
    {"id": 1, "name": "Masa 1", "capacity": 4},
    {"id": 2, "name": "Masa 2", "capacity": 6}
  ],
  "available_groups": [
    {"id": 1, "name": "Bahse Grup", "capacity": 8}
  ]
}
```

## Güvenlik Önerileri

### Production Ortamı için:
1. **Güçlü SECRET_KEY oluşturun**:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

2. **HTTPS kullanın** - Production'da SSL sertifikası zorunlu

3. **Veritabanını güvenli hale getirin** - SQLite yerine PostgreSQL kullanın
4. **Güvenlik güncellemelerini takip edin**
5. **Log dosyalarını düzenli kontrol edin**
6. **Backup stratejinizi belirleyin**

## Geliştirme

### Test Çalıştırma
```bash
pytest
```

### Code Linting
```bash
flake8 app/
```

### Code Formatting
```bash
black app/
```

## Sorun Giderme

### Sık Karşılaşılan Sorunlar

1. **"No module named 'flask'" hatası**:
   - Sanal ortamın etkinleştirildiğinden emin olun
   - `pip install -r requirements.txt` komutunu tekrar çalıştırın

2. **Veritabanı hatası**:
   - `python create_database.py` komutunu tekrar çalıştırın
   - `instance/` klasörünün var olduğundan emin olun

3. **Email gönderimi çalışmıyor**:
   - `.env` dosyasındaki email ayarlarını kontrol edin
   - Gmail için "App Password" kullanın
4. **Rate limit hatası**:
   - Birkaç dakika bekleyin veya rate limit ayarlarını config'den değiştirin

### Log Dosyaları
Hata durumunda `logs/restaurant.log` dosyasını kontrol edin.

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakın.

## Destek

Sorularınız için:
- GitHub Issues kullanın
- Email: ozgursari1982@gmail.com

---

**Restaurant Lezzet Rezervasyon Sistemi** - Modern, güvenli ve kullanıcı dostu restoran yönetimi!