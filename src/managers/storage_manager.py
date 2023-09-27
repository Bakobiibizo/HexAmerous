# A Python class that encapsulates the database operations related to storage paths.
# This class will use SQLite for demonstration purposes
import sqlite3
from pathlib import Path
from typing import List, Dict

pathlb = Path()

class StoragePathDBManager:
    """ 
    Database manager for sql style data base. 
    """
    def __init__(self, db_path=':memory:')-> None:
        self.conn = sqlite3.connect(db_path)
        self.create_table()
    
    def create_table(self)-> None:
        """
        Create a table in the database
        """
        query = '''
        CREATE TABLE IF NOT EXISTS storage_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL
        );
        '''
        self.conn.execute(query)
        self.conn.commit()
    
    def insert_path(self, name: str, path: str)-> None:
        """
        Insert a new path
        """
        query = 'INSERT INTO storage_paths (name, path) VALUES (?, ?)'
        self.conn.execute(query, (name, path))
        self.conn.commit()
    
    def get_all_paths(self)-> List[Dict[str, str]]:
        """
        Fetch all paths
        """
        query = 'SELECT * FROM storage_paths'
        cursor = self.conn.execute(query)
        return cursor.fetchall()
    
    def update_path(self, name: str, path: str)-> None:
        """
        Update the database entry for a path
        """
        query = 'UPDATE storage_paths SET path = ? WHERE name = ?'
        self.conn.execute(query, (path, name))
        self.conn.commit()
    
    def delete_path(self, name: str)-> None:
        """
        Delete a path from the database
        """
        query = 'DELETE FROM storage_paths WHERE name = ?'
        self.conn.execute(query, (name,))
        self.conn.commit()
    
    def close(self)-> None:
        """
        Close the connection
        """
        self.conn.close()

# Initialize the database manager
db_manager = StoragePathDBManager()

# Insert some sample paths
db_manager.insert_path('SYSTEM_MESSAGES_PATH', str(pathlb.cwd() / "docs" / "system_message" / ".json"))
db_manager.insert_path('AGENTS_PATH', str(pathlb.cwd() / "docs" / "agents" / ".json"))
db_manager.insert_path('TOOLS_PATH', str(pathlb.cwd() / "docs" / "tools" / ".json"))
db_manager.insert_path('HISTORY_MESSAGES_PATH', str(pathlb.cwd() / "docs" / "history" / ".json"))

# Fetch and display all paths
all_paths = db_manager.get_all_paths()
for row in all_paths:
    print(f"ID: {row[0]}, Name: {row[1]}, Path: {row[2]}")

# Update a path
db_manager.update_path('SYSTEM_MESSAGES_PATH', '/new_docs/system_message/.json')

# Fetch and display all paths after the update
print("\nAfter Update:")
all_paths = db_manager.get_all_paths()
for row in all_paths:
    print(f"ID: {row[0]}, Name: {row[1]}, Path: {row[2]}")

# Close the database connection
db_manager.close()
