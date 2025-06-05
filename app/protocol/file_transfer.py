from . import datetime, timezone

def create_file_transfer(sender_id: str, filename: str, data_bytes: bytes, chunk_size: int = 65536) -> list:
    """
    Divide um arquivo em chunks de 64kb e retorna uma lista de dicionários,
    cada um representando um pedaço.
    """
    total_size = len(data_bytes)
    chunks = []
    total_chunks = (total_size + chunk_size - 1) // chunk_size
    for idx in range(total_chunks):
        start = idx * chunk_size
        end = start + chunk_size
        chunk_data = data_bytes[start:end]
        chunks.append({
            "type": "file",
            "sender_id": sender_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "filename": filename,
            "filesize": total_size,
            "chunk_index": idx,
            "total_chunks": total_chunks,
            "data": chunk_data.hex(),  # converte bytes para hex para JSON
        })
    return chunks
