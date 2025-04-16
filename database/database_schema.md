# Veritabanı Şeması

Bu dosya, restoran rezervasyon ve masa yönetimi sistemi için gerekli veritabanı tablolarını ve ilişkilerini tanımlar.

## Tablolar

### users
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `username` TEXT NOT NULL UNIQUE
- `password` TEXT NOT NULL
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `last_login` TIMESTAMP

### tables
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `name` TEXT NOT NULL UNIQUE
- `capacity` INTEGER NOT NULL
- `type` TEXT NOT NULL  -- ('kare', 'yuvarlak', 'diğer')
- `x_position` FLOAT DEFAULT 0
- `y_position` FLOAT DEFAULT 0
- `is_active` BOOLEAN DEFAULT 1
- `status` TEXT DEFAULT 'empty'  -- ('empty', 'occupied', 'reserved', 'available')

### table_groups
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `name` TEXT NOT NULL
- `capacity` INTEGER NOT NULL
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `is_active` BOOLEAN DEFAULT 1

### table_group_members
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `group_id` INTEGER NOT NULL
- `table_id` INTEGER NOT NULL
- FOREIGN KEY (`group_id`) REFERENCES `table_groups` (`id`)
- FOREIGN KEY (`table_id`) REFERENCES `tables` (`id`)

### customers
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `name` TEXT NOT NULL
- `phone` TEXT NOT NULL
- `email` TEXT
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `last_visit_date` TIMESTAMP
- `total_visits` INTEGER DEFAULT 0
- `notes` TEXT

### reservations
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `customer_id` INTEGER
- `customer_name` TEXT NOT NULL
- `phone` TEXT NOT NULL
- `email` TEXT
- `party_size` INTEGER NOT NULL
- `reservation_date` DATE NOT NULL
- `start_time` TIME NOT NULL
- `end_time` TIME NOT NULL
- `special_requests` TEXT
- `status` TEXT DEFAULT 'pending'  -- ('pending', 'completed', 'cancelled')
- `arrival_status` TEXT  -- ('arrived', 'no-show', NULL)
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)

### reservation_tables
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `reservation_id` INTEGER NOT NULL
- `table_id` INTEGER
- `table_group_id` INTEGER
- FOREIGN KEY (`reservation_id`) REFERENCES `reservations` (`id`)
- FOREIGN KEY (`table_id`) REFERENCES `tables` (`id`)
- FOREIGN KEY (`table_group_id`) REFERENCES `table_groups` (`id`)
- CHECK ((`table_id` IS NULL AND `table_group_id` IS NOT NULL) OR (`table_id` IS NOT NULL AND `table_group_id` IS NULL))

### no_show_customers
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `reservation_id` INTEGER NOT NULL
- `customer_id` INTEGER
- `customer_name` TEXT NOT NULL
- `phone` TEXT NOT NULL
- `email` TEXT
- `reservation_date` DATE NOT NULL
- `start_time` TIME NOT NULL
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- FOREIGN KEY (`reservation_id`) REFERENCES `reservations` (`id`)
- FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)

## İlişkiler

- Bir masa birden fazla rezervasyona atanabilir (farklı zaman dilimlerinde).
- Bir masa grubu birden fazla rezervasyona atanabilir (farklı zaman dilimlerinde).
- Bir rezervasyon ya bir veya birden fazla tekil masaya YA DA bir masa grubuna atanabilir.
- Bir müşteri birden fazla rezervasyon yapabilir.
- Bir masa grubu birden fazla masadan oluşabilir.
- Bir masa sadece bir aktif masa grubuna ait olabilir.
