import json
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app,
    abort
)
from config import db
from models.usuario_model import Usuario, PerfilEnum
from controllers.logs_controller import registrar_log
from utils.decorators import perfil_obrigatorio, login_obrigatorio, verificar_lockdown


# ============================================================
# 🏠 HOME
# ============================================================
@login_obrigatorio
@verificar_lockdown
def home():
    try:
        perfil = session.get("usuario_perfil")
        lockdown_ativo = current_app.config.get("LOCKDOWN_ATIVO", False)

        return render_template(
            "index.html",
            titulo="Página Principal",
            perfil=perfil,
            lockdown_ativo=lockdown_ativo
        )

    except Exception as e:
        registrar_log("ERRO_HOME", "Sistema", f"Erro ao carregar home: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao carregar a página inicial."
        ), 500


# ============================================================
# 👥 LISTAR USUÁRIOS
# ============================================================
@login_obrigatorio
@verificar_lockdown
@perfil_obrigatorio(PerfilEnum.GERENTE, PerfilEnum.ADMIN_SEGURANCA)
def listar_usuarios():
    try:
        usuarios = Usuario.query.all()
        return render_template(
            "usuarios.html",
            titulo="Lista de usuários",
            usuarios=usuarios
        )

    except Exception as e:
        registrar_log("ERRO_LISTAR_USUARIOS", "Usuario", f"Erro ao listar usuários: {e}")
        flash("Erro ao carregar a lista de usuários.", "danger")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao carregar lista de usuários."
        ), 500


# ============================================================
# ➕ CADASTRAR USUÁRIO
# ============================================================
@login_obrigatorio
@verificar_lockdown
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def cadastrar_usuario():
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            senha = request.form.get("password", "").strip()
            perfil = request.form.get("perfil", PerfilEnum.FUNCIONARIO.name)

            novo_usuario = Usuario(
                name=name,
                email=email,
                perfil=PerfilEnum[perfil]
            )

            novo_usuario.set_senha(senha)

            db.session.add(novo_usuario)
            db.session.commit()

            registrar_log(
                tipo_operacao="CRIAR",
                tipo_modelo="Usuario",
                descricao=f"Novo usuário cadastrado: {name} (Perfil: {perfil})",
                modificacoes=json.dumps({
                    "name": name,
                    "email": email,
                    "perfil": perfil
                })
            )

            flash("Usuário cadastrado com sucesso!", "success")
            return redirect(url_for("listar_usuarios"))

        except Exception as e:
            registrar_log("ERRO_CADASTRAR_USUARIO", "Usuario", f"Erro ao cadastrar: {e}")
            db.session.rollback()
            flash("Erro ao cadastrar usuário.", "danger")
            return render_template(
                "404.html",
                error_code=500,
                error_message="Erro ao cadastrar usuário."
            ), 500

    try:
        return render_template(
            "cadastrar_usuario.html",
            titulo="Cadastro de Usuários",
            perfis=PerfilEnum
        )

    except Exception as e:
        registrar_log("ERRO_RENDER_CADASTRAR_USUARIO", "Sistema", f"Erro ao renderizar página: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao carregar página de cadastro."
        ), 500


# ============================================================
# ✏️ EDITAR USUÁRIO
# ============================================================
@login_obrigatorio
@verificar_lockdown
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def editar_usuario(id):
    try:
        usuario = Usuario.query.get(id)
    except Exception as e:
        registrar_log("ERRO_BUSCAR_USUARIO_EDITAR", "Usuario", f"Erro ao buscar usuário {id}: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao buscar usuário."
        ), 500

    if not usuario:
        abort(404)

    if request.method == "POST":
        try:
            dados_antigos = {
                "name": usuario.name,
                "email": usuario.email,
                "perfil": usuario.perfil.name,
                "senha_alterada": False
            }

            usuario.name = request.form.get("name", "").strip()
            usuario.email = request.form.get("email", "").strip()
            nova_senha = request.form.get("password", "").strip()
            perfil = request.form.get("perfil")

            if nova_senha:
                usuario.set_senha(nova_senha)
                dados_antigos["senha_alterada"] = True

            if perfil:
                usuario.perfil = PerfilEnum[perfil]

            db.session.commit()

            dados_novos = {
                "name": usuario.name,
                "email": usuario.email,
                "perfil": usuario.perfil.name
            }

            registrar_log(
                tipo_operacao="ATUALIZAR",
                tipo_modelo="Usuario",
                descricao=f"Usuário {usuario.name} (ID: {id}) atualizado.",
                modificacoes=json.dumps({
                    "antes": dados_antigos,
                    "depois": dados_novos
                })
            )

            flash("Usuário atualizado com sucesso!", "success")
            return redirect(url_for("listar_usuarios"))

        except Exception as e:
            registrar_log("ERRO_EDITAR_USUARIO", "Usuario", f"Erro ao editar usuário {id}: {e}")
            db.session.rollback()
            flash("Erro ao atualizar usuário.", "danger")
            return render_template(
                "404.html",
                error_code=500,
                error_message="Erro ao atualizar usuário."
            ), 500

    try:
        return render_template(
            "editar_usuario.html",
            titulo="Edição de Usuário",
            usuario=usuario,
            perfis=PerfilEnum
        )

    except Exception as e:
        registrar_log("ERRO_RENDER_EDITAR_USUARIO", "Sistema", f"Erro ao renderizar edição: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao carregar página de edição."
        ), 500


# ============================================================
# 🗑️ DELETAR USUÁRIO
# ============================================================
@login_obrigatorio
@verificar_lockdown
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def deletar_usuario(id):
    try:
        usuario = Usuario.query.get(id)
    except Exception as e:
        registrar_log("ERRO_BUSCAR_USUARIO_DELETAR", "Usuario", f"Erro ao buscar usuário {id}: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao buscar usuário."
        ), 500

    if not usuario:
        abort(404)

    try:
        info_usuario_deletado = {
            "name": usuario.name,
            "email": usuario.email,
            "perfil": usuario.perfil.name
        }

        db.session.delete(usuario)
        db.session.commit()

        registrar_log(
            tipo_operacao="DELETAR",
            tipo_modelo="Usuario",
            descricao=f"Usuário deletado: {info_usuario_deletado['name']} (ID: {id})",
            modificacoes=json.dumps(info_usuario_deletado)
        )

        flash("Usuário deletado com sucesso!", "success")
        return redirect(url_for("listar_usuarios"))

    except Exception as e:
        registrar_log("ERRO_DELETAR_USUARIO", "Usuario", f"Erro ao deletar usuário {id}: {e}")
        db.session.rollback()
        flash("Erro ao deletar usuário.", "danger")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao deletar usuário."
        ), 500
