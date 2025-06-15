class ClusterCoordinator:
    
    def __init__(self, nodes=None):
        self.nodes = nodes or [] 
        
    def add_node(self, node):
        self.nodes.append(node)

    def remove_node(self, node):
        self.nodes.remove(node)
        
    def get_primary_node(self):
        if not self.nodes:
            raise Exception("Nenhum nó disponível no cluster.")
        
        return self.nodes[0]
        
    def get_node_for_record(self, record_id):
        if not self.nodes:
            raise Exception("Nenhum nó disponível no cluster.")
        
        node_index = hash(record_id) % len(self.nodes)
        return self.nodes[node_index]

    def distribute_request(self, request):
        if not self.nodes:
            raise Exception("Nenhum nó disponível no cluster.")
        
        node = self.nodes[0]
        return node.process_request(request)

    def get_cluster_status(self):
        return [node.get_status() for node in self.nodes]