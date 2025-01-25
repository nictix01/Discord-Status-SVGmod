from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
UPDATE_INTERVAL = 60  # Seconds between updates
ADMIN_ROLE_NAME = "Admin"  # Required role to use commands