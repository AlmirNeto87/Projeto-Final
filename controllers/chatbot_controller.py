from flask import Blueprint, render_template, request, jsonify
from utils.decorators import login_obrigatorio, perfil_obrigatorio
from models.usuario_model import PerfilEnum
from services.chatbot_service import responder_pergunta

chatbot_bp = Blueprint("chatbot", __name__)

# Página do chatbot
@chatbot_bp.route("/chatbot")
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def pagina_chatbot():
    return render_template("chatbot.html")


# Endpoint de pergunta
@chatbot_bp.route("/chatbot/perguntar", methods=["POST"])
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def perguntar():
    data = request.get_json()
    pergunta = data.get("pergunta", "")

    resposta = responder_pergunta(pergunta)

    return jsonify({"resposta": resposta})