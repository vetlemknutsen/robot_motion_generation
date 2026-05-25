import sqlite3
import os
from pathlib import Path

from motion_pipeline.storage.base import MotionStore

# Stores generated motions in a local SQLite file so they survive across runs
class SQLiteMotionStore(MotionStore):
    def __init__(self, db_path: str):
        # expanduser s paths like "~/motions.db" work
        self.db_path = os.path.expanduser(db_path) 
        # check_same_thread = False so multiple threads can share the conn
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    # Create the motions table on first use
    def _init_db(self):
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS motions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                robot TEXT NOT NULL,
                rml TEXT NOT NULL
            )                        
        """)
    
    # Save a new motion. Using ? placeholders to avoid SQL injection
    def insert(self, name: str, robot: str, rml: str) -> None:
        self.connection.execute("INSERT INTO motions (name, robot, rml) VALUES (?, ?, ?)", (name, robot, rml))
        self.connection.commit()

    def delete(self, id: int) -> None:
        self.connection.execute("DELETE FROM motions WHERE id = ?", (id,))
        self.connection.commit()

    # Returns one row tuple or None if not found
    def get(self, id:int):
        command = self.connection.execute("SELECT * FROM motions WHERE id = ?", (id,))
        return command.fetchone()

    # Return every motion in the table. Used by the frontend to list them.
    def get_all(self) -> None:
        command = self.connection.execute("SELECT * FROM  motions")
        return command.fetchall()

    # Close the DB on shutdown
    def close(self) -> None:
        self.connection.close()

