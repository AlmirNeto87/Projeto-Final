from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from config import db
from models.usuario_model import Usuario

auth_bp = Blueprint("auth", __name__)

# rota de login
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(email=email, senha=senha).first()

        if usuario:
            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.name
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("home"))
        else:
            flash("E-mail ou senha inválidos!", "danger")

    return render_template("login.html", titulo="Login")


# rota de logout
@auth_bp.route("/logout")
def logout():
    session.pop("usuario_logado", None)
    flash("Logout realizado!", "info")
    return redirect(url_for("auth.login"))


# Decorador para proteger rotas
def login_obrigatorio(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_logado" not in session:
            flash("Faça login primeiro!", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function
