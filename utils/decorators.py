# utils/decorators.py

from functools import wraps
from flask import flash, redirect, url_for, session, request
from models.usuario_model import Usuario, PerfilEnum 
from controllers.logs_controller import registrar_log 
import json # Necessário para serializar listas de perfis permitidos

def login_obrigatorio(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            
            # LOG: ACESSO NEGADO - NÃO LOGADO
            registrar_log(
                tipo_operacao="ACESSO_NEGADO", 
                tipo_modelo="Sistema", 
                descricao=f"Acesso à URL {request.path} negado. Não logado.",
                modificacoes=f"Rota: {request.path}"
            )
            
            flash("Você precisa estar logado para acessar esta página!", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def perfil_obrigatorio(*perfis_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            usuario_id = session.get("usuario_id")
            
            # Se não está logado, redireciona para login (login_obrigatorio deveria pegar isso)
            if not usuario_id:
                return redirect(url_for("login"))

            usuario = Usuario.query.get(usuario_id)
            
            # Verifica se o perfil do usuário está na lista de perfis permitidos
            if usuario.perfil.value not in perfis_permitidos: # Usa .value para comparar string
                print(usuario.perfil.value)
                # LOG: ACESSO NEGADO POR PERFIL
                try:
                    perfis_str = [p.value for p in perfis_permitidos] # Converte Enum para string
                    print(perfis_str)
                except AttributeError:
                     # Se já for string (como na lista de Veiculo), usa diretamente
                    perfis_str = list(perfis_permitidos)
                    print(perfis_str) 
                    
                registrar_log(
                    tipo_operacao="ACESSO_NEGADO",
                    tipo_modelo="Sistema",
                    descricao=f"Acesso à URL {request.path} negado. Perfil insuficiente.",
                    modificacoes=json.dumps({
                        "perfil_usuario": usuario.perfil.value,
                        "rota": request.path,
                        "perfis_permitidos": perfis_str
                    })
                )
                
                flash("Você não tem permissão para acessar esta página!", "danger")
                return redirect(url_for("home"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator