import sqlite3
import json
import os
import datetime

class SQLiteDatabaseNode:
    """
    Database node implementation that uses SQLite for persistent storage.
    """
    def __init__(self, node_id, db_file):
        """
        Initialize the SQLite database node.
        
        Args:
            node_id (str): Unique identifier for this node
            db_file (str): Path to the SQLite database file
        """
        self.node_id = node_id
        self.db_file = db_file
        self.connected_nodes = []
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        
        # Initialize database and tables
        self._initialize_database()
    
    def _initialize_database(self):
        """Create the necessary tables if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    timestamp TEXT,
                    sender TEXT,
                    data_json TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            print(f"[+] SQLite database initialized for node {self.node_id} at {self.db_file}")
            
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to initialize SQLite database: {e}")
    
    def _get_connection(self):
        """Get a connection to the SQLite database."""
        return sqlite3.connect(self.db_file)
    
    def store_data(self, key, value):
        """
        Store data in the SQLite database.
        
        Args:
            key (str): The unique identifier for the data
            value (dict): The data to store
        
        Returns:
            str: The key of the stored data
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Extract fields from value
            content = value.get('content', '')
            timestamp = value.get('timestamp', datetime.datetime.now().isoformat())
            sender = value.get('sender', 'Unknown')
            
            # Convert the entire value dict to JSON for storage
            data_json = json.dumps(value)
            
            # Insert or replace data
            sql = """
                INSERT OR REPLACE INTO messages (id, content, timestamp, sender, data_json)
                VALUES (?, ?, ?, ?, ?)
            """
            
            cursor.execute(sql, (key, content, timestamp, sender, data_json))
            
            conn.commit()
            conn.close()
            return key
            
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to store data in SQLite: {e}")
            return None
    
    def retrieve_data(self, key):
        """
        Retrieve data from the SQLite database.
        
        Args:
            key (str): The key of the data to retrieve
        
        Returns:
            dict: The retrieved data or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT data_json FROM messages WHERE id = ?", (key,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
            
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to retrieve data from SQLite: {e}")
            return None
    
    def update_data(self, key, value):
        """
        Update data in the SQLite database.
        
        Args:
            key (str): The key of the data to update
            value (dict): The new data
        
        Returns:
            bool: True if successful, False otherwise
        """
        # For SQLite, store_data handles both insert and update
        return self.store_data(key, value) is not None
    
    def delete_data(self, key):
        """
        Delete data from the SQLite database.
        
        Args:
            key (str): The key of the data to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM messages WHERE id = ?", (key,))
            
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            return success
            
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to delete data from SQLite: {e}")
            return False
    
    def list_data(self, filter_criteria=None, limit=50, offset=0):
        """
        List data from the SQLite database with optional filtering.
        
        Args:
            filter_criteria (dict): Optional criteria to filter records
            limit (int): Maximum number of records to return
            offset (int): Starting position for records
        
        Returns:
            list: Records matching criteria
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            sql = "SELECT data_json FROM messages"
            params = []
            
            # Add WHERE clause if filter criteria provided
            if filter_criteria:
                where_clauses = []
                for key, value in filter_criteria.items():
                    if key in ['id', 'sender']:
                        where_clauses.append(f"{key} = ?")
                        params.append(value)
                
                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)
            
            # Add ORDER BY, LIMIT, and OFFSET
            sql += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            conn.close()
            
            # Convert JSON strings back to dictionaries
            return [json.loads(row[0]) for row in results]
            
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to list data from SQLite: {e}")
            return []
    
    def connect_to_node(self, other_node):
        """Connect to another node for replication."""
        if other_node not in self.connected_nodes:
            self.connected_nodes.append(other_node)
            
            # Add this node to the other node's connected nodes if not already there
            if self not in other_node.connected_nodes:
                other_node.connected_nodes.append(self)
    
    def synchronize_data(self):
        """Synchronize data with connected nodes."""
        # This would involve more complex logic in a real system
        # For simplicity, we're not implementing full synchronization
        pass
    
    def __repr__(self):
        return f"SQLiteDatabaseNode(node_id={self.node_id})"