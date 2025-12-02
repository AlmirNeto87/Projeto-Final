from config import db

# Inicializacao do BD 
class Produto(db.Model):
  __tablename__ = "produtos"
  
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(100), nullable=False)
  price = db.Column(db.Float, nullable=False)
  imagem = db.Column(db.String(255))

#Funcao de referencia apenas pra informar sobre a criacao do BD
def __repr__(self):
  return f"<Produto {self.name}>"