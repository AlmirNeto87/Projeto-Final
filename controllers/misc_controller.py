from functools import wraps
from flask import flash, redirect, render_template, request, session, url_for, current_app
from utils.decorators import login_obrigatorio, perfil_obrigatorio, verificar_lockdown
from controllers.logs_controller import registrar_log

# Modelos
from models.usuario_model import Usuario, PerfilEnum
from models.veiculo_model import Veiculo
from models.equipamento_model import Equipamento


# ================================
# CONSTANTES USADAS NOS FILTROS
# ================================
TIPO_OPCOES = ['Usuário', 'Veículo', 'Equipamento']
TIPO_PERFIL = [p.value for p in PerfilEnum]
STATUS_VEICULO_OPCOES = Veiculo.SITUACAO_OPCOES
NIVEIS_PERIGO_OPCOES = ['Baixo', 'Médio', 'Alto']
TODOS = "Todos"


# ================================
# CONTROLLER: BUSCA ADMINISTRATIVA
# ================================
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
@verificar_lockdown
def buscar_adm():
    resultados = {'usuarios': [], 'veiculos': [], 'equipamentos': []}

    termo_busca = request.args.get('termo_busca', '').strip()
    filtro_tipo = request.args.get('tipo', TODOS)
    filtro_perfil = request.args.get('perfil')
    filtro_status_veiculo = request.args.get('status_veiculo')
    filtro_local_veiculo = request.args.get('local_veiculo')
    filtro_nivel_perigo = request.args.get('nivel_perigo')

    filtros_ativos = {
        'termo_busca': termo_busca,
        'tipo': filtro_tipo,
        'perfil': filtro_perfil,
        'status_veiculo': filtro_status_veiculo,
        'local_veiculo': filtro_local_veiculo,
        'nivel_perigo': filtro_nivel_perigo,
    }

    filtros_preenchidos = (
        termo_busca
        or filtro_tipo != TODOS
        or any([filtro_perfil, filtro_status_veiculo, filtro_local_veiculo, filtro_nivel_perigo])
    )

    if filtros_preenchidos:
        try:
            # USUÁRIOS
            if filtro_tipo in ['Usuário', TODOS]:
                query = Usuario.query
                if termo_busca:
                    query = query.filter(Usuario.name.ilike(f"%{termo_busca}%"))
                if filtro_perfil and filtro_perfil in TIPO_PERFIL:
                    try:
                        perfil_enum = PerfilEnum(filtro_perfil)
                        query = query.filter_by(perfil=perfil_enum)
                    except Exception:
                        flash("Perfil inválido.", "warning")
                resultados['usuarios'] = query.all()

            # VEÍCULOS
            if filtro_tipo in ['Veículo', TODOS]:
                query = Veiculo.query
                if termo_busca:
                    query = query.filter(Veiculo.modelo.ilike(f"%{termo_busca}%"))
                if filtro_status_veiculo in STATUS_VEICULO_OPCOES:
                    query = query.filter_by(situacao=filtro_status_veiculo)
                if filtro_local_veiculo:
                    query = query.filter(Veiculo.local_armazenamento.ilike(f"%{filtro_local_veiculo}%"))
                resultados['veiculos'] = query.all()

            # EQUIPAMENTOS
            if filtro_tipo in ['Equipamento', TODOS]:
                query = Equipamento.query
                if termo_busca:
                    query = query.filter(Equipamento.nome.ilike(f"%{termo_busca}%"))
                if filtro_nivel_perigo in NIVEIS_PERIGO_OPCOES:
                    query = query.filter_by(nivel_perigo=filtro_nivel_perigo)
                resultados['equipamentos'] = query.all()

            registrar_log(
                tipo_operacao="BUSCA_ADMIN",
                tipo_modelo="Sistema",
                descricao="Busca administrativa realizada.",
                modificacoes=str(filtros_ativos)
            )

        except Exception as e:
            registrar_log("ERRO_BUSCA_ADMIN", "Sistema", f"Erro: {e}")
            flash("Erro ao realizar a busca.", "danger")
            return redirect(url_for("internal_server_error"))

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


# ================================
# ➤➤ FUNÇÕES DO LOCKDOWN ⬅⬅
# ================================

@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def ativar_lockdown():
    current_app.config["LOCKDOWN_ATIVO"] = True

    registrar_log(
        "LOCKDOWN_ATIVADO",
        "Sistema",
        "Lockdown ativado pelo administrador.",
        modificacoes=None
    )

    flash("⚠️ Lockdown ativado com sucesso!", "warning")
    return redirect(url_for("home"))


@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def desativar_lockdown():
    current_app.config["LOCKDOWN_ATIVO"] = False

    registrar_log(
        "LOCKDOWN_DESATIVADO",
        "Sistema",
        "Lockdown desativado pelo administrador.",
        modificacoes=None
    )

    flash("🔓 Lockdown desativado.", "success")
    return redirect(url_for("home"))


# ================================
# PÁGINA DE BLOQUEIO
# ================================
def pagina_bloqueio():
    return render_template("bloqueio.html", titulo="Acesso Restrito")


# ================================
# PÁGINAS ESTÁTICAS
# ================================
def sobre():
    return render_template("sobre.html", titulo="Sobre")


def contatos():
    return render_template("contatos.html", titulo="Contatos")


# ================================
# ERROR HANDLERS
# ================================
def page_not_found(e):
    perfil = session.get("usuario_perfil", None)
    return render_template(
        '404.html',
        error_code=404,
        error_message="Página não encontrada.",
        perfil_usuario=perfil
    ), 404


def internal_server_error(e):
    perfil = session.get("usuario_perfil", None)
    return render_template(
        '404.html',
        error_code=500,
        error_message="Erro interno no servidor.",
        perfil_usuario=perfil
    ), 500
