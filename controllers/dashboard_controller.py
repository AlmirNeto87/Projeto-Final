from flask import Blueprint, render_template, request, jsonify, current_app
from utils.decorators import login_obrigatorio, perfil_obrigatorio, verificar_lockdown
from models.usuario_model import Usuario, PerfilEnum
from models.veiculo_model import Veiculo
from models.equipamento_model import Equipamento
from models.log_model import Log
from config import db
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint("dashboard", __name__)


# Página principal do dashboard (só Admin de Segurança)
@dashboard_bp.route("/dashboard")
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
@verificar_lockdown
def dashboard():
    try:
        # Cards resumo
        total_usuarios = Usuario.query.count()
        total_veiculos = Veiculo.query.count()
        total_equipamentos = Equipamento.query.count()

        hoje = datetime.now().date()
        acessos_negados_hoje = Log.query.filter(
            Log.tipo_operacao == "ACESSO_NEGADO",
            func.date(Log.horario) == hoje
        ).count()

        # Usuários por perfil
        usuarios_por_perfil = (
            db.session.query(Usuario.perfil, func.count(Usuario.id))
            .group_by(Usuario.perfil)
            .all()
        )
        grafico_usuarios_labels = [p.value for p, _ in usuarios_por_perfil]
        grafico_usuarios_valores = [q for _, q in usuarios_por_perfil]

        # Logins últimos 7 dias
        sete_dias = datetime.now() - timedelta(days=7)
        logins_por_dia = (
            db.session.query(func.date(Log.horario), func.count(Log.id))
            .filter(Log.tipo_operacao == "LOGIN_SUCESSO")
            .filter(Log.horario >= sete_dias)
            .group_by(func.date(Log.horario))
            .order_by(func.date(Log.horario))
            .all()
        )
        grafico_login_labels = [str(d) for d, _ in logins_por_dia]
        grafico_login_valores = [q for _, q in logins_por_dia]

        # Operações por tipo
        operacoes = (
            db.session.query(Log.tipo_operacao, func.count(Log.id))
            .group_by(Log.tipo_operacao)
            .all()
        )
        grafico_operacao_labels = [op for op, _ in operacoes]
        grafico_operacao_valores = [q for _, q in operacoes]

        # Últimos logs
        ultimos_logs = Log.query.order_by(Log.id.desc()).limit(20).all()

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
            registrar_log("ERRO_DASHBOARD", "Dashboard", f"Erro ao carregar dashboard: {e}")
        except:
            pass
        current_app.logger.exception("Erro ao renderizar dashboard")
        return render_template("404.html", titulo="Erro", error_code=500, error_message="Erro ao carregar dashboard"), 500



# Rota API: retorna dados JSON para cada entidade
@dashboard_bp.route("/dashboard/data/<entity>", methods=["GET"])
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
@verificar_lockdown
def dashboard_data(entity):
    try:
        if entity == "usuarios":
            usuarios_por_perfil = (
                db.session.query(Usuario.perfil, func.count(Usuario.id))
                .group_by(Usuario.perfil)
                .all()
            )
            labels = [p.value for p, _ in usuarios_por_perfil]
            values = [q for _, q in usuarios_por_perfil]

            rows = [
                {"id": u.id, "name": u.name, "email": u.email, "perfil": u.perfil.value}
                for u in Usuario.query.order_by(Usuario.id.desc()).limit(50).all()
            ]

            return jsonify({
                "entity": "usuarios",
                "chart": {"type": "pie", "labels": labels, "values": values},
                "table": rows
            })

        elif entity == "veiculos":
            veiculos_por_situacao = (
                db.session.query(Veiculo.situacao, func.count(Veiculo.id))
                .group_by(Veiculo.situacao)
                .all()
            )
            labels = [s for s, _ in veiculos_por_situacao]
            values = [q for _, q in veiculos_por_situacao]

            rows = [
                {"id": v.id, "marca": v.marca, "modelo": v.modelo, "ano": v.ano_fabricacao, "situacao": v.situacao}
                for v in Veiculo.query.order_by(Veiculo.id.desc()).limit(50).all()
            ]

            return jsonify({
                "entity": "veiculos",
                "chart": {"type": "bar", "labels": labels, "values": values},
                "table": rows
            })

        elif entity == "equipamentos":
            equipamentos_por_nivel = (
                db.session.query(Equipamento.nivel_perigo, func.count(Equipamento.id))
                .group_by(Equipamento.nivel_perigo)
                .all()
            )
            labels = [n for n, _ in equipamentos_por_nivel]
            values = [q for _, q in equipamentos_por_nivel]

            rows = [
                {"id": e.id, "nome": e.nome, "quantidade": e.quantidade, "situacao": e.situacao, "nivel_perigo": e.nivel_perigo}
                for e in Equipamento.query.order_by(Equipamento.id.desc()).limit(50).all()
            ]

            return jsonify({
                "entity": "equipamentos",
                "chart": {"type": "bar", "labels": labels, "values": values},
                "table": rows
            })

        else:
            return jsonify({"error": "entity inválida"}), 400

    except Exception as e:
        try:
            from controllers.logs_controller import registrar_log
            registrar_log("ERRO_DASHBOARD_API", "Dashboard", f"Erro na API /dashboard/data/{entity}: {e}")
        except:
            pass
        current_app.logger.exception("Erro na API de dashboard")
        return jsonify({"error": "Erro interno"}), 500
