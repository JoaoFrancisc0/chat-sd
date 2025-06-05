from message import dict_to_message
from file_transfer import file_dict_to_chunks
from . import json

def unmarshall(payload: bytes) -> dict:
    """Converte bytes JSON em dicionário com dados de texto ou arquivo."""
    data = json.loads(payload.decode("utf-8"))
    tipo = data.get("type")
    if tipo == "text":
        return dict_to_message(data)
    elif tipo == "file":
        return file_dict_to_chunks(data)
    else:
        raise ValueError(f"Tipo desconhecido: {tipo}")
    