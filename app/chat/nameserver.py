import socket
import threading
import json

class NameServer:
    
    def __init__(self, host='0.0.0.0', port=50000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.name_mapping = {}
        self.lock = threading.Lock()

    def lookup_server(self):
        try:
            print(f"[*] Consultando o Servidor de Nomes em {self.name_server_host}:{self.name_server_port}...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
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
        
        print(f"[*] Tentando conexão direta...")
        self.host = '192.168.10.9'
        self.port = 8080
        print(f"[*] Usando endereço padrão: {self.host}:{self.port}")
        return True

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"[*] Servidor de Nomes iniciado e escutando em {self.host}:{self.port}")

        try:
            while True:
                conn, addr = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print("[NameServer] Desligando o servidor de nomes...")
        finally:
            self.server_socket.close()

if __name__ == '__main__':
    name_server = NameServer()
    name_server.start()
