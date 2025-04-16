class TableGroup:
    def __init__(self, id, name, capacity, created_at, is_active):
        self.id = id
        self.name = name
        self.capacity = capacity
        self.created_at = created_at
        self.is_active = is_active
    
    @staticmethod
    def get_all(db, active_only=True):
        query = 'SELECT * FROM table_groups'
        
        if active_only:
            query += ' WHERE is_active = 1'
        
        query += ' ORDER BY name'
        
        table_groups = db.execute(query).fetchall()
        return table_groups
    
    @staticmethod
    def get_by_id(db, group_id):
        table_group_data = db.execute(
            'SELECT * FROM table_groups WHERE id = ?',
            (group_id,)
        ).fetchone()
        
        if table_group_data:
            return TableGroup(
                table_group_data['id'],
                table_group_data['name'],
                table_group_data['capacity'],
                table_group_data['created_at'],
                table_group_data['is_active']
            )
        return None
    
    @staticmethod
    def create(db, name, capacity):
        db.execute(
            '''
            INSERT INTO table_groups (
                name, capacity, created_at, is_active
            ) VALUES (?, ?, CURRENT_TIMESTAMP, 1)
            ''',
            (name, capacity)
        )
        db.commit()
        
        # Son eklenen masa grubunu döndür
        return db.execute('SELECT * FROM table_groups WHERE id = last_insert_rowid()').fetchone()
    
    @staticmethod
    def update(db, group_id, name=None, capacity=None, is_active=None):
        # Güncellenecek alanları belirle
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        
        if capacity is not None:
            updates.append('capacity = ?')
            params.append(capacity)
        
        if is_active is not None:
            updates.append('is_active = ?')
            params.append(is_active)
        
        if not updates:
            return False
        
        # Güncelleme sorgusu oluştur
        query = f'UPDATE table_groups SET {", ".join(updates)} WHERE id = ?'
        params.append(group_id)
        
        db.execute(query, params)
        db.commit()
        return True
    
    @staticmethod
    def delete(db, group_id):
        # Fiziksel silme yerine is_active = 0 yaparak pasif hale getir
        db.execute(
            'UPDATE table_groups SET is_active = 0 WHERE id = ?',
            (group_id,)
        )
        db.commit()
        return True
    
    @staticmethod
    def add_table(db, group_id, table_id):
        # Masanın başka bir aktif gruba ait olup olmadığını kontrol et
        existing_group = db.execute(
            '''
            SELECT tgm.group_id 
            FROM table_group_members tgm
            JOIN table_groups tg ON tgm.group_id = tg.id
            WHERE tgm.table_id = ? AND tg.is_active = 1
            ''',
            (table_id,)
        ).fetchone()
        
        if existing_group:
            # Masa zaten başka bir gruba ait
            return False
        
        # Masayı gruba ekle
        db.execute(
            'INSERT INTO table_group_members (group_id, table_id) VALUES (?, ?)',
            (group_id, table_id)
        )
        
        # Grup kapasitesini güncelle
        db.execute(
            '''
            UPDATE table_groups 
            SET capacity = (
                SELECT SUM(t.capacity) 
                FROM tables t
                JOIN table_group_members tgm ON t.id = tgm.table_id
                WHERE tgm.group_id = ?
            )
            WHERE id = ?
            ''',
            (group_id, group_id)
        )
        
        db.commit()
        return True
    
    @staticmethod
    def remove_table(db, group_id, table_id):
        # Masayı gruptan çıkar
        db.execute(
            'DELETE FROM table_group_members WHERE group_id = ? AND table_id = ?',
            (group_id, table_id)
        )
        
        # Grup kapasitesini güncelle
        db.execute(
            '''
            UPDATE table_groups 
            SET capacity = (
                SELECT COALESCE(SUM(t.capacity), 0) 
                FROM tables t
                JOIN table_group_members tgm ON t.id = tgm.table_id
                WHERE tgm.group_id = ?
            )
            WHERE id = ?
            ''',
            (group_id, group_id)
        )
        
        db.commit()
        return True
    
    @staticmethod
    def get_tables(db, group_id):
        # Gruba ait masaları al
        tables = db.execute(
            '''
            SELECT t.* 
            FROM tables t
            JOIN table_group_members tgm ON t.id = tgm.table_id
            WHERE tgm.group_id = ?
            ORDER BY t.name
            ''',
            (group_id,)
        ).fetchall()
        
        return tables
    
    @staticmethod
    def split(db, group_id):
        # Grubu pasif hale getir
        db.execute(
            'UPDATE table_groups SET is_active = 0 WHERE id = ?',
            (group_id,)
        )
        
        # Grup üyeliklerini sil
        db.execute(
            'DELETE FROM table_group_members WHERE group_id = ?',
            (group_id,)
        )
        
        db.commit()
        return True
    
    @staticmethod
    def get_available_groups(db, date, start_time, end_time, party_size, exclude_res_id=None):
        # Belirli bir tarih ve saat aralığında müsait olan masa gruplarını bul
        query = '''
        SELECT tg.* FROM table_groups tg
        WHERE tg.is_active = 1
        AND tg.capacity >= ?
        AND tg.id NOT IN (
            SELECT rt.table_group_id FROM reservation_tables rt
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
