import socket
import threading
import uuid
from datetime import datetime
import json

from app.protocol.marshaller import marshall_message
from app.protocol.unmarshaller import unmarshall
from app.protocol.message import create_message

class ServidorChat:
    def __init__(self, name="Servidor.com", host='0.0.0.0', port=55555, storage_api=None, name_server_host='127.0.0.1', name_server_port=50000):
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

        try:
            msg_dict = unmarshall(mensagem)
        except Exception as e:
            print(f"[ERRO] Falha ao desserializar mensagem: {e}")
            return

        if self.storage_api:
            try:
                msg_id = str(uuid.uuid4())  # Generate unique ID
                sender = self.usuario_por_socket.get(conexao_cliente, "Desconhecido")
                timestamp = datetime.now().isoformat()
                
                message_data = {
                    "id": msg_id,
                    "sender": sender,
                    "content": msg_dict.get("content", ""),
                    "timestamp": timestamp,
                    "type": "text"
                }
                
                result = self.storage_api.store_message(msg_id, message_data)
                
                if result:
                    print(f"[+] Message {msg_id} replicated to all nodes")
                else:
                    print(f"[!] Failed to replicate message {msg_id}")
                    
            except Exception as e:
                print(f"[ERRO] Falha ao armazenar mensagem: {e}")

        mensagem_bytes = marshall_message(msg_dict)

        with self.lock:
            for cliente in self.clientes_conectados:
                if cliente != conexao_cliente:
                    try:
                        cliente.send(mensagem_bytes)
                    except socket.error:
                        self.remover_cliente(cliente)

    def remover_cliente(self, cliente_socket):
        if cliente_socket in self.clientes_conectados:
            usuario = self.usuario_por_socket.get(cliente_socket, "Desconhecido")
            cliente_socket.close()
            self.clientes_conectados.remove(cliente_socket)
            
            if cliente_socket in self.usuario_por_socket:
                del self.usuario_por_socket[cliente_socket]
                
            print(f"[-] Cliente {usuario} desconectado. {len(self.clientes_conectados)} cliente(s) conectado(s).")


    def lidar_cliente(self, conexao_cliente, endereco_cliente):
        print(f"[+] Nova conexão de {endereco_cliente[0]}:{endereco_cliente[1]}")

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
        if not self.storage_api:
            self._enviar_mensagem_sistema(conexao_cliente, "Histórico de mensagens não disponível.")
            return
            
        try:
            print(f"[*] Enviando histórico de mensagens para cliente (limite: {limite})...")
            self._enviar_mensagem_sistema(conexao_cliente, "Carregando histórico de mensagens...")
            self.storage_api.verify_nodes()
            
            mensagens = self.storage_api.get_messages(limit=limite)
            
            if not mensagens or len(mensagens) == 0:
                self._enviar_mensagem_sistema(conexao_cliente, "Nenhuma mensagem no histórico.")
                return
                
            try:
                mensagens.sort(key=lambda m: m.get('timestamp', ''), reverse=False)
            except Exception as e:
                print(f"[AVISO] Erro ao ordenar mensagens: {e}")
            
            mensagens_enviadas = 0
            for msg in mensagens:
                try:
                    sender = msg.get('sender', 'Desconhecido')
                    content = msg.get('content', '')
                    
                    history_msg = {
                        'type': 'text',
                        'sender_id': sender,
                        'content': content,
                        'timestamp': msg.get('timestamp', ''),
                        'is_history': True
                    }
                    
                    conexao_cliente.send(marshall_message(history_msg))
                    mensagens_enviadas += 1
                    
                    time.sleep(0.01)
                    
                except Exception as e:
                    print(f"[ERRO] Falha ao enviar mensagem do histórico: {e}")
            
            print(f"[+] Histórico enviado: {mensagens_enviadas} mensagens")
            self._enviar_mensagem_sistema(conexao_cliente, f"Histórico carregado: {mensagens_enviadas} mensagens.")
            
        except Exception as e:
            print(f"[ERRO] Falha ao enviar histórico: {e}")
            self._enviar_mensagem_sistema(conexao_cliente, "Erro ao carregar histórico de mensagens.")

    def _enviar_mensagem_sistema(self, conexao_cliente, conteudo):
        try:
            msg = {
                'type': 'text',
                'sender_id': 'Sistema',
                'content': conteudo,
                'timestamp': datetime.now().isoformat()
            }
            conexao_cliente.send(marshall_message(msg))
        except Exception as e:
            print(f"[ERRO] Falha ao enviar mensagem de sistema: {e}")



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
