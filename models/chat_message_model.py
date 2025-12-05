from config import db
from datetime import datetime,timezone

class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    de_id = db.Column(db.Integer, nullable=False)
    para_id = db.Column(db.Integer, nullable=False)
    texto = db.Column(db.Text, nullable=False)
    horario = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.utcnow().replace(tzinfo=timezone.utc),
        nullable=False
    )

    
