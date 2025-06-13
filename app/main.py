import os
from chat.servidor import servidor
from storage.database_node import DatabaseNode
from storage.replication_manager import ReplicationManager
from storage.cluster_coordinator import ClusterCoordinator
from storage.storage_api import StorageAPI

def initialize_storage():
    """Inicializar sistema de storage distribuído"""
    # Criar diretórios de dados se não existirem
    for i in range(3):
        os.makedirs(f"./data/node{i+1}", exist_ok=True)
    
    # Criar nós
    nodes = []
    for i in range(3):
        node = DatabaseNode(f"node{i+1}", f"./data/node{i+1}")
        nodes.append(node)
    
    # Conectar nós entre si
    for i, node in enumerate(nodes):
        for other_node in nodes[i+1:]:
            node.connect_to_node(other_node)
    
    # Inicializar gerenciadores
    replication_manager = ReplicationManager(nodes)
    cluster_coordinator = ClusterCoordinator(nodes)
    storage_api = StorageAPI(replication_manager, cluster_coordinator)
    
    return storage_api

def main():
    print("Iniciando sistema de chat distribuído...")
    
    # Inicializar storage
    storage_api = initialize_storage()
    print("Sistema de storage inicializado com sucesso!")
    
    # Iniciar servidor com storage
    servidor = servidor(storage_api=storage_api)
    servidor.start()

if __name__ == "__main__":
    main()