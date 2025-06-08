
DATABASE_HOST = 'localhost'
DATABASE_PORT = 27017
DATABASE_NAME = 'chat_db'
REPLICATION_FACTOR = 3
CLUSTER_NODES = [
    {'host': 'localhost', 'port': 27017},
    {'host': 'localhost', 'port': 27018},
    {'host': 'localhost', 'port': 27019},
]
TIMEOUT = 5000  # in milliseconds
LOG_LEVEL = 'INFO'  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
