from flask import render_template, request, redirect, url_for, flash, session
from config import db
from models.equipamento_model import Equipamento
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
            if not usuario_perfil or usuario_perfil not in [p.value for p in perfis_permitidos]:
                flash("Você não tem permissão para acessar esta página!", "danger")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# -----------------------------
# ROTAS DE CRUD PARA EQUIPAMENTOS
# -----------------------------

# Todos os perfis podem listar
@login_obrigatorio
def listar_equipamentos():
    
    perfil_usuario = session.get("usuario_perfil")
    
    equipamentos = Equipamento.query.all()
    # Adicionando SITUACAO_OPCOES para facilitar a filtragem ou exibição
    situacoes_permitidas = ['Ativo', 'Manutencao', 'Defeituoso']
    return render_template("equipamentos.html", titulo="Lista de Equipamentos", 
                           equipamentos=equipamentos, situacoes=situacoes_permitidas, perfil=perfil_usuario)

# Gerente e Administrador podem cadastrar
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.GERENTE, PerfilEnum.ADMIN_SEGURANCA)
def cadastrar_equipamento():
    if request.method == 'POST':
        nome = request.form["nome"]
        quantidade = int(request.form["quantidade"])
        data_vencimento_str = request.form["data_vencimento"]
        descricao = request.form["descricao"]
        nivel_perigo = request.form["nivel_perigo"]
        
        # NOVO CAMPO: Recebe a situação do formulário
        situacao = request.form["situacao"] 

        try:
            data_vencimento = datetime.strptime(data_vencimento_str, "%Y-%m-%d").date()
        except ValueError:
            # Em um cenário real, você deve retornar para o formulário com o erro
            flash("Data de vencimento inválida. Use o formato AAAA-MM-DD.", "danger")
            return redirect(url_for("cadastrar_equipamento"))

        novo_equipamento = Equipamento(
            nome=nome,
            quantidade=quantidade,
            data_vencimento=data_vencimento,
            descricao=descricao,
            nivel_perigo=nivel_perigo,
            # NOVO CAMPO: Adiciona a situação
            situacao=situacao 
        )

        db.session.add(novo_equipamento)
        db.session.commit()
        flash("Equipamento cadastrado com sucesso!", "success")
        return redirect(url_for("listar_equipamentos"))

    # Passa as opções de situação para o template de cadastro
    situacoes_permitidas = ['Ativo', 'Manutencao', 'Defeituoso']
    return render_template("cadastrar_equipamento.html", 
                           titulo="Cadastro de Equipamentos", 
                           situacoes=situacoes_permitidas)

# Apenas Administrador pode editar
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def editar_equipamento(id):
    equipamento = Equipamento.query.get(id)

    if not equipamento:
        return render_template("404.html", descErro="Equipamento não encontrado")

    if request.method == "POST":
        equipamento.nome = request.form["nome"]
        equipamento.quantidade = int(request.form["quantidade"])
        equipamento.descricao = request.form["descricao"]
        equipamento.nivel_perigo = request.form["nivel_perigo"]
        
        # NOVO CAMPO: Atualiza a situação
        equipamento.situacao = request.form["situacao"] 

        data_vencimento_str = request.form["data_vencimento"]
        try:
            equipamento.data_vencimento = datetime.strptime(data_vencimento_str, "%Y-%m-%d").date()
        except ValueError:
            # Em um cenário real, você deve retornar para o formulário com o erro
            flash("Data de vencimento inválida. Use o formato AAAA-MM-DD.", "danger")
            return redirect(url_for("editar_equipamento", id=id))

        db.session.commit()
        flash("Equipamento atualizado com sucesso!", "success")
        return redirect(url_for("listar_equipamentos"))

    # Passa as opções de situação para o template de edição
    situacoes_permitidas = ['Ativo', 'Manutencao', 'Defeituoso']
    return render_template("editar_equipamento.html", 
                           titulo="Edição de Equipamento", 
                           equipamento=equipamento, 
                           situacoes=situacoes_permitidas)

# Apenas Administrador pode deletar
@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def deletar_equipamento(id):
    equipamento = Equipamento.query.get(id)

    if not equipamento:
        return render_template("404.html", descErro="Equipamento não encontrado")

    db.session.delete(equipamento)
    db.session.commit()
    flash("Equipamento deletado com sucesso!", "success")
    return redirect(url_for("listar_equipamentos"))