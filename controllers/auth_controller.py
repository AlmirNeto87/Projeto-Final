from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.usuario_model import Usuario
from controllers.logs_controller import registrar_log
from config import db

auth_bp = Blueprint("auth", __name__)


# ============================================
# 🔐 LOGIN
# ============================================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    try:
        # Usuário já logado → redireciona
        if "usuario_id" in session:
            return redirect(url_for("home"))

        if request.method == "POST":
            email = request.form.get("email", "").strip()
            senha = request.form.get("senha", "")

            usuario = Usuario.query.filter_by(email=email).first()

            # LOGIN OK
            if usuario and usuario.checar_senha(senha):
                session["usuario_id"] = usuario.id
                session["usuario_nome"] = usuario.name
                session["usuario_perfil"] = usuario.perfil.value

                registrar_log(
                    tipo_operacao="LOGIN_SUCESSO",
                    tipo_modelo="Usuario",
                    descricao=f"Usuário {usuario.name} logou com sucesso."
                )

                flash("Login realizado com sucesso!", "success")
                return redirect(url_for("home"))

            # LOGIN FALHOU
            registrar_log(
                tipo_operacao="LOGIN_FALHO",
                tipo_modelo="Usuario",
                descricao=f"Tentativa de login falhou — email informado: {email}"
            )

            flash("E-mail ou senha inválidos!", "danger")

        return render_template("login.html", titulo="Login")

    except Exception as e:
        registrar_log(
            "ERRO_LOGIN",
            "Usuario",
            f"Erro inesperado no login: {e}"
        )
        db.session.rollback()

        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro interno ao processar o login."
        ), 500


# ============================================
# 🚪 LOGOUT
# ============================================
@auth_bp.route("/logout")
def logout():
    try:
        usuario_nome = session.get("usuario_nome", "Usuário Desconhecido")
        usuario_id = session.get("usuario_id", 0)

        registrar_log(
            tipo_operacao="LOGOUT",
            tipo_modelo="Usuario",
            descricao=f"Usuário {usuario_nome} (ID: {usuario_id}) deslogou."
        )

        session.clear()

        flash("Você saiu da sessão.", "info")
        return redirect(url_for("auth.login"))

    except Exception as e:
        registrar_log("ERRO_LOGOUT", "Usuario", f"Erro inesperado no logout: {e}")

        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro interno ao realizar logout."
        ), 500
