from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from flask_login import login_required
import datetime

from ..models.customer import Customer

bp = Blueprint('customers', __name__, url_prefix='/customers')

@bp.route('/')
@login_required
def index():
    db = g.db
    customers = Customer.get_all(db)
    return render_template('customers/index.html', customers=customers)

@bp.route('/new', methods=('GET', 'POST'))
@login_required
def new():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form.get('email', '')
        notes = request.form.get('notes', '')
        db = g.db
        
        error = None
        
        if not name:
            error = 'Müşteri adı gereklidir.'
        elif not phone:
            error = 'Telefon numarası gereklidir.'
        
        # Telefon numarasının benzersiz olup olmadığını kontrol et
        existing_customer = Customer.get_by_phone(db, phone)
        if existing_customer:
            error = 'Bu telefon numarası ile kayıtlı bir müşteri zaten var.'
        
        if error is None:
            Customer.create(db, name, phone, email, notes)
            flash('Müşteri başarıyla oluşturuldu.', 'success')
            return redirect(url_for('customers.index'))
        
        flash(error, 'error')
    
    return render_template('customers/new.html')

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    db = g.db
    customer = Customer.get_by_id(db, id)
    
    if not customer:
        flash('Müşteri bulunamadı.', 'error')
        return redirect(url_for('customers.index'))
    
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form.get('email', '')
        notes = request.form.get('notes', '')
        
        error = None
        
        if not name:
            error = 'Müşteri adı gereklidir.'
        elif not phone:
            error = 'Telefon numarası gereklidir.'
        
        # Telefon numarası değiştiyse, benzersiz olup olmadığını kontrol et
        if phone != customer.phone:
            existing_customer = Customer.get_by_phone(db, phone)
            if existing_customer:
                error = 'Bu telefon numarası ile kayıtlı bir müşteri zaten var.'
        
        if error is None:
            Customer.update(db, id, name=name, phone=phone, email=email, notes=notes)
            flash('Müşteri başarıyla güncellendi.', 'success')
            return redirect(url_for('customers.index'))
        
        flash(error, 'error')
    
    return render_template('customers/edit.html', customer=customer)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    db = g.db
    customer = Customer.get_by_id(db, id)
    
    if not customer:
        flash('Müşteri bulunamadı.', 'error')
        return redirect(url_for('customers.index'))
    
    success = Customer.delete(db, id)
    
    if success:
        flash('Müşteri başarıyla silindi.', 'success')
    else:
        flash('Müşteri silinemedi. Rezervasyonları olan müşteriler silinemez.', 'error')
    
    return redirect(url_for('customers.index'))

@bp.route('/no-shows')
@login_required
def no_shows():
    db = g.db
    no_shows = Customer.get_no_shows(db)
    return render_template('customers/no_shows.html', no_shows=no_shows)
