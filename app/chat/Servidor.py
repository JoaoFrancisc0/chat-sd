import socket
import threading
import json
import uuid
from datetime import datetime

class ServidorChat:
    """
    Classe que representa o servidor de chat em grupo.
    Gerencia múltiplas conexões de clientes e retransmite as mensagens para o grupo.
    """
    def __init__(self, host='0.0.0.0', port=55555, storage_api=None):
        """
        Inicializa o servidor com o host e a porta especificados.

        Args:
            host (str): Endereço IP para o servidor escutar. '0.0.0.0' permite conexões de qualquer interface.
            port (int): Porta para o servidor escutar.
            storage_api (StorageAPI): API para armazenamento distribuído das mensagens.
        """
        self.host = host
        self.port = port
        self.servidor_socket = None
        self.clientes_conectados = [] # Lista para armazenar os sockets dos clientes
        self.lock = threading.Lock() # Lock para garantir acesso seguro à lista de clientes
        self.storage_api = storage_api # API para armazenamento distribuído
        self.usuario_por_socket = {} # Mapeia sockets para nomes de usuário

    def transmitir_mensagem(self, mensagem, conexao_cliente):
        """
        Envia uma mensagem para todos os clientes conectados, exceto para o remetente.
        Também armazena a mensagem no sistema de storage distribuído.

        Args:
            mensagem (bytes): A mensagem a ser transmitida.
            conexao_cliente (socket): O socket do cliente que enviou a mensagem.
        """
        # Primeiro, armazena a mensagem no storage se disponível
        if self.storage_api:
            try:
                # Decodifica a mensagem
                msg_text = mensagem.decode('utf-8')
                
                # Cria um ID único para a mensagem
                msg_id = str(uuid.uuid4())
                
                # Prepara dados para armazenamento
                message_data = {
                    "id": msg_id,
                    "content": msg_text,
                    "timestamp": datetime.now().isoformat(),
                    "sender": self.usuario_por_socket.get(conexao_cliente, "Desconhecido")
                }
                
                # Armazena no storage distribuído
                self.storage_api.create(message_data)
                print(f"[*] Mensagem armazenada no storage com ID: {msg_id}")
            except Exception as e:
                print(f"[ERRO] Falha ao armazenar mensagem: {e}")
        
        # Depois, transmite a mensagem para todos os clientes conectados
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
                # Recebe a mensagem do cliente (o tamanho do buffer pode ser ajustado)
                mensagem = conexao_cliente.recv(4096)
                if mensagem:
                    msg_text = mensagem.decode('utf-8')
                    print(f"[*] Mensagem recebida de {endereco_cliente[0]}: {msg_text}")
                    
                    # Extrai nome de usuário da primeira mensagem
                    if conexao_cliente not in self.usuario_por_socket:
                        # Processa primeira mensagem para extrair usuário
                        if msg_text.startswith("(") and "entrou no chat" in msg_text:
                            usuario = msg_text.split("(")[1].split(" entrou no chat")[0]
                            self.usuario_por_socket[conexao_cliente] = usuario
                            print(f"[*] Usuário identificado: {usuario}")
                    
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
            # Enviar mensagem informativa
            conexao_cliente.send("[Sistema] Carregando histórico de mensagens...\n".encode('utf-8'))
        
            # Buscar as mensagens armazenadas, ordenadas por timestamp (mais recentes primeiro)
            mensagens = self.storage_api.list_records(limit=limite)
            
            if not mensagens:
                conexao_cliente.send("[Sistema] Nenhuma mensagem anterior encontrada.\n".encode('utf-8'))
                return
                
            # Enviar cabeçalho do histórico
            conexao_cliente.send(f"[Sistema] Exibindo as últimas {len(mensagens)} mensagens:\n".encode('utf-8'))
            
            # Ordenar mensagens por timestamp (da mais antiga para a mais recente)
            mensagens.sort(key=lambda x: x.get('timestamp', ''))
            
            # Enviar cada mensagem do histórico
            for msg in mensagens:
                try:
                    # Formatar mensagem para exibição
                    sender = msg.get('sender', 'Desconhecido')
                    content = msg.get('content', '')
                    
                    # Se content já incluir o sender (como em "Usuario: texto"), usar diretamente
                    if ': ' in content and not content.startswith('[Sistema]'):
                        formatted_msg = f"{content}\n"
                    else:
                        formatted_msg = f"{sender}: {content}\n"
                    
                    conexao_cliente.send(formatted_msg.encode('utf-8'))
                except Exception as e:
                    print(f"[ERRO] Erro ao enviar mensagem do histórico: {e}")
            
            # Enviar separador após o histórico
            conexao_cliente.send("[Sistema] Fim do histórico. Você está conectado ao chat.\n".encode('utf-8'))
            
        except Exception as e:
            print(f"[ERRO] Falha ao recuperar histórico: {e}")
            conexao_cliente.send("[Sistema] Erro ao carregar histórico de mensagens.\n".encode('utf-8'))

    def iniciar_servidor(self):
        """
        Inicia o servidor, aguardando por conexões de clientes.
        """
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