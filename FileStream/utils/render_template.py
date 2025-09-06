import aiohttp
import jinja2
import urllib.parse
from FileStream.config import Telegram, Server
from FileStream.utils.database import Database
from FileStream.utils.human_readable import humanbytes

# Initialize database
db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)

# Jinja2 template loader
def load_template(path: str):
    with open(path, encoding="utf-8") as f:
        return jinja2.Template(f.read())

async def render_page(db_id: str):
    """
    Render a play/download page for the given file ID
    """
    file_data = await db.get_file(db_id)
    if not file_data:
        return "File not found"

    # File details
    file_url = urllib.parse.urljoin(Server.URL, f"dl/{file_data['_id']}")
    file_size = humanbytes(file_data["file_size"])
    file_name = file_data["file_name"].replace("_", " ")
    mime_type = file_data.get("mime_type", "")

    # Decide template: play.html for videos, dl.html for others
    if mime_type.startswith("video"):
        template_file = "FileStream/template/play.html"
    else:
        template_file = "FileStream/template/dl.html"
        # If not a video, confirm size via HEAD request
        async with aiohttp.ClientSession() as session:
            async with session.head(file_url) as resp:
                if resp.headers.get("Content-Length"):
                    file_size = humanbytes(int(resp.headers["Content-Length"]))

    # Load template
    template = load_template(template_file)

    # Render with values
    return template.render(
        file_name=file_name,
        file_url=file_url,
        file_size=file_size
    )
