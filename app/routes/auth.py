from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import logging
from datetime import datetime

from ..models.user import User
from ..services.validation_service import validation_service

bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

# Rate limiter decorator - fallback oluştur
def rate_limit_decorator(limit_string):
    """Rate limiting decorator with fallback"""
    def decorator(f):
        # Flask-Limiter var mı kontrol et
        try:
            limiter = current_app.extensions.get('limiter')
            if limiter:
                return limiter.limit(limit_string)(f)
        except:
            pass
        # Eğer limiter yoksa normal fonksiyonu döndür
        return f
    return decorator

@bp.route('/login', methods=('GET', 'POST'))
@rate_limit_decorator("5 per minute")
def login():
    """Güvenli giriş işlemi - Rate limiting ve logging ile"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = validation_service.sanitize_input(request.form.get('username', ''))
        password = request.form.get('password', '')
        
        # Input validation
        if not username or not password:
            flash('Kullanıcı adı ve şifre gereklidir.', 'error')
            logger.warning(f"Login attempt with missing credentials from {request.remote_addr}")
            return render_template('auth/login.html')
        
        if len(username) > 50 or len(password) > 100:
            flash('Geçersiz giriş bilgileri.', 'error')
            logger.warning(f"Login attempt with oversized credentials from {request.remote_addr}")
            return render_template('auth/login.html')
        
        try:
            db = g.db
            error = None
            
            # Parameterized query kullan
            user_data = db.execute(
                'SELECT * FROM users WHERE username = ?', (username,)
            ).fetchone()
            
            if user_data is None:
                error = 'Geçersiz kullanıcı adı veya şifre.'
                logger.warning(f"Failed login attempt for username '{username}' from {request.remote_addr}")
            elif not check_password_hash(user_data['password'], password):
                error = 'Geçersiz kullanıcı adı veya şifre.'
                logger.warning(f"Failed password check for username '{username}' from {request.remote_addr}")
            
            if error is None:
                user = User(user_data['id'], user_data['username'])
                login_user(user, remember=True, duration=current_app.config.get('PERMANENT_SESSION_LIFETIME'))
                
                # Last login güncelle
                User.update_last_login(db, user_data['id'])
                
                # Next page redirect
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('dashboard.index')
                
                flash('Başarıyla giriş yaptınız.', 'success')
                logger.info(f"Successful login for user '{username}' from {request.remote_addr}")
                return redirect(next_page)
            
            flash(error, 'error')
            
        except Exception as e:
            logger.error(f"Login error for username '{username}': {e}")
            flash('Giriş sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """Güvenli çıkış işlemi"""
    username = current_user.username if current_user.is_authenticated else 'Unknown'
    logout_user()
    
    # Session'ı temizle
    session.clear()
    
    flash('Başarıyla çıkış yaptınız.', 'success')
    logger.info(f"User '{username}' logged out from {request.remote_addr}")
    return redirect(url_for('auth.login'))

@bp.route('/change-password', methods=('GET', 'POST'))
@login_required
@rate_limit_decorator("3 per minute")
def change_password():
    """Şifre değiştirme - Güvenli validasyon ile"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        error = None
        
        # Input validation
        if not current_password or not new_password or not confirm_password:
            error = 'Tüm alanlar gereklidir.'
        elif len(new_password) < 8:
            error = 'Yeni şifre en az 8 karakter olmalıdır.'
        elif len(new_password) > 100:
            error = 'Şifre çok uzun.'
        elif new_password != confirm_password:
            error = 'Yeni şifreler eşleşmiyor.'
        elif not any(c.isupper() for c in new_password):
            error = 'Şifre en az bir büyük harf içermelidir.'
        elif not any(c.islower() for c in new_password):
            error = 'Şifre en az bir küçük harf içermelidir.'
        elif not any(c.isdigit() for c in new_password):
            error = 'Şifre en az bir rakam içermelidir.'
        
        if error is None:
            try:
                db = g.db
                user_data = db.execute(
                    'SELECT * FROM users WHERE id = ?', (current_user.id,)
                ).fetchone()
                
                if not check_password_hash(user_data['password'], current_password):
                    error = 'Mevcut şifre yanlış.'
                    logger.warning(f"Wrong current password attempt by user {current_user.username}")
                else:
                    # Şifreyi güncelle
                    new_password_hash = generate_password_hash(new_password)
                    db.execute(
                        'UPDATE users SET password = ?, updated_at = ? WHERE id = ?',
                        (new_password_hash, datetime.now(), current_user.id)
                    )
                    db.commit()
                    
                    flash('Şifreniz başarıyla değiştirildi. Güvenlik için tekrar giriş yapın.', 'success')
                    logger.info(f"Password changed for user {current_user.username}")
                    
                    # Güvenlik için logout yap
                    logout_user()
                    return redirect(url_for('auth.login'))
                    
            except Exception as e:
                logger.error(f"Password change error for user {current_user.username}: {e}")
                error = 'Şifre değiştirme sırasında bir hata oluştu.'
        
        if error:
            flash(error, 'error')
    
    return render_template('auth/change_password.html')

@bp.route('/profile')
@login_required
def profile():
    """Kullanıcı profil sayfası"""
    try:
        db = g.db
        user_data = db.execute(
            'SELECT username, created_at, last_login FROM users WHERE id = ?', 
            (current_user.id,)
        ).fetchone()
        
        # Son aktiviteleri al
        recent_logins = db.execute(
            'SELECT last_login FROM users WHERE id = ? ORDER BY last_login DESC LIMIT 5',
            (current_user.id,)
        ).fetchall()
        
        return render_template('auth/profile.html', 
                             user_data=user_data, 
                             recent_logins=recent_logins)
                             
    except Exception as e:
        logger.error(f"Profile page error for user {current_user.username}: {e}")
        flash('Profil bilgileri yüklenirken hata oluştu.', 'error')
        return redirect(url_for('dashboard.index'))