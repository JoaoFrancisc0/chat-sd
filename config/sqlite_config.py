import os

# Get the base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SQLite Database Configuration
SQLITE_CONFIG = {
    'db_dir': os.path.join(BASE_DIR, 'data'),  # Directory to store database files
    'node1_db': os.path.join(BASE_DIR, 'data', 'chat_node1.db'),
    'node2_db': os.path.join(BASE_DIR, 'data', 'chat_node2.db'),
    'node3_db': os.path.join(BASE_DIR, 'data', 'chat_node3.db')
}