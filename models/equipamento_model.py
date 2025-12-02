from config import db

# Inicialização do BD 
class Equipamento(db.Model):
    __tablename__ = "equipamentos"

    # Definição das opções permitidas para a situação do equipamento
    SITUACAO_OPCOES = ['Manutencao', 'Defeituoso', 'Ativo']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    nivel_perigo = db.Column(db.String(50), nullable=False)
    
    # Nova Característica: Situacao
    # Definido como String, com tamanho suficiente para a maior opção ('Manutencao')
    # Pode-se adicionar um 'default' se for o caso.
    situacao = db.Column(db.String(20), nullable=False, default='Ativo') 

    def __repr__(self):
        return f"<Equipamento {self.nome}>"