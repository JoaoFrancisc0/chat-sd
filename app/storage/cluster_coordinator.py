class ClusterCoordinator:
    """
    Classe que coordena a comunicação e a operação de um cluster de nós de banco de dados distribuído.
    Gerencia a adição e remoção de nós, bem como a distribuição de requisições.
    """
    
    def __init__(self, nodes=None):
        self.nodes = nodes or []  # Lista de nós no cluster

    def add_node(self, node):
        """
        Adiciona um novo nó ao cluster.

        Args:
            node (DatabaseNode): O nó a ser adicionado.
        """
        self.nodes.append(node)

    def remove_node(self, node):
        """
        Remove um nó do cluster.

        Args:
            node (DatabaseNode): O nó a ser removido.
        """
        self.nodes.remove(node)
        
    def get_primary_node(self):
        """
        Retorna o nó primário para operações de escrita.
        
        Returns:
            DatabaseNode: O nó primário
        """
        if not self.nodes:
            raise Exception("Nenhum nó disponível no cluster.")
        
        # Aqui utilizamos o primeiro nó como primário para simplificar
        # Em um sistema real, seria necessário implementar eleição de líder
        return self.nodes[0]
        
    def get_node_for_record(self, record_id):
        """
        Determina qual nó deve lidar com uma operação para um registro específico.
        
        Args:
            record_id (str): O ID do registro
            
        Returns:
            DatabaseNode: O nó responsável pelo registro
        """
        if not self.nodes:
            raise Exception("Nenhum nó disponível no cluster.")
            
        # Implementação simples: hash do ID para distribuir entre os nós
        # Em sistemas reais, geralmente usa-se hash consistente
        node_index = hash(record_id) % len(self.nodes)
        return self.nodes[node_index]

    def distribute_request(self, request):
        """
        Distribui uma requisição entre os nós do cluster.

        Args:
            request (dict): A requisição a ser distribuída.
        
        Returns:
            dict: A resposta do nó que processou a requisição.
        """
        # Implementação simples de distribuição de requisições
        if not self.nodes:
            raise Exception("Nenhum nó disponível no cluster.")
        
        # Aqui, apenas selecionamos o primeiro nó para simplificar
        node = self.nodes[0]
        return node.process_request(request)

    def get_cluster_status(self):
        """
        Retorna o status atual do cluster, incluindo os nós ativos.

        Returns:
            list: Lista de nós ativos no cluster.
        """
        return [node.get_status() for node in self.nodes]