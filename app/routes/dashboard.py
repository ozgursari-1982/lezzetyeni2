from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from flask_login import login_required
import datetime

from ..models.reservation import Reservation
from ..models.table import Table
from ..models.table_group import TableGroup

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
@login_required
def index():
    db = g.db
    today = datetime.date.today()
    
    # Bugünkü bekleyen rezervasyonlar
    pending_reservations = db.execute(
        '''
        SELECT r.*, c.name as customer_name 
        FROM reservations r
        LEFT JOIN customers c ON r.customer_id = c.id
        WHERE r.reservation_date = ? AND r.status = 'pending'
        ORDER BY r.start_time
        ''',
        (today,)
    ).fetchall()
    
    # İçerideki misafirler
    current_guests = db.execute(
        '''
        SELECT r.*, c.name as customer_name 
        FROM reservations r
        LEFT JOIN customers c ON r.customer_id = c.id
        WHERE r.reservation_date = ? AND r.status = 'completed' AND r.arrival_status = 'arrived'
        ORDER BY r.start_time
        ''',
        (today,)
    ).fetchall()
    
    # Gelmeyen müşteriler
    no_shows = db.execute(
        '''
        SELECT r.*, c.name as customer_name 
        FROM reservations r
        LEFT JOIN customers c ON r.customer_id = c.id
        WHERE r.reservation_date = ? AND r.status = 'cancelled' AND r.arrival_status = 'no-show'
        ORDER BY r.start_time
        ''',
        (today,)
    ).fetchall()
    
    # Widget verileri
    # Bekleyen rezervasyon sayısı
    pending_count = len(pending_reservations)
    
    # İçerideki toplam misafir sayısı
    guest_count = sum(r['party_size'] for r in current_guests)
    
    # Boş masa sayısı
    empty_tables = db.execute(
        "SELECT COUNT(*) as count FROM tables WHERE status = 'empty' AND is_active = 1"
    ).fetchone()['count']
    
    # Dolu/rezerve masa sayısı
    occupied_tables = db.execute(
        "SELECT COUNT(*) as count FROM tables WHERE status IN ('occupied', 'reserved') AND is_active = 1"
    ).fetchone()['count']
    
    # Gelmeyen rezervasyon sayısı
    no_show_count = len(no_shows)
    
    # Seçilen tarih (varsayılan: bugün)
    selected_date = request.args.get('date', today.isoformat())
    try:
        selected_date = datetime.date.fromisoformat(selected_date)
    except ValueError:
        selected_date = today
    
    # Seçilen tarihe göre rezervasyonları güncelle
    if selected_date != today:
        pending_reservations = db.execute(
            '''
            SELECT r.*, c.name as customer_name 
            FROM reservations r
            LEFT JOIN customers c ON r.customer_id = c.id
            WHERE r.reservation_date = ? AND r.status = 'pending'
            ORDER BY r.start_time
            ''',
            (selected_date,)
        ).fetchall()
        
        current_guests = db.execute(
            '''
            SELECT r.*, c.name as customer_name 
            FROM reservations r
            LEFT JOIN customers c ON r.customer_id = c.id
            WHERE r.reservation_date = ? AND r.status = 'completed' AND r.arrival_status = 'arrived'
            ORDER BY r.start_time
            ''',
            (selected_date,)
        ).fetchall()
        
        no_shows = db.execute(
            '''
            SELECT r.*, c.name as customer_name 
            FROM reservations r
            LEFT JOIN customers c ON r.customer_id = c.id
            WHERE r.reservation_date = ? AND r.status = 'cancelled' AND r.arrival_status = 'no-show'
            ORDER BY r.start_time
            ''',
            (selected_date,)
        ).fetchall()
    
    return render_template('dashboard/index.html',
                          pending_reservations=pending_reservations,
                          current_guests=current_guests,
                          no_shows=no_shows,
                          pending_count=pending_count,
                          guest_count=guest_count,
                          empty_tables=empty_tables,
                          occupied_tables=occupied_tables,
                          no_show_count=no_show_count,
                          today=today,
                          selected_date=selected_date)
