from app.protocol.message import dict_to_message
from app.protocol.file_transfer import file_dict_to_chunks
from . import json

def unmarshall(payload: bytes) -> dict:
    data = json.loads(payload.decode("utf-8"))
    tipo = data.get("type")
    if tipo == "text":
        return dict_to_message(data)
    elif tipo == "file":
        return file_dict_to_chunks(data)
    else:
        raise ValueError(f"Tipo desconhecido: {tipo}")
    

def unmarshall_with_length(buffer: bytes):
    try:
        buffer_str = buffer.decode("utf-8")
        data = json.loads(buffer_str)
        consumed = len(buffer_str.encode("utf-8"))
        
        tipo = data.get("type")
        if tipo == "text":
            return dict_to_message(data), consumed
        elif tipo == "file":
            return file_dict_to_chunks(data), consumed
        else:
            raise ValueError(f"Tipo desconhecido: {tipo}")
            
    except json.JSONDecodeError as e:
        if "Extra data" in str(e):
            valid_json = buffer[:e.pos].decode("utf-8")
            data = json.loads(valid_json)
            
            tipo = data.get("type")
            if tipo == "text":
                return dict_to_message(data), e.pos
            elif tipo == "file":
                return file_dict_to_chunks(data), e.pos
            else:
                raise ValueError(f"Tipo desconhecido: {tipo}")
        else:
            raise