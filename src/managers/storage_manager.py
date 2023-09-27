"""
A Python class that encapsulates the database operations related to storage paths.
This class will use SQLite for demonstration purposes
"""
import sqlite3
from typing import List, Dict
from pathlib import Path
from src.helpers.log_helper import get_logger
from src.data_models.storage import StoragePathABC, StoragePathModel, StoragePathEnum, get_queries

logger = get_logger()

pathlib_path = Path

class StoragePathDBManager(StoragePathABC):
    """ 
    Database manager for SQL-style databases. 
    """
    def __init__(self, db_connection: sqlite3.Connection):
        super().__init__(db_connection=db_connection)
        logger.info("Initializing StoragePathDBManager")
        self.connection = db_connection
        self.create_tables()
  
    def create_tables(self)-> None:
        """
        Create tables in the database
        """
        logger.info("Creating tables")
        for enum_member in StoragePathEnum:
            query = get_queries(enum_member)
            try:
                self.connection.execute(query)
                self.connection.commit()
            except sqlite3.Error as error:
                logger.error(f"Failed to create table: {error}")
    
    def insert_model(self, storage_path_model: StoragePathModel) -> None:
        """
        Insert a model into the database
        """
        logger.info("Inserting model")
        name = storage_path_model.name
        model = storage_path_model.model_dump()
        self.insert_into_db(name, model)

    def insert_into_db(self, name: str, model: str):
        """
        extracted common method
        """
        query = 'INSERT INTO storage_paths (name, model) VALUES (?, ?)'
        try:
            self.connection.execute(query, (name, model))
            self.connection.commit()
        except sqlite3.Error as error:
            logger.error(f"Failed to insert model: {error}")
    
    def get_all_paths(self)-> List[Dict[str, str]]:
        """
        Fetch all paths from the database
        """
        query = 'SELECT * FROM storage_paths'
        try:
            cursor = self.connection.execute(query)
            return cursor.fetchall()
        except sqlite3.Error as error:
            logger.error(f"Failed to fetch paths: {error}")
            return []
    
    def update_path(self, name: str, storage_path_model: StoragePathModel) -> None:
        """
        Update a model in the database
        """
        model = storage_path_model.model_dump()
        query = 'UPDATE storage_paths SET model = ? WHERE name = ?'
        try:
            self.connection.execute(query, (model, name))
            self.connection.commit()
        except sqlite3.Error as error:
            logger.error(f"Failed to update model: {error}")
    
    def delete_path(self, name: str) -> None:
        """
        Delete a model from the database
        """
        query = 'DELETE FROM storage_paths WHERE name = ?'
        try:
            self.connection.execute(query, (name,))
            self.connection.commit()
        except sqlite3.Error as error:
            logger.error(f"Failed to delete model: {error}")
    
    def close(self) -> None:
        """
        Close the database connection
        """
        self.connection.close()

# Initialize the database manager
db_manager = StoragePathDBManager(sqlite3.connect(':memory:'))

# Close the database connection
db_manager.close()
