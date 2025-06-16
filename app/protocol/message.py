from . import datetime, timezone

def create_message(sender_id: str, content: str) -> dict:
    return {
        "type": "text",
        "sender_id": sender_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content": content,
        "message_id": "",
    }


def message_to_dict(msg: dict) -> dict:
    return msg


def dict_to_message(data: dict) -> dict:
    # Aqui poderíamos validar campos obrigatórios
    if data.get("type") != "text":
        raise ValueError(f"Tipo inesperado: {data.get('type')}")
    return {
        "type": data["type"],
        "sender_id": data["sender_id"],
        "timestamp": data["timestamp"],
        "content": data["content"],
        "message_id": "",
    }
