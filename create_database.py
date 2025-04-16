import os
import sqlite3
from app import create_app
from werkzeug.security import generate_password_hash

# Veritabanı dosyasının yolu
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'restaurant.sqlite')

# Veritabanı şeması
SCHEMA = [
    '''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
    ''',
    '''
    CREATE TABLE tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        capacity INTEGER NOT NULL,
        type TEXT NOT NULL,
        x_position FLOAT DEFAULT 0,
        y_position FLOAT DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        status TEXT DEFAULT 'empty'
    )
    ''',
    '''
    CREATE TABLE table_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    ''',
    '''
    CREATE TABLE table_group_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        table_id INTEGER NOT NULL,
        FOREIGN KEY (group_id) REFERENCES table_groups (id),
        FOREIGN KEY (table_id) REFERENCES tables (id)
    )
    ''',
    '''
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_visit_date TIMESTAMP,
        total_visits INTEGER DEFAULT 0,
        notes TEXT
    )
    ''',
    '''
    CREATE TABLE reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        customer_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        party_size INTEGER NOT NULL,
        reservation_date DATE NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME NOT NULL,
        special_requests TEXT,
        status TEXT DEFAULT 'pending',
        arrival_status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    ''',
    '''
    CREATE TABLE reservation_tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reservation_id INTEGER NOT NULL,
        table_id INTEGER,
        table_group_id INTEGER,
        FOREIGN KEY (reservation_id) REFERENCES reservations (id),
        FOREIGN KEY (table_id) REFERENCES tables (id),
        FOREIGN KEY (table_group_id) REFERENCES table_groups (id),
        CHECK ((table_id IS NULL AND table_group_id IS NOT NULL) OR (table_id IS NOT NULL AND table_group_id IS NULL))
    )
    ''',
    '''
    CREATE TABLE no_show_customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reservation_id INTEGER NOT NULL,
        customer_id INTEGER,
        customer_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        reservation_date DATE NOT NULL,
        start_time TIME NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (reservation_id) REFERENCES reservations (id),
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    '''
]

# Örnek veriler
SAMPLE_DATA = [
    # Kullanıcılar
    "INSERT INTO users (username, password) VALUES ('admin', ?)",
    
    # Masalar
    "INSERT INTO tables (name, capacity, type, x_position, y_position) VALUES ('Masa 1', 2, 'kare', 50, 50)",
    "INSERT INTO tables (name, capacity, type, x_position, y_position) VALUES ('Masa 2', 2, 'kare', 200, 50)",
    "INSERT INTO tables (name, capacity, type, x_position, y_position) VALUES ('Masa 3', 4, 'kare', 350, 50)",
    "INSERT INTO tables (name, capacity, type, x_position, y_position) VALUES ('Masa 4', 4, 'kare', 500, 50)",
    "INSERT INTO tables (name, capacity, type, x_position, y_position) VALUES ('Masa 5', 6, 'dikdörtgen', 50, 200)",
    "INSERT INTO tables (name, capacity, type, x_position, y_position) VALUES ('Masa 6', 6, 'dikdörtgen', 250, 200)",
    "INSERT INTO tables (name, capacity, type, x_position, y_position) VALUES ('Masa 7', 8, 'dikdörtgen', 450, 200)",
    "INSERT INTO tables (name, capacity, type, x_position, y_position) VALUES ('Masa 8', 2, 'yuvarlak', 50, 350)",
    "INSERT INTO tables (name, capacity, type, x_position, y_position) VALUES ('Masa 9', 2, 'yuvarlak', 200, 350)",
    "INSERT INTO tables (name, capacity, type, x_position, y_position) VALUES ('Masa 10', 4, 'yuvarlak', 350, 350)",
    
    # Müşteriler
    "INSERT INTO customers (name, phone, email, total_visits) VALUES ('Ahmet Yılmaz', '05551234567', 'ahmet@example.com', 3)",
    "INSERT INTO customers (name, phone, email, total_visits) VALUES ('Ayşe Demir', '05559876543', 'ayse@example.com', 1)",
    "INSERT INTO customers (name, phone, email, total_visits) VALUES ('Mehmet Kaya', '05553456789', 'mehmet@example.com', 2)",
    "INSERT INTO customers (name, phone, email, total_visits) VALUES ('Fatma Şahin', '05557654321', 'fatma@example.com', 0)"
]

def init_db():
    """Veritabanını oluştur ve örnek verileri ekle."""
    # Instance klasörünü oluştur
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Eğer veritabanı dosyası varsa sil
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    # Veritabanı bağlantısı oluştur
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Şemayı oluştur
    for query in SCHEMA:
        conn.execute(query)
    
    # Örnek verileri ekle
    admin_password = generate_password_hash('admin123')
    conn.execute(SAMPLE_DATA[0], (admin_password,))
    
    for query in SAMPLE_DATA[1:]:
        conn.execute(query)
    
    conn.commit()
    conn.close()
    
    print(f"Veritabanı başarıyla oluşturuldu: {DB_PATH}")

if __name__ == '__main__':
    init_db()
