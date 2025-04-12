import os
from dotenv import load_dotenv

def get_bot_token() -> str:
    """
    Get the bot token from environment variables.
    
    Returns:
        str: The bot token
        
    Raises:
        ValueError: If BOT_TOKEN environment variable is not set
    """
    load_dotenv()
    token = os.getenv('BOT_TOKEN')
    if token is None:
        raise ValueError("BOT_TOKEN environment variable is not set")
    return token