from models.usuario_model import Usuario
from models.veiculo_model import Veiculo
from models.equipamento_model import Equipamento
from models.log_model import Log
from config import db
from sqlalchemy import func
from datetime import datetime, timedelta

# ===============================
# 🔒 FUNÇÕES SEGURAS (READ ONLY)
# ===============================

def total_usuarios():
    return Usuario.query.count()

def usuarios_por_perfil():
    dados = db.session.query(
        Usuario.perfil, func.count()
    ).group_by(Usuario.perfil).all()

    return {perfil.value: qtd for perfil, qtd in dados}

def veiculos_ativos():
    return Veiculo.query.filter_by(situacao="Ativo").count()

def acessos_negados_hoje():
    hoje = datetime.now().date()
    return Log.query.filter(
        Log.tipo_operacao == "ACESSO_NEGADO",
        func.date(Log.horario) == hoje
    ).count()

def equipamentos_alto_risco():
    return Equipamento.query.filter_by(nivel_perigo="Alto").count()


# ===============================
# 🤖 IA (simples + segura)
# ===============================

def responder_pergunta(pergunta):
    p = pergunta.lower()

    try:
        if "quantos usuarios" in p:
            return f"Total de usuários: {total_usuarios()}"

        elif "perfil" in p:
            dados = usuarios_por_perfil()
            return f"Usuários por perfil: {dados}"

        elif "veiculos ativos" in p:
            return f"Veículos ativos: {veiculos_ativos()}"

        elif "acessos negados" in p:
            return f"Acessos negados hoje: {acessos_negados_hoje()}"

        elif "alto risco" in p:
            return f"Equipamentos de alto risco: {equipamentos_alto_risco()}"

        else:
            return "Não entendi sua pergunta. Tente algo como: 'quantos usuários existem?'"

    except Exception as e:
        return f"Erro ao processar pergunta: {str(e)}"