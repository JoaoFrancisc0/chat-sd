import socket
import threading
import json

from app.protocol.marshaller import marshall_message
from app.protocol.unmarshaller import unmarshall
from app.protocol.unmarshaller import unmarshall_with_length
from app.protocol.message import create_message

class ClienteChat:

    def __init__(self, server_name='Servidor.com', name_server_host='0.0.0.0', name_server_port=50000):
        self.server_name = server_name
        self.name_server_host = name_server_host
        self.name_server_port = name_server_port
        self.host = None
        self.port = None
        self.cliente_socket = None
        self.nome_usuario = None

    def lookup_server(self):
        try:
            print(f"[*] Consultando o Servidor de Nomes em {self.name_server_host}:{self.name_server_port}...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)  # Add timeout
                s.connect((self.name_server_host, self.name_server_port))
                request = {'action': 'lookup', 'name': self.server_name}
                s.send(json.dumps(request).encode('utf-8'))
                response_data = s.recv(1024)
                response = json.loads(response_data.decode('utf-8'))
                if response.get('status') == 'found':
                    self.host, self.port = response['address']
                    print(f"[+] Servidor encontrado em {self.host}:{self.port}")
                    return True
                else:
                    print(f"[AVISO] Servidor '{self.server_name}' não encontrado no Servidor de Nomes.")
                    return False
        except socket.timeout:
            print(f"[AVISO] Tempo limite excedido ao contatar o Servidor de Nomes.")
        except ConnectionRefusedError:
            print(f"[AVISO] Servidor de Nomes não está aceitando conexões.")
        except Exception as e:
            print(f"[AVISO] Falha ao consultar o Servidor de Nomes: {e}")
    
        # Fallback to direct connection
        print(f"[*] Tentando conexão direta...")
        self.host = '192.168.10.9'  # Use your actual IP here
        self.port = 8080
        print(f"[*] Usando endereço padrão: {self.host}:{self.port}")
        return True

    def receber_mensagens(self):
  
        buffer = b""
        
        while True:
            try:
                chunk = self.cliente_socket.recv(4096)
                if not chunk:
                    print("\n[!] Conexão com o servidor perdida.")
                    self.cliente_socket.close()
                    break
                    
                buffer += chunk
                
                while buffer:
                    try:
                        msg_dict, consumed = unmarshall_with_length(buffer)
                        
                        buffer = buffer[consumed:]
                        
                        if msg_dict.get("type") == "text":
                            sender = msg_dict.get("sender_id", "Desconhecido")
                            content = msg_dict.get("content", "")
                            is_history = msg_dict.get("is_history", False)
                            
                            if sender == "Sistema":
                                print(f"[Sistema] {content}")
                            else:
                                # Add [Histórico] prefix for history messages
                                prefix = "[Histórico] " if is_history else ""
                                print(f"{prefix}{sender}: {content}")
                    
                    except ValueError as e:
                        if "desconhecido" in str(e).lower():
                            print(f"[ERRO] {e}")
                            buffer = b""
                        else:
                            print(f"[ERRO] Erro ao processar mensagem: {e}")
                            break
                            
                    except json.JSONDecodeError as e:
                        if "Expecting value" in str(e) or "Unterminated string" in str(e):
                            break
                        else:
                            print(f"[ERRO] Erro de JSON: {e}")
                            buffer = b""  
                            break
                            
                    except Exception as e:
                        print(f"[ERRO] Mensagem inválida recebida: {e}")
                        buffer = b"" 
                        break
                        
            except ConnectionAbortedError:
                break
            except Exception as e:
                print(f"[ERRO] Erro ao receber mensagem: {e}")
                self.cliente_socket.close()
                break

    def enviar_mensagens(self):
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
