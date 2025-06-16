import sqlite3
import json
import os
import datetime
import shutil

class SQLiteDatabaseNode:

    def __init__(self, node_id, db_file):
        self.node_id = node_id
        self.db_file = db_file
        self.connected_nodes = []
        
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        
        self._initialize_database()
        
        print(f"[+] SQLite node {node_id} initialized at {db_file}")
    
    def _initialize_database(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
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
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to initialize SQLite database: {e}")
    
    def exists(self):
        if not os.path.exists(self.db_file):
            print(f"[!] Database file for node {self.node_id} doesn't exist")
            return False
            
        try:
            # Try to open and query the database
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master")
            result = cursor.fetchone()
            conn.close()
            return True
        except sqlite3.Error:
            print(f"[!] Database file for node {self.node_id} exists but is corrupted")
            return False
    
    def store_data(self, key, value):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            content = value.get('content', '')
            timestamp = value.get('timestamp', datetime.datetime.now().isoformat())
            sender = value.get('sender', 'Unknown')
            
            data_json = json.dumps(value)
            
            sql = """
                INSERT OR REPLACE INTO messages (id, content, timestamp, sender, data_json)
                VALUES (?, ?, ?, ?, ?)
            """
            
            cursor.execute(sql, (key, content, timestamp, sender, data_json))
            
            conn.commit()
            conn.close()
            return key
            
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to store data in SQLite node {self.node_id}: {e}")
            return None
    
    def retrieve_data(self, key):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT data_json FROM messages WHERE id = ?", (key,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
            
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to retrieve data from SQLite node {self.node_id}: {e}")
            return None
    
    def list_data(self, filter_criteria=None, limit=100, offset=0):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            sql = "SELECT data_json FROM messages"
            params = []
            
            if filter_criteria:
                where_clauses = []
                for key, value in filter_criteria.items():
                    if key in ['id', 'sender']:
                        where_clauses.append(f"{key} = ?")
                        params.append(value)
                
                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)
            
            sql += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            conn.close()
            
            return [json.loads(row[0]) for row in results]
            
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to list data from SQLite node {self.node_id}: {e}")
            return []
    
    def count_records(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM messages")
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to count records in SQLite node {self.node_id}: {e}")
            return 0
    
    def connect_to_node(self, other_node):
        if other_node not in self.connected_nodes:
            self.connected_nodes.append(other_node)
            
            if self not in other_node.connected_nodes:
                other_node.connected_nodes.append(self)
    
    def copy_from(self, source_node):
        if not source_node.exists():
            print(f"[ERROR] Source node {source_node.node_id} doesn't exist")
            return 0
            
        try:
            if os.path.exists(self.db_file):
                os.remove(self.db_file)
            
            self._initialize_database()
            
            records = source_node.list_data(limit=10000) 
            
            count = 0
            for record in records:
                if 'id' in record:
                    self.store_data(record['id'], record)
                    count += 1
            
            print(f"[+] Copied {count} records from node {source_node.node_id} to node {self.node_id}")
            return count
        except Exception as e:
            print(f"[ERROR] Failed to copy data from node {source_node.node_id}: {e}")
            return 0
    
    def __repr__(self):
        return f"SQLiteDatabaseNode(node_id={self.node_id})"