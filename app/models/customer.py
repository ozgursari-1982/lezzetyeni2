class Customer:
    def __init__(self, id, name, phone, email, created_at, last_visit_date, total_visits, notes):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.created_at = created_at
        self.last_visit_date = last_visit_date
        self.total_visits = total_visits
        self.notes = notes
    
    @staticmethod
    def get_all(db):
        customers = db.execute(
            'SELECT * FROM customers ORDER BY name'
        ).fetchall()
        return customers
    
    @staticmethod
    def get_by_id(db, customer_id):
        customer_data = db.execute(
            'SELECT * FROM customers WHERE id = ?',
            (customer_id,)
        ).fetchone()
        
        if customer_data:
            return Customer(
                customer_data['id'],
                customer_data['name'],
                customer_data['phone'],
                customer_data['email'],
                customer_data['created_at'],
                customer_data['last_visit_date'],
                customer_data['total_visits'],
                customer_data['notes']
            )
        return None
    
    @staticmethod
    def get_by_phone(db, phone):
        customer_data = db.execute(
            'SELECT * FROM customers WHERE phone = ?',
            (phone,)
        ).fetchone()
        
        if customer_data:
            return Customer(
                customer_data['id'],
                customer_data['name'],
                customer_data['phone'],
                customer_data['email'],
                customer_data['created_at'],
                customer_data['last_visit_date'],
                customer_data['total_visits'],
                customer_data['notes']
            )
        return None
    
    @staticmethod
    def create(db, name, phone, email=None, notes=None):
        db.execute(
            '''
            INSERT INTO customers (
                name, phone, email, created_at, total_visits, notes
            ) VALUES (?, ?, ?, CURRENT_TIMESTAMP, 0, ?)
            ''',
            (name, phone, email, notes)
        )
        db.commit()
        
        # Son eklenen müşteriyi döndür
        return db.execute('SELECT * FROM customers WHERE id = last_insert_rowid()').fetchone()
    
    @staticmethod
    def update(db, customer_id, name=None, phone=None, email=None, notes=None):
        # Güncellenecek alanları belirle
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        
        if phone is not None:
            updates.append('phone = ?')
            params.append(phone)
        
        if email is not None:
            updates.append('email = ?')
            params.append(email)
        
        if notes is not None:
            updates.append('notes = ?')
            params.append(notes)
        
        if not updates:
            return False
        
        # Güncelleme sorgusu oluştur
        query = f'UPDATE customers SET {", ".join(updates)} WHERE id = ?'
        params.append(customer_id)
        
        db.execute(query, params)
        db.commit()
        return True
    
    @staticmethod
    def delete(db, customer_id):
        # Müşterinin rezervasyonlarını kontrol et
        reservations = db.execute(
            'SELECT id FROM reservations WHERE customer_id = ?',
            (customer_id,)
        ).fetchall()
        
        if reservations:
            # Rezervasyonları olan müşteri silinemez
            return False
        
        # Müşteriyi sil
        db.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
        db.commit()
        return True
    
    @staticmethod
    def get_no_shows(db):
        no_shows = db.execute(
            '''
            SELECT nsc.*, c.total_visits 
            FROM no_show_customers nsc
            LEFT JOIN customers c ON nsc.customer_id = c.id
            ORDER BY nsc.reservation_date DESC, nsc.start_time DESC
            '''
        ).fetchall()
        return no_shows
