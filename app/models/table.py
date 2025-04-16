class Table:
    def __init__(self, id, name, capacity, type, x_position, y_position, is_active, status):
        self.id = id
        self.name = name
        self.capacity = capacity
        self.type = type
        self.x_position = x_position
        self.y_position = y_position
        self.is_active = is_active
        self.status = status
    
    @staticmethod
    def get_all(db):
        tables = db.execute(
            'SELECT * FROM tables WHERE is_active = 1 ORDER BY name'
        ).fetchall()
        return tables
    
    @staticmethod
    def get_by_id(db, table_id):
        table_data = db.execute(
            'SELECT * FROM tables WHERE id = ?',
            (table_id,)
        ).fetchone()
        if table_data:
            return Table(
                table_data['id'],
                table_data['name'],
                table_data['capacity'],
                table_data['type'],
                table_data['x_position'],
                table_data['y_position'],
                table_data['is_active'],
                table_data['status']
            )
        return None
    
    @staticmethod
    def create(db, name, capacity, type, x_position=0, y_position=0):
        db.execute(
            'INSERT INTO tables (name, capacity, type, x_position, y_position, is_active, status) VALUES (?, ?, ?, ?, ?, 1, "empty")',
            (name, capacity, type, x_position, y_position)
        )
        db.commit()
        
        # Son eklenen masayı döndür
        return db.execute('SELECT * FROM tables WHERE id = last_insert_rowid()').fetchone()
    
    @staticmethod
    def update(db, table_id, name=None, capacity=None, type=None, x_position=None, y_position=None, is_active=None, status=None):
        # Güncellenecek alanları belirle
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        
        if capacity is not None:
            updates.append('capacity = ?')
            params.append(capacity)
        
        if type is not None:
            updates.append('type = ?')
            params.append(type)
        
        if x_position is not None:
            updates.append('x_position = ?')
            params.append(x_position)
        
        if y_position is not None:
            updates.append('y_position = ?')
            params.append(y_position)
        
        if is_active is not None:
            updates.append('is_active = ?')
            params.append(is_active)
        
        if status is not None:
            updates.append('status = ?')
            params.append(status)
        
        if not updates:
            return False
        
        # Güncelleme sorgusu oluştur
        query = f'UPDATE tables SET {", ".join(updates)} WHERE id = ?'
        params.append(table_id)
        
        db.execute(query, params)
        db.commit()
        return True
    
    @staticmethod
    def delete(db, table_id):
        # Fiziksel silme yerine is_active = 0 yaparak pasif hale getir
        db.execute(
            'UPDATE tables SET is_active = 0 WHERE id = ?',
            (table_id,)
        )
        db.commit()
        return True
    
    @staticmethod
    def get_available_tables(db, date, start_time, end_time, party_size, exclude_res_id=None):
        # Belirli bir tarih ve saat aralığında müsait olan masaları bul
        query = '''
        SELECT t.* FROM tables t
        WHERE t.is_active = 1
        AND t.capacity >= ?
        AND t.id NOT IN (
            SELECT rt.table_id FROM reservation_tables rt
            JOIN reservations r ON rt.reservation_id = r.id
            WHERE r.reservation_date = ?
            AND r.status != 'cancelled'
            AND (
                (r.start_time < ? AND r.end_time > ?) OR
                (r.start_time < ? AND r.end_time > ?) OR
                (r.start_time >= ? AND r.end_time <= ?)
            )
        '''
        
        params = [party_size, date, end_time, start_time, start_time, start_time, start_time, end_time]
        
        if exclude_res_id:
            query += ' AND r.id != ?'
            params.append(exclude_res_id)
        
        query += ')'
        
        return db.execute(query, params).fetchall()
    
    @staticmethod
    def update_position(db, table_id, x_position, y_position):
        db.execute(
            'UPDATE tables SET x_position = ?, y_position = ? WHERE id = ?',
            (x_position, y_position, table_id)
        )
        db.commit()
        return True
