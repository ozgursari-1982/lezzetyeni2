from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username
    
    @staticmethod
    def get_by_username(db, username):
        user_data = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user_data:
            return User(user_data['id'], user_data['username'])
        return None
    
    @staticmethod
    def create(db, username, password_hash):
        db.execute(
            'INSERT INTO users (username, password, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)',
            (username, password_hash)
        )
        db.commit()
        return User.get_by_username(db, username)
    
    @staticmethod
    def update_last_login(db, user_id):
        db.execute(
            'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
            (user_id,)
        )
        db.commit()
