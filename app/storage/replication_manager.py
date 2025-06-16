import os
import time

class ReplicationManager:
    def __init__(self, nodes):
        self.nodes = nodes
        print(f"[+] ReplicationManager initialized with {len(nodes)} nodes")
    
    def store_with_replication(self, key, data):
        success_count = 0
        errors = []
        
        for node in self.nodes:
            try:
                if not node.exists():
                    self.recover_node(node)
                
                result = node.store_data(key, data)
                if result:
                    success_count += 1
                else:
                    errors.append(f"Node {node.node_id} returned None")
            except Exception as e:
                errors.append(f"Error on node {node.node_id}: {str(e)}")
        
        if success_count == len(self.nodes):
            print(f"[+] Data with key '{key}' successfully replicated to all {len(self.nodes)} nodes")
            return True
        elif success_count > 0:
            print(f"[!] Partial replication: Data saved to {success_count} of {len(self.nodes)} nodes")
            print(f"[!] Errors: {', '.join(errors)}")
            return True
        else:
            print(f"[ERROR] Replication failed: {', '.join(errors)}")
            return False
    
    def retrieve_with_fallback(self, key):
        for node in self.nodes:
            try:
                if node.exists():
                    data = node.retrieve_data(key)
                    if data:
                        return data
            except Exception as e:
                print(f"[WARNING] Failed to retrieve from node {node.node_id}: {e}")
        
        print(f"[WARNING] Data with key '{key}' not found on any node")
        return None
    
    def verify_nodes(self):
        print("[*] Verifying node health...")
        
        missing_nodes = []
        for node in self.nodes:
            if not node.exists():
                print(f"[!] Node {node.node_id} is missing or corrupted")
                missing_nodes.append(node)
                
        if not missing_nodes:
            print("[+] All nodes are healthy")
            return True
            
        print(f"[!] Found {len(missing_nodes)} missing nodes - attempting recovery")
        
        healthy_nodes = [n for n in self.nodes if n not in missing_nodes]
        
        if not healthy_nodes:
            print("[ERROR] No healthy nodes available for recovery")
            return False
            
        for node in missing_nodes:
            recovered = self.recover_node(node, source_nodes=healthy_nodes)
            if not recovered:
                print(f"[ERROR] Failed to recover node {node.node_id}")
                return False
                
        print("[+] All nodes recovered and healthy")
        return True
        
    def recover_node(self, node_to_recover, source_nodes=None):
        print(f"[*] Attempting to recover node {node_to_recover.node_id}...")
        
        if source_nodes is None:
            source_nodes = [n for n in self.nodes if n != node_to_recover]
        
        best_source = None
        max_records = 0
        
        for source in source_nodes:
            if source.exists():
                try:
                    record_count = source.count_records()
                    print(f"[*] Source node {source.node_id} has {record_count} records")
                    if record_count > max_records:
                        max_records = record_count
                        best_source = source
                except Exception as e:
                    print(f"[WARNING] Error checking source node {source.node_id}: {e}")
        
        if best_source is None:
            print("[ERROR] No valid source node found for recovery")
            return False
            
        print(f"[+] Using node {best_source.node_id} with {max_records} records as source")
        
        try:
            os.makedirs(os.path.dirname(node_to_recover.db_file), exist_ok=True)
            
            records_copied = node_to_recover.copy_from(best_source)
            
            if records_copied > 0:
                print(f"[+] Successfully recovered node {node_to_recover.node_id} with {records_copied} records")
                return True
            else:
                print(f"[ERROR] Recovery copied 0 records to node {node_to_recover.node_id}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to recover node {node_to_recover.node_id}: {e}")
            return False
    
    def synchronize_nodes(self):
        print("[*] Synchronizing data across all nodes...")
        
        if not self.verify_nodes():
            print("[ERROR] Cannot synchronize because some nodes are unhealthy")
            return False
            
        node_records = {}
        for node in self.nodes:
            try:
                count = node.count_records()
                node_records[node.node_id] = count
                print(f"[*] Node {node.node_id} has {count} records")
            except Exception as e:
                print(f"[ERROR] Failed to count records in node {node.node_id}: {e}")
                return False
        
        best_node_id = max(node_records, key=node_records.get)
        best_node = next(n for n in self.nodes if n.node_id == best_node_id)
        best_count = node_records[best_node_id]
        
        print(f"[+] Node {best_node_id} has the most records ({best_count})")
        
        if all(count == best_count for count in node_records.values()):
            print("[+] All nodes are already in sync")
            return True
            
        for node in self.nodes:
            if node.node_id != best_node_id:
                print(f"[*] Syncing node {node.node_id} from {best_node_id}...")
                try:
                    records_copied = node.copy_from(best_node)
                    print(f"[+] Copied {records_copied} records to node {node.node_id}")
                except Exception as e:
                    print(f"[ERROR] Failed to sync node {node.node_id}: {e}")
                    return False
        
        print("[+] All nodes synchronized successfully")
        return True