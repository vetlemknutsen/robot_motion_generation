import sqlite3
import os
from pathlib import Path

class DatabaseLogic:
    def __init__(self, db_path):
        self.db_path = os.path.expanduser(db_path) 
        self.connection = sqlite3.connect(self.db_path)
        self._init_db()


    def _init_db(self):
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS motions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                robot TEXT NOT NULL,
                                rml TEXT NOT NULL
            )                        
        """)
    
    def insert(self, name: str, robot: str, rml: str):
        self.connection.execute("INSERT INTO motions (name, robot, rml) VALUES (?, ?, ?)", (name, robot, rml))
        self.connection.commit()

    def delete(self, id: int):
        self.connection.execute("DELETE FROM motions WHERE id = ?", (id,))
        self.connection.commit()

    def get(self, id:int):
        command = self.connection.execute("SELECT * FROM motions WHERE id = ?", (id,))
        return command.fetchone()

    def get_all(self):
        command = self.connection.execute("SELECT * FROM  motions")
        return command.fetchall()


