"""
Abstract base class and model for the storage manager.
"""
import sqlite3
from abc import ABC, abstractmethod
from typing import List, Dict
from pydantic import BaseModel



class Storage(BaseModel):
    conn: sqlite3.connect


class StoragePathDBManager(ABC):
    """ 
    Database manager for sql style data base. 
    """
    def __init__(self, db_path=':memory:')-> None:
        """
        Initialize the class
        """

    @abstractmethod
    def create_table(self)-> None:
        """
        Create a table in the database
        """

    @abstractmethod
    def insert_path(self, name: str, new_path: str)-> None:
        """
        Insert a new path
        """

    @abstractmethod
    def get_all_paths(self)-> List[Dict[str, str]]:
        """
        Fetch all paths
        """

    @abstractmethod
    def update_path(self, name: str, new_path: str)-> None:
        """
        Update the database entry for a path
        """

    @abstractmethod
    def delete_path(self, name: str)-> None:
        """
        Delete a path from the database
        """

    @abstractmethod
    def close(self)-> None:
        """
        Close the connection
        """
