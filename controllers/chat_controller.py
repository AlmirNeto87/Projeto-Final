# controllers/chat_controller.py
from flask import (
    Blueprint, render_template, session, jsonify, current_app, request
)
from utils.decorators import login_obrigatorio, verificar_lockdown
from models.usuario_model import Usuario, PerfilEnum
from models.chat_message_model import ChatMessage
from config import db, socketio

from flask_socketio import emit, join_room, leave_room
from datetime import datetime, timezone

chat_bp = Blueprint("chat", __name__)

# Lista global de usuários online
# { user_id: socket_sid }
online_users = {}


# ============================================================
# 1. Página do chat
# ============================================================
@chat_bp.route("/chat")
@login_obrigatorio
@verificar_lockdown
def chat():
    return render_template(
        "chat.html",
        titulo="Chat Interno",
        usuario_id=session["usuario_id"],
        usuario_nome=session["usuario_nome"],
        usuario_perfil=session["usuario_perfil"]
    )


# ============================================================
# 2. Contatos permitidos
# ============================================================
@chat_bp.route("/chat/contatos")
@login_obrigatorio
def contatos():

    usuario_logado = Usuario.query.get(session["usuario_id"])
    perfil = usuario_logado.perfil

    if perfil == PerfilEnum.FUNCIONARIO:
        permitidos = Usuario.query.filter(
            Usuario.perfil == PerfilEnum.FUNCIONARIO,
            Usuario.id != usuario_logado.id
        ).all()

    elif perfil == PerfilEnum.GERENTE:
        permitidos = Usuario.query.filter(
            Usuario.perfil.in_([PerfilEnum.FUNCIONARIO, PerfilEnum.GERENTE]),
            Usuario.id != usuario_logado.id
        ).all()

    else:  # ADMIN
        permitidos = Usuario.query.filter(Usuario.id != usuario_logado.id).all()

    return jsonify([
        {
            "id": u.id,
            "nome": u.name,
            "perfil": u.perfil.value,
            "online": u.id in online_users
        }
        for u in permitidos
    ])


# ============================================================
# 3. SOCKET — Conexão
# ============================================================
@socketio.on("connect")
def handle_connect():
    try:
        uid = session.get("usuario_id")
        if not uid:
            return

        # registra o socket do usuário
        online_users[uid] = request.sid
        join_room(uid)

        emit("user_online", {"id": uid, "nome": session.get("usuario_nome")}, broadcast=True)

    except Exception as e:
        current_app.logger.error(f"[CHAT] Erro ao conectar socket: {e}")


# ============================================================
# 4. SOCKET — Desconexão
# ============================================================
@socketio.on("disconnect")
def handle_disconnect():
    try:
        uid = session.get("usuario_id")
        if not uid:
            return

        online_users.pop(uid, None)
        leave_room(uid)

        emit("user_offline", {"id": uid}, broadcast=True)

    except Exception as e:
        current_app.logger.error(f"[CHAT] Erro ao desconectar socket: {e}")


# ============================================================
# 5. SOCKET — Enviar mensagem
# ============================================================
@socketio.on("send_message")
def handle_send_message(data):

    try:
        de_id = session["usuario_id"]
        de_nome = session["usuario_nome"]
        para_id = data.get("para")
        texto = data.get("texto", "").strip()

        if not texto:
            return

        # salva UTC → usando utcnow() conforme pedido
        ts = datetime.utcnow().replace(tzinfo=timezone.utc)

        msg = ChatMessage(
            de_id=de_id,
            para_id=para_id,
            texto=texto,
            horario=ts
        )

        db.session.add(msg)
        db.session.commit()

        # envia ao destino
        emit(
            "receive_message",
            {
                "de": de_id,
                "nome": de_nome,
                "texto": texto,
                "horario": ts.isoformat()
            },
            room=para_id
        )

        # reflete no emissor
        emit(
            "message_sent",
            {
                "para": para_id,
                "texto": texto,
                "horario": ts.isoformat()
            },
            room=de_id
        )

    except Exception as e:
        current_app.logger.error(f"[CHAT] Erro ao enviar mensagem: {e}")


# ============================================================
# 6. SOCKET — Carregar histórico (para o chat.js novo)
# ============================================================
@socketio.on("load_messages")
def handle_load_messages(data):
    try:
        usuario_id = session["usuario_id"]
        contato_id = data.get("para")

        mensagens = ChatMessage.query.filter(
            ((ChatMessage.de_id == usuario_id) & (ChatMessage.para_id == contato_id)) |
            ((ChatMessage.de_id == contato_id) & (ChatMessage.para_id == usuario_id))
        ).order_by(ChatMessage.horario.asc()).all()

        lista = [
            {
                "de": m.de_id,
                "para": m.para_id,
                "texto": m.texto,
                "horario": m.horario.isoformat()
            }
            for m in mensagens
        ]

        emit("load_messages_response", lista, room=request.sid)

    except Exception as e:
        current_app.logger.error(f"[CHAT] Erro ao carregar histórico: {e}")


# ============================================================
# 7. REST — Histórico via HTTP
# ============================================================
@chat_bp.route("/chat/historico/<int:contato_id>")
@login_obrigatorio
def historico(contato_id):
    usuario_id = session["usuario_id"]

    mensagens = ChatMessage.query.filter(
        ((ChatMessage.de_id == usuario_id) & (ChatMessage.para_id == contato_id)) |
        ((ChatMessage.de_id == contato_id) & (ChatMessage.para_id == usuario_id))
    ).order_by(ChatMessage.horario.asc()).all()

    return jsonify([
        {
            "de": m.de_id,
            "para": m.para_id,
            "texto": m.texto,
            "horario": m.horario.isoformat()
        }
        for m in mensagens
    ])
