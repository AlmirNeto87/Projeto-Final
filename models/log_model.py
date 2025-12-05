from datetime import datetime, timezone
from config import db

class Log(db.Model):
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True)

    # Timestamp REAL UTC — NÃO depende do Windows
    horario = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.utcnow().replace(tzinfo=timezone.utc),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True
    )
    usuario_nome = db.Column(db.String(150), nullable=True)
    usuario_perfil = db.Column(db.String(50), nullable=True)

    tipo_operacao = db.Column(db.String(30), nullable=False)
    tipo_modelo = db.Column(db.String(50), nullable=False)

    descricao = db.Column(db.Text, nullable=True)
    modificacoes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        try:
            horario_str = self.horario.isoformat()
        except Exception:
            horario_str = str(self.horario)
        return f"<Log id={self.id} operacao='{self.tipo_operacao}' modelo='{self.tipo_modelo}' horario='{horario_str}'>"
