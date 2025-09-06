import aiohttp
import jinja2
import urllib.parse
import logging

from FileStream.config import Telegram, Server
from FileStream.utils.database import Database
from FileStream.utils.human_readable import humanbytes

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)


class InvalidHash(Exception):
    """Raised when secure hash validation fails."""
    pass


async def render_page(db_id, secure_hash, src=None):
    # Fetch file data from DB
    file_data = await db.get_file(db_id)

    # Verify secure hash using unique_id (first 6 chars)
    if file_data["file_unique_id"][:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data['file_unique_id'][:6]}")
        logging.debug(f"Invalid hash for DB file with - ID {db_id}")
        raise InvalidHash

    # Build secure file URL
    src = urllib.parse.urljoin(
        Server.URL,
        f"dl/{file_data['_id']}?hash={secure_hash}"
    )

    # Human readable file size
    file_size = humanbytes(file_data["file_size"])
    file_name = file_data["file_name"].replace("_", " ")

    # Choose template based on file type
    tag = file_data["mime_type"].split("/")[0].strip()
    if tag in ["video", "audio"]:
        template_file = "FileStream/template/play.html"
    else:
        template_file = "FileStream/template/dl.html"
        async with aiohttp.ClientSession() as s:
            async with s.get(src) as u:
                file_size = humanbytes(int(u.headers.get("Content-Length")))

    # Render template
    with open(template_file, encoding="utf-8") as f:
        template = jinja2.Template(f.read())

    return template.render(
        file_name=file_name,
        file_url=src,
        file_size=file_size,
        file_unique_id=file_data["file_unique_id"],
    )
