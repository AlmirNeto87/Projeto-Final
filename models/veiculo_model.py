from config import db
from datetime import date # Importação útil para campos de data/ano

# Inicialização do BD 
class Veiculo(db.Model):
    __tablename__ = "veiculos"

    # Definição das opções permitidas para a situação do veículo
    SITUACAO_OPCOES = ['Ativo', 'Manutencao', 'Defeituoso']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Características solicitadas:
    modelo = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    # Usando db.Integer para Ano de Fabricacao (opcionalmente, poderia ser db.String ou db.Date)
    ano_fabricacao = db.Column(db.Integer, nullable=False) 
    cor = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    placa = db.Column(db.String(10),nullable=False)
    local_armazenamento = db.Column(db.String(100), nullable=False)
    
    # Situação: com as opções Ativo, Manutencao, Defeituoso
    situacao = db.Column(db.String(20), nullable=False, default='Ativo') 

    def __repr__(self):
        return f"<Veiculo {self.marca} {self.modelo} ({self.ano_fabricacao})>"