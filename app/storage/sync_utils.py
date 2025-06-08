from threading import Lock

class SyncUtils:
    """
    Utility class for synchronizing data across nodes in a distributed database.
    """

    def __init__(self):
        self.lock = Lock()

    def synchronize_data(self, source_data, target_node):
        """
        Synchronizes data from the source to the target node.

        Args:
            source_data (dict): The data to be synchronized.
            target_node (DatabaseNode): The target node to synchronize data to.
        """
        with self.lock:
            target_node.store_data(source_data)

    def broadcast_update(self, data, nodes):
        """
        Broadcasts an update to all nodes in the cluster.

        Args:
            data (dict): The data to be broadcasted.
            nodes (list): A list of DatabaseNode instances to receive the update.
        """
        for node in nodes:
            self.synchronize_data(data, node)

    def resolve_conflicts(self, local_data, remote_data):
        """
        Resolves conflicts between local and remote data.

        Args:
            local_data (dict): The local data.
            remote_data (dict): The remote data.

        Returns:
            dict: The resolved data.
        """
        # Example conflict resolution strategy: prefer remote data
        return remote_data if remote_data else local_data

    def sync_with_node(self, local_data, remote_node):
        """
        Synchronizes local data with a remote node.

        Args:
            local_data (dict): The local data to synchronize.
            remote_node (DatabaseNode): The remote node to synchronize with.
        """
        remote_data = remote_node.retrieve_data()
        resolved_data = self.resolve_conflicts(local_data, remote_data)
        self.synchronize_data(resolved_data, remote_node)