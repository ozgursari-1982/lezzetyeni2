import os
import sqlite3
import datetime
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, g, render_template, flash, redirect, url_for, session, request
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Environment variables'ı yükle
load_dotenv()

# SQLite tarih/zaman adaptörleri
def adapt_datetime(dt):
    return dt.isoformat()

def convert_datetime(s):
    try:
        return datetime.datetime.fromisoformat(s.decode())
    except:
        return s

def adapt_date(d):
    return d.isoformat()

def convert_date(s):
    try:
        return datetime.date.fromisoformat(s.decode())
    except:
        return s

def adapt_time(t):
    return t.isoformat()

def convert_time(s):
    try:
        return datetime.time.fromisoformat(s.decode())
    except:
        return s

sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter("timestamp", convert_datetime)
sqlite3.register_adapter(datetime.date, adapt_date)
sqlite3.register_converter("date", convert_date)
sqlite3.register_adapter(datetime.time, adapt_time)
sqlite3.register_converter("time", convert_time)

def create_app(config_name=None):
    # Uygulama oluşturma ve yapılandırma
    app = Flask(__name__, instance_relative_config=True)
    
    # Konfigürasyon yükleme
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Instance klasörünün var olduğundan emin ol
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Upload klasörünü oluştur
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass
    
    # Logging konfigürasyonu
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/restaurant.log',
                                         maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Restaurant Reservation System startup')
    
    # Güvenlik eklentilerini başlat
    csrf = CSRFProtect(app)
    
    # Rate limiting
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # HTTPS ve güvenlik headers (sadece production'da)
    if app.config.get('FORCE_HTTPS', False):
        talisman = Talisman(
            app,
            force_https=True,
            strict_transport_security=True,
            content_security_policy={
                'default-src': "'self'",
                'script-src': "'self' 'unsafe-inline'",
                'style-src': "'self' 'unsafe-inline'",
                'img-src': "'self' data:",
                'font-src': "'self'"
            }
        )
    
    # Veritabanı bağlantısı
    def get_db():
        if 'db' not in g:
            g.db = sqlite3.connect(
                app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    app.teardown_appcontext(close_db)

    # Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Lütfen bu sayfaya erişmek için giriş yapın.'
    login_manager.session_protection = 'strong'
    login_manager.init_app(app)

    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            db = get_db()
            user_data = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            if user_data:
                return User(user_data['id'], user_data['username'])
        except Exception as e:
            app.logger.error(f'Error loading user {user_id}: {e}')
        return None

    # Blueprint'leri kaydet
    from .routes import auth, dashboard, reservations, tables, customers

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(reservations.bp)
    app.register_blueprint(tables.bp)
    app.register_blueprint(customers.bp)

    # Ana sayfa yönlendirmesi
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))

    # Hata işleyicileri
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning(f'404 error: {request.url}')
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f'500 error: {e}')
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        app.logger.warning(f'Rate limit exceeded: {request.remote_addr}')
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(400)
    def bad_request(e):
        app.logger.warning(f'Bad request: {request.url} - {e}')
        return render_template('errors/400.html'), 400

    # Güvenlik headers'ları ekle
    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    return app