from flask import render_template, request, redirect, url_for, flash, session
from config import db
from models.equipamento_model import Equipamento
from models.usuario_model import PerfilEnum
from utils.decorators import login_obrigatorio, perfil_obrigatorio, verificar_lockdown
from controllers.logs_controller import registrar_log
from datetime import datetime


# ======================================================
# LISTAR EQUIPAMENTOS
# ======================================================
@login_obrigatorio
@verificar_lockdown
def listar_equipamentos():
    try:
        perfil_usuario = session.get("usuario_perfil")
        equipamentos = Equipamento.query.all()
        situacoes_permitidas = Equipamento.SITUACAO_OPCOES

        return render_template(
            "equipamentos.html",
            titulo="Lista de Equipamentos",
            equipamentos=equipamentos,
            situacoes=situacoes_permitidas,
            perfil=perfil_usuario
        )

    except Exception as e:
        registrar_log("ERRO_LISTAR_EQUIPAMENTOS", "Equipamento", f"Erro ao listar equipamentos: {e}")
        flash("Erro ao carregar lista de equipamentos.", "danger")
        return redirect(url_for("internal_server_error"))


# ======================================================
# CADASTRAR EQUIPAMENTO
# ======================================================
@login_obrigatorio
@verificar_lockdown
@perfil_obrigatorio(PerfilEnum.GERENTE, PerfilEnum.ADMIN_SEGURANCA)
def cadastrar_equipamento():
    if request.method == 'POST':
        try:
            nome = request.form["nome"]
            quantidade = int(request.form["quantidade"])
            data_vencimento_str = request.form["data_vencimento"]
            descricao = request.form["descricao"]
            nivel_perigo = request.form["nivel_perigo"]
            situacao = request.form["situacao"]

            try:
                data_vencimento = datetime.strptime(data_vencimento_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Data de vencimento inválida. Use o formato AAAA-MM-DD.", "danger")
                return redirect(url_for("cadastrar_equipamento"))

            novo = Equipamento(
                nome=nome,
                quantidade=quantidade,
                data_vencimento=data_vencimento,
                descricao=descricao,
                nivel_perigo=nivel_perigo,
                situacao=situacao
            )

            db.session.add(novo)
            db.session.commit()

            registrar_log(
                tipo_operacao="CRIAR",
                tipo_modelo="Equipamento",
                descricao=f"Equipamento cadastrado: {nome}",
                modificacoes={
                    "nome": nome,
                    "quantidade": quantidade,
                    "vencimento": data_vencimento_str,
                    "situacao": situacao
                }
            )

            flash("Equipamento cadastrado com sucesso!", "success")
            return redirect(url_for("listar_equipamentos"))

        except Exception as e:
            registrar_log("ERRO_CADASTRAR_EQUIPAMENTO", "Equipamento", f"Erro ao cadastrar: {e}")
            db.session.rollback()
            flash("Erro ao cadastrar equipamento.", "danger")
            return redirect(url_for("internal_server_error"))

    try:
        return render_template(
            "cadastrar_equipamento.html",
            titulo="Cadastro de Equipamentos",
            situacoes=Equipamento.SITUACAO_OPCOES
        )
    except Exception as e:
        registrar_log("ERRO_RENDER_CADASTRAR_EQUIPAMENTO", "Sistema", f"Erro ao renderizar formulário: {e}")
        return redirect(url_for("internal_server_error"))


# ======================================================
# EDITAR EQUIPAMENTO
# ======================================================
@login_obrigatorio
@verificar_lockdown
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def editar_equipamento(id):
    try:
        equipamento = Equipamento.query.get(id)
    except Exception as e:
        registrar_log("ERRO_BUSCAR_EQUIPAMENTO_EDITAR", "Equipamento", f"Erro ao buscar equipamento: {e}")
        return redirect(url_for("internal_server_error"))

    if not equipamento:
        return render_template("404.html", descErro="Equipamento não encontrado")

    if request.method == "POST":
        try:
            antigo = {
                "nome": equipamento.nome,
                "quantidade": equipamento.quantidade,
                "descricao": equipamento.descricao,
                "nivel_perigo": equipamento.nivel_perigo,
                "situacao": equipamento.situacao,
                "vencimento": str(equipamento.data_vencimento)
            }

            equipamento.nome = request.form["nome"]
            equipamento.quantidade = int(request.form["quantidade"])
            equipamento.descricao = request.form["descricao"]
            equipamento.nivel_perigo = request.form["nivel_perigo"]
            equipamento.situacao = request.form["situacao"]

            try:
                equipamento.data_vencimento = datetime.strptime(
                    request.form["data_vencimento"], "%Y-%m-%d"
                ).date()
            except ValueError:
                flash("Data de vencimento inválida. Use o formato AAAA-MM-DD.", "danger")
                return redirect(url_for("editar_equipamento", id=id))

            db.session.commit()

            registrar_log(
                tipo_operacao="ATUALIZAR",
                tipo_modelo="Equipamento",
                descricao=f"Equipamento atualizado: {equipamento.nome}",
                modificacoes={"antes": antigo, "depois": {
                    "nome": equipamento.nome,
                    "quantidade": equipamento.quantidade,
                    "descricao": equipamento.descricao,
                    "nivel_perigo": equipamento.nivel_perigo,
                    "situacao": equipamento.situacao,
                    "vencimento": str(equipamento.data_vencimento)
                }}
            )

            flash("Equipamento atualizado com sucesso!", "success")
            return redirect(url_for("listar_equipamentos"))

        except Exception as e:
            registrar_log("ERRO_EDITAR_EQUIPAMENTO", "Equipamento", f"Erro ao editar equipamento {id}: {e}")
            db.session.rollback()
            flash("Erro ao atualizar equipamento.", "danger")
            return redirect(url_for("internal_server_error"))

    try:
        return render_template(
            "editar_equipamento.html",
            titulo="Edição de Equipamento",
            equipamento=equipamento,
            situacoes=Equipamento.SITUACAO_OPCOES
        )
    except Exception as e:
        registrar_log("ERRO_RENDER_EDITAR_EQUIPAMENTO", "Sistema", f"Erro ao renderizar página de edição: {e}")
        return redirect(url_for("internal_server_error"))


# ======================================================
# DELETAR EQUIPAMENTO
# ======================================================
@login_obrigatorio
@verificar_lockdown
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def deletar_equipamento(id):
    try:
        equipamento = Equipamento.query.get(id)
    except Exception as e:
        registrar_log("ERRO_BUSCAR_EQUIPAMENTO_DELETAR", "Equipamento", f"Erro ao buscar equipamento: {e}")
        return redirect(url_for("internal_server_error"))

    if not equipamento:
        return render_template("404.html", descErro="Equipamento não encontrado")

    try:
        info = {
            "nome": equipamento.nome,
            "quantidade": equipamento.quantidade,
            "situacao": equipamento.situacao
        }

        db.session.delete(equipamento)
        db.session.commit()

        registrar_log(
            tipo_operacao="DELETAR",
            tipo_modelo="Equipamento",
            descricao=f"Equipamento deletado: {info['nome']}",
            modificacoes=info
        )

        flash("Equipamento deletado com sucesso!", "success")
        return redirect(url_for("listar_equipamentos"))

    except Exception as e:
        registrar_log("ERRO_DELETAR_EQUIPAMENTO", "Equipamento", f"Erro ao deletar equipamento {id}: {e}")
        db.session.rollback()
        flash("Erro ao deletar equipamento.", "danger")
        return redirect(url_for("internal_server_error"))
