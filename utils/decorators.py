from functools import wraps
from flask import flash, redirect, url_for, session, request, current_app
from models.usuario_model import Usuario, PerfilEnum
import json


# =====================================================
# FUNÇÃO INTERNA — NORMALIZAR PERFIL
# =====================================================
def _normalize_perfil_input(p):
    """Normaliza um perfil recebido (enum, string, etc)."""
    try:
        return p.value
    except Exception:
        try:
            return PerfilEnum[p].value
        except Exception:
            return str(p)


# =====================================================
# DECORATOR — LOGIN OBRIGATÓRIO
# =====================================================
def login_obrigatorio(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        from controllers.logs_controller import registrar_log  # import seguro

        if "usuario_id" not in session:
            try:
                registrar_log(
                    "ACESSO_NEGADO",
                    "Sistema",
                    f"Tentativa de acesso sem login na rota: {request.path}",
                    modificacoes=json.dumps({"rota": request.path}, ensure_ascii=False)
                )
            except Exception:
                pass

            flash("Você precisa estar logado para acessar esta página.", "danger")
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return decorator


# =====================================================
# DECORATOR — PERFIL OBRIGATÓRIO
# =====================================================
def perfil_obrigatorio(*perfis_permitidos):
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            from controllers.logs_controller import registrar_log

            usuario_id = session.get("usuario_id")

            # Usuário não logado
            if not usuario_id:
                flash("Você precisa estar logado!", "danger")
                return redirect(url_for("auth.login"))

            # Carregar usuário
            usuario = Usuario.query.get(usuario_id)
            if not usuario:
                session.clear()
                flash("Sessão expirada ou inválida.", "warning")
                return redirect(url_for("auth.login"))

            # Normalizar perfis permitidos
            perfis_validos = [_normalize_perfil_input(p) for p in perfis_permitidos]
            perfil_usuario = usuario.perfil.value

            # Verificar permissão
            if perfil_usuario not in perfis_validos:
                try:
                    registrar_log(
                        "ACESSO_NEGADO",
                        "Sistema",
                        f"Perfil sem permissão para acessar a rota {request.path}",
                        modificacoes=json.dumps({
                            "rota": request.path,
                            "perfil_usuario": perfil_usuario,
                            "perfis_permitidos": perfis_validos
                        }, ensure_ascii=False)
                    )
                except Exception:
                    pass

                flash("Você não tem permissão para acessar esta funcionalidade.", "danger")
                return redirect(url_for("home"))

            return f(*args, **kwargs)

        return decorator
    return wrapper


# =====================================================
# DECORATOR — VERIFICAR LOCKDOWN
# =====================================================
def verificar_lockdown(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        lockdown_ativo = current_app.config.get("LOCKDOWN_ATIVO", False)

        # Lockdown desligado → passa direto
        if not lockdown_ativo:
            return f(*args, **kwargs)

        # Admin de Segurança pode ignorar lockdown
        perfil_atual = session.get("usuario_perfil")
        if perfil_atual == PerfilEnum.ADMIN_SEGURANCA.value:
            return f(*args, **kwargs)

        # Demais perfis são bloqueados
        return redirect(url_for("pagina_bloqueio"))

    return decorator
