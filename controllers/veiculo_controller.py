from flask import render_template, request, redirect, url_for, flash, session
from config import db
# IMPORTAÇÃO ATUALIZADA para o novo modelo
from models.veiculo_model import Veiculo 
from controllers.usuario_controller import login_obrigatorio, PerfilEnum
from datetime import datetime
from functools import wraps

# -----------------------------
# DECORATOR PARA RESTRIÇÃO POR PERFIL
# (Mantido como estava)
# -----------------------------
def perfil_obrigatorio(*perfis_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            usuario_perfil = session.get("usuario_perfil")
            # Adicionando PerfilEnum para garantir que o perfil do usuário está na lista permitida
            perfis_validos = [p.value for p in perfis_permitidos]
            if not usuario_perfil or usuario_perfil not in perfis_validos:
                flash("Você não tem permissão para acessar esta página!", "danger")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# -----------------------------
# ROTAS DE CRUD PARA VEÍCULOS
# As rotas listadas abaixo assumem que você configurou as URLs (endpoints) no seu arquivo principal
# como 'listar_veiculos', 'cadastrar_veiculo', etc.
# -----------------------------

# Somente Gerente e Administrador podem listar (conforme requisito)
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.GERENTE, PerfilEnum.ADMIN_SEGURANCA)
def listar_veiculos():
    
    perfil_usuario = session.get("usuario_perfil") # A chave correta da sessão
    
    veiculos = Veiculo.query.all()
    # Opções de situação definidas no modelo Veiculo
    situacoes_permitidas = Veiculo.SITUACAO_OPCOES 
    return render_template("veiculos.html", 
                           titulo="Lista de Veículos", 
                           veiculos=veiculos, 
                           situacoes=situacoes_permitidas, perfil =perfil_usuario)

# Somente Gerente e Administrador podem cadastrar
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.GERENTE, PerfilEnum.ADMIN_SEGURANCA)
def cadastrar_veiculo():
    situacoes_permitidas = Veiculo.SITUACAO_OPCOES 
    
    if request.method == 'POST':
        # 1. Obter dados do formulário
        modelo = request.form["modelo"]
        marca = request.form["marca"]
        ano_fabricacao = request.form["ano_fabricacao"]
        cor = request.form["cor"]
        descricao = request.form["descricao"]
        local_armazenamento = request.form["local_armazenamento"]
        placa = request.form["placa"]  # Novo campo de placa
        situacao = request.form["situacao"] 

        # 2. Validação básica (garantir que ano é um número inteiro)
        try:
            ano = int(ano_fabricacao)
        except ValueError:
            flash("Ano de Fabricação inválido. Deve ser um número inteiro.", "danger")
            return redirect(url_for("cadastrar_veiculo"))
        
        # 3. Criar e Salvar o Veículo
        novo_veiculo = Veiculo(
            modelo=modelo,
            marca=marca,
            ano_fabricacao=ano,
            cor=cor,
            descricao=descricao,
            placa=placa,  # Salvando a placa
            local_armazenamento=local_armazenamento,
            situacao=situacao 
        )

        db.session.add(novo_veiculo)
        db.session.commit()
        flash("Veículo cadastrado com sucesso!", "success")
        return redirect(url_for("listar_veiculos"))

    # Renderiza o template, passando as opções de situação
    return render_template("cadastrar_veiculo.html", 
                           titulo="Cadastro de Veículo", 
                           situacoes=situacoes_permitidas)

# Somente Gerente e Administrador podem editar
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def editar_veiculo(id):
    veiculo = Veiculo.query.get(id)
    situacoes_permitidas = Veiculo.SITUACAO_OPCOES

    if not veiculo:
        return render_template("404.html", descErro="Veículo não encontrado")

    if request.method == "POST":
        # 1. Atualizar campos
        veiculo.modelo = request.form["modelo"]
        veiculo.marca = request.form["marca"]
        veiculo.cor = request.form["cor"]
        veiculo.descricao = request.form["descricao"]
        veiculo.local_armazenamento = request.form["local_armazenamento"]
        veiculo.placa = request.form["placa"]  # Atualizando a placa
        veiculo.situacao = request.form["situacao"] 
        
        # 2. Validação para ano de fabricação
        ano_fabricacao_str = request.form["ano_fabricacao"]
        try:
            veiculo.ano_fabricacao = int(ano_fabricacao_str)
        except ValueError:
            flash("Ano de Fabricação inválido. Deve ser um número inteiro.", "danger")
            return redirect(url_for("editar_veiculo", id=id))
        
        # 3. Commit
        db.session.commit()
        flash("Veículo atualizado com sucesso!", "success")
        return redirect(url_for("listar_veiculos"))

    # Renderiza o template, passando o objeto Veiculo e as opções de situação
    return render_template("editar_veiculo.html", 
                           titulo="Edição de Veículo", 
                           veiculo=veiculo, 
                           situacoes=situacoes_permitidas)

# Somente Gerente e Administrador podem deletar
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def deletar_veiculo(id):
    veiculo = Veiculo.query.get(id)

    if not veiculo:
        return render_template("404.html", descErro="Veículo não encontrado")

    db.session.delete(veiculo)
    db.session.commit()
    flash("Veículo deletado com sucesso!", "success")
    return redirect(url_for("listar_veiculos"))
