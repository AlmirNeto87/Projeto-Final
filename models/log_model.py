from datetime import datetime, timezone
from config import db

class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Informações de Tempo e Usuário
    horario = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True) # Pode ser nulo para operações sem login (ex: login/logout)
    usuario_nome = db.Column(db.String(100), nullable=True)
    usuario_perfil = db.Column(db.String(50), nullable=True)

    # Informações da Operação
    tipo_operacao = db.Column(db.String(50), nullable=False)  # Ex: 'CRIAR', 'LER', 'ATUALIZAR', 'DELETAR', 'LOGIN', 'ACESSO_NEGADO'
    tipo_modelo = db.Column(db.String(50), nullable=False)    # Ex: 'Usuario', 'Veiculo', 'Equipamento', 'Sistema'
    
    # Detalhes
    descricao = db.Column(db.Text, nullable=True)             # Descrição curta (ex: "Tentativa de acesso não autorizado por João")
    modificacoes = db.Column(db.Text, nullable=True)          # JSON ou String complexa para alterações CRUD

    def __repr__(self):
        return f"<Log {self.tipo_operacao} em {self.tipo_modelo} por {self.usuario_nome}>"