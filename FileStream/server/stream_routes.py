from flask import Blueprint, request, Response, abort, stream_with_context
from pyrogram import Client
from FileStream.utils.file_properties import get_file_properties

stream_routes = Blueprint("stream_routes", __name__)

@stream_routes.route("/dl/<file_id>")
def stream_file(file_id):
    """
    Stream file directly for VLC, MX Player, nPlayer, Browser
    """
    app: Client = request.app

    try:
        # Get file info
        file_properties = app.loop.run_until_complete(get_file_properties(app, file_id))
        if not file_properties:
            abort(404)

        file_size = file_properties.file_size
        file_name = file_properties.file_name
        mime_type = file_properties.mime_type or "application/octet-stream"

        range_header = request.headers.get("Range", None)
        if range_header:
            byte1, byte2 = 0, None
            if "=" in range_header:
                ranges = range_header.split("=")[1]
                if "-" in ranges:
                    parts = ranges.split("-")
                    if parts[0]:
                        byte1 = int(parts[0])
                    if parts[1]:
                        byte2 = int(parts[1])
            length = file_size - byte1
            if byte2 is not None:
                length = byte2 - byte1 + 1

            def generate():
                for chunk in app.stream_media(file_id, offset=byte1, limit=length):
                    yield chunk

            rv = Response(stream_with_context(generate()),
                          status=206, mimetype=mime_type)
            rv.headers.add("Content-Range", f"bytes {byte1}-{byte1+length-1}/{file_size}")
            rv.headers.add("Accept-Ranges", "bytes")
            rv.headers.add("Content-Length", str(length))
            rv.headers.add("Content-Disposition", f'inline; filename="{file_name}"')
            return rv

        # Full file stream if no range header
        def generate_full():
            for chunk in app.stream_media(file_id):
                yield chunk

        rv = Response(stream_with_context(generate_full()), mimetype=mime_type)
        rv.headers.add("Content-Length", str(file_size))
        rv.headers.add("Content-Disposition", f'inline; filename="{file_name}"')
        rv.headers.add("Accept-Ranges", "bytes")
        return rv

    except Exception as e:
        print(f"Streaming error: {e}")
        abort(500)
