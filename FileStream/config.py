from os import environ as env
from dotenv import load_dotenv

load_dotenv()

class Telegram:
    API_ID = int(env.get("API_ID", "29224369"))
    API_HASH = str(env.get("API_HASH", "766627e7954ccc7d54fa5556f8ff3f65"))
    BOT_TOKEN = str(env.get("BOT_TOKEN", "7243323940:AAFTIOqvqnDcxe1V0e2Q4kRFfTm0vWZsgao"))
    OWNER_ID = int(env.get('OWNER_ID', '949657126'))
    WORKERS = int(env.get("WORKERS", "8"))  # 6 workers = 6 commands at once
    DATABASE_URL = str(env.get('DATABASE_URL', 'mongodb+srv://johnwick:NO5VzwVgSrJ9KBtC@cluster0.5iie9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'))
    UPDATES_CHANNEL = str(env.get('UPDATES_CHANNEL', "Telegram"))
    SESSION_NAME = str(env.get('SESSION_NAME', 'FileStream'))
    FORCE_SUB_ID = env.get('FORCE_SUB_ID', None)
    FORCE_SUB = env.get('FORCE_UPDATES_CHANNEL', False)
    FORCE_SUB = True if str(FORCE_SUB).lower() == "true" else False
    SLEEP_THRESHOLD = int(env.get("SLEEP_THRESHOLD", "60"))
    FILE_PIC = env.get('FILE_PIC', "https://graph.org/file/a319f6b9ce3b993c6e22f.jpg")
    START_PIC = env.get('START_PIC', "https://graph.org/file/a319f6b9ce3b993c6e22f.jpg")
    VERIFY_PIC = env.get('VERIFY_PIC', "https://graph.org/file/736e21cc0efa4d8c2a0e4.jpg")
    MULTI_CLIENT = False
    FLOG_CHANNEL = int(env.get("FLOG_CHANNEL", None))   # Logs channel for file logs
    ULOG_CHANNEL = int(env.get("ULOG_CHANNEL", None))   # Logs channel for user logs
    MODE = env.get("MODE", "primary")
    SECONDARY = True if MODE.lower() == "secondary" else False
    AUTH_USERS = list(set(int(x) for x in str(env.get("AUTH_USERS", "")).split()))

class Server:
    PORT = int(env.get("PORT", 8080))
    BIND_ADDRESS = str(env.get("BIND_ADDRESS", "0.0.0.0"))
    PING_INTERVAL = int(env.get("PING_INTERVAL", "1200"))
    HAS_SSL = str(env.get("HAS_SSL", "1").lower()) in ("1", "true", "t", "yes", "y")
    NO_PORT = str(env.get("NO_PORT", "1").lower()) in ("1", "true", "t", "yes", "y")
    FQDN = str(env.get("FQDN", BIND_ADDRESS))
    URL = "https://movie-loverz-bot-e60fe5f150c6.herokuapp.com/".format(
        "s" if HAS_SSL else "https://movie-loverz-bot-e60fe5f150c6.herokuapp.com/", FQDN, "https://movie-loverz-bot-e60fe5f150c6.herokuapp.com/" if NO_PORT else ":" + str(PORT)
    )



