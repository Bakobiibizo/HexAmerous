# Let's create a Python class that encapsulates the database operations related to storage paths.
# This class will use SQLite for demonstration purposes, but the same principles apply for other databases.

class StoragePathDBManager:
    def __init__(self, db_path=':memory:'):
        self.conn = sqlite3.connect(db_path)
        self.create_table()
    
    def create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS storage_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL
        );
        '''
        self.conn.execute(query)
        self.conn.commit()
    
    def insert_path(self, name, path):
        query = 'INSERT INTO storage_paths (name, path) VALUES (?, ?)'
        self.conn.execute(query, (name, path))
        self.conn.commit()
    
    def get_all_paths(self):
        query = 'SELECT * FROM storage_paths'
        cursor = self.conn.execute(query)
        return cursor.fetchall()
    
    def update_path(self, name, new_path):
        query = 'UPDATE storage_paths SET path = ? WHERE name = ?'
        self.conn.execute(query, (new_path, name))
        self.conn.commit()
    
    def delete_path(self, name):
        query = 'DELETE FROM storage_paths WHERE name = ?'
        self.conn.execute(query, (name,))
        self.conn.commit()
    
    def close(self):
        self.conn.close()

# Initialize the database manager
db_manager = StoragePathDBManager()

# Insert some sample paths
db_manager.insert_path('SYSTEM_MESSAGES_PATH', '/docs/system_message/.json')
db_manager.insert_path('AGENTS_PATH', '/docs/agents/.json')

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
