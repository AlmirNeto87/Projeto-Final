from flask import render_template, request, redirect, url_for, flash, session
from config import db
from models.veiculo_model import Veiculo
from models.usuario_model import PerfilEnum
from utils.decorators import login_obrigatorio, perfil_obrigatorio, verificar_lockdown
from controllers.logs_controller import registrar_log


# ======================================================
# LISTAR VEÍCULOS
# ======================================================
@login_obrigatorio
@verificar_lockdown
@perfil_obrigatorio(PerfilEnum.GERENTE, PerfilEnum.ADMIN_SEGURANCA)
def listar_veiculos():
    try:
        perfil_usuario = session.get("usuario_perfil")
        veiculos = Veiculo.query.all()
        situacoes = Veiculo.SITUACAO_OPCOES

        return render_template(
            "veiculos.html",
            titulo="Lista de Veículos",
            veiculos=veiculos,
            situacoes=situacoes,
            perfil=perfil_usuario
        )

    except Exception as e:
        registrar_log("ERRO_LISTAR_VEICULOS", "Veiculo", f"Erro ao listar veículos: {e}")
        flash("Erro ao carregar a lista de veículos.", "danger")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao listar veículos."
        ), 500


# ======================================================
# CADASTRAR VEÍCULO
# ======================================================
@login_obrigatorio
@verificar_lockdown
@perfil_obrigatorio(PerfilEnum.GERENTE, PerfilEnum.ADMIN_SEGURANCA)
def cadastrar_veiculo():
    situacoes = Veiculo.SITUACAO_OPCOES

    if request.method == 'POST':
        try:
            modelo = request.form["modelo"]
            marca = request.form["marca"]
            ano_fabricacao_str = request.form["ano_fabricacao"]
            cor = request.form["cor"]
            descricao = request.form["descricao"]
            local_armazenamento = request.form["local_armazenamento"]
            placa = request.form["placa"]
            situacao = request.form["situacao"]

            # Validação do ano
            try:
                ano = int(ano_fabricacao_str)
            except ValueError:
                flash("Ano de Fabricação inválido. Deve ser um número inteiro.", "danger")
                return redirect(url_for("cadastrar_veiculo"))

            novo = Veiculo(
                modelo=modelo,
                marca=marca,
                ano_fabricacao=ano,
                cor=cor,
                descricao=descricao,
                placa=placa,
                local_armazenamento=local_armazenamento,
                situacao=situacao
            )

            db.session.add(novo)
            db.session.commit()

            registrar_log(
                tipo_operacao="CRIAR",
                tipo_modelo="Veiculo",
                descricao=f"Veículo cadastrado: {marca} {modelo}",
                modificacoes={
                    "modelo": modelo,
                    "marca": marca,
                    "ano_fabricacao": ano,
                    "cor": cor,
                    "placa": placa,
                    "situacao": situacao
                }
            )

            flash("Veículo cadastrado com sucesso!", "success")
            return redirect(url_for("listar_veiculos"))

        except Exception as e:
            registrar_log("ERRO_CADASTRAR_VEICULO", "Veiculo", f"Erro ao cadastrar: {e}")
            db.session.rollback()
            flash("Erro ao cadastrar veículo.", "danger")
            return render_template(
                "404.html",
                error_code=500,
                error_message="Erro ao cadastrar veículo."
            ), 500

    try:
        return render_template(
            "cadastrar_veiculo.html",
            titulo="Cadastro de Veículo",
            situacoes=situacoes
        )
    except Exception as e:
        registrar_log("ERRO_RENDER_CADASTRAR_VEICULO", "Sistema",
                      f"Erro ao renderizar formulário: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao carregar formulário de cadastro."
        ), 500


# ======================================================
# EDITAR VEÍCULO
# ======================================================
@login_obrigatorio
@verificar_lockdown
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def editar_veiculo(id):
    try:
        veiculo = Veiculo.query.get(id)
    except Exception as e:
        registrar_log("ERRO_BUSCAR_VEICULO_EDITAR", "Veiculo", f"Erro ao buscar veículo: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao buscar veículo."
        ), 500

    if not veiculo:
        return render_template(
            "404.html",
            error_code=404,
            error_message="Veículo não encontrado."
        ), 404

    situacoes = Veiculo.SITUACAO_OPCOES

    if request.method == "POST":
        try:
            antes = {
                "modelo": veiculo.modelo,
                "marca": veiculo.marca,
                "ano_fabricacao": veiculo.ano_fabricacao,
                "cor": veiculo.cor,
                "descricao": veiculo.descricao,
                "placa": veiculo.placa,
                "local_armazenamento": veiculo.local_armazenamento,
                "situacao": veiculo.situacao
            }

            veiculo.modelo = request.form["modelo"]
            veiculo.marca = request.form["marca"]
            veiculo.cor = request.form["cor"]
            veiculo.descricao = request.form["descricao"]
            veiculo.local_armazenamento = request.form["local_armazenamento"]
            veiculo.placa = request.form["placa"]
            veiculo.situacao = request.form["situacao"]

            try:
                veiculo.ano_fabricacao = int(request.form["ano_fabricacao"])
            except ValueError:
                flash("Ano de Fabricação inválido.", "danger")
                return redirect(url_for("editar_veiculo", id=id))

            db.session.commit()

            registrar_log(
                tipo_operacao="ATUALIZAR",
                tipo_modelo="Veiculo",
                descricao=f"Veículo atualizado: {veiculo.marca} {veiculo.modelo}",
                modificacoes={
                    "antes": antes,
                    "depois": {
                        "modelo": veiculo.modelo,
                        "marca": veiculo.marca,
                        "ano_fabricacao": veiculo.ano_fabricacao,
                        "cor": veiculo.cor,
                        "descricao": veiculo.descricao,
                        "placa": veiculo.placa,
                        "local_armazenamento": veiculo.local_armazenamento,
                        "situacao": veiculo.situacao
                    }
                }
            )

            flash("Veículo atualizado com sucesso!", "success")
            return redirect(url_for("listar_veiculos"))

        except Exception as e:
            registrar_log("ERRO_EDITAR_VEICULO", "Veiculo", f"Erro ao editar veículo {id}: {e}")
            db.session.rollback()
            flash("Erro ao atualizar veículo.", "danger")
            return render_template(
                "404.html",
                error_code=500,
                error_message="Erro ao atualizar veículo."
            ), 500

    try:
        return render_template(
            "editar_veiculo.html",
            titulo="Edição de Veículo",
            veiculo=veiculo,
            situacoes=situacoes
        )
    except Exception as e:
        registrar_log("ERRO_RENDER_EDITAR_VEICULO", "Sistema",
                      f"Erro ao renderizar página de edição: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao carregar página de edição."
        ), 500


# ======================================================
# DELETAR VEÍCULO
# ======================================================
@login_obrigatorio
@verificar_lockdown
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def deletar_veiculo(id):
    try:
        veiculo = Veiculo.query.get(id)
    except Exception as e:
        registrar_log("ERRO_BUSCAR_VEICULO_DELETAR", "Veiculo",
                      f"Erro ao buscar veículo para deletar: {e}")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao buscar veículo para deletar."
        ), 500

    if not veiculo:
        return render_template(
            "404.html",
            error_code=404,
            error_message="Veículo não encontrado."
        ), 404

    try:
        resumo = {
            "modelo": veiculo.modelo,
            "marca": veiculo.marca,
            "placa": veiculo.placa
        }

        db.session.delete(veiculo)
        db.session.commit()

        registrar_log(
            tipo_operacao="DELETAR",
            tipo_modelo="Veiculo",
            descricao=f"Veículo deletado: {resumo['marca']} {resumo['modelo']}",
            modificacoes=resumo
        )

        flash("Veículo deletado com sucesso!", "success")
        return redirect(url_for("listar_veiculos"))

    except Exception as e:
        registrar_log("ERRO_DELETAR_VEICULO", "Veiculo", f"Erro ao deletar veículo {id}: {e}")
        db.session.rollback()
        flash("Erro ao deletar veículo.", "danger")
        return render_template(
            "404.html",
            error_code=500,
            error_message="Erro ao deletar veículo."
        ), 500
