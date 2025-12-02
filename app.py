from flask import Flask
from config import db, DATABASE_URI
# Importações dos controllers de Produto e Usuário
from controllers import misc_controller, usuario_controller, equipamento_controller, veiculo_controller
from mock.usuarios_mock import criar_dados_mock_usuarios 
from mock.equipamentos_mock import criar_dados_mock_equipamentos
from mock.veiculos_mock import criar_dados_mock_veiculos



#Instanciando o objeto Flask a variavel app
app = Flask(__name__)

# Necessário para gerenciar sessões
app.secret_key = "sua_chave_super_secreta" # troque por algo seguro

# Define qual o banco de dados usar
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
# Desativa o rastreamento de modificações para economizar memória
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa a extensão com a aplicação
db.init_app(app)




# -----------------------------
# ROTAS DE AUTENTICAÇÃO E HOME
# -----------------------------

# Definind rotas de login e logout
app.add_url_rule("/login", "login", usuario_controller.login, methods=["GET", "POST"])
app.add_url_rule("/logout", "logout", usuario_controller.logout)


# Utilizacao das rotas sem o uso dos Decorators
app.add_url_rule("/", "home", usuario_controller.home)
app.add_url_rule("/home", "home", usuario_controller.home)

# -----------------------------
# ROTAS PARA CRUD DE USUÁRIOS
# -----------------------------
app.add_url_rule("/usuarios", "listar_usuarios", usuario_controller.listar_usuarios)
app.add_url_rule("/usuarios/cadastro", "cadastrar_usuario", usuario_controller.cadastrar_usuario, methods=["GET", "POST"])
app.add_url_rule("/usuarios/editar/<int:id>", "editar_usuario", usuario_controller.editar_usuario, methods=["GET", "POST"])
app.add_url_rule("/usuarios/deletar/<int:id>", "deletar_usuario", usuario_controller.deletar_usuario)




# =====================================
# NOVO: ROTAS PARA CRUD DE EQUIPAMENTOS
# =====================================
app.add_url_rule("/equipamentos", "listar_equipamentos", equipamento_controller.listar_equipamentos)
app.add_url_rule("/equipamentos/cadastro", "cadastrar_equipamento", equipamento_controller.cadastrar_equipamento, methods=["GET", "POST"])
app.add_url_rule("/equipamentos/editar/<int:id>", "editar_equipamento", equipamento_controller.editar_equipamento, methods=["GET", "POST"])
app.add_url_rule("/equipamentos/deletar/<int:id>", "deletar_equipamento", equipamento_controller.deletar_equipamento)


# =====================================
# NOVO: ROTAS PARA CRUD DE VEÍCULOS
# =====================================
app.add_url_rule("/veiculos", "listar_veiculos", veiculo_controller.listar_veiculos)
app.add_url_rule("/veiculos/cadastro", "cadastrar_veiculo", veiculo_controller.cadastrar_veiculo, methods=["GET", "POST"])
app.add_url_rule("/veiculos/editar/<int:id>", "editar_veiculo", veiculo_controller.editar_veiculo, methods=["GET", "POST"])
app.add_url_rule("/veiculos/deletar/<int:id>", "deletar_veiculo", veiculo_controller.deletar_veiculo)


# -----------------------------
# ROTAS PARA PÁGINAS ESTÁTICAS E ERROS
# -----------------------------
app.add_url_rule("/sobre", "sobre", misc_controller.sobre)
app.add_url_rule("/contatos", "contatos", misc_controller.contatos)

# =====================================
# NOVO: ROTA DE BUSCA ADMINISTRATIVA
# =====================================
app.add_url_rule("/admin/buscar", "buscar_adm", misc_controller.buscar_adm)


# Registro dos manipuladores de erros
app.register_error_handler(404, misc_controller.page_not_found)
app.register_error_handler(500, misc_controller.internal_server_error)

# Cria as tabelas em falta no banco com contexto da aplicação
with app.app_context():
    db.create_all()
    
    # Chama a função de mock de usuarios APÓS a criação das tabelas
    criar_dados_mock_usuarios(app,db)
    
    ## Chama a função de mock de equipamentos APÓS a criação das tabelas
    criar_dados_mock_equipamentos(app, db)

    ### Chama a função de mock de Veiculos APÓS a criação das tabelas
    criar_dados_mock_veiculos(app, db)

# Executa a aplicação
if __name__ == "__main__":
    app.run(debug=True)