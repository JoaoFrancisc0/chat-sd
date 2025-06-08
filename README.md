# Chat-SD Project

Chat-SD is a distributed chat application that allows users to communicate in real-time. The application consists of a server that manages multiple client connections and a protocol for message handling and file transfers. The storage layer is designed to be fault-tolerant and distributed, ensuring data integrity and availability.

## Project Structure

```
chat-sd
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── chat
│   │   ├── Cliente.py
│   │   └── Servidor.py
│   ├── protocol
│   │   ├── __init__.py
│   │   ├── file_transfer.py
│   │   ├── marshaller.py
│   │   ├── message.py
│   │   └── unmarshaller.py
│   └── storage
│       ├── __init__.py
│       ├── database_node.py
│       ├── replication_manager.py
│       ├── cluster_coordinator.py
│       ├── storage_api.py
│       └── sync_utils.py
├── config
│   └── settings_template.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Features

- **Real-time Messaging**: Users can send and receive messages instantly.
- **File Transfer**: Supports sending files in chunks.
- **Distributed Database**: Utilizes a fault-tolerant distributed database architecture.
- **Scalability**: Can handle multiple clients simultaneously.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd chat-sd
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the server:
   ```
   python run_integrated_chat.py
   ```
2. Connect a client:
   ```
   python -m app.chat.cliente
   ```

## Configuration

Customize the settings in `config/settings_template.py` as needed for your environment.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
