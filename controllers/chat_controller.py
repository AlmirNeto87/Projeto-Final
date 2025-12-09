from flask import (
    Blueprint, render_template, session, jsonify, current_app, request
)
from utils.decorators import login_obrigatorio, verificar_lockdown
from models.usuario_model import Usuario, PerfilEnum
from models.chat_message_model import ChatMessage
from models.chat_sessao_model import ChatSessao
from config import db, socketio

from flask_socketio import emit, join_room, leave_room
from datetime import datetime, timezone

chat_bp = Blueprint("chat", __name__)

# Mapa: { user_id : socket_sid }
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
# 2. Contatos permitidos + sessões ativas + APENAS online
# ============================================================
@chat_bp.route("/chat/contatos")
@login_obrigatorio
@verificar_lockdown
def contatos():

    usuario_logado = Usuario.query.get(session["usuario_id"])
    perfil = usuario_logado.perfil

    # ------------------------------
    # 🔹 1) Permissões originais
    # ------------------------------
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
        permitidos = Usuario.query.filter(
            Usuario.id != usuario_logado.id
        ).all()

    # ------------------------------
    # 🔹 2) Sessões ativas (para manter conversas abertas)
    # ------------------------------
    sessoes = ChatSessao.query.filter_by(ativa=True).all()

    ids_sessao = []
    for s in sessoes:
        if s.usuario1_id == usuario_logado.id:
            ids_sessao.append(s.usuario2_id)
        elif s.usuario2_id == usuario_logado.id:
            ids_sessao.append(s.usuario1_id)

    # ------------------------------
    # 🔹 3) Somar permitidos + sessões
    # ------------------------------
    contatos_ids = {u.id for u in permitidos}
    contatos_ids.update(ids_sessao)

    # ------------------------------
    # 🔹 4) Filtrar apenas os online
    # ------------------------------
    online_ids = [uid for uid in contatos_ids if uid in online_users]

    # ------------------------------
    # 🔹 5) Buscar apenas usuários online
    # ------------------------------
    usuarios_final = Usuario.query.filter(Usuario.id.in_(online_ids)).all()

    # ------------------------------
    # 🔹 6) Resposta final
    # ------------------------------
    return jsonify([
        {
            "id": u.id,
            "nome": u.name,
            "perfil": u.perfil.value,
            "online": True
        }
        for u in usuarios_final
    ])


# ============================================================
# 3. Criar ou ativar sessão
# ============================================================
def criar_ou_ativar_sessao(user1, user2):

    sessao = ChatSessao.query.filter(
        ((ChatSessao.usuario1_id == user1) & (ChatSessao.usuario2_id == user2)) |
        ((ChatSessao.usuario1_id == user2) & (ChatSessao.usuario2_id == user1))
    ).first()

    if sessao:
        sessao.ativa = True
    else:
        db.session.add(ChatSessao(
            usuario1_id=user1,
            usuario2_id=user2,
            ativa=True
        ))

    db.session.commit()


# ============================================================
# 4. Fechar sessão manualmente (REST)
# ============================================================
@chat_bp.route("/chat/fechar/<int:contato_id>", methods=["POST"])
@login_obrigatorio
def fechar_sessao(contato_id):
    uid = session["usuario_id"]

    sessao = ChatSessao.query.filter(
        ((ChatSessao.usuario1_id == uid) & (ChatSessao.usuario2_id == contato_id)) |
        ((ChatSessao.usuario1_id == contato_id) & (ChatSessao.usuario2_id == uid))
    ).first()

    if sessao:
        sessao.ativa = False
        db.session.commit()

    # Mensagem em tempo real para o outro usuário
    socketio.emit(
        "sessao_fechada",
        {"de": uid},
        room=contato_id
    )

    return jsonify({"ok": True})


# ============================================================
# 5. SOCKET — Conexão
# ============================================================
@socketio.on("connect")
def handle_connect():
    try:
        uid = session.get("usuario_id")
        if not uid:
            return

        online_users[uid] = request.sid
        join_room(uid)

        emit("user_online", {
            "id": uid,
            "nome": session["usuario_nome"],
            "perfil": session["usuario_perfil"]
        }, broadcast=True)

    except Exception as e:
        current_app.logger.error(f"[CHAT] Erro ao conectar socket: {e}")


# ============================================================
# 6. SOCKET — Desconexão
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
# 7. SOCKET — Enviar mensagem
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

        # ativa/reativa sessão
        criar_ou_ativar_sessao(de_id, para_id)

        ts = datetime.utcnow().replace(tzinfo=timezone.utc)

        # salva no banco
        msg = ChatMessage(
            de_id=de_id,
            para_id=para_id,
            texto=texto,
            horario=ts
        )
        db.session.add(msg)
        db.session.commit()

        # envia para outro
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

        # confirmação para o emissor
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
# 8. SOCKET — Carregar histórico
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

        emit(
            "load_messages_response",
            [
                {
                    "de": m.de_id,
                    "texto": m.texto,
                    "horario": m.horario.isoformat()
                }
                for m in mensagens
            ],
            room=request.sid
        )

    except Exception as e:
        current_app.logger.error(f"[CHAT] Erro ao carregar histórico: {e}")


# ============================================================
# 9. REST — Histórico HTTP
# ============================================================
@chat_bp.route("/chat/historico/<int:contato_id>")
@login_obrigatorio
@verificar_lockdown
def historico(contato_id):
    usuario_id = session["usuario_id"]

    mensagens = ChatMessage.query.filter(
        ((ChatMessage.de_id == usuario_id) & (ChatMessage.para_id == contato_id)) |
        ((ChatMessage.de_id == contato_id) & (ChatMessage.para_id == usuario_id))
    ).order_by(ChatMessage.horario.asc()).all()

    return jsonify([
        {
            "de": m.de_id,
            "texto": m.texto,
            "horario": m.horario.isoformat()
        }
        for m in mensagens
    ])
