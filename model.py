import sqlite3
import sys
from typing import List


class Model:
    def __init__(self, file: str):
        self.db = sqlite3.connect(file, check_same_thread=False)
        cur = self.db.cursor()
        cur.execute('CREATE TABLE IF NOt EXISTS users (id INTEGER PRIMARY KEY)')
        cur.execute('CREATE TABLE IF NOT EXISTS products (name VARCHAR PRIMARY KEY)')
        self.db.commit()

    def read_chats(self) -> List[int]:
        cur = self.db.cursor()
        rows = cur.execute('SELECT id FROM users').fetchall()
        return [row[0] for row in rows]

    def add_chat(self, chat: int) -> None:
        cur = self.db.cursor()
        cur.execute('INSERT OR IGNORE INTO users VALUES (?)', (chat,))
        self.db.commit()

    def delete_chat(self, chat: int) -> None:
        cur = self.db.cursor()
        cur.execute('DELETE FROM users WHERE id=?', (chat,))
        self.db.commit()

    def read_products(self) -> List[str]:
        cur = self.db.cursor()
        rows = cur.execute('SELECT name FROM products').fetchall()
        return [row[0] for row in rows]

    def add_product(self, product) -> None:
        cur = self.db.cursor()
        cur.execute('INSERT OR IGNORE INTO products VALUES (?)', (product,))
        self.db.commit()

    def delete_product(self, product) -> None:
        cur = self.db.cursor()
        cur.execute('DELETE FROM products WHERE name=?', (product,))
        self.db.commit()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        db = sys.argv[1]
    else:
        db = 'bot.sqlite'
    Model(db)
