import socket
import threading
import json

# Importa o protocolo
from app.protocol.marshaller import marshall_message
from app.protocol.unmarshaller import unmarshall

class ClienteChat:
    """
    Classe que representa o cliente do chat.
    Conecta-se ao servidor e permite o envio e recebimento de mensagens.
    """
    def __init__(self, server_name='Servidor.com', name_server_host='127.0.0.1', name_server_port=50000):
        """
        Inicializa o cliente com o host e a porta do servidor.

        Args:
            server_name (str): O nome do servidor de chat para se conectar.
            name_server_host (str): Endereço IP do servidor de nomes.
            name_server_port (int): Porta do servidor de nomes.
        """
        self.server_name = server_name
        self.name_server_host = name_server_host
        self.name_server_port = name_server_port
        self.host = None
        self.port = None
        self.cliente_socket = None
        self.nome_usuario = None

    def lookup_server(self):
        """
        Consulta o servidor de nomes para obter o endereço do servidor de chat.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.name_server_host, self.name_server_port))
                request = {'action': 'lookup', 'name': self.server_name}
                s.send(json.dumps(request).encode('utf-8'))
                response_data = s.recv(1024)
                response = json.loads(response_data.decode('utf-8'))
                if response.get('status') == 'found':
                    self.host, self.port = response['address']
                    return True
                else:
                    print(f"[ERRO] Servidor '{self.server_name}' não encontrado.")
                    return False
        except Exception as e:
            print(f"[ERRO] Falha ao consultar o Servidor de Nomes: {e}")
            return False

    def receber_mensagens(self):
        """
        Função executada em uma thread para receber mensagens do servidor.
        """
        while True:
            try:
                # Recebe a mensagem do servidor
                mensagem = self.cliente_socket.recv(4096)
                if not mensagem:
                    print("\n[!] Conexão com o servidor perdida.")
                    self.cliente_socket.close()
                    break
                try:
                    msg_dict = unmarshall(mensagem)
                    # Exibe a mensagem formatada
                    if msg_dict.get("type") == "text":
                        sender = msg_dict.get("sender_id", "Desconhecido")
                        content = msg_dict.get("content", "")
                        if sender == "Sistema":
                            print(content)
                        else:
                            print(f"{sender}: {content}")
                except Exception as e:
                    print(f"[ERRO] Mensagem inválida recebida: {e}")
            except ConnectionAbortedError:
                break
            except Exception as e:
                print(f"[ERRO] Erro ao receber mensagem: {e}")
                self.cliente_socket.close()
                break

    def enviar_mensagens(self):
        """
        Função executada na thread principal para enviar mensagens do usuário.
        """
        # A primeira mensagem enviada será o nome do usuário
        mensagem_inicial = {
            "type": "text",
            "sender_id": self.nome_usuario,
            "timestamp": "",
            "content": f"({self.nome_usuario} entrou no chat)"
        }
        self.cliente_socket.send(marshall_message(mensagem_inicial))

        while True:
            try:
                # Lê a entrada do usuário
                texto_mensagem = input()

                # Permite que o usuário saia do chat
                if texto_mensagem.lower() == 'sair':
                    print("[!] Saindo do chat...")
                    self.cliente_socket.close()
                    break
                
                # Formata a mensagem com o nome do usuário e envia
                mensagem_completa = {
                    "type": "text",
                    "sender_id": self.nome_usuario,
                    "timestamp": "",
                    "content": texto_mensagem
                }
                self.cliente_socket.send(marshall_message(mensagem_completa))
            except (EOFError, KeyboardInterrupt):
                # Lida com Ctrl+D ou Ctrl+C para sair
                print("\n[!] Desconectando...")
                self.cliente_socket.close()
                break
            except Exception as e:
                print(f"[ERRO] Erro ao enviar mensagem: {e}")
                self.cliente_socket.close()
                break


    def iniciar(self):
        """
        Inicia a conexão com o servidor e as threads de envio/recebimento.
        """
        if not self.lookup_server():
            return
        
        self.nome_usuario = input("Digite seu nome de usuário: ")
        
        # Cria e conecta o socket do cliente
        self.cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.cliente_socket.connect((self.host, self.port))
            print(f"[*] Conectado ao servidor de chat.")
            print("Digite 'sair' a qualquer momento para se desconectar.")
        except ConnectionRefusedError:
            print(f"[ERRO] Não foi possível se conectar ao servidor. Verifique se o servidor está rodando.")
            return

        # Cria e inicia a thread para receber mensagens
        thread_recebimento = threading.Thread(target=self.receber_mensagens)
        thread_recebimento.daemon = True
        thread_recebimento.start()

        # Inicia o loop de envio de mensagens na thread principal
        self.enviar_mensagens()

if __name__ == '__main__':
    # Agora o cliente se conecta usando o nome do servidor
    server_name_to_connect = input("Digite o nome do servidor (ex: Servidor.com): ")
    cliente = ClienteChat(server_name=server_name_to_connect)
    cliente.iniciar()
