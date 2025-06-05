from . import datetime, timezone

def create_message(sender_id: str, content: str) -> dict:
    """Cria um dicionário representando uma mensagem de texto."""
    return {
        "type": "text",
        "sender_id": sender_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content": content,
    }
