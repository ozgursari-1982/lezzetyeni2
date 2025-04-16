from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from flask_login import login_required
import datetime

from ..models.reservation import Reservation
from ..models.customer import Customer
from ..models.table import Table
from ..models.table_group import TableGroup

bp = Blueprint('reservations', __name__, url_prefix='/reservations')

@bp.route('/')
@login_required
def index():
    db = g.db
    date_str = request.args.get('date', datetime.date.today().isoformat())
    
    try:
        selected_date = datetime.date.fromisoformat(date_str)
    except ValueError:
        selected_date = datetime.date.today()
    
    # Rezervasyonları al
    reservations = Reservation.get_all(db, date=selected_date)
    
    return render_template('reservations/index.html', reservations=reservations, selected_date=selected_date)

@bp.route('/new', methods=('GET', 'POST'))
@login_required
def new():
    db = g.db
    
    if request.method == 'POST':
        # Form verilerini al
        customer_name = request.form['customer_name']
        phone = request.form['phone']
        email = request.form.get('email', '')
        party_size = int(request.form['party_size'])
        reservation_date = datetime.date.fromisoformat(request.form['reservation_date'])
        start_time = datetime.time.fromisoformat(request.form['start_time'])
        duration = int(request.form['duration'])
        special_requests = request.form.get('special_requests', '')
        
        # Bitiş saatini hesapla
        start_datetime = datetime.datetime.combine(reservation_date, start_time)
        end_datetime = start_datetime + datetime.timedelta(hours=duration)
        end_time = end_datetime.time()
        
        # Masa veya masa grubu seçimi
        table_ids = request.form.getlist('table_id')
        table_group_id = request.form.get('table_group_id')
        
        error = None
        
        # Temel doğrulamalar
        if not customer_name:
            error = 'Müşteri adı gereklidir.'
        elif not phone:
            error = 'Telefon numarası gereklidir.'
        elif party_size <= 0:
            error = 'Kişi sayısı geçerli değil.'
        elif not (table_ids or table_group_id):
            error = 'En az bir masa veya masa grubu seçilmelidir.'
        
        # Müsaitlik kontrolü
        if not error and table_ids:
            for table_id in table_ids:
                available_tables = Table.get_available_tables(
                    db, reservation_date, start_time, end_time, 1
                )
                available_table_ids = [t['id'] for t in available_tables]
                
                if int(table_id) not in available_table_ids:
                    error = 'Seçilen masalardan biri belirtilen zaman aralığında müsait değil.'
                    break
        
        if not error and table_group_id:
            available_groups = TableGroup.get_available_groups(
                db, reservation_date, start_time, end_time, party_size
            )
            available_group_ids = [g['id'] for g in available_groups]
            
            if int(table_group_id) not in available_group_ids:
                error = 'Seçilen masa grubu belirtilen zaman aralığında müsait değil.'
        
        if error is None:
            # Müşteri kaydı var mı kontrol et
            customer = Customer.get_by_phone(db, phone)
            customer_id = None
            
            if customer:
                customer_id = customer.id
            else:
                # Yeni müşteri oluştur
                new_customer = Customer.create(db, customer_name, phone, email)
                customer_id = new_customer['id']
            
            # Rezervasyon oluştur
            new_reservation = Reservation.create(
                db, customer_id, customer_name, phone, email, party_size,
                reservation_date, start_time, end_time, special_requests
            )
            
            # Masa veya masa grubu ata
            if table_ids:
                Reservation.assign_tables(db, new_reservation['id'], table_ids=table_ids)
            elif table_group_id:
                Reservation.assign_tables(db, new_reservation['id'], table_group_id=table_group_id)
            
            flash('Rezervasyon başarıyla oluşturuldu.', 'success')
            return redirect(url_for('reservations.index'))
        
        flash(error, 'error')
    
    # Varsayılan değerler
    today = datetime.date.today()
    default_time = datetime.time(19, 0)  # 19:00
    
    return render_template('reservations/new.html', 
                          default_date=today, 
                          default_time=default_time,
                          default_duration=2)

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    db = g.db
    reservation = Reservation.get_by_id(db, id)
    
    if not reservation:
        flash('Rezervasyon bulunamadı.', 'error')
        return redirect(url_for('reservations.index'))
    
    if request.method == 'POST':
        # Form verilerini al
        customer_name = request.form['customer_name']
        phone = request.form['phone']
        email = request.form.get('email', '')
        party_size = int(request.form['party_size'])
        reservation_date = datetime.date.fromisoformat(request.form['reservation_date'])
        start_time = datetime.time.fromisoformat(request.form['start_time'])
        duration = int(request.form['duration'])
        special_requests = request.form.get('special_requests', '')
        status = request.form['status']
        arrival_status = request.form.get('arrival_status')
        
        # Bitiş saatini hesapla
        start_datetime = datetime.datetime.combine(reservation_date, start_time)
        end_datetime = start_datetime + datetime.timedelta(hours=duration)
        end_time = end_datetime.time()
        
        # Masa veya masa grubu seçimi
        table_ids = request.form.getlist('table_id')
        table_group_id = request.form.get('table_group_id')
        
        error = None
        
        # Temel doğrulamalar
        if not customer_name:
            error = 'Müşteri adı gereklidir.'
        elif not phone:
            error = 'Telefon numarası gereklidir.'
        elif party_size <= 0:
            error = 'Kişi sayısı geçerli değil.'
        elif status != 'cancelled' and not (table_ids or table_group_id):
            error = 'En az bir masa veya masa grubu seçilmelidir.'
        
        # İptal edilmemiş rezervasyonlar için müsaitlik kontrolü
        if not error and status != 'cancelled':
            if table_ids:
                for table_id in table_ids:
                    available_tables = Table.get_available_tables(
                        db, reservation_date, start_time, end_time, 1, exclude_res_id=id
                    )
                    available_table_ids = [t['id'] for t in available_tables]
                    
                    if int(table_id) not in available_table_ids:
                        error = 'Seçilen masalardan biri belirtilen zaman aralığında müsait değil.'
                        break
            
            if not error and table_group_id:
                available_groups = TableGroup.get_available_groups(
                    db, reservation_date, start_time, end_time, party_size, exclude_res_id=id
                )
                available_group_ids = [g['id'] for g in available_groups]
                
                if int(table_group_id) not in available_group_ids:
                    error = 'Seçilen masa grubu belirtilen zaman aralığında müsait değil.'
        
        if error is None:
            # Müşteri kaydı var mı kontrol et
            customer = Customer.get_by_phone(db, phone)
            customer_id = None
            
            if customer:
                customer_id = customer.id
            else:
                # Yeni müşteri oluştur
                new_customer = Customer.create(db, customer_name, phone, email)
                customer_id = new_customer['id']
            
            # Rezervasyonu güncelle
            Reservation.update(
                db, id, customer_id=customer_id, customer_name=customer_name,
                phone=phone, email=email, party_size=party_size,
                reservation_date=reservation_date, start_time=start_time,
                end_time=end_time, special_requests=special_requests,
                status=status, arrival_status=arrival_status
            )
            
            # İptal edilmemiş rezervasyonlar için masa veya masa grubu ata
            if status != 'cancelled':
                if table_ids:
                    Reservation.assign_tables(db, id, table_ids=table_ids)
                elif table_group_id:
                    Reservation.assign_tables(db, id, table_group_id=table_group_id)
            
            flash('Rezervasyon başarıyla güncellendi.', 'success')
            return redirect(url_for('reservations.index'))
        
        flash(error, 'error')
    
    # Rezervasyona atanan masaları veya masa grubunu al
    assigned_tables = Reservation.get_tables_for_reservation(db, id)
    
    # Rezervasyon süresi (saat)
    start_datetime = datetime.datetime.combine(
        reservation.reservation_date, reservation.start_time
    )
    end_datetime = datetime.datetime.combine(
        reservation.reservation_date, reservation.end_time
    )
    duration = (end_datetime - start_datetime).seconds // 3600
    
    return render_template('reservations/edit.html', 
                          reservation=reservation,
                          assigned_tables=assigned_tables,
                          duration=duration)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    db = g.db
    reservation = Reservation.get_by_id(db, id)
    
    if not reservation:
        flash('Rezervasyon bulunamadı.', 'error')
        return redirect(url_for('reservations.index'))
    
    Reservation.delete(db, id)
    
    flash('Rezervasyon başarıyla silindi.', 'success')
    return redirect(url_for('reservations.index'))

@bp.route('/<int:id>/confirm-arrival', methods=('POST',))
@login_required
def confirm_arrival(id):
    db = g.db
    reservation = Reservation.get_by_id(db, id)
    
    if not reservation:
        flash('Rezervasyon bulunamadı.', 'error')
        return redirect(url_for('reservations.index'))
    
    Reservation.confirm_arrival(db, id)
    
    flash('Müşteri gelişi başarıyla onaylandı.', 'success')
    return redirect(url_for('reservations.index'))

@bp.route('/<int:id>/confirm-no-show', methods=('POST',))
@login_required
def confirm_no_show(id):
    db = g.db
    reservation = Reservation.get_by_id(db, id)
    
    if not reservation:
        flash('Rezervasyon bulunamadı.', 'error')
        return redirect(url_for('reservations.index'))
    
    Reservation.confirm_no_show(db, id)
    
    flash('Müşteri gelmedi olarak işaretlendi.', 'success')
    return redirect(url_for('reservations.index'))

@bp.route('/<int:id>/cancel', methods=('POST',))
@login_required
def cancel(id):
    db = g.db
    reservation = Reservation.get_by_id(db, id)
    
    if not reservation:
        flash('Rezervasyon bulunamadı.', 'error')
        return redirect(url_for('reservations.index'))
    
    Reservation.cancel(db, id)
    
    flash('Rezervasyon başarıyla iptal edildi.', 'success')
    return redirect(url_for('reservations.index'))
