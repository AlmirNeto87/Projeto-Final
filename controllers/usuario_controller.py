import json # Importação necessária para serializar modificações
from flask import render_template, request, redirect, url_for, session, flash
from functools import wraps
from config import db
from models.usuario_model import Usuario, PerfilEnum
from controllers.logs_controller import registrar_log 
from utils.decorators import perfil_obrigatorio, login_obrigatorio



# Rota de login
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.checar_senha(senha):
            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.name
            session["usuario_perfil"] = usuario.perfil.value
            
            # LOG: LOGIN BEM-SUCEDIDO
            registrar_log(
                tipo_operacao="LOGIN_SUCESSO", 
                tipo_modelo="Usuario", 
                descricao=f"Usuário {usuario.name} logou com sucesso.",
            )
            
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("home"))
        else:
            
            # LOG: LOGIN FALHO
            registrar_log(
                tipo_operacao="LOGIN_FALHO", 
                tipo_modelo="Usuario", 
                descricao=f"Tentativa de login falha para o e-mail: {email}.",
            )
            
            flash("E-mail ou senha inválidos!", "danger")

    return render_template("login.html", titulo="Login")

# Rota de logout
def logout():
    # Obtém as informações antes de limpar a sessão
    usuario_nome = session.get("usuario_nome", "Usuário Desconhecido")
    usuario_id = session.get("usuario_id", 0)

    # LOG: LOGOUT
    registrar_log(
        tipo_operacao="LOGOUT", 
        tipo_modelo="Usuario", 
        descricao=f"Usuário {usuario_nome} (ID: {usuario_id}) deslogou.",
    )
    
    session.clear()
    flash("Você saiu da sessão.", "info")
    return redirect(url_for("login"))

# Rota da página principal (index)
@login_obrigatorio
def home():
    # Não logamos o acesso à home, pois é uma operação muito frequente.
    perfil = session.get("usuario_perfil")
    return render_template("index.html", titulo="Página Principal", perfil=perfil)


# Rotas para CRUD de Usuários

# Listar usuários
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.GERENTE, PerfilEnum.ADMIN_SEGURANCA)
def listar_usuarios():
    # Geralmente, não logamos a leitura (GET) de listas, a menos que seja um relatório sensível.
    usuarios = Usuario.query.all()
    return render_template("usuarios.html", titulo="Lista de usuários", usuarios=usuarios)

# Cadastrar usuários → apenas ADMIN_SEGURANCA
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def cadastrar_usuario():
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        senha = request.form["password"]
        perfil = request.form.get("perfil", PerfilEnum.FUNCIONARIO.name)

        novo_usuario = Usuario(name=name, email=email, perfil=PerfilEnum[perfil])
        novo_usuario.set_senha(senha)

        db.session.add(novo_usuario)
        db.session.commit()
        
        # LOG: CRIAR USUÁRIO
        registrar_log(
            tipo_operacao="CRIAR",
            tipo_modelo="Usuario",
            descricao=f"Novo Usuário cadastrado: {name} (Perfil: {perfil})",
            # Serializa os dados criados para registro
            modificacoes=json.dumps({"name": name, "email": email, "perfil": perfil}) 
        )

        flash("Usuário cadastrado com sucesso!", "success")
        return redirect(url_for("listar_usuarios"))

    return render_template("cadastrar_usuario.html", titulo="Cadastro de Usuários", perfis=PerfilEnum)

# Editar usuários → apenas ADMIN_SEGURANCA
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def editar_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return render_template("404.html", descErro="Usuário não encontrado")

    if request.method == "POST":
        
        # Dados ANTIGOS antes da modificação
        dados_antigos = {
            "name": usuario.name, 
            "email": usuario.email, 
            "perfil": usuario.perfil.name, 
            "senha_alterada": False
        }
        
        usuario.name = request.form["name"]
        usuario.email = request.form["email"]
        nova_senha = request.form["password"]
        perfil = request.form.get("perfil")

        if nova_senha:
            usuario.set_senha(nova_senha)
            dados_antigos["senha_alterada"] = True # Indica que a senha foi modificada
            
        if perfil:
            usuario.perfil = PerfilEnum[perfil]

        db.session.commit()
        
        # Dados NOVOS após a modificação
        dados_novos = {
            "name": usuario.name, 
            "email": usuario.email, 
            "perfil": usuario.perfil.name
        }
        
        # LOG: ATUALIZAR USUÁRIO
        registrar_log(
            tipo_operacao="ATUALIZAR",
            tipo_modelo="Usuario",
            descricao=f"Usuário {usuario.name} (ID: {id}) atualizado.",
            modificacoes=json.dumps({"antes": dados_antigos, "depois": dados_novos}) 
        )
        
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for("listar_usuarios"))

    return render_template("editar_usuario.html", titulo="Edição de Usuário", usuario=usuario, perfis=PerfilEnum)

# Deletar usuários → apenas ADMIN_SEGURANCA
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def deletar_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return render_template("404.html", descErro="Usuário não encontrado")

    # Informações para o log antes de deletar
    info_usuario_deletado = {"name": usuario.name, "email": usuario.email, "perfil": usuario.perfil.name}

    db.session.delete(usuario)
    db.session.commit()
    
    # LOG: DELETAR USUÁRIO
    registrar_log(
        tipo_operacao="DELETAR",
        tipo_modelo="Usuario",
        descricao=f"Usuário deletado: {info_usuario_deletado['name']} (ID: {id})",
        modificacoes=json.dumps(info_usuario_deletado) # Registra quem foi deletado
    )

    flash("Usuário deletado com sucesso!", "success")
    return redirect(url_for("listar_usuarios"))