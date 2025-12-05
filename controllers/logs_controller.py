from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, make_response, current_app
)
from config import db
from models.log_model import Log
from utils.decorators import login_obrigatorio, perfil_obrigatorio, verificar_lockdown
from models.usuario_model import PerfilEnum
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import csv
import io
import json

logs_bp = Blueprint("logs", __name__)

# ================================================================
# FUSO HORÁRIO DO BRASIL (OFICIAL)
# ================================================================
FUSO_BR = ZoneInfo("America/Sao_Paulo")

def utc_to_brasil(dt_utc):
    if not dt_utc:
        return None
    # garante que dt_utc é timezone-aware em UTC
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
    return dt_utc.astimezone(FUSO_BR)

# ================================================================
# REGISTRAR LOG
# ================================================================
def registrar_log(tipo_operacao: str, tipo_modelo: str, descricao: str, modificacoes=None):
    try:
        usuario_id = session.get("usuario_id", 0)
        usuario_nome = session.get("usuario_nome", "Sistema")
        usuario_perfil = session.get("usuario_perfil", "N/A")

        if isinstance(modificacoes, dict):
            modificacoes = json.dumps(modificacoes, ensure_ascii=False)

        novo_log = Log(
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            usuario_perfil=usuario_perfil,
            tipo_operacao=tipo_operacao,
            tipo_modelo=tipo_modelo,
            descricao=descricao,
            modificacoes=modificacoes
        )

        db.session.add(novo_log)
        db.session.commit()

    except Exception as e:
        db.session.rollback()

        try:
            erro_log = Log(
                usuario_id=0,
                usuario_nome="Sistema",
                usuario_perfil="N/A",
                tipo_operacao="ERRO_LOG",
                tipo_modelo="Log",
                descricao=f"Falha ao salvar log original: {e}",
                modificacoes=None
            )
            db.session.add(erro_log)
            db.session.commit()
        except:
            db.session.rollback()


# ================================================================
# LISTAR LOGS
# ================================================================
@logs_bp.route("/logs", methods=["GET"])
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
@verificar_lockdown
def listar_logs():

    query = Log.query

    # Filtro de usuário
    usuario = request.args.get("usuario")
    if usuario:
        query = query.filter(Log.usuario_nome.ilike(f"%{usuario}%"))

    # Filtro de operação
    tipo = request.args.get("tipo")
    if tipo:
        query = query.filter(Log.tipo_operacao.ilike(f"%{tipo}%"))

    # Filtro de datas
    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")

    try:
        if data_inicio:
            dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.filter(Log.horario >= dt_inicio)

        if data_fim:
            dt_fim = datetime.strptime(data_fim, "%Y-%m-%d")
            query = query.filter(Log.horario <= dt_fim)
    except Exception:
        flash("Datas inválidas no filtro!", "danger")

    logs = query.order_by(Log.id.desc()).all()

    # Converte horário para o Brasil
    for log in logs:
        log.horario_brasil = utc_to_brasil(log.horario)

    return render_template(
        "logs.html",
        titulo="Logs do Sistema",
        logs=logs
    )


# ================================================================
# EXPORTAR LOGS CSV
# ================================================================
@logs_bp.route("/logs/exportar")
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
@verificar_lockdown
def exportar_logs():

    logs = Log.query.order_by(Log.id.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Data/Hora (Brasil)", "Usuário", "Perfil",
        "Operação", "Modelo", "Descrição", "Modificações"
    ])

    for log in logs:
        data_br = utc_to_brasil(log.horario).strftime("%d/%m/%Y %H:%M:%S")
        writer.writerow([
            log.id,
            data_br,
            log.usuario_nome,
            log.usuario_perfil,
            log.tipo_operacao,
            log.tipo_modelo,
            log.descricao,
            log.modificacoes or ""
        ])

    output.seek(0)

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=logs.csv"
    response.headers["Content-Type"] = "text/csv"

    return response


# ================================================================
# EXPORTAR JSON
# ================================================================
@logs_bp.route("/logs/exportar_json")
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
@verificar_lockdown
def exportar_logs_json():

    logs = Log.query.order_by(Log.id.desc()).all()

    lista_logs = [{
        "id": log.id,
        "horario": utc_to_brasil(log.horario).strftime("%Y-%m-%d %H:%M:%S"),
        "usuario_id": log.usuario_id,
        "usuario_nome": log.usuario_nome,
        "usuario_perfil": log.usuario_perfil,
        "tipo_operacao": log.tipo_operacao,
        "tipo_modelo": log.tipo_modelo,
        "descricao": log.descricao,
        "modificacoes": log.modificacoes
    } for log in logs]

    conteudo_json = json.dumps(lista_logs, ensure_ascii=False, indent=4)

    response = make_response(conteudo_json)
    response.headers["Content-Disposition"] = "attachment; filename=logs.json"
    response.headers["Content-Type"] = "application/json; charset=utf-8"

    return response
