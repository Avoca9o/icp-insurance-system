import os
import pytest
from bot.config import get_bot_token

@pytest.fixture
def clean_modules():
    # Save original environment and .env file state
    original_token = os.environ.get('BOT_TOKEN')
    env_file = '.env'
    env_exists = os.path.exists(env_file)
    env_content = None
    
    if env_exists:
        with open(env_file, 'r') as f:
            env_content = f.read()
        os.remove(env_file)
    
    # Clean up before test
    if 'BOT_TOKEN' in os.environ:
        del os.environ['BOT_TOKEN']
    
    yield
    
    # Restore original environment and .env file
    if original_token is not None:
        os.environ['BOT_TOKEN'] = original_token
    elif 'BOT_TOKEN' in os.environ:
        del os.environ['BOT_TOKEN']
    
    if env_exists and env_content is not None:
        with open(env_file, 'w') as f:
            f.write(env_content)

def test_bot_token_from_env(clean_modules):
    # Set test token
    test_token = "test_token_123"
    os.environ['BOT_TOKEN'] = test_token
    
    # Verify token is correctly retrieved
    assert get_bot_token() == test_token

def test_bot_token_missing(clean_modules):
    # Verify exception is raised when token is missing
    with pytest.raises(ValueError, match="BOT_TOKEN environment variable is not set"):
        get_bot_token() 