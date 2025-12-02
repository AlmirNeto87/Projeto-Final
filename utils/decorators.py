from functools import wraps
from flask import flash, redirect, url_for, session, request, current_app
from models.usuario_model import Usuario, PerfilEnum
import json


# =====================================================
# NORMALIZA PERFIL
# =====================================================
def _normalize_perfil_input(p):
    try:
        return p.value
    except Exception:
        try:
            return PerfilEnum[p].value
        except Exception:
            return str(p)


# =====================================================
# LOGIN OBRIGATÓRIO
# =====================================================
def login_obrigatorio(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from controllers.logs_controller import registrar_log

        if "usuario_id" not in session:
            try:
                registrar_log(
                    "ACESSO_NEGADO",
                    "Sistema",
                    f"Acesso negado à rota {request.path} — usuário não logado.",
                    modificacoes=json.dumps({"rota": request.path}, ensure_ascii=False)
                )
            except:
                pass

            flash("Você precisa estar logado para acessar esta página!", "danger")
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)
    return decorated_function


# =====================================================
# PERFIL OBRIGATÓRIO
# =====================================================
def perfil_obrigatorio(*perfis_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from controllers.logs_controller import registrar_log

            usuario_id = session.get("usuario_id")

            if not usuario_id:
                flash("Você precisa estar logado!", "danger")
                return redirect(url_for("auth.login"))

            usuario = Usuario.query.get(usuario_id)
            if not usuario:
                session.clear()
                flash("Sessão inválida.", "warning")
                return redirect(url_for("auth.login"))

            perfis_validos = [_normalize_perfil_input(p) for p in perfis_permitidos]
            usuario_perfil_str = usuario.perfil.value

            if usuario_perfil_str not in perfis_validos:
                try:
                    registrar_log(
                        "ACESSO_NEGADO",
                        "Sistema",
                        f"Acesso negado à rota {request.path}. Perfil insuficiente.",
                        modificacoes=json.dumps({
                            "rota": request.path,
                            "perfil_usuario": usuario_perfil_str,
                            "perfis_permitidos": perfis_validos
                        }, ensure_ascii=False)
                    )
                except:
                    pass

                flash("Você não tem permissão para acessar esta página!", "danger")
                return redirect(url_for("home"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# =====================================================
# DECORATOR — VERIFICAR LOCKDOWN (AGORA SIM!)
# =====================================================
def verificar_lockdown(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Se lockdown desligado → passa
        if not current_app.config.get("LOCKDOWN_ATIVO", False):
            return f(*args, **kwargs)

        # Se for Admin Segurança → passa
        usuario_perfil = session.get("usuario_perfil")
        if usuario_perfil == PerfilEnum.ADMIN_SEGURANCA.value:
            return f(*args, **kwargs)

        # Outros perfis → bloqueados
        return redirect(url_for("pagina_bloqueio"))

    return decorated_function
