import os
from flask import render_template, request, redirect, url_for, session, flash
from config import db
from models.produto_model import Produto
from werkzeug.utils import secure_filename
from controllers.usuario_controller import login_obrigatorio, PerfilEnum
from functools import wraps

# -----------------------------
# DECORATOR PARA RESTRIÇÃO POR PERFIL
# -----------------------------
def perfil_obrigatorio(*perfis_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            usuario_perfil = session.get("usuario_perfil")
            if not usuario_perfil or usuario_perfil not in [p.value for p in perfis_permitidos]:
                flash("Você não tem permissão para acessar esta página!", "danger")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# -----------------------------
# ROTAS DE CRUD PARA PRODUTOS
# -----------------------------
def home():
    return render_template("index.html", titulo="Home Page")

# Todos os perfis podem listar
@login_obrigatorio
def listar_produtos():
    produtos = Produto.query.all()
    return render_template("produtos.html", titulo="Lista de produtos", produtos=produtos)

# Gerente e Administrador podem cadastrar
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.GERENTE, PerfilEnum.ADMIN_SEGURANCA)
def cadastrar_produto():
    if request.method == 'POST':
        name = request.form["name"]
        price = float(request.form["price"])
        imagem_file = request.files.get("imagem")
        caminho_imagem = None

        if imagem_file:
            filename = secure_filename(imagem_file.filename)
            caminho_imagem = f"images/{filename}"
            imagem_file.save(os.path.join("static", caminho_imagem))

        novo_produto = Produto(name=name, price=price, imagem=caminho_imagem)
        db.session.add(novo_produto)
        db.session.commit()

        flash("Produto cadastrado com sucesso!", "success")
        return redirect(url_for("listar_produtos"))

    return render_template("cadastrar_produto.html", titulo="Cadastro de Produtos")

# Apenas Administrador pode editar
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def editar_produto(id):
    produto = Produto.query.get(id)

    if not produto:
        return render_template("404.html", descErro="Produto não encontrado")

    if request.method == "POST":
        produto.name = request.form["name"]
        produto.price = float(request.form["price"])

        imagem_file = request.files.get("imagem")
        if imagem_file:
            filename = secure_filename(imagem_file.filename)
            caminho_imagem = f"images/{filename}"
            imagem_file.save(os.path.join("static", caminho_imagem))
            produto.imagem = caminho_imagem

        db.session.commit()
        flash("Produto atualizado com sucesso!", "success")
        return redirect(url_for("listar_produtos"))

    return render_template("editar_produto.html", titulo="Edição de Produto", produto=produto)

# Apenas Administrador pode deletar
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def deletar_produto(id):
    produto = Produto.query.get(id)

    if not produto:
        return render_template("404.html", descErro="Produto não encontrado")

    db.session.delete(produto)
    db.session.commit()
    flash("Produto deletado com sucesso!", "success")
    return redirect(url_for("listar_produtos"))


