from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app
)
from utils.decorators import login_obrigatorio, perfil_obrigatorio, verificar_lockdown
from controllers.logs_controller import registrar_log

# Modelos
from models.usuario_model import Usuario, PerfilEnum
from models.veiculo_model import Veiculo
from models.equipamento_model import Equipamento


# =====================================================================
# CONSTANTES DE FILTRO
# =====================================================================
TIPO_OPCOES = ["Usuário", "Veículo", "Equipamento"]
TIPO_PERFIL = [p.value for p in PerfilEnum]
STATUS_VEICULO_OPCOES = Veiculo.SITUACAO_OPCOES
NIVEIS_PERIGO_OPCOES = ["Baixo", "Médio", "Alto"]
TODOS = "Todos"


# =====================================================================
# BUSCA ADMINISTRATIVA (Somente Admin de Segurança)
# =====================================================================
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
@verificar_lockdown
def buscar_adm():
    """Painel avançado de busca administrativa."""
    try:

        resultados = {"usuarios": [], "veiculos": [], "equipamentos": []}

        termo_busca = request.args.get("termo_busca", "").strip()
        filtro_tipo = request.args.get("tipo", TODOS)
        filtro_perfil = request.args.get("perfil")
        filtro_status_veiculo = request.args.get("status_veiculo")
        filtro_local_veiculo = request.args.get("local_veiculo")
        filtro_nivel_perigo = request.args.get("nivel_perigo")

        filtros_ativos = {
            "termo_busca": termo_busca,
            "tipo": filtro_tipo,
            "perfil": filtro_perfil,
            "status_veiculo": filtro_status_veiculo,
            "local_veiculo": filtro_local_veiculo,
            "nivel_perigo": filtro_nivel_perigo,
        }

        filtros_preenchidos = (
            termo_busca
            or filtro_tipo != TODOS
            or any([
                filtro_perfil,
                filtro_status_veiculo,
                filtro_local_veiculo,
                filtro_nivel_perigo
            ])
        )

        if filtros_preenchidos:

            # =============================
            # FILTRAR USUÁRIOS
            # =============================
            if filtro_tipo in ["Usuário", TODOS]:
                query = Usuario.query

                if termo_busca:
                    query = query.filter(Usuario.name.ilike(f"%{termo_busca}%"))

                if filtro_perfil and filtro_perfil in TIPO_PERFIL:
                    try:
                        query = query.filter_by(perfil=PerfilEnum(filtro_perfil))
                    except:
                        flash("Perfil inválido informado.", "warning")

                resultados["usuarios"] = query.all()

            # =============================
            # FILTRAR VEÍCULOS
            # =============================
            if filtro_tipo in ["Veículo", TODOS]:
                query = Veiculo.query

                if termo_busca:
                    query = query.filter(Veiculo.modelo.ilike(f"%{termo_busca}%"))

                if filtro_status_veiculo in STATUS_VEICULO_OPCOES:
                    query = query.filter_by(situacao=filtro_status_veiculo)

                if filtro_local_veiculo:
                    query = query.filter(
                        Veiculo.local_armazenamento.ilike(f"%{filtro_local_veiculo}%")
                    )

                resultados["veiculos"] = query.all()

            # =============================
            # FILTRAR EQUIPAMENTOS
            # =============================
            if filtro_tipo in ["Equipamento", TODOS]:
                query = Equipamento.query

                if termo_busca:
                    query = query.filter(Equipamento.nome.ilike(f"%{termo_busca}%"))

                if filtro_nivel_perigo in NIVEIS_PERIGO_OPCOES:
                    query = query.filter_by(nivel_perigo=filtro_nivel_perigo)

                resultados["equipamentos"] = query.all()

            # Registro de log da ação
            registrar_log(
                "BUSCA_ADMIN",
                "Sistema",
                "Busca administrativa realizada.",
                modificacoes=str(filtros_ativos)
            )

        return render_template(
            "buscar_adm.html",
            titulo="Busca Administrativa de Recursos",
            resultados=resultados,
            tipo_opcoes=TIPO_OPCOES,
            tipos_perfil=TIPO_PERFIL,
            status_veiculo_opcoes=STATUS_VEICULO_OPCOES,
            niveis_perigo_opcoes=NIVEIS_PERIGO_OPCOES,
            **filtros_ativos
        )

    except Exception as e:
        registrar_log("ERRO_BUSCA_ADMIN", "Sistema", f"Erro inesperado: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao realizar a busca administrativa."
        ), 500


# =====================================================================
# LOCKDOWN — ATIVAR / DESATIVAR
# =====================================================================
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def ativar_lockdown():
    try:
        current_app.config["LOCKDOWN_ATIVO"] = True

        registrar_log(
            "LOCKDOWN_ATIVADO",
            "Sistema",
            "Lockdown ativado pelo administrador."
        )

        flash("⚠️ Lockdown ativado com sucesso!", "warning")
        return redirect(url_for("home"))

    except Exception as e:
        registrar_log("ERRO_ATIVAR_LOCKDOWN", "Sistema", f"Erro: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao ativar o lockdown."
        ), 500


@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def desativar_lockdown():
    try:
        current_app.config["LOCKDOWN_ATIVO"] = False

        registrar_log(
            "LOCKDOWN_DESATIVADO",
            "Sistema",
            "Lockdown desativado pelo administrador."
        )

        flash("🔓 Lockdown desativado.", "success")
        return redirect(url_for("home"))

    except Exception as e:
        registrar_log("ERRO_DESATIVAR_LOCKDOWN", "Sistema", f"Erro: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao desativar o lockdown."
        ), 500


# =====================================================================
# PÁGINA DE BLOQUEIO
# =====================================================================
def pagina_bloqueio():
    try:
        return render_template("bloqueio.html", titulo="Acesso Restrito")
    except Exception as e:
        registrar_log("ERRO_PAGINA_BLOQUEIO", "Sistema", f"Erro: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao exibir página de bloqueio."
        ), 500


# =====================================================================
# PÁGINAS ESTÁTICAS
# =====================================================================
def sobre():
    try:
        return render_template("sobre.html", titulo="Sobre")
    except Exception as e:
        registrar_log("ERRO_SOBRE", "Sistema", f"Erro: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao carregar a página Sobre."
        ), 500


def contatos():
    try:
        return render_template("contatos.html", titulo="Contatos")
    except Exception as e:
        registrar_log("ERRO_CONTATOS", "Sistema", f"Erro: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao carregar a página de contatos."
        ), 500


# =====================================================================
# TRATAMENTO DE ERROS
# =====================================================================
def page_not_found(e):
    perfil = session.get("usuario_perfil")
    return render_template(
        "404.html",
        error_code=404,
        error_message="Página não encontrada.",
        perfil_usuario=perfil
    ), 404


def internal_server_error(e):
    perfil = session.get("usuario_perfil")
    return render_template(
        "404.html",
        error_code=500,
        error_message="Erro interno no servidor.",
        perfil_usuario=perfil
    ), 500
