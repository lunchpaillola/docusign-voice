from app import create_app
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(
        host='0.0.0.0',  # Makes it externally visible
        port=port,
        debug=(os.getenv('NODE_ENV') == 'development')
    ) 