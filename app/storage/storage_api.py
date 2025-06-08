class StorageAPI:
    def __init__(self, replication_manager, cluster_coordinator):
        self.replication_manager = replication_manager
        self.cluster_coordinator = cluster_coordinator

    def create(self, data):
        node = self.cluster_coordinator.get_primary_node()
        return node.store_data(data["id"], data)  # Passando id como chave e data como valor

    def read(self, record_id):
        """Read a record from the distributed database."""
        node = self.cluster_coordinator.get_node_for_record(record_id)
        return node.retrieve_data(record_id)

    def update(self, record_id, data):
        """Update an existing record in the distributed database."""
        node = self.cluster_coordinator.get_node_for_record(record_id)
        return node.update_data(record_id, data)

    def delete(self, record_id):
        """Delete a record from the distributed database."""
        node = self.cluster_coordinator.get_node_for_record(record_id)
        return node.delete_data(record_id)
        
    def list_records(self, filter_criteria=None, limit=50, offset=0):
        """
        List records from the distributed database with optional filtering.
        
        Args:
            filter_criteria (dict): Optional criteria to filter records
            limit (int): Maximum number of records to return
            offset (int): Starting position for records to return
            
        Returns:
            list: List of records matching criteria
        """
        primary_node = self.cluster_coordinator.get_primary_node()
        return primary_node.list_data(filter_criteria, limit, offset)