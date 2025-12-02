from config import db
from werkzeug.security import generate_password_hash, check_password_hash
import enum

# Enum para tipos de perfil
class PerfilEnum(enum.Enum):
    FUNCIONARIO = "Funcionário"
    GERENTE = "Gerente"
    ADMIN_SEGURANCA = "Administrador de Segurança"

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)  # armazena hash da senha
    perfil = db.Column(db.Enum(PerfilEnum), default=PerfilEnum.FUNCIONARIO, nullable=False)

    # Método para definir senha (gera hash)
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    # Método para verificar senha
    def checar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f"<Usuario {self.name}, Perfil: {self.perfil.value}>"
