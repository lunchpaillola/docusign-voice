from app import create_app
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    config = Config()
    config.bind = ["localhost:3000"]
    asyncio.run(serve(app, config)) 