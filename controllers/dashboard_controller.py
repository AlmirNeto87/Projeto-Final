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
        # Resumo das entidades
        # ==============================
        total_usuarios = Usuario.query.count()
        total_veiculos = Veiculo.query.count()
        total_equipamentos = Equipamento.query.count()

        # ==============================
        # Acessos negados HOJE (BR)
        # ==============================
        hoje = datetime.now(FUSO_BR).date()  # CORRIGIDO

        acessos_negados_hoje = (
            Log.query
            .filter(Log.tipo_operacao == "ACESSO_NEGADO")
            .filter(func.date(Log.horario) == hoje)
            .count()
        )

        # ==============================
        # Usuários por perfil
        # ==============================
        usuarios_por_perfil = (
            db.session.query(Usuario.perfil, func.count(Usuario.id))
            .group_by(Usuario.perfil)
            .all()
        )

        grafico_usuarios_labels = [perfil.value for perfil, _ in usuarios_por_perfil]
        grafico_usuarios_valores = [qtd for _, qtd in usuarios_por_perfil]

        # ==============================
        # Logins últimos 7 dias (BR)
        # ==============================
        sete_dias_atras = datetime.now(FUSO_BR) - timedelta(days=7)  # CORRIGIDO

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
        # Operações por tipo
        # ==============================
        operacoes = (
            db.session.query(Log.tipo_operacao, func.count(Log.id))
            .group_by(Log.tipo_operacao)
            .all()
        )

        grafico_operacao_labels = [op for op, _ in operacoes]
        grafico_operacao_valores = [qtd for _, qtd in operacoes]

        # ==============================
        # Últimos 20 logs (convertidos)
        # ==============================
        ultimos_logs = Log.query.order_by(Log.id.desc()).limit(20).all()

        for log in ultimos_logs:
            log.horario_brasil = ajustar_para_brasil(log.horario)  # CORRIGIDO

        # ==============================
        # Renderização
        # ==============================
        return render_template(
            "dashboard.html",
            titulo="Dashboard do Sistema",
            total_usuarios=total_usuarios,
            total_veiculos=total_veiculos,
            total_equipamentos=total_equipamentos,
            acessos_negados_hoje=acessos_negados_hoje,
            grafico_usuarios_labels=grafico_usuarios_labels,
            grafico_usuarios_valores=grafico_usuarios_valores,
            grafico_login_labels=grafico_login_labels,
            grafico_login_valores=grafico_login_valores,
            grafico_operacao_labels=grafico_operacao_labels,
            grafico_operacao_valores=grafico_operacao_valores,
            ultimos_logs=ultimos_logs
        )

    except Exception as e:
        try:
            from controllers.logs_controller import registrar_log
            registrar_log("ERRO_DASHBOARD", "Dashboard", f"Falha ao carregar dashboard: {e}")
        except:
            pass

        current_app.logger.exception("Falha ao renderizar dashboard")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao carregar dashboard."
        ), 500



# ====================================================
# API — DADOS DO DASHBOARD (JSON)
# ====================================================
@dashboard_bp.route("/dashboard/data/<entity>", methods=["GET"])
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
@verificar_lockdown
def dashboard_data(entity):
    try:
        # --------------------------
        # USUÁRIOS
        # --------------------------
        if entity == "usuarios":
            usuarios_por_perfil = (
                db.session.query(Usuario.perfil, func.count(Usuario.id))
                .group_by(Usuario.perfil)
                .all()
            )

            labels = [perfil.value for perfil, _ in usuarios_por_perfil]
            values = [qtd for _, qtd in usuarios_por_perfil]

            rows = [
                {
                    "id": u.id,
                    "name": u.name,
                    "email": u.email,
                    "perfil": u.perfil.value
                }
                for u in Usuario.query.order_by(Usuario.id.desc()).limit(50).all()
            ]

            return jsonify({
                "entity": "usuarios",
                "chart": {"type": "pie", "labels": labels, "values": values},
                "table": rows
            })

        # --------------------------
        # VEÍCULOS
        # --------------------------
        elif entity == "veiculos":
            veiculos_por_situacao = (
                db.session.query(Veiculo.situacao, func.count(Veiculo.id))
                .group_by(Veiculo.situacao)
                .all()
            )

            labels = [sit for sit, _ in veiculos_por_situacao]
            values = [qtd for _, qtd in veiculos_por_situacao]

            rows = [
                {
                    "id": v.id,
                    "marca": v.marca,
                    "modelo": v.modelo,
                    "ano": v.ano_fabricacao,
                    "situacao": v.situacao
                }
                for v in Veiculo.query.order_by(Veiculo.id.desc()).limit(50).all()
            ]

            return jsonify({
                "entity": "veiculos",
                "chart": {"type": "bar", "labels": labels, "values": values},
                "table": rows
            })

        # --------------------------
        # EQUIPAMENTOS
        # --------------------------
        elif entity == "equipamentos":
            equipamentos_por_nivel = (
                db.session.query(Equipamento.nivel_perigo, func.count(Equipamento.id))
                .group_by(Equipamento.nivel_perigo)
                .all()
            )

            labels = [nivel for nivel, _ in equipamentos_por_nivel]
            values = [qtd for _, qtd in equipamentos_por_nivel]

            rows = [
                {
                    "id": e.id,
                    "nome": e.nome,
                    "quantidade": e.quantidade,
                    "situacao": e.situacao,
                    "nivel_perigo": e.nivel_perigo
                }
                for e in Equipamento.query.order_by(Equipamento.id.desc()).limit(50).all()
            ]

            return jsonify({
                "entity": "equipamentos",
                "chart": {"type": "bar", "labels": labels, "values": values},
                "table": rows
            })

        return jsonify({"error": "entity inválida"}), 400

    except Exception as e:
        try:
            from controllers.logs_controller import registrar_log
            registrar_log("ERRO_DASHBOARD_API", "Dashboard",
                          f"Erro na rota API /dashboard/data/{entity}: {e}")
        except:
            pass

        current_app.logger.exception("Erro na API de dashboard")
        return jsonify({"error": "Erro interno no servidor"}), 500
