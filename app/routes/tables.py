from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from flask_login import login_required, current_user
import datetime

from ..models.table import Table
from ..models.table_group import TableGroup
from ..models.reservation import Reservation

bp = Blueprint('tables', __name__, url_prefix='/tables')

@bp.route('/')
@login_required
def index():
    db = g.db
    tables = Table.get_all(db)
    return render_template('tables/index.html', tables=tables)

@bp.route('/<int:table_id>')
@login_required
def detail(table_id):
    db = g.db
    table = Table.get_by_id(db, table_id)
    
    if not table:
        flash('Masa bulunamadı.', 'error')
        return redirect(url_for('tables.index'))
    
    # Bugünkü rezervasyonları al
    today = datetime.date.today()
    reservations = db.execute(
        '''
        SELECT r.* 
        FROM reservations r
        JOIN reservation_tables rt ON r.id = rt.reservation_id
        WHERE rt.table_id = ? AND r.reservation_date = ? AND r.status != 'cancelled'
        ORDER BY r.start_time
        ''',
        (table_id, today)
    ).fetchall()
    
    return render_template('tables/detail.html', table=table, reservations=reservations)

@bp.route('/<int:table_id>/clear', methods=['POST'])
@login_required
def clear_table(table_id):
    db = g.db
    table = Table.get_by_id(db, table_id)
    
    if not table:
        flash('Masa bulunamadı.', 'error')
        return redirect(url_for('tables.index'))
    
    # Masanın durumunu güncelle
    Table.update(db, table_id, status='empty')
    
    # İlişkili aktif rezervasyonu bul ve bitiş saatini güncelle
    reservation = db.execute(
        '''
        SELECT r.* 
        FROM reservations r
        JOIN reservation_tables rt ON r.id = rt.reservation_id
        WHERE rt.table_id = ? AND r.status = 'completed' AND r.arrival_status = 'arrived'
        AND r.reservation_date = CURRENT_DATE
        ''',
        (table_id,)
    ).fetchone()
    
    if reservation:
        # Bitiş saatini şu anki saat olarak güncelle
        now = datetime.datetime.now().time()
        Reservation.update(db, reservation['id'], end_time=now)
    
    flash('Masa başarıyla boşaltıldı.', 'success')
    return redirect(url_for('tables.index'))

@bp.route('/management')
@login_required
def management():
    db = g.db
    tables = Table.get_all(db)
    table_groups = TableGroup.get_all(db)
    
    return render_template('tables/management.html', tables=tables, table_groups=table_groups)

@bp.route('/availability-schedule')
@login_required
def availability_schedule():
    db = g.db
    date_str = request.args.get('date', datetime.date.today().isoformat())
    
    try:
        selected_date = datetime.date.fromisoformat(date_str)
    except ValueError:
        selected_date = datetime.date.today()
    
    tables = Table.get_all(db)
    
    # Saat dilimleri (12:00 - 23:00, yarım saatlik dilimler)
    time_slots = []
    start = datetime.time(12, 0)
    for i in range(23):
        hour = (start.hour + i // 2) % 24
        minute = (start.minute + (i % 2) * 30) % 60
        time_slots.append(datetime.time(hour, minute))
    
    # Her masa için müsaitlik durumunu al
    schedule_data = {}
    for table in tables:
        schedule_data[table['id']] = {}
        for time_slot in time_slots:
            # Varsayılan olarak müsait
            schedule_data[table['id']][time_slot.isoformat()] = 'available'
    
    # Rezervasyonları al ve çizelgeyi güncelle
    reservations = db.execute(
        '''
        SELECT r.*, rt.table_id, rt.table_group_id
        FROM reservations r
        JOIN reservation_tables rt ON r.id = rt.reservation_id
        WHERE r.reservation_date = ? AND r.status != 'cancelled'
        ''',
        (selected_date,)
    ).fetchall()
    
    for reservation in reservations:
        # Masa grubu ise, gruptaki tüm masaları işaretle
        if reservation['table_group_id']:
            tables_in_group = TableGroup.get_tables(db, reservation['table_group_id'])
            for table in tables_in_group:
                mark_reservation_in_schedule(schedule_data, table['id'], reservation, time_slots)
        # Tekil masa ise
        elif reservation['table_id']:
            mark_reservation_in_schedule(schedule_data, reservation['table_id'], reservation, time_slots)
    
    return render_template(
        'tables/availability_schedule.html', 
        tables=tables, 
        time_slots=time_slots, 
        schedule_data=schedule_data,
        selected_date=selected_date
    )

def mark_reservation_in_schedule(schedule_data, table_id, reservation, time_slots):
    start_time = reservation['start_time']
    end_time = reservation['end_time']
    
    for time_slot in time_slots:
        if start_time <= time_slot < end_time:
            if reservation['arrival_status'] == 'arrived':
                schedule_data[table_id][time_slot.isoformat()] = 'occupied'
            else:
                schedule_data[table_id][time_slot.isoformat()] = 'reserved'

# API Endpoints
@bp.route('/api/update-table-position', methods=['POST'])
@login_required
def api_update_table_position():
    db = g.db
    data = request.json
    
    if not data or 'table_id' not in data or 'x_position' not in data or 'y_position' not in data:
        return jsonify({'success': False, 'message': 'Geçersiz veri.'}), 400
    
    table_id = data['table_id']
    x_position = data['x_position']
    y_position = data['y_position']
    
    success = Table.update_position(db, table_id, x_position, y_position)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Masa konumu güncellenemedi.'}), 500

@bp.route('/api/add-table', methods=['POST'])
@login_required
def api_add_table():
    db = g.db
    data = request.json
    
    if not data or 'name' not in data or 'capacity' not in data or 'type' not in data:
        return jsonify({'success': False, 'message': 'Geçersiz veri.'}), 400
    
    name = data['name']
    capacity = data['capacity']
    type = data['type']
    x_position = data.get('x_position', 0)
    y_position = data.get('y_position', 0)
    
    # Masa adının benzersiz olup olmadığını kontrol et
    existing_table = db.execute('SELECT id FROM tables WHERE name = ?', (name,)).fetchone()
    if existing_table:
        return jsonify({'success': False, 'message': 'Bu isimde bir masa zaten var.'}), 400
    
    try:
        new_table = Table.create(db, name, capacity, type, x_position, y_position)
        return jsonify({'success': True, 'table': dict(new_table)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/merge-tables', methods=['POST'])
@login_required
def api_merge_tables():
    db = g.db
    data = request.json
    
    if not data or 'name' not in data or 'table_ids' not in data or not data['table_ids']:
        return jsonify({'success': False, 'message': 'Geçersiz veri.'}), 400
    
    name = data['name']
    table_ids = data['table_ids']
    
    # Masa grubunun toplam kapasitesini hesapla
    total_capacity = 0
    for table_id in table_ids:
        table = Table.get_by_id(db, table_id)
        if table:
            total_capacity += table['capacity']
    
    try:
        # Masa grubu oluştur
        new_group = TableGroup.create(db, name, total_capacity)
        
        # Masaları gruba ekle
        for table_id in table_ids:
            TableGroup.add_table(db, new_group['id'], table_id)
        
        return jsonify({'success': True, 'group': dict(new_group)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/split-table-group/<int:group_id>', methods=['POST'])
@login_required
def api_split_table_group(group_id):
    db = g.db
    
    try:
        success = TableGroup.split(db, group_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Masa grubu ayrılamadı.'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/check-availability', methods=['GET'])
@login_required
def api_check_availability():
    db = g.db
    date_str = request.args.get('date')
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    party_size = request.args.get('party_size', type=int)
    exclude_res_id = request.args.get('exclude_res_id', type=int)
    
    if not date_str or not start_time_str or not end_time_str or not party_size:
        return jsonify({'success': False, 'message': 'Eksik parametreler.'}), 400
    
    try:
        date = datetime.date.fromisoformat(date_str)
        start_time = datetime.time.fromisoformat(start_time_str)
        end_time = datetime.time.fromisoformat(end_time_str)
    except ValueError:
        return jsonify({'success': False, 'message': 'Geçersiz tarih veya saat formatı.'}), 400
    
    # Müsait masaları ve masa gruplarını bul
    available_tables = Table.get_available_tables(db, date, start_time, end_time, party_size, exclude_res_id)
    available_groups = TableGroup.get_available_groups(db, date, start_time, end_time, party_size, exclude_res_id)
    
    return jsonify({
        'success': True,
        'available_tables': [dict(table) for table in available_tables],
        'available_groups': [dict(group) for group in available_groups]
    })

@bp.route('/api/get-schedule', methods=['GET'])
@login_required
def api_get_schedule():
    db = g.db
    date_str = request.args.get('date', datetime.date.today().isoformat())
    
    try:
        selected_date = datetime.date.fromisoformat(date_str)
    except ValueError:
        return jsonify({'success': False, 'message': 'Geçersiz tarih formatı.'}), 400
    
    tables = Table.get_all(db)
    
    # Saat dilimleri (12:00 - 23:00, yarım saatlik dilimler)
    time_slots = []
    start = datetime.time(12, 0)
    for i in range(23):
        hour = (start.hour + i // 2) % 24
        minute = (start.minute + (i % 2) * 30) % 60
        time_slots.append(datetime.time(hour, minute).isoformat())
    
    # Her masa için müsaitlik durumunu al
    schedule_data = {}
    for table in tables:
        schedule_data[table['id']] = {time_slot: 'available' for time_slot in time_slots}
    
    # Rezervasyonları al ve çizelgeyi güncelle
    reservations = db.execute(
        '''
        SELECT r.*, rt.table_id, rt.table_group_id, c.name as customer_name
        FROM reservations r
        LEFT JOIN customers c ON r.customer_id = c.id
        JOIN reservation_tables rt ON r.id = rt.reservation_id
        WHERE r.reservation_date = ? AND r.status != 'cancelled'
        ''',
        (selected_date,)
    ).fetchall()
    
    reservation_data = {}
    for reservation in reservations:
        res_id = reservation['id']
        if res_id not in reservation_data:
            reservation_data[res_id] = {
                'id': res_id,
                'customer_name': reservation['customer_name'] or reservation['customer_name'],
                'party_size': reservation['party_size'],
                'start_time': reservation['start_time'].isoformat(),
                'end_time': reservation['end_time'].isoformat(),
                'status': reservation['status'],
                'arrival_status': reservation['arrival_status'],
                'tables': [],
                'table_group': None
            }
        
        # Masa grubu ise
        if reservation['table_group_id']:
            group = TableGroup.get_by_id(db, reservation['table_group_id'])
            if group:
                reservation_data[res_id]['table_group'] = dict(group)
                tables_in_group = TableGroup.get_tables(db, reservation['table_group_id'])
                for table in tables_in_group:
                    update_schedule_for_reservation(schedule_data, table['id'], reservation, time_slots)
        # Tekil masa ise
        elif reservation['table_id']:
            table = Table.get_by_id(db, reservation['table_id'])
            if table:
                reservation_data[res_id]['tables'].append(dict(table))
                update_schedule_for_reservation(schedule_data, reservation['table_id'], reservation, time_slots)
    
    return jsonify({
        'success': True,
        'schedule_data': schedule_data,
        'reservations': list(reservation_data.values()),
        'time_slots': time_slots
    })

def update_schedule_for_reservation(schedule_data, table_id, reservation, time_slots):
    start_time = reservation['start_time'].isoformat()
    end_time = reservation['end_time'].isoformat()
    
    for time_slot in time_slots:
        if start_time <= time_slot < end_time:
            status = 'reserved'
            if reservation['arrival_status'] == 'arrived':
                status = 'occupied'
            
            if table_id in schedule_data and time_slot in schedule_data[table_id]:
                schedule_data[table_id][time_slot] = {
                    'status': status,
                    'reservation_id': reservation['id']
                }
