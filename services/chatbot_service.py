import google.generativeai as genai
import os

from models.usuario_model import Usuario
from models.veiculo_model import Veiculo
from models.equipamento_model import Equipamento
from models.log_model import Log
from config import db
from sqlalchemy import func
from datetime import datetime

genai.configure(api_key="")

model = genai.GenerativeModel("models/gemini-1.5-flash")

print("Modelos disponíveis para você:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")

# =========================================
# 🔒 FUNÇÕES SEGURAS (READ ONLY)
# =========================================

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


# =========================================
# 🤖 MAPA DE FUNÇÕES DISPONÍVEIS
# =========================================

FUNCOES = {
    "total_usuarios": total_usuarios,
    "usuarios_por_perfil": usuarios_por_perfil,
    "veiculos_ativos": veiculos_ativos,
    "acessos_negados_hoje": acessos_negados_hoje,
    "equipamentos_alto_risco": equipamentos_alto_risco
}


# =========================================
# 🤖 IA — INTERPRETAÇÃO NATURAL
# =========================================

def interpretar_com_ia(pergunta):
    prompt = f"""
    Você é um assistente de sistema interno.

    Escolha qual função deve ser usada:

    - total_usuarios
    - usuarios_por_perfil
    - veiculos_ativos
    - acessos_negados_hoje
    - equipamentos_alto_risco

    Responda SOMENTE com o nome da função.

    Pergunta: {pergunta}
    """

    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            candidate_count=1,
            stop_sequences=['\n'], # Para ela parar logo após a primeira linha
            temperature=0.0,       # Deixa a IA menos criativa e mais precisa
        )
    )

    return response.text.strip()


# =========================================
# 🤖 RESPOSTA FINAL
# =========================================

def responder_pergunta(pergunta):
    try:
        func_name = interpretar_com_ia(pergunta)

        if func_name in FUNCOES:
            resultado = FUNCOES[func_name]()

            return f"Resultado: {resultado}"

        return "Não consegui entender sua pergunta."

    except Exception as e:
        return f"Erro na IA: {str(e)}"