import os
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"

db = SQLAlchemy()

# SocketIO: cors_allowed_origins="*" facilita desenvolvimento local / ngrok.
# manage_session=False para evitar que o Flask-SocketIO tente gerenciar a session
# (você já usa `session` do Flask diretamente nos handlers).
socketio = SocketIO(cors_allowed_origins="*", manage_session=False)