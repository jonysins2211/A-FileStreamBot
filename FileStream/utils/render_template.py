from aiohttp import web
import os, re
from FileStream.utils.database import Database
from FileStream.config import Telegram

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)

async def dl_handler(request):
    file_id = request.match_info.get("id")
    file_data = await db.get_file(file_id)
    file_path = file_data["file_path"]   # Adjust if you store differently
    file_size = os.path.getsize(file_path)

    range_header = request.headers.get("Range", None)
    if range_header:
        # Parse Range header
        match = re.search(r"bytes=(\d+)-(\d*)", range_header)
        if match:
            start = int(match.group(1))
            end = match.group(2)
            end = int(end) if end else file_size - 1
        else:
            start, end = 0, file_size - 1
    else:
        start, end = 0, file_size - 1

    length = end - start + 1

    headers = {
        "Content-Type": file_data.get("mime_type", "video/mp4"),
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(length),
    }

    async def file_stream(resp):
        with open(file_path, "rb") as f:
            f.seek(start)
            chunk_size = 1024 * 1024  # 1 MB chunks
            remaining = length
            while remaining > 0:
                data = f.read(min(chunk_size, remaining))
                if not data:
                    break
                await resp.write(data)
                remaining -= len(data)

    status = 206 if range_header else 200
    return web.Response(body=file_stream, status=status, headers=headers)
