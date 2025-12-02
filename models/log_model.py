from datetime import datetime, timezone
from config import db


class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)

    # Timestamp com timezone correto (lambda evita cache de data)
    horario = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Informações do usuário
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id', ondelete="SET NULL"),
        nullable=True
    )
    usuario_nome = db.Column(db.String(150), nullable=True)
    usuario_perfil = db.Column(db.String(50), nullable=True)

    # Operação (CRUD, LOGIN, NEGADO, etc)
    tipo_operacao = db.Column(db.String(30), nullable=False)
    tipo_modelo = db.Column(db.String(50), nullable=False)

    # Descrições e dados
    descricao = db.Column(db.Text, nullable=True)
    modificacoes = db.Column(db.Text, nullable=True)  # JSON ou string

    def __repr__(self):
        return f"<Log {self.tipo_operacao} em {self.tipo_modelo} às {self.horario}>"
