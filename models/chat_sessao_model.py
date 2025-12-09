from config import db
from datetime import datetime, timezone

class ChatSessao(db.Model):
    __tablename__ = "chat_sessoes"

    id = db.Column(db.Integer, primary_key=True)

    usuario1_id = db.Column(db.Integer, nullable=False)
    usuario2_id = db.Column(db.Integer, nullable=False)

    ativa = db.Column(db.Boolean, default=True, nullable=False)

    criado_em = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.utcnow().replace(tzinfo=timezone.utc),
        nullable=False
    )

    def envolve(self, uid):
        """Retorna True se o usuário fizer parte da sessão."""
        return uid == self.usuario_a or uid == self.usuario_b

    def outro_usuario(self, uid):
        """Retorna o ID do outro participante."""
        return self.usuario_b if uid == self.usuario_a else self.usuario_a
