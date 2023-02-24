import sqlite3

class UsersDB:
    def __init__(self) -> None:
        self.database = sqlite3.connect(
            "users.db"
        )
        self.cursor = self.database.cursor()
        
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (nickname TEXT, id INTEGER, valueAwaiter TEXT, ageFrom INTEGER, city TEXT, userList TEXT, number INTEGER DEFAULT 0)")
        
    def update(self, id: str, queries: str):
        with self.database:
            self.cursor.execute(f"UPDATE users SET {queries} WHERE id = '{id}'")

    def get(self, id: str, queries: str):
        with self.database:
            return self.cursor.execute(f"SELECT {queries} FROM users WHERE id = '{id}'").fetchone()
    
    def add_user(self, nickname: str, user_id: str, valueAwaiter: str = "", ageFrom: int = 0, city: str = "", users: str = "", number: int = 0) -> str:
        with self.database:
            self.cursor.execute(f"INSERT INTO users VALUES {(nickname, user_id, valueAwaiter, ageFrom, city, users, number)}")
