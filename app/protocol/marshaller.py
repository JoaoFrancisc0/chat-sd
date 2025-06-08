from app.protocol.message import message_to_dict
from . import json

def marshall_message(msg: dict) -> bytes:
    """Converte dicionário de mensagem em bytes JSON."""
    payload = message_to_dict(msg)
    return json.dumps(payload).encode("utf-8")


def marshall_file_chunk(file_chunk: dict) -> bytes:
    """Converte dicionário de chunk de arquivo em bytes JSON."""
    # Supondo que file_chunk já esteja em formato de dicionário válido
    return json.dumps(file_chunk).encode("utf-8")
