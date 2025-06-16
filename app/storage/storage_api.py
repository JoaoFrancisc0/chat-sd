import time

class StorageAPI:

    def __init__(self, replication_manager, cluster_coordinator=None):
        self.replication_manager = replication_manager
        self.cluster_coordinator = cluster_coordinator
    
    def store_message(self, message_id, message_data):
        self.verify_nodes()
        
        success = self.replication_manager.store_with_replication(message_id, message_data)
        if success:
            return message_id
        return None
    
    def get_message(self, message_id):
        return self.replication_manager.retrieve_with_fallback(message_id)
    
    def get_messages(self, limit=50):
        self.verify_nodes()
        
        for node in self.replication_manager.nodes:
            try:
                if node.exists():
                    messages = node.list_data(limit=limit)
                    if messages and len(messages) > 0:
                        print(f"[+] Retrieved {len(messages)} messages from node {node.node_id}")
                        return messages
            except Exception as e:
                print(f"[WARNING] Failed to get messages from node {node.node_id}: {e}")
        
        print("[WARNING] No messages found in any node")
        return []
    
    def verify_nodes(self):
        return self.replication_manager.verify_nodes()
    
    def synchronize(self):
        return self.replication_manager.synchronize_nodes()