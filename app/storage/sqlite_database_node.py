import sqlite3
import json
import os
import datetime

class SQLiteDatabaseNode:
    def __init__(self, node_id, db_file):
        self.node_id = node_id
        self.db_file = db_file
        self.connected_nodes = []
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    sender_id TEXT,
                    timestamp TEXT,
                    filename TEXT,
                    filesize INTEGER,
                    chunk_index INTEGER,
                    total_chunks INTEGER,
                    data TEXT,
                    data_json TEXT
                )
            """)
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to initialize SQLite database: {e}")
    
    def _get_connection(self):
        return sqlite3.connect(self.db_file)
    
    def store_data(self, data):
        """
        Armazena um dicionário de mensagem ou chunk de arquivo.
        """
        key = data.get("id") or data.get("filename") or str(datetime.datetime.now().timestamp())
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO messages
                (id, type, sender_id, timestamp, filename, filesize, chunk_index, total_chunks, data, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                key,
                data.get("type", ""),
                data.get("sender_id", ""),
                data.get("timestamp", ""),
                data.get("filename", ""),
                data.get("filesize", 0),
                data.get("chunk_index", 0),
                data.get("total_chunks", 0),
                data.get("data", ""),
                json.dumps(data)
            ))
            conn.commit()
            conn.close()
            return key
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to store data in SQLite: {e}")
            return None
    
    def retrieve_data(self, key):
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
    
    def update_data(self, key, data):
        return self.store_data(data) is not None
    
    def delete_data(self, key):
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
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql = "SELECT data_json FROM messages"
            params = []
            if filter_criteria:
                where_clauses = []
                for key, value in filter_criteria.items():
                    if key in ['id', 'sender_id', 'type', 'filename']:
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
            print(f"[ERROR] Failed to list data from SQLite: {e}")
            return []
    
    def connect_to_node(self, other_node):
        if other_node not in self.connected_nodes:
            self.connected_nodes.append(other_node)
            if self not in other_node.connected_nodes:
                other_node.connected_nodes.append(self)
    
    def synchronize_data(self):
        pass
    
    def __repr__(self):
        return f"SQLiteDatabaseNode(node_id={self.node_id})"