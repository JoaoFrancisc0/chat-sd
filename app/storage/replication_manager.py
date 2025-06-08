class ReplicationManager:
    """
    Classe que gerencia a replicação de dados entre múltiplos nós do banco de dados.
    Garante a tolerância a falhas e a consistência dos dados.
    """
    def __init__(self, nodes):
        """
        Inicializa o gerenciador de replicação com uma lista de nós.

        Args:
            nodes (list): Lista de instâncias de DatabaseNode.
        """
        self.nodes = nodes

    def replicate_data(self, data):
        """
        Replica os dados para todos os nós disponíveis.

        Args:
            data (dict): Dados a serem replicados.
        """
        for node in self.nodes:
            try:
                node.store_data(data)
            except Exception as e:
                print(f"Erro ao replicar dados para o nó {node}: {e}")

    def synchronize_nodes(self):
        """
        Sincroniza os dados entre os nós para garantir a consistência.
        """
        for node in self.nodes:
            for other_node in self.nodes:
                if node != other_node:
                    try:
                        data = node.get_data()
                        other_node.store_data(data)
                    except Exception as e:
                        print(f"Erro ao sincronizar dados entre {node} e {other_node}: {e}")

    def check_node_health(self):
        """
        Verifica a saúde de cada nó e remove nós não saudáveis da lista.
        """
        healthy_nodes = []
        for node in self.nodes:
            if node.is_healthy():
                healthy_nodes.append(node)
            else:
                print(f"Nó {node} não está saudável e será removido.")
        self.nodes = healthy_nodes

    def handle_node_failure(self, failed_node):
        """
        Lida com a falha de um nó, redistribuindo dados conforme necessário.

        Args:
            failed_node (DatabaseNode): O nó que falhou.
        """
        print(f"Lidando com a falha do nó {failed_node}. Redistribuindo dados...")
        for node in self.nodes:
            if node != failed_node:
                try:
                    data = failed_node.get_data()
                    node.store_data(data)
                except Exception as e:
                    print(f"Erro ao redistribuir dados para o nó {node}: {e}")