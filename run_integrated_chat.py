import os
import sys
import threading
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.storage.sqlite_database_node import SQLiteDatabaseNode
from app.storage.cluster_coordinator import ClusterCoordinator
from app.storage.storage_api import StorageAPI
from app.storage.replication_manager import ReplicationManager
from app.chat.servidor import ServidorChat

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
NODE1_DB = os.path.join(DATA_DIR, 'chat_node1.db')
NODE2_DB = os.path.join(DATA_DIR, 'chat_node2.db')
NODE3_DB = os.path.join(DATA_DIR, 'chat_node3.db')

os.makedirs(DATA_DIR, exist_ok=True)

def health_check_thread(storage_api):
    while True:
        try:
            print("\n[*] Running node health check...")
            storage_api.verify_nodes()
            
            if int(time.time()) % 300 < 60: 
                print("[*] Running full data synchronization...")
                storage_api.synchronize()
                
            print("[*] Health check complete")
            time.sleep(60)  
        except Exception as e:
            print(f"[ERROR] Health check failed: {e}")
            time.sleep(30) 

def create_storage_system():
    print("[*] Initializing distributed storage system...")
    
    node1 = SQLiteDatabaseNode(node_id="node1", db_file=NODE1_DB)
    node2 = SQLiteDatabaseNode(node_id="node2", db_file=NODE2_DB)
    node3 = SQLiteDatabaseNode(node_id="node3", db_file=NODE3_DB)
    
    node1.connect_to_node(node2)
    node2.connect_to_node(node3)
    node1.connect_to_node(node3)
    
    print(f"[+] Created 3 SQLite storage nodes")
    
    coordinator = ClusterCoordinator()
    coordinator.add_node(node1)
    coordinator.add_node(node2)
    coordinator.add_node(node3)
    
    replication_manager = ReplicationManager([node1, node2, node3])
    
    storage_api = StorageAPI(
        replication_manager=replication_manager,
        cluster_coordinator=coordinator
    )
    
    print("[*] Verifying node health and synchronizing data...")
    storage_api.verify_nodes()
    storage_api.synchronize()
    
    print("[+] Storage system initialized with replication")
    return storage_api

def main():
    storage_api = create_storage_system()
    
    health_thread = threading.Thread(
        target=health_check_thread, 
        args=(storage_api,),
        daemon=True
    )
    health_thread.start()
    
    host = '192.168.10.9'  # Accept connections from any IP
    port = 8080       # Higher port to avoid permission issues
    
    print(f"[*] Starting chat server on {host}:{port} with integrated storage...")
    chat_server = ServidorChat(host=host, port=port, storage_api=storage_api)
    
    try:
        chat_server.iniciar_servidor()
    except KeyboardInterrupt:
        print("\n[!] Server shutdown by user")
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")

if __name__ == "__main__":
    main() 