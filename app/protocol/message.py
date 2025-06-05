from . import datetime, timezone

def create_message(sender_id: str, content: str) -> dict:
    """Cria um dicionário representando uma mensagem de texto."""
    return {
        "type": "text",
        "sender_id": sender_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content": content,
    }


def message_to_dict(msg: dict) -> dict:
    """Retorna a representação em dicionário (identidade, já é dict)."""
    return msg


def dict_to_message(data: dict) -> dict:
    """Valida e retorna o dicionário da mensagem."""
    # Aqui poderíamos validar campos obrigatórios
    if data.get("type") != "text":
        raise ValueError(f"Tipo inesperado: {data.get('type')}")
    return {
        "type": data["type"],
        "sender_id": data["sender_id"],
        "timestamp": data["timestamp"],
        "content": data["content"],
    }
