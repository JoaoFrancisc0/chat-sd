import os
import sys

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar os módulos diretamente
from app.storage.database_node import DatabaseNode
from app.storage.cluster_coordinator import ClusterCoordinator
from app.storage.storage_api import StorageAPI
from app.chat.Servidor import ServidorChat

# Resto do código permanece igual
def create_storage_system():
    """Configura e retorna o sistema de storage distribuído"""
    print("[*] Inicializando sistema de storage distribuído...")
    
    # Criar nós de database
    node1 = DatabaseNode(node_id="node1", storage_path="./data/node1")
    node2 = DatabaseNode(node_id="node2", storage_path="./data/node2")
    node3 = DatabaseNode(node_id="node3", storage_path="./data/node3")
    
    
    # Conectar os nós entre si
    node1.connect_to_node(node2)
    node2.connect_to_node(node3)
    node1.connect_to_node(node3)
    
    print(f"[+] Criados 3 nós de storage: {node1.node_id}, {node2.node_id}, {node3.node_id}")
    
    # Criar coordenador de cluster
    coordinator = ClusterCoordinator()
    coordinator.add_node(node1)
    coordinator.add_node(node2)
    coordinator.add_node(node3)
    
    print("[+] Coordenador de cluster inicializado com 3 nós")
    
    # Criar API de Storage
    storage_api = StorageAPI(replication_manager=None, cluster_coordinator=coordinator)
    
    print("[+] API de Storage inicializada")
    return storage_api

def main():
    """Função principal que inicia o sistema integrado"""
    # Garantir que os diretórios de dados existam
    os.makedirs("./data/node1", exist_ok=True)
    os.makedirs("./data/node2", exist_ok=True)
    os.makedirs("./data/node3", exist_ok=True)
    
    # Inicializar o sistema de storage
    storage_api = create_storage_system()
    
    # Configurar e iniciar o servidor de chat
    host = '0.0.0.0'  # Aceita conexões de qualquer IP
    port = 55555      # Porta padrão
    
    print(f"[*] Iniciando servidor de chat em {host}:{port} com storage integrado...")
    chat_server = ServidorChat(host=host, port=port, storage_api=storage_api)
    
    # Iniciar o servidor (este método bloqueia a execução)
    try:
        chat_server.iniciar_servidor()
    except KeyboardInterrupt:
        print("\n[!] Servidor encerrado pelo usuário")
    except Exception as e:
        print(f"[ERRO] Falha ao iniciar servidor: {e}")

if __name__ == "__main__":
    main()