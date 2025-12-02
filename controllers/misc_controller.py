from functools import wraps
from flask import flash, redirect, render_template, request, session, url_for
from controllers.usuario_controller import login_obrigatorio
from models.usuario_model import Usuario, PerfilEnum 
from models.veiculo_model import Veiculo
from models.equipamento_model import Equipamento
# Importar o decorador que você utiliza para verificar o login
# from utils.decorators import login_obrigatorio 

# Lista de status/situações relevantes para os modelos
TIPO_PERFIL = ['Funcionário', 'Gerente', 'Administrador de Segurança']
STATUS_OPCOES = ['Ativo', 'Manutencao', 'Defeituoso']
TIPO_OPCOES = ['Usuário', 'Veículo', 'Equipamento']

# Decorator para verificar perfil
def perfil_obrigatorio(*perfis_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            usuario_id = session.get("usuario_id")
            if not usuario_id:
                flash("Você precisa estar logado para acessar esta página!", "danger")
                return redirect(url_for("login"))

            usuario = Usuario.query.get(usuario_id)
            if usuario.perfil not in perfis_permitidos:
                flash("Você não tem permissão para acessar esta página!", "danger")
                return redirect(url_for("home"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Lista de status/situações relevantes para os modelos
TIPO_PERFIL = [p.value for p in PerfilEnum] # ['Funcionário', 'Gerente', 'Administrador de Segurança']
STATUS_VEICULO_OPCOES = ['Ativo', 'Manutencao', 'Defeituoso'] # Renomeado
NIVEIS_PERIGO_OPCOES = ['Baixo', 'Médio', 'Alto'] # Exemplo: Adicione seus níveis reais
TIPO_OPCOES = ['Usuário', 'Veículo', 'Equipamento']
TODOS = 'Todos'

# O decorator perfil_obrigatorio foi omitido por brevidade

@login_obrigatorio
@perfil_obrigatorio(PerfilEnum.ADMIN_SEGURANCA)
def buscar_adm():

    
    # 1. Obter e Tratar Parâmetros de Busca Genéricos
    resultados = { 'usuarios': [], 'veiculos': [], 'equipamentos': [] }
    termo_busca = request.args.get('termo_busca', '').strip() # Novo: para busca por Nome
    filtro_tipo = request.args.get('tipo', TODOS)
    
    # 2. Obter e Tratar Parâmetros de Filtros Específicos
    filtro_perfil = request.args.get('perfil')
    filtro_status_veiculo = request.args.get('status_veiculo')
    filtro_local_veiculo = request.args.get('local_veiculo')
    filtro_nivel_perigo = request.args.get('nivel_perigo') # Exemplo: Campo para Equipamento
    
    # Dicionário para passar para o template
    filtros_ativos = {
        'termo_busca': termo_busca, 'tipo': filtro_tipo, 'perfil': filtro_perfil,
        'status_veiculo': filtro_status_veiculo, 'local_veiculo': filtro_local_veiculo,
        'nivel_perigo': filtro_nivel_perigo,
    }

    # Se houver qualquer parâmetro de busca, execute a pesquisa
    if termo_busca or filtro_tipo != TODOS or any(v for v in [filtro_perfil, filtro_status_veiculo, filtro_local_veiculo, filtro_nivel_perigo]):
        
        # --- Lógica de Busca ---
        
        # 1. Busca em USUÁRIOS
        if filtro_tipo in ['Usuário', TODOS]:
            query = Usuario.query
            
            # FILTRO: Nome (Busca por Nome em todos os modelos)
            if termo_busca:
                query = query.filter(Usuario.name.ilike(f"%{termo_busca}%"))
            
            # FILTRO ESPECÍFICO: Perfil
            if filtro_perfil and filtro_perfil in TIPO_PERFIL:
                try:
                    # Converte string para o objeto Enum
                    perfil_enum = PerfilEnum(filtro_perfil)
                    query = query.filter_by(perfil=perfil_enum)
                except ValueError:
                    # Trata caso a string não seja um valor válido de PerfilEnum
                    flash(f"Perfil '{filtro_perfil}' inválido para a busca.", "warning")
            
            resultados['usuarios'] = query.all()
            
        # 2. Busca em VEÍCULOS
        if filtro_tipo in ['Veículo', TODOS]:
            query = Veiculo.query
            
            # FILTRO: Modelo
            if termo_busca:
                # Assumindo que 'nome' é um campo adequado para busca de Veículos
                query = query.filter(Veiculo.modelo.ilike(f"%{termo_busca}%")) 
                
            # FILTRO ESPECÍFICO: Status
            if filtro_status_veiculo and filtro_status_veiculo in STATUS_VEICULO_OPCOES:
                query = query.filter_by(situacao=filtro_status_veiculo)
                
            # FILTRO ESPECÍFICO: Local de Armazenamento
            if filtro_local_veiculo:
                # Busca parcial, case-insensitive (ilike)
                query = query.filter(Veiculo.local_armazenamento.ilike(f"%{filtro_local_veiculo}%"))
            
            resultados['veiculos'] = query.all()
                
        # 3. Busca em EQUIPAMENTOS
        if filtro_tipo in ['Equipamento', TODOS]:
            query = Equipamento.query
            
            # FILTRO: Nome
            if termo_busca:
                 # Assumindo que 'nome' é um campo adequado para busca de Equipamentos
                query = query.filter(Equipamento.nome.ilike(f"%{termo_busca}%"))
            
            # FILTRO ESPECÍFICO: Nível de Perigo
            if filtro_nivel_perigo and filtro_nivel_perigo in NIVEIS_PERIGO_OPCOES:
                # Assumindo que o campo se chama 'nivel_de_perigo'
                query = query.filter_by(nivel_perigo=filtro_nivel_perigo)
            
            resultados['equipamentos'] = query.all()

    # Adicione os novos filtros específicos ao contexto do template
    return render_template(
        "buscar_adm.html", 
        titulo="Busca Administrativa de Recursos",
        resultados=resultados,
        tipo_opcoes=TIPO_OPCOES,
        tipos_perfil=TIPO_PERFIL, # Novo
        status_veiculo_opcoes=STATUS_VEICULO_OPCOES, # Novo (Renomeado)
        niveis_perigo_opcoes=NIVEIS_PERIGO_OPCOES, # Novo
        # Filtros ativos:
        **filtros_ativos # Desempacota o dicionário de filtros ativos
    )



# -----------------------------
# ROTAS EXTRAS
# -----------------------------
def sobre():
    return render_template("sobre.html", titulo="Sobre")

def contatos():
    return render_template("contatos.html", titulo="Contatos")

# -----------------------------
# ROTAS DE TRATAMENTO DE ERROS
# -----------------------------
def page_not_found(e):
    return render_template('404.html', error_code=404, error_message="Página não encontrada."), 404

def internal_server_error(e):
    return render_template('404.html', error_code=500, error_message="Erro interno no servidor. Tente novamente mais tarde."), 500