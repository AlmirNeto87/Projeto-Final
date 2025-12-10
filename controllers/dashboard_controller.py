from flask import Blueprint, render_template, request, jsonify, current_app
from utils.decorators import login_obrigatorio, perfil_obrigatorio, verificar_lockdown
from models.usuario_model import Usuario, PerfilEnum
from models.veiculo_model import Veiculo
from models.equipamento_model import Equipamento
from models.log_model import Log
from config import db
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

dashboard_bp = Blueprint("dashboard", __name__)

# ============================================
# Fuso horário — Brasil (UTC-3)
# ============================================
FUSO_BR = ZoneInfo("America/Sao_Paulo")

def ajustar_para_brasil(dt):
    """Converte datetime UTC para horário do Brasil (UTC-3)."""
    if not dt:
        return None
    # garante que dt_utc é timezone-aware em UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(FUSO_BR)

# ====================================================
# DASHBOARD PRINCIPAL (ADMIN DE SEGURANÇA)
# ====================================================
@dashboard_bp.route("/dashboard")
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
@verificar_lockdown
def dashboard():
    try:
        # ==============================
        # RESUMO
        # ==============================
        total_usuarios = Usuario.query.count()
        total_veiculos = Veiculo.query.count()
        total_equipamentos = Equipamento.query.count()

        # ==============================
        # ACESSOS NEGADOS HOJE
        # ==============================
        hoje = datetime.now(FUSO_BR).date()

        acessos_negados_hoje = (
            Log.query
            .filter(Log.tipo_operacao == "ACESSO_NEGADO")
            .filter(func.date(Log.horario) == hoje)
            .count()
        )

        # ==============================
        # USUÁRIOS POR PERFIL
        # ==============================
        usuarios_por_perfil = (
            db.session.query(Usuario.perfil, func.count(Usuario.id))
            .group_by(Usuario.perfil)
            .all()
        )

        grafico_usuarios_labels = [perfil.value for perfil, _ in usuarios_por_perfil]
        grafico_usuarios_valores = [qtd for _, qtd in usuarios_por_perfil]

        # ==============================
        # LOGINS ÚLTIMOS 7 DIAS
        # ==============================
        sete_dias_atras = datetime.now(FUSO_BR) - timedelta(days=7)

        logins_por_dia = (
            db.session.query(func.date(Log.horario), func.count(Log.id))
            .filter(Log.tipo_operacao == "LOGIN_SUCESSO")
            .filter(Log.horario >= sete_dias_atras)
            .group_by(func.date(Log.horario))
            .order_by(func.date(Log.horario))
            .all()
        )

        grafico_login_labels = [str(data) for data, _ in logins_por_dia]
        grafico_login_valores = [qtd for _, qtd in logins_por_dia]

        # ==============================
        # OPERACOES POR TIPO
        # ==============================
        operacoes = (
            db.session.query(Log.tipo_operacao, func.count(Log.id))
            .group_by(Log.tipo_operacao)
            .all()
        )

        grafico_operacao_labels = [op for op, _ in operacoes]
        grafico_operacao_valores = [qtd for _, qtd in operacoes]

        # ==============================
        # ÚLTIMOS LOGS
        # ==============================
        ultimos_logs = Log.query.order_by(Log.id.desc()).limit(20).all()

        for log in ultimos_logs:
            log.horario_brasil = ajustar_para_brasil(log.horario)

        # ==============================
        # RENDERIZAÇÃO
        # ==============================
        return render_template(
            "dashboard.html",
            titulo="Dashboard do Sistema",
            total_usuarios=total_usuarios,
            total_veiculos=total_veiculos,
            total_equipamentos=total_equipamentos,
            acessos_negados_hoje=acessos_negados_hoje,

            # gráficos iniciais do servidor
            grafico_usuarios_labels=grafico_usuarios_labels,
            grafico_usuarios_valores=grafico_usuarios_valores,
            grafico_login_labels=grafico_login_labels,
            grafico_login_valores=grafico_login_valores,
            grafico_operacao_labels=grafico_operacao_labels,
            grafico_operacao_valores=grafico_operacao_valores,

            ultimos_logs=ultimos_logs
        )

    except Exception as e:
        current_app.logger.exception("Falha ao renderizar dashboard")
        return render_template("404.html",
                               error_code=500,
                               error_message="Erro ao carregar dashboard."), 500



# ====================================================
# API — DADOS DO DASHBOARD (JSON)
# ====================================================
@dashboard_bp.route("/dashboard/data/<entity>", methods=["GET"])
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
@verificar_lockdown
def dashboard_data(entity):
    try:

        # =====================================================
        # USUÁRIOS
        # =====================================================
        if entity == "usuarios":
            usuarios_por_perfil = (
                db.session.query(Usuario.perfil, func.count(Usuario.id))
                .group_by(Usuario.perfil)
                .all()
            )

            chart_main = {
                "type": "pie",
                "labels": [perfil.value for perfil, _ in usuarios_por_perfil],
                "values": [qtd for _, qtd in usuarios_por_perfil],
                "title": "Distribuição por Perfil"
            }

            # gráfico secundário = logins últimos 7 dias
            sete_dias_atras = datetime.now(FUSO_BR) - timedelta(days=7)
            logins = (
                db.session.query(func.date(Log.horario), func.count(Log.id))
                .filter(Log.tipo_operacao == "LOGIN_SUCESSO")
                .filter(Log.horario >= sete_dias_atras)
                .group_by(func.date(Log.horario))
                .all()
            )

            chart2 = {
                "type": "line",
                "labels": [str(d) for d, _ in logins],
                "values": [q for _, q in logins],
                "title": "Logins - Últimos 7 dias"
            }

            rows = [
                {
                    "ID": u.id,
                    "Nome": u.name,
                    "Email": u.email,
                    "Perfil": u.perfil.value
                }
                for u in Usuario.query.order_by(Usuario.id.desc()).all()
            ]

            return jsonify({
                "entity": "usuarios",
                "chart": chart_main,
                "chart2": chart2,
                "table": rows
            })


        # =====================================================
        # VEÍCULOS
        # =====================================================
        if entity == "veiculos":

            # gráfico principal = situação
            por_situacao = (
                db.session.query(Veiculo.situacao, func.count(Veiculo.id))
                .group_by(Veiculo.situacao)
                .all()
            )
            

            chart_main = {
                "type": "pie",
                "labels": [sit for sit, _ in por_situacao],
                "values": [qtd for _, qtd in por_situacao],
                "title": "Situação dos Veículos"
            }

            # gráfico secundário = quantidade por localidade (exemplo)
            por_local = (
                db.session.query(Veiculo.local_armazenamento, func.count(Veiculo.id))
                .group_by(Veiculo.local_armazenamento)
                .all()
            )

            chart2 = {
                "type": "bar",
                "labels": [(loc if loc else "Não informado") for loc, _ in por_local],
                "values": [qtd for _, qtd in por_local],
                "title": "Localização dos Veículos"
            }

            rows = [
                {
                    "ID": v.id,
                    "Marca": v.marca,
                    "Modelo": v.modelo,
                    "Ano": v.ano_fabricacao,
                    "Situação": v.situacao,
                    "Localização": v.local_armazenamento
                }
                for v in Veiculo.query.order_by(Veiculo.id.desc()).all()
            ]

            return jsonify({
                "entity": "veiculos",
                "chart": chart_main,
                "chart2": chart2,
                "table": rows
            })


        # =====================================================
        # EQUIPAMENTOS
        # =====================================================
        if entity == "equipamentos":

            # gráfico principal = nível de perigo
            por_perigo = (
                db.session.query(Equipamento.nivel_perigo, func.count(Equipamento.id))
                .group_by(Equipamento.nivel_perigo)
                .all()
            )

            chart_main = {
                "type": "bar",
                "labels": [n for n, _ in por_perigo],
                "values": [qtd for _, qtd in por_perigo],
                "title": "Nível de Perigo"
            }

            # gráfico secundário = situação
            por_situacao = (
                db.session.query(Equipamento.situacao, func.count(Equipamento.id))
                .group_by(Equipamento.situacao)
                .all()
            )

            chart2 = {
                "type": "pie",
                "labels": [s for s, _ in por_situacao],
                "values": [qtd for _, qtd in por_situacao],
                "title": "Situação dos Equipamentos"
            }

            rows = [
                {
                    "ID": e.id,
                    "Nome": e.nome,
                    "Qtd": e.quantidade,
                    "Situação": e.situacao,
                    "Perigo": e.nivel_perigo
                }
                for e in Equipamento.query.order_by(Equipamento.id.desc()).all()
            ]

            return jsonify({
                "entity": "equipamentos",
                "chart": chart_main,
                "chart2": chart2,
                "table": rows
            })


        return jsonify({"error": "entity inválida"}), 400


    except Exception as e:
        current_app.logger.exception(f"Erro na API dashboard: {e}")
        return jsonify({"error": "Erro interno"}), 500
