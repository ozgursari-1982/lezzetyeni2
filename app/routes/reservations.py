from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify, current_app
from flask_login import login_required, current_user
import datetime
import logging
from typing import Dict, List, Optional

from ..models.reservation import Reservation
from ..models.customer import Customer
from ..models.table import Table
from ..models.table_group import TableGroup
from ..services.validation_service import validation_service
from ..services.email_service import email_service

bp = Blueprint('reservations', __name__, url_prefix='/reservations')
logger = logging.getLogger(__name__)

# Rate limiter decorator - fallback oluştur
def rate_limit_decorator(limit_string):
    """Rate limiting decorator with fallback"""
    def decorator(f):
        try:
            limiter = current_app.extensions.get('limiter')
            if limiter:
                return limiter.limit(limit_string)(f)
        except:
            pass
        return f
    return decorator

@bp.route('/')
@login_required
def index():
    """Rezervasyon listesi - filtreleme ve sayfalama ile"""
    try:
        db = g.db
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Filtreler
        date_str = request.args.get('date', datetime.date.today().isoformat())
        status_filter = request.args.get('status', 'all')
        search_query = request.args.get('search', '').strip()
        
        try:
            selected_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            selected_date = datetime.date.today()
            flash('Geçersiz tarih formatı, bugünün tarihi kullanıldı.', 'warning')
        
        # Rezervasyonları al
        reservations = Reservation.get_all(
            db, 
            date=selected_date, 
            status=status_filter if status_filter != 'all' else None,
            search=search_query,
            page=page,
            per_page=per_page
        )
        
        # İstatistikleri al (eğer metodlar varsa)
        try:
            stats = {
                'total_reservations': len(reservations) if reservations else 0,
                'confirmed_count': len([r for r in reservations if r.get('status') == 'confirmed']) if reservations else 0,
                'pending_count': len([r for r in reservations if r.get('status') == 'pending']) if reservations else 0,
                'cancelled_count': len([r for r in reservations if r.get('status') == 'cancelled']) if reservations else 0,
                'no_show_count': len([r for r in reservations if r.get('status') == 'no_show']) if reservations else 0
            }
        except:
            stats = {'total_reservations': 0, 'confirmed_count': 0, 'pending_count': 0, 'cancelled_count': 0, 'no_show_count': 0}
        
        return render_template('reservations/index.html', 
                             reservations=reservations or [], 
                             selected_date=selected_date,
                             stats=stats,
                             current_page=page,
                             search_query=search_query,
                             status_filter=status_filter)
                             
    except Exception as e:
        logger.error(f"Error loading reservations: {e}")
        flash('Rezervasyonlar yüklenirken hata oluştu.', 'error')
        return render_template('reservations/index.html', 
                             reservations=[], 
                             selected_date=datetime.date.today(),
                             stats={},
                             current_page=1,
                             search_query='',
                             status_filter='all')

@bp.route('/new', methods=('GET', 'POST'))
@login_required
@rate_limit_decorator("10 per minute")
def new():
    """Yeni rezervasyon oluşturma - validation ve email bildirim ile"""
    if request.method == 'POST':
        try:
            # Form verilerini al ve temizle
            form_data = {
                'customer_name': validation_service.sanitize_input(request.form.get('customer_name', '')),
                'phone': validation_service.sanitize_input(request.form.get('phone', '')),
                'email': validation_service.sanitize_input(request.form.get('email', '')),
                'party_size': request.form.get('party_size', 0),
                'reservation_date': request.form.get('reservation_date', ''),
                'start_time': request.form.get('start_time', ''),
                'duration': request.form.get('duration', 2),
                'special_requests': validation_service.sanitize_input(request.form.get('special_requests', ''))
            }
            
            # Validation
            is_valid, validation_errors = validation_service.validate_reservation_data(form_data)
            
            if not is_valid:
                for error in validation_errors:
                    flash(error, 'error')
                return render_template('reservations/new.html', 
                                     form_data=form_data,
                                     default_date=datetime.date.today(),
                                     default_time=datetime.time(19, 0),
                                     default_duration=2)
            
            # Tarih ve saat çevirileri
            party_size = int(form_data['party_size'])
            reservation_date = datetime.date.fromisoformat(form_data['reservation_date'])
            start_time = datetime.time.fromisoformat(form_data['start_time'])
            duration = int(form_data['duration'])
            
            # Bitiş saatini hesapla
            start_datetime = datetime.datetime.combine(reservation_date, start_time)
            end_datetime = start_datetime + datetime.timedelta(hours=duration)
            end_time = end_datetime.time()
            
            # Masa seçimi
            table_ids = request.form.getlist('table_id')
            table_group_id = request.form.get('table_group_id')
            
            if not table_ids and not table_group_id:
                flash('En az bir masa veya masa grubu seçilmelidir.', 'error')
                return render_template('reservations/new.html', form_data=form_data)
            
            # Müsaitlik kontrolü
            availability_error = check_table_availability(
                g.db, table_ids, table_group_id, reservation_date, 
                start_time, end_time, party_size
            )
            
            if availability_error:
                flash(availability_error, 'error')
                return render_template('reservations/new.html', form_data=form_data)
            
            # Müşteri kontrolü ve oluşturma
            customer_id = handle_customer_creation(
                g.db, form_data['customer_name'], form_data['phone'], form_data['email']
            )
            
            # Rezervasyon oluştur
            new_reservation = Reservation.create(
                g.db, customer_id, form_data['customer_name'], form_data['phone'], 
                form_data['email'], party_size, reservation_date, start_time, 
                end_time, form_data['special_requests']
            )
            
            # Masa atama
            if table_ids:
                Reservation.assign_tables(g.db, new_reservation['id'], table_ids=table_ids)
            elif table_group_id:
                Reservation.assign_tables(g.db, new_reservation['id'], table_group_id=table_group_id)
            
            # Email bildirimi gönder (opsiyonel)
            if form_data['email']:
                try:
                    reservation_details = {
                        'id': new_reservation['id'],
                        'date': reservation_date.strftime('%d.%m.%Y'),
                        'time': start_time.strftime('%H:%M'),
                        'party_size': party_size,
                        'table': get_table_names_for_reservation(g.db, new_reservation['id'])
                    }
                    
                    email_service.send_reservation_confirmation(
                        form_data['email'], form_data['customer_name'], reservation_details
                    )
                except Exception as e:
                    logger.warning(f"Email gönderilemedi: {e}")
                    # Email hatası rezervasyon oluşturmasını engellemez
            
            flash('Rezervasyon başarıyla oluşturuldu.', 'success')
            logger.info(f"New reservation created by {current_user.username}: ID {new_reservation['id']}")
            return redirect(url_for('reservations.index'))
            
        except ValueError as e:
            flash(f'Geçersiz veri formatı: {e}', 'error')
            logger.warning(f"Invalid data format in reservation creation: {e}")
        except Exception as e:
            flash('Rezervasyon oluşturulurken hata oluştu.', 'error')
            logger.error(f"Error creating reservation: {e}")
    
    # GET isteği için varsayılan değerler
    today = datetime.date.today()
    default_time = datetime.time(19, 0)
    
    return render_template('reservations/new.html', 
                          default_date=today, 
                          default_time=default_time,
                          default_duration=2,
                          form_data={})

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
@rate_limit_decorator("10 per minute")
def edit(id):
    """Rezervasyon düzenleme - validation ve logging ile"""
    try:
        db = g.db
        reservation = Reservation.get_by_id(db, id)
        
        if not reservation:
            flash('Rezervasyon bulunamadı.', 'error')
            return redirect(url_for('reservations.index'))
        
        if request.method == 'POST':
            # Form verilerini al ve temizle
            form_data = {
                'customer_name': validation_service.sanitize_input(request.form.get('customer_name', '')),
                'phone': validation_service.sanitize_input(request.form.get('phone', '')),
                'email': validation_service.sanitize_input(request.form.get('email', '')),
                'party_size': request.form.get('party_size', 0),
                'reservation_date': request.form.get('reservation_date', ''),
                'start_time': request.form.get('start_time', ''),
                'duration': request.form.get('duration', 2),
                'special_requests': validation_service.sanitize_input(request.form.get('special_requests', '')),
                'status': request.form.get('status', 'pending'),
                'arrival_status': request.form.get('arrival_status')
            }
            
            # Validation
            is_valid, validation_errors = validation_service.validate_reservation_data(form_data)
            
            if not is_valid:
                for error in validation_errors:
                    flash(error, 'error')
                return render_template('reservations/edit.html', 
                                     reservation=reservation,
                                     form_data=form_data)
            
            # Tarih ve saat çevirileri
            party_size = int(form_data['party_size'])
            reservation_date = datetime.date.fromisoformat(form_data['reservation_date'])
            start_time = datetime.time.fromisoformat(form_data['start_time'])
            duration = int(form_data['duration'])
            status = form_data['status']
            
            # Bitiş saatini hesapla
            start_datetime = datetime.datetime.combine(reservation_date, start_time)
            end_datetime = start_datetime + datetime.timedelta(hours=duration)
            end_time = end_datetime.time()
            
            # Masa seçimi (iptal edilenler hariç)
            table_ids = request.form.getlist('table_id')
            table_group_id = request.form.get('table_group_id')
            
            if status != 'cancelled' and not table_ids and not table_group_id:
                flash('En az bir masa veya masa grubu seçilmelidir.', 'error')
                return render_template('reservations/edit.html', reservation=reservation)
            
            # Müsaitlik kontrolü (iptal edilenler ve mevcut rezervasyon hariç)
            if status != 'cancelled':
                availability_error = check_table_availability(
                    db, table_ids, table_group_id, reservation_date, 
                    start_time, end_time, party_size, exclude_res_id=id
                )
                
                if availability_error:
                    flash(availability_error, 'error')
                    return render_template('reservations/edit.html', reservation=reservation)
            
            # Müşteri kontrolü
            customer_id = handle_customer_creation(
                db, form_data['customer_name'], form_data['phone'], form_data['email']
            )
            
            # Rezervasyonu güncelle
            Reservation.update(
                db, id, customer_id=customer_id, customer_name=form_data['customer_name'],
                phone=form_data['phone'], email=form_data['email'], party_size=party_size,
                reservation_date=reservation_date, start_time=start_time,
                end_time=end_time, special_requests=form_data['special_requests'],
                status=status, arrival_status=form_data['arrival_status']
            )
            
            # Masa atama (iptal edilenler hariç)
            if status != 'cancelled':
                if table_ids:
                    Reservation.assign_tables(db, id, table_ids=table_ids)
                elif table_group_id:
                    Reservation.assign_tables(db, id, table_group_id=table_group_id)
            
            flash('Rezervasyon başarıyla güncellendi.', 'success')
            logger.info(f"Reservation {id} updated by {current_user.username}")
            return redirect(url_for('reservations.index'))
        
        # GET isteği - mevcut verileri yükle
        assigned_tables = Reservation.get_tables_for_reservation(db, id)
        
        # Rezervasyon süresi hesapla
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
                              
    except Exception as e:
        logger.error(f"Error editing reservation {id}: {e}")
        flash('Rezervasyon düzenleme sırasında hata oluştu.', 'error')
        return redirect(url_for('reservations.index'))

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Rezervasyon silme - logging ile"""
    try:
        db = g.db
        reservation = Reservation.get_by_id(db, id)
        
        if not reservation:
            flash('Rezervasyon bulunamadı.', 'error')
            return redirect(url_for('reservations.index'))
        
        Reservation.delete(db, id)
        
        flash('Rezervasyon başarıyla silindi.', 'success')
        logger.info(f"Reservation {id} deleted by {current_user.username}")
        
    except Exception as e:
        logger.error(f"Error deleting reservation {id}: {e}")
        flash('Rezervasyon silme sırasında hata oluştu.', 'error')
        
    return redirect(url_for('reservations.index'))

@bp.route('/<int:id>/confirm-arrival', methods=('POST',))
@login_required
def confirm_arrival(id):
    """Müşteri gelişi onaylama"""
    try:
        db = g.db
        reservation = Reservation.get_by_id(db, id)
        
        if not reservation:
            flash('Rezervasyon bulunamadı.', 'error')
        else:
            Reservation.confirm_arrival(db, id)
            flash('Müşteri gelişi başarıyla onaylanıyor.', 'success')
            logger.info(f"Arrival confirmed for reservation {id} by {current_user.username}")
            
    except Exception as e:
        logger.error(f"Error confirming arrival for reservation {id}: {e}")
        flash('Geliş onaylama sırasında hata oluştu.', 'error')
        
    return redirect(url_for('reservations.index'))

@bp.route('/<int:id>/confirm-no-show', methods=('POST',))
@login_required
def confirm_no_show(id):
    """Müşteri gelmedi olarak işaretleme"""
    try:
        db = g.db
        reservation = Reservation.get_by_id(db, id)
        
        if not reservation:
            flash('Rezervasyon bulunamadı.', 'error')
        else:
            Reservation.confirm_no_show(db, id)
            flash('Müşteri gelmedi olarak işaretlendi.', 'success')
            logger.info(f"No-show confirmed for reservation {id} by {current_user.username}")
            
    except Exception as e:
        logger.error(f"Error confirming no-show for reservation {id}: {e}")
        flash('No-show işaretleme sırasında hata oluştu.', 'error')
        
    return redirect(url_for('reservations.index'))

@bp.route('/<int:id>/cancel', methods=('POST',))
@login_required
def cancel(id):
    """Rezervasyon iptal etme"""
    try:
        db = g.db
        reservation = Reservation.get_by_id(db, id)
        
        if not reservation:
            flash('Rezervasyon bulunamadı.', 'error')
        else:
            Reservation.cancel(db, id)
            flash('Rezervasyon başarıyla iptal edildi.', 'success')
            logger.info(f"Reservation {id} cancelled by {current_user.username}")
            
    except Exception as e:
        logger.error(f"Error cancelling reservation {id}: {e}")
        flash('Rezervasyon iptal etme sırasında hata oluştu.', 'error')
        
    return redirect(url_for('reservations.index'))

# API Endpoints
@bp.route('/api/availability', methods=['GET'])
@login_required
def api_availability():
    """Masa müsaitlik durumu API"""
    try:
        date_str = request.args.get('date')
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        party_size = request.args.get('party_size', type=int)
        
        if not all([date_str, start_time_str, end_time_str, party_size]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        date = datetime.date.fromisoformat(date_str)
        start_time = datetime.time.fromisoformat(start_time_str)
        end_time = datetime.time.fromisoformat(end_time_str)
        
        db = g.db
        available_tables = Table.get_available_tables(db, date, start_time, end_time, party_size)
        available_groups = TableGroup.get_available_groups(db, date, start_time, end_time, party_size)
        
        return jsonify({
            'available_tables': [dict(table) for table in available_tables] if available_tables else [],
            'available_groups': [dict(group) for group in available_groups] if available_groups else []
        })
        
    except Exception as e:
        logger.error(f"API availability error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Yardımcı fonksiyonlar
def check_table_availability(db, table_ids: List[str], table_group_id: Optional[str], 
                           reservation_date, start_time, end_time, party_size: int,
                           exclude_res_id: Optional[int] = None) -> Optional[str]:
    """Masa müsaitlik kontrolü"""
    try:
        if table_ids:
            for table_id in table_ids:
                available_tables = Table.get_available_tables(
                    db, reservation_date, start_time, end_time, 1, exclude_res_id=exclude_res_id
                )
                available_table_ids = [t['id'] for t in available_tables] if available_tables else []
                
                if int(table_id) not in available_table_ids:
                    return 'Seçilen masalardan biri belirtilen zaman aralığında müsait değil.'
        
        if table_group_id:
            available_groups = TableGroup.get_available_groups(
                db, reservation_date, start_time, end_time, party_size, exclude_res_id=exclude_res_id
            )
            available_group_ids = [g['id'] for g in available_groups] if available_groups else []
            
            if int(table_group_id) not in available_group_ids:
                return 'Seçilen masa grubu belirtilen zaman aralığında müsait değil.'
        
        return None
        
    except Exception as e:
        logger.error(f"Error checking table availability: {e}")
        return 'Müsaitlik kontrolü sırasında hata oluştu.'

def handle_customer_creation(db, customer_name: str, phone: str, email: str) -> Optional[int]:
    """Müşteri kaydı kontrolü ve oluşturma"""
    try:
        customer = Customer.get_by_phone(db, phone)
        
        if customer:
            return customer.id
        else:
            new_customer = Customer.create(db, customer_name, phone, email)
            return new_customer['id'] if new_customer else None
            
    except Exception as e:
        logger.error(f"Error handling customer creation: {e}")
        return None

def get_table_names_for_reservation(db, reservation_id: int) -> str:
    """Rezervasyon için masa isimlerini al"""
    try:
        tables = Reservation.get_tables_for_reservation(db, reservation_id)
        if tables:
            return ', '.join([table['name'] for table in tables])
        return 'Masa belirtilmemiş'
        
    except Exception as e:
        logger.error(f"Error getting table names for reservation {reservation_id}: {e}")
        return 'Bilinmeyen masa'