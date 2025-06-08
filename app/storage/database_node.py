class DatabaseNode:
    def __init__(self, node_id, storage_path):
        self.node_id = node_id
        self.storage_path = storage_path
        self.data_store = {}
        self.connected_nodes = []

    def store_data(self, key, value):
        self.data_store[key] = value
        return key

    def retrieve_data(self, key):
        return self.data_store.get(key, None)
        
    def update_data(self, key, value):
        if key in self.data_store:
            self.data_store[key] = value
            return True
        return False
        
    def delete_data(self, key):
        if key in self.data_store:
            del self.data_store[key]
            return True
        return False
        
    def list_data(self, filter_criteria=None, limit=50, offset=0):
        """
        List data matching the given criteria.
        
        Args:
            filter_criteria (dict): Criteria to filter records
            limit (int): Maximum number of records to return
            offset (int): Starting position for records
            
        Returns:
            list: Records matching criteria
        """
        results = []
        
        # Get all keys in reverse chronological order (assuming IDs or timestamps)
        all_keys = sorted(self.data_store.keys(), reverse=True)
        
        # Apply offset
        if offset < len(all_keys):
            all_keys = all_keys[offset:]
        else:
            return []
            
        # Apply limit
        all_keys = all_keys[:limit]
        
        # Gather data
        for key in all_keys:
            data = self.data_store[key]
            
            # Apply filter if specified
            if filter_criteria is not None:
                match = True
                for k, v in filter_criteria.items():
                    if k not in data or data[k] != v:
                        match = False
                        break
                
                if not match:
                    continue
            
            results.append(data)
            
        return results

    def connect_to_node(self, other_node):
        if other_node not in self.connected_nodes:
            self.connected_nodes.append(other_node)
            other_node.connected_nodes.append(self)

    def synchronize_data(self):
        for node in self.connected_nodes:
            for key, value in node.data_store.items():
                if key not in self.data_store:
                    self.store_data(key, value)

    def __repr__(self):
        return f"DatabaseNode(node_id={self.node_id}, storage_path={self.storage_path})"