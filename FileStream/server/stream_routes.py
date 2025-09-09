import math
import mimetypes
import logging
import traceback
from aiohttp import web
from FileStream.bot import multi_clients, work_loads
from FileStream.config import Telegram
from FileStream.server.exceptions import FIleNotFound, InvalidHash
from FileStream import utils

routes = web.RouteTableDef()

@routes.get("/dl/{file_id}")
async def stream_file(request: web.Request):
    """
    Stream file directly for VLC, MX Player, nPlayer, Browser
    """
    try:
        file_id = request.match_info["file_id"]

        # Pick least loaded client
        index = min(work_loads, key=work_loads.get)
        tg_client = multi_clients[index]

        # Create streamer
        tg_connect = utils.ByteStreamer(tg_client)
        file_info = await tg_connect.get_file_properties(file_id, multi_clients)

        if not file_info:
            raise FIleNotFound("File not found!")

        file_size = file_info.file_size
        file_name = utils.get_name(file_info)
        mime_type = file_info.mime_type or mimetypes.guess_type(file_name)[0] or "application/octet-stream"

        # Handle Range header
        range_header = request.headers.get("Range", None)
        if range_header:
            from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
            from_bytes = int(from_bytes) if from_bytes else 0
            until_bytes = int(until_bytes) if until_bytes else file_size - 1
        else:
            from_bytes = 0
            until_bytes = file_size - 1

        if from_bytes < 0 or until_bytes >= file_size or until_bytes < from_bytes:
            return web.Response(
                status=416,
                headers={"Content-Range": f"bytes */{file_size}"},
                text="416: Range Not Satisfiable"
            )

        chunk_size = 1024 * 1024
        offset = from_bytes - (from_bytes % chunk_size)
        first_part_cut = from_bytes - offset
        last_part_cut = until_bytes % chunk_size + 1
        part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)

        body = tg_connect.yield_file(
            file_info, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
        )

        headers = {
            "Content-Type": mime_type,
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(until_bytes - from_bytes + 1),
            "Accept-Ranges": "bytes",
            "Content-Disposition": f'inline; filename="{file_name}"'
        }

        return web.Response(
            status=206 if range_header else 200,
            body=body,
            headers=headers
        )

    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except Exception as e:
        traceback.print_exc()
        logging.error(f"Streaming error: {e}")
        raise web.HTTPInternalServerError(text="Internal Server Error")
