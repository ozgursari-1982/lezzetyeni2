import os
import sqlite3
import datetime
from flask import Flask, g, render_template, flash, redirect, url_for, session
from flask_login import LoginManager, current_user
from werkzeug.security import generate_password_hash

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

def create_app(test_config=None):
    # Uygulama oluşturma ve yapılandırma
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'restaurant.sqlite'),
        UPLOAD_FOLDER=os.path.join(app.static_folder, 'uploads'),
    )

    if test_config is None:
        # Test değilse, config.py'den yapılandırma yükle (varsa)
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Test ise, test yapılandırmasını yükle
        app.config.from_mapping(test_config)

    # Instance klasörünün var olduğundan emin ol
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

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
    login_manager.init_app(app)

    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        db = get_db()
        user_data = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user_data:
            return User(user_data['id'], user_data['username'])
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

    # 404 Hata Sayfası
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    # 500 Hata Sayfası
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app
