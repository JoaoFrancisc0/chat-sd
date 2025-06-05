from message import message_to_dict
from . import json

def marshall_message(msg: dict) -> bytes:
    """Converte dicionário de mensagem em bytes JSON."""
    payload = message_to_dict(msg)
    return json.dumps(payload).encode("utf-8")
