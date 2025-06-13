# cliente.py
import socket
import threading

# Importa o protocolo
from ..protocol.marshaller import marshall_message
from ..protocol.unmarshaller import unmarshall
from ..protocol.message import create_message

class ClienteChat:
    """
    Classe que representa o cliente do chat.
    Conecta-se ao servidor e permite o envio e recebimento de mensagens.
    """
    def __init__(self, host='127.0.0.1', port=55555):
        """
        Inicializa o cliente com o host e a porta do servidor.

        Args:
            host (str): Endereço IP do servidor. '127.0.0.1' é o localhost.
            port (int): Porta do servidor.
        """
        self.host = host
        self.port = port
        self.cliente_socket = None
        self.nome_usuario = None

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
        message = f"({self.nome_usuario} entrou no chat)"
        mensagem_inicial = create_message(self.nome_usuario, message)
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
                mensagem_completa = create_message(self.nome_usuario, texto_mensagem)
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
        self.nome_usuario = input("Digite seu nome de usuário: ")
        
        # Cria e conecta o socket do cliente
        self.cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.cliente_socket.connect((self.host, self.port))
            print(f"[*] Conectado ao servidor de chat em {self.host}:{self.port}")
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
    # Se estiver rodando em máquinas diferentes na mesma rede,
    # substitua '127.0.0.1' pelo endereço IP da máquina do servidor.
    cliente = ClienteChat(host='127.0.0.1')
    cliente.iniciar()