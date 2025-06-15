from threading import Lock

class SyncUtils:
    def __init__(self):
        self.lock = Lock()

    def synchronize_data(self, source_data, target_node):
        with self.lock:
            target_node.store_data(source_data)

    def broadcast_update(self, data, nodes):
        for node in nodes:
            self.synchronize_data(data, node)

    def resolve_conflicts(self, local_data, remote_data):
        return remote_data if remote_data else local_data

    def sync_with_node(self, local_data, remote_node):
        remote_data = remote_node.retrieve_data()
        resolved_data = self.resolve_conflicts(local_data, remote_data)
        self.synchronize_data(resolved_data, remote_node)