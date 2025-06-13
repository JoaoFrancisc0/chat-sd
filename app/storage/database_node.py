class DatabaseNode:
    def __init__(self, node_id, storage_path):
        self.node_id = node_id
        self.storage_path = storage_path
        self.data_store = {}
        self.connected_nodes = []

    def store_data(self, data):
        """
        Armazena um dicionário de mensagem ou chunk de arquivo.
        O campo 'id' deve ser usado como chave.
        """
        key = data.get("id") or data.get("filename") or str(len(self.data_store))
        self.data_store[key] = data
        return key

    def retrieve_data(self, key):
        return self.data_store.get(key, None)
        
    def update_data(self, key, data):
        if key in self.data_store:
            self.data_store[key] = data
            return True
        return False
        
    def delete_data(self, key):
        if key in self.data_store:
            del self.data_store[key]
            return True
        return False
        
    def list_data(self, filter_criteria=None, limit=50, offset=0):
        """
        Lista dados (mensagens ou chunks) com base nos critérios.
        """
        results = []
        all_keys = sorted(self.data_store.keys(), reverse=True)
        if offset < len(all_keys):
            all_keys = all_keys[offset:]
        else:
            return []
        all_keys = all_keys[:limit]
        for key in all_keys:
            data = self.data_store[key]
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
                    self.store_data(value)

    def __repr__(self):
        return f"DatabaseNode(node_id={self.node_id}, storage_path={self.storage_path})"