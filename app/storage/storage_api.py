class StorageAPI:
    def __init__(self, replication_manager, cluster_coordinator):
        self.replication_manager = replication_manager
        self.cluster_coordinator = cluster_coordinator

    def create(self, message_id, data):
        node = self.cluster_coordinator.get_primary_node()
        return node.store_data(message_id, data) 

    def read(self, record_id):
        node = self.cluster_coordinator.get_node_for_record(record_id)
        return node.retrieve_data(record_id)

    def update(self, record_id, data):
        node = self.cluster_coordinator.get_node_for_record(record_id)
        return node.update_data(record_id, data)

    def delete(self, record_id):
        node = self.cluster_coordinator.get_node_for_record(record_id)
        return node.delete_data(record_id)
        
    def list_records(self, filter_criteria=None, limit=50, offset=0):
        primary_node = self.cluster_coordinator.get_primary_node()
        return primary_node.list_data(filter_criteria, limit, offset)