import os
from datetime import timedelta

class Config:
    # Güvenlik anahtarı - environment variable'dan alınacak
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Veritabanı konfigürasyonu
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///instance/restaurant.sqlite'
    
    # Session konfigürasyonu
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_COOKIE_SECURE = True  # HTTPS için
    SESSION_COOKIE_HTTPONLY = True  # XSS koruması
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF koruması
    
    # CSRF koruması
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 saat
    
    # Upload konfigürasyonu
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB maksimum dosya boyutu
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app', 'static', 'uploads')
    
    # Email konfigürasyonu (opsiyonel)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Güvenlik headers
    FORCE_HTTPS = True
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Development için HTTP kullanılabilir
    FORCE_HTTPS = False
    
class ProductionConfig(Config):
    DEBUG = False
    
class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False  # Test için CSRF devre dışı
    SESSION_COOKIE_SECURE = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}