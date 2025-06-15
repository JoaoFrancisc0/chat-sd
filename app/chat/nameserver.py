import socket
import threading
import json

class NameServer:
    
    def __init__(self, host='0.0.0.0', port=50000):
        """
        Inicializa o servidor de nomes.

        Args:
            host (str): Endereço IP para o servidor de nomes escutar.
            port (int): Porta para o servidor de nomes escutar.
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.name_mapping = {}  # Dicionário para mapear nomes para (IP, porta)
        self.lock = threading.Lock()

    def handle_client(self, conn, addr):
        """
        Lida com conexões de clientes (servidores de chat ou clientes de chat).
        """
        print(f"[NameServer] Nova conexão de {addr}")
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                
                request = json.loads(data.decode('utf-8'))
                
                # Se for um servidor de chat registrando-se
                if request.get('action') == 'register':
                    server_name = request.get('name')
                    server_port = request.get('port')
                    if server_name and server_port:
                        with self.lock:
                            self.name_mapping[server_name] = (addr[0], server_port)
                        print(f"[NameServer] Servidor '{server_name}' registrado com o endereço {addr[0]}:{server_port}")
                        conn.send(json.dumps({'status': 'registered'}).encode('utf-8'))
                
                # Se for um cliente de chat consultando um endereço
                elif request.get('action') == 'lookup':
                    server_name = request.get('name')
                    with self.lock:
                        address = self.name_mapping.get(server_name)
                    
                    if address:
                        response = {'status': 'found', 'address': address}
                    else:
                        response = {'status': 'not_found'}
                    conn.send(json.dumps(response).encode('utf-8'))

        except Exception as e:
            print(f"[NameServer] Erro: {e}")
        finally:
            print(f"[NameServer] Conexão de {addr} fechada.")
            conn.close()

    def start(self):
        """
        Inicia o servidor de nomes.
        """
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
