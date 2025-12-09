from flask import Flask, redirect, url_for
from config import db, DATABASE_URI, socketio

# Controladores normais
from controllers import misc_controller, usuario_controller, equipamento_controller, veiculo_controller

# Blueprints
from controllers.auth_controller import auth_bp
from controllers.logs_controller import logs_bp
from controllers.dashboard_controller import dashboard_bp
from controllers.chat_controller import chat_bp

# Mocks
from mock.usuarios_mock import criar_dados_mock_usuarios
from mock.equipamentos_mock import criar_dados_mock_equipamentos
from mock.veiculos_mock import criar_dados_mock_veiculos


app = Flask(__name__)
app.config["SECRET_KEY"] = "sua_chave_super_secreta"

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# =============================================================
# 🔐 MODO LOCKDOWN
# =============================================================
app.config["LOCKDOWN_ATIVO"] = False

db.init_app(app)
socketio.init_app(app)


# =============================================================
# BLUEPRINTS
# =============================================================
app.register_blueprint(auth_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(chat_bp)

# Página inicial interna
app.add_url_rule("/home", "home", usuario_controller.home)

# =============================================================
# ROTA RAIZ → LOGIN
# =============================================================
@app.route("/")
def index():
    return redirect(url_for("auth.login"))


# =============================================================
# CRUD USUÁRIOS
# =============================================================
app.add_url_rule("/usuarios", "listar_usuarios", usuario_controller.listar_usuarios)
app.add_url_rule("/usuarios/cadastro", "cadastrar_usuario", usuario_controller.cadastrar_usuario, methods=["GET", "POST"])
app.add_url_rule("/usuarios/editar/<int:id>", "editar_usuario", usuario_controller.editar_usuario, methods=["GET", "POST"])
app.add_url_rule("/usuarios/deletar/<int:id>", "deletar_usuario", usuario_controller.deletar_usuario)

# =============================================================
# CRUD EQUIPAMENTOS
# =============================================================
app.add_url_rule("/equipamentos", "listar_equipamentos", equipamento_controller.listar_equipamentos)
app.add_url_rule("/equipamentos/cadastro", "cadastrar_equipamento", equipamento_controller.cadastrar_equipamento, methods=["GET", "POST"])
app.add_url_rule("/equipamentos/editar/<int:id>", "editar_equipamento", equipamento_controller.editar_equipamento, methods=["GET", "POST"])
app.add_url_rule("/equipamentos/deletar/<int:id>", "deletar_equipamento", equipamento_controller.deletar_equipamento)

# =============================================================
# CRUD VEÍCULOS
# =============================================================
app.add_url_rule("/veiculos", "listar_veiculos", veiculo_controller.listar_veiculos)
app.add_url_rule("/veiculos/cadastro", "cadastrar_veiculo", veiculo_controller.cadastrar_veiculo, methods=["GET", "POST"])
app.add_url_rule("/veiculos/editar/<int:id>", "editar_veiculo", veiculo_controller.editar_veiculo, methods=["GET", "POST"])
app.add_url_rule("/veiculos/deletar/<int:id>", "deletar_veiculo", veiculo_controller.deletar_veiculo)

# =============================================================
# PÁGINAS ESTÁTICAS
# =============================================================
app.add_url_rule("/sobre", "sobre", misc_controller.sobre)
app.add_url_rule("/contatos", "contatos", misc_controller.contatos)

# =============================================================
# ADMIN
# =============================================================
app.add_url_rule("/admin/buscar", "buscar_adm", misc_controller.buscar_adm)
app.add_url_rule("/admin/lockdown/ativar", "ativar_lockdown", misc_controller.ativar_lockdown)
app.add_url_rule("/admin/lockdown/desativar", "desativar_lockdown", misc_controller.desativar_lockdown)
app.add_url_rule("/bloqueio", "pagina_bloqueio", misc_controller.pagina_bloqueio)

# =============================================================
# ERROS
# =============================================================
app.register_error_handler(404, misc_controller.page_not_found)
app.register_error_handler(500, misc_controller.internal_server_error)

# =============================================================
# TABELAS + MOCKS
# =============================================================
with app.app_context():
    db.create_all()
    criar_dados_mock_usuarios(app, db)
    criar_dados_mock_equipamentos(app, db)
    criar_dados_mock_veiculos(app, db)

# =============================================================
# INICIAR COM SOCKETIO
# =============================================================
if __name__ == "__main__":
    socketio.run(app, debug=True)
