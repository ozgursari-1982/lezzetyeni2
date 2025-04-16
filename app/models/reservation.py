class Reservation:
    def __init__(self, id, customer_id, customer_name, phone, email, party_size, 
                 reservation_date, start_time, end_time, special_requests, 
                 status, arrival_status, created_at, updated_at):
        self.id = id
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.phone = phone
        self.email = email
        self.party_size = party_size
        self.reservation_date = reservation_date
        self.start_time = start_time
        self.end_time = end_time
        self.special_requests = special_requests
        self.status = status
        self.arrival_status = arrival_status
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def get_all(db, date=None, status=None):
        query = '''
        SELECT r.*, c.name as customer_name 
        FROM reservations r
        LEFT JOIN customers c ON r.customer_id = c.id
        WHERE 1=1
        '''
        params = []
        
        if date:
            query += ' AND r.reservation_date = ?'
            params.append(date)
        
        if status:
            query += ' AND r.status = ?'
            params.append(status)
        
        query += ' ORDER BY r.reservation_date, r.start_time'
        
        return db.execute(query, params).fetchall()
    
    @staticmethod
    def get_by_id(db, reservation_id):
        reservation_data = db.execute(
            '''
            SELECT r.*, c.name as customer_name 
            FROM reservations r
            LEFT JOIN customers c ON r.customer_id = c.id
            WHERE r.id = ?
            ''',
            (reservation_id,)
        ).fetchone()
        
        if reservation_data:
            return Reservation(
                reservation_data['id'],
                reservation_data['customer_id'],
                reservation_data['customer_name'],
                reservation_data['phone'],
                reservation_data['email'],
                reservation_data['party_size'],
                reservation_data['reservation_date'],
                reservation_data['start_time'],
                reservation_data['end_time'],
                reservation_data['special_requests'],
                reservation_data['status'],
                reservation_data['arrival_status'],
                reservation_data['created_at'],
                reservation_data['updated_at']
            )
        return None
    
    @staticmethod
    def create(db, customer_id, customer_name, phone, email, party_size, 
               reservation_date, start_time, end_time, special_requests=None):
        # Rezervasyon oluştur
        db.execute(
            '''
            INSERT INTO reservations (
                customer_id, customer_name, phone, email, party_size, 
                reservation_date, start_time, end_time, special_requests, 
                status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''',
            (customer_id, customer_name, phone, email, party_size, 
             reservation_date, start_time, end_time, special_requests)
        )
        db.commit()
        
        # Son eklenen rezervasyonu döndür
        return db.execute('SELECT * FROM reservations WHERE id = last_insert_rowid()').fetchone()
    
    @staticmethod
    def update(db, reservation_id, customer_id=None, customer_name=None, phone=None, 
               email=None, party_size=None, reservation_date=None, start_time=None, 
               end_time=None, special_requests=None, status=None, arrival_status=None):
        # Güncellenecek alanları belirle
        updates = []
        params = []
        
        if customer_id is not None:
            updates.append('customer_id = ?')
            params.append(customer_id)
        
        if customer_name is not None:
            updates.append('customer_name = ?')
            params.append(customer_name)
        
        if phone is not None:
            updates.append('phone = ?')
            params.append(phone)
        
        if email is not None:
            updates.append('email = ?')
            params.append(email)
        
        if party_size is not None:
            updates.append('party_size = ?')
            params.append(party_size)
        
        if reservation_date is not None:
            updates.append('reservation_date = ?')
            params.append(reservation_date)
        
        if start_time is not None:
            updates.append('start_time = ?')
            params.append(start_time)
        
        if end_time is not None:
            updates.append('end_time = ?')
            params.append(end_time)
        
        if special_requests is not None:
            updates.append('special_requests = ?')
            params.append(special_requests)
        
        if status is not None:
            updates.append('status = ?')
            params.append(status)
        
        if arrival_status is not None:
            updates.append('arrival_status = ?')
            params.append(arrival_status)
        
        if not updates:
            return False
        
        # updated_at alanını güncelle
        updates.append('updated_at = CURRENT_TIMESTAMP')
        
        # Güncelleme sorgusu oluştur
        query = f'UPDATE reservations SET {", ".join(updates)} WHERE id = ?'
        params.append(reservation_id)
        
        db.execute(query, params)
        db.commit()
        return True
    
    @staticmethod
    def delete(db, reservation_id):
        # İlişkili kayıtları sil
        db.execute('DELETE FROM reservation_tables WHERE reservation_id = ?', (reservation_id,))
        db.execute('DELETE FROM no_show_customers WHERE reservation_id = ?', (reservation_id,))
        
        # Rezervasyonu sil
        db.execute('DELETE FROM reservations WHERE id = ?', (reservation_id,))
        db.commit()
        return True
    
    @staticmethod
    def assign_tables(db, reservation_id, table_ids=None, table_group_id=None):
        # Önce mevcut masa atamalarını temizle
        db.execute('DELETE FROM reservation_tables WHERE reservation_id = ?', (reservation_id,))
        
        # Masa veya masa grubu ata
        if table_ids:
            for table_id in table_ids:
                db.execute(
                    'INSERT INTO reservation_tables (reservation_id, table_id) VALUES (?, ?)',
                    (reservation_id, table_id)
                )
        elif table_group_id:
            db.execute(
                'INSERT INTO reservation_tables (reservation_id, table_group_id) VALUES (?, ?)',
                (reservation_id, table_group_id)
            )
        
        db.commit()
        return True
    
    @staticmethod
    def confirm_arrival(db, reservation_id):
        # Rezervasyon durumunu güncelle
        db.execute(
            '''
            UPDATE reservations 
            SET status = 'completed', arrival_status = 'arrived', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            ''',
            (reservation_id,)
        )
        
        # İlişkili masaların durumunu güncelle
        db.execute(
            '''
            UPDATE tables 
            SET status = 'occupied' 
            WHERE id IN (
                SELECT table_id FROM reservation_tables WHERE reservation_id = ?
            )
            ''',
            (reservation_id,)
        )
        
        # Müşterinin ziyaret sayısını artır
        db.execute(
            '''
            UPDATE customers 
            SET total_visits = total_visits + 1, last_visit_date = CURRENT_TIMESTAMP 
            WHERE id = (
                SELECT customer_id FROM reservations WHERE id = ?
            )
            ''',
            (reservation_id,)
        )
        
        db.commit()
        return True
    
    @staticmethod
    def confirm_no_show(db, reservation_id):
        # Rezervasyon bilgilerini al
        reservation = db.execute('SELECT * FROM reservations WHERE id = ?', (reservation_id,)).fetchone()
        
        if not reservation:
            return False
        
        # Rezervasyon durumunu güncelle
        db.execute(
            '''
            UPDATE reservations 
            SET status = 'cancelled', arrival_status = 'no-show', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            ''',
            (reservation_id,)
        )
        
        # no_show_customers tablosuna kayıt ekle
        db.execute(
            '''
            INSERT INTO no_show_customers (
                reservation_id, customer_id, customer_name, phone, email, 
                reservation_date, start_time, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''',
            (
                reservation_id, 
                reservation['customer_id'], 
                reservation['customer_name'], 
                reservation['phone'], 
                reservation['email'], 
                reservation['reservation_date'], 
                reservation['start_time']
            )
        )
        
        db.commit()
        return True
    
    @staticmethod
    def cancel(db, reservation_id):
        # Rezervasyon durumunu güncelle
        db.execute(
            '''
            UPDATE reservations 
            SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            ''',
            (reservation_id,)
        )
        
        db.commit()
        return True
    
    @staticmethod
    def get_tables_for_reservation(db, reservation_id):
        # Rezervasyona atanan masaları veya masa grubunu al
        tables = db.execute(
            '''
            SELECT t.* 
            FROM tables t
            JOIN reservation_tables rt ON t.id = rt.table_id
            WHERE rt.reservation_id = ?
            ''',
            (reservation_id,)
        ).fetchall()
        
        table_group = db.execute(
            '''
            SELECT tg.* 
            FROM table_groups tg
            JOIN reservation_tables rt ON tg.id = rt.table_group_id
            WHERE rt.reservation_id = ?
            ''',
            (reservation_id,)
        ).fetchone()
        
        return {
            'tables': tables,
            'table_group': table_group
        }
