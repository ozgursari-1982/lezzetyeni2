from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from ..models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = g.db
        
        error = None
        user_data = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if user_data is None:
            error = 'Geçersiz kullanıcı adı.'
        elif not check_password_hash(user_data['password'], password):
            error = 'Geçersiz şifre.'
        
        if error is None:
            user = User(user_data['id'], user_data['username'])
            login_user(user)
            User.update_last_login(db, user_data['id'])
            
            next_page = session.get('next', url_for('index'))
            session.pop('next', None)
            
            flash('Başarıyla giriş yaptınız.', 'success')
            return redirect(next_page)
        
        flash(error, 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/change-password', methods=('GET', 'POST'))
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        db = g.db
        
        error = None
        user_data = db.execute(
            'SELECT * FROM users WHERE id = ?', (current_user.id,)
        ).fetchone()
        
        if not check_password_hash(user_data['password'], current_password):
            error = 'Mevcut şifre yanlış.'
        elif new_password != confirm_password:
            error = 'Yeni şifreler eşleşmiyor.'
        elif len(new_password) < 6:
            error = 'Şifre en az 6 karakter olmalıdır.'
        
        if error is None:
            db.execute(
                'UPDATE users SET password = ? WHERE id = ?',
                (generate_password_hash(new_password), current_user.id)
            )
            db.commit()
            
            flash('Şifreniz başarıyla değiştirildi.', 'success')
            return redirect(url_for('index'))
        
        flash(error, 'error')
    
    return render_template('auth/change_password.html')
