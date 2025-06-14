import socket
import threading
import uuid
from datetime import datetime
import json

# Importa o protocolo
from app.protocol.marshaller import marshall_message
from app.protocol.unmarshaller import unmarshall
from app.protocol.message import create_message

class ServidorChat:
    """
    Classe que representa o servidor de chat em grupo.
    Gerencia múltiplas conexões de clientes e retransmite as mensagens para o grupo.
    """
    def __init__(self, name="Servidor.com", host='0.0.0.0', port=55555, storage_api=None, name_server_host='127.0.0.1', name_server_port=50000):
        """
        Inicializa o servidor com o host e a porta especificados.

        Args:
            host (str): Endereço IP para o servidor escutar. '0.0.0.0' permite conexões de qualquer interface.
            port (int): Porta para o servidor escutar.
            storage_api (StorageAPI): API para armazenamento distribuído das mensagens.
        """
        self.name = name
        self.host = host
        self.port = port
        self.servidor_socket = None
        self.clientes_conectados = [] # Lista para armazenar os sockets dos clientes
        self.lock = threading.Lock() # Lock para garantir acesso seguro à lista de clientes
        self.storage_api = storage_api # API para armazenamento distribuído
        self.usuario_por_socket = {} # Mapeia sockets para nomes de usuário
        self.name_server_host = name_server_host
        self.name_server_port = name_server_port

    def register_with_name_server(self):
        """
        Registra este servidor de chat com o servidor de nomes.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.name_server_host, self.name_server_port))
                request = {'action': 'register', 'name': self.name, 'port': self.port}
                s.send(json.dumps(request).encode('utf-8'))
                response = s.recv(1024)
                print(f"[*] Resposta do Servidor de Nomes: {response.decode('utf-8')}")
        except Exception as e:
            print(f"[ERRO] Falha ao registrar com o Servidor de Nomes: {e}")

    def transmitir_mensagem(self, mensagem, conexao_cliente):
        """
        Envia uma mensagem para todos os clientes conectados, exceto para o remetente.
        Também armazena a mensagem no sistema de storage distribuído.
        """
        # Decodifica e desserializa a mensagem recebida
        try:
            msg_dict = unmarshall(mensagem)
        except Exception as e:
            print(f"[ERRO] Falha ao desserializar mensagem: {e}")
            return

        # Armazena no storage se disponível
        if self.storage_api:
            try:
                msg_id = str(uuid.uuid4())
                sender = self.usuario_por_socket.get(conexao_cliente, "Desconhecido")
                message = msg_dict.get("content", "")
                message_data = create_message(sender, message)
                self.storage_api.create(msg_id, message_data)
                print(f"[*] Mensagem armazenada no storage com ID: {msg_id}")
            except Exception as e:
                print(f"[ERRO] Falha ao armazenar mensagem: {e}")

        # Re-serializa a mensagem para enviar aos outros clientes
        mensagem_bytes = marshall_message(msg_dict)

        with self.lock:
            for cliente in self.clientes_conectados:
                if cliente != conexao_cliente:
                    try:
                        cliente.send(mensagem_bytes)
                    except socket.error:
                        self.remover_cliente(cliente)

    def remover_cliente(self, cliente_socket):
        """Remove um cliente da lista de conectados."""
        if cliente_socket in self.clientes_conectados:
            usuario = self.usuario_por_socket.get(cliente_socket, "Desconhecido")
            cliente_socket.close()
            self.clientes_conectados.remove(cliente_socket)
            
            # Remove do mapeamento de usuários
            if cliente_socket in self.usuario_por_socket:
                del self.usuario_por_socket[cliente_socket]
                
            print(f"[-] Cliente {usuario} desconectado. {len(self.clientes_conectados)} cliente(s) conectado(s).")


    def lidar_cliente(self, conexao_cliente, endereco_cliente):
        """
        Função executada em uma thread para cada cliente.
        Recebe mensagens do cliente e as retransmite para o grupo.

        Args:
            conexao_cliente (socket): O objeto de socket para o cliente.
            endereco_cliente (tuple): O endereço (IP, porta) do cliente.
        """
        print(f"[+] Nova conexão de {endereco_cliente[0]}:{endereco_cliente[1]}")

        # Envia histórico de mensagens para o novo cliente
        if self.storage_api:
            try:
                self.enviar_historico(conexao_cliente)
            except Exception as e:
                print(f"[ERRO] Falha ao enviar histórico: {e}")

        while True:
            try:
                mensagem = conexao_cliente.recv(4096)
                if mensagem:
                    try:
                        msg_dict = unmarshall(mensagem)
                        print(f"[*] Mensagem recebida de {endereco_cliente[0]}: {msg_dict.get('content', '')}")
                    except Exception as e:
                        print(f"[ERRO] Mensagem inválida recebida: {e}")
                        continue

                    # Extrai nome de usuário da primeira mensagem
                    if conexao_cliente not in self.usuario_por_socket:
                        if msg_dict.get("type") == "text" and "entrou no chat" in msg_dict.get("content", ""):
                            usuario = msg_dict.get("sender_id", "Desconhecido")
                            self.usuario_por_socket[conexao_cliente] = usuario
                            print(f"[*] Usuário identificado: {usuario}")

                    self.transmitir_mensagem(mensagem, conexao_cliente)
                else:
                    self.remover_cliente(conexao_cliente)
                    break
            except socket.error:
                with self.lock:
                    self.remover_cliente(conexao_cliente)
                break

    def enviar_historico(self, conexao_cliente, limite=50):
        """
        Envia as últimas mensagens do histórico para um cliente recém-conectado.
        
        Args:
            conexao_cliente (socket): Socket do cliente para enviar o histórico
            limite (int): Número máximo de mensagens a recuperar
        """
        if not self.storage_api:
            return
            
        try:
            sender = "Sistema"
            message = "[Sistema] Carregando histórico de mensagens..."
            conexao_cliente.send(marshall_message(create_message(sender, message)))
        
            mensagens = self.storage_api.list_records(limit=limite)
            
            if not mensagens:
                message = "[Sistema] Nenhuma mensagem anterior encontrada."
                conexao_cliente.send(marshall_message(create_message(sender, message)))
                return
                
            message = f"[Sistema] Exibindo as últimas {len(mensagens)} mensagens:"
            conexao_cliente.send(marshall_message(create_message(sender, message)))
            
            mensagens.sort(key=lambda x: x.get('timestamp', ''))
            
            for msg in mensagens:
                try:
                    sender = msg.get('sender', 'Desconhecido')
                    message = msg.get('content', '')
                    create_message(sender, message)
                    conexao_cliente.send(marshall_message(create_message(sender, message)))
                except Exception as e:
                    print(f"[ERRO] Erro ao enviar mensagem do histórico: {e}")
            
            sender = "Sistema"
            message = "[Sistema] Fim do histórico. Você está conectado ao chat."
            conexao_cliente.send(marshall_message(create_message(sender, message)))
        except Exception as e:
            print(f"[ERRO] Falha ao recuperar histórico: {e}")
            sender = "Sistema"
            message = "[Sistema] Erro ao carregar histórico de mensagens."
            conexao_cliente.send(marshall_message(create_message(sender, message)))

    def iniciar_servidor(self):
        """
        Inicia o servidor, aguardando por conexões de clientes.
        """
        self.register_with_name_server()
        self.servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor_socket.bind((self.host, self.port))
        self.servidor_socket.listen()

        print(f"[*] Servidor de chat iniciado e escutando em {self.host}:{self.port}")
        print(f"[*] Storage {'conectado' if self.storage_api else 'não disponível'}")

        while True:
            try:
                # Aceita uma nova conexão
                conexao_cliente, endereco_cliente = self.servidor_socket.accept()

                # Adiciona o novo cliente à lista de forma segura
                with self.lock:
                    self.clientes_conectados.append(conexao_cliente)
                
                print(f"[!] Conexão aceita de {endereco_cliente[0]}:{endereco_cliente[1]}")
                print(f"[*] Total de clientes conectados: {len(self.clientes_conectados)}")

                # Cria e inicia uma nova thread para gerenciar a comunicação com o cliente
                thread_cliente = threading.Thread(target=self.lidar_cliente, args=(conexao_cliente, endereco_cliente))
                thread_cliente.daemon = True # Permite que o programa principal saia mesmo que as threads estejam ativas
                thread_cliente.start()

            except KeyboardInterrupt:
                print("\n[!] Servidor sendo desligado...")
                self.servidor_socket.close()
                break
            except Exception as e:
                print(f"[ERRO] Ocorreu um erro: {e}")
                self.servidor_socket.close()
                break

# Renomear a classe principal para compatibilidade com o main.py
Servidor = ServidorChat

if __name__ == '__main__':
    servidor_chat = ServidorChat()
    servidor_chat.iniciar_servidor()
