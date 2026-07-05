import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
from flask import Flask
from flask_cors import CORS
from routes import api
from database import Database
import logging
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

app.register_blueprint(api)

@app.before_request
def initialize():
    # Attempt to initialize DB if it hasn't been done. 
    if not getattr(app, '_db_initialized', False):
        try:
            Database.initialize_db()
            app._db_initialized = True
        except Exception as e:
            logger.warning(f"Failed to auto-initialize DB. Check credentials. {e}")

if __name__ == '__main__':
    port = 5000
    logger.info(f"Starting Customer Review Analysis Agent server on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)
