import socket
import threading

class ServidorChat:
    """
    Classe que representa o servidor de chat em grupo.
    Gerencia múltiplas conexões de clientes e retransmite as mensagens para o grupo.
    """
    def __init__(self, host='0.0.0.0', port=55555):
        """
        Inicializa o servidor com o host e a porta especificados.

        Args:
            host (str): Endereço IP para o servidor escutar. '0.0.0.0' permite conexões de qualquer interface.
            port (int): Porta para o servidor escutar.
        """
        self.host = host
        self.port = port
        self.servidor_socket = None
        self.clientes_conectados = [] # Lista para armazenar os sockets dos clientes
        self.lock = threading.Lock() # Lock para garantir acesso seguro à lista de clientes

    def transmitir_mensagem(self, mensagem, conexao_cliente):
        """
        Envia uma mensagem para todos os clientes conectados, exceto para o remetente.

        Args:
            mensagem (bytes): A mensagem a ser transmitida.
            conexao_cliente (socket): O socket do cliente que enviou a mensagem.
        """
        with self.lock:
            for cliente in self.clientes_conectados:
                # Verifica se o cliente não é o remetente para evitar que ele receba sua própria mensagem
                if cliente != conexao_cliente:
                    try:
                        cliente.send(mensagem)
                    except socket.error:
                        # Em caso de erro (ex: cliente desconectado), remove-o da lista
                        self.remover_cliente(cliente)

    def remover_cliente(self, cliente_socket):
        """Remove um cliente da lista de conectados."""
        if cliente_socket in self.clientes_conectados:
            cliente_socket.close()
            self.clientes_conectados.remove(cliente_socket)
            print(f"[-] Conexão perdida. {len(self.clientes_conectados)} cliente(s) conectado(s).")


    def lidar_cliente(self, conexao_cliente, endereco_cliente):
        """
        Função executada em uma thread para cada cliente.
        Recebe mensagens do cliente e as retransmite para o grupo.

        Args:
            conexao_cliente (socket): O objeto de socket para o cliente.
            endereco_cliente (tuple): O endereço (IP, porta) do cliente.
        """
        print(f"[+] Nova conexão de {endereco_cliente[0]}:{endereco_cliente[1]}")

        while True:
            try:
                # Recebe a mensagem do cliente (o tamanho do buffer pode ser ajustado)
                mensagem = conexao_cliente.recv(4096)
                if mensagem:
                    print(f"[*] Mensagem recebida de {endereco_cliente[0]}: {mensagem.decode('utf-8')}")
                    # Retransmite a mensagem para os outros clientes
                    self.transmitir_mensagem(mensagem, conexao_cliente)
                else:
                    # Se não receber dados, o cliente se desconectou
                    self.remover_cliente(conexao_cliente)
                    break
            except socket.error:
                # Se ocorrer um erro, remove o cliente e encerra o loop
                with self.lock:
                    self.remover_cliente(conexao_cliente)
                break

    def iniciar_servidor(self):
        """
        Inicia o servidor, aguardando por conexões de clientes.
        """
        self.servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor_socket.bind((self.host, self.port))
        self.servidor_socket.listen()

        print(f"[*] Servidor de chat iniciado e escutando em {self.host}:{self.port}")

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

if __name__ == '__main__':
    # Cria uma instância do servidor e o inicia
    servidor_chat = ServidorChat()
    servidor_chat.iniciar_servidor()