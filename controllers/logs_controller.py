from flask import session
from config import db
from models.log_model import Log # Importe o modelo Log

def registrar_log(tipo_operacao: str, tipo_modelo: str, descricao: str, modificacoes: str = None):
    """
    Função auxiliar para registrar uma operação no banco de dados de Logs.
    """
    # Tenta obter informações do usuário logado na sessão
    usuario_id = session.get("usuario_id")
    usuario_nome = session.get("usuario_nome") # Assuma que você salva o nome na sessão no login
    usuario_perfil = session.get("usuario_perfil") # Assuma que você salva o perfil na sessão no login

    novo_log = Log(
        usuario_id=usuario_id,
        usuario_nome=usuario_nome,
        usuario_perfil=usuario_perfil,
        tipo_operacao=tipo_operacao,
        tipo_modelo=tipo_modelo,
        descricao=descricao,
        modificacoes=modificacoes
    )

    db.session.add(novo_log)
    # É importante que o commit seja feito aqui ou no final da operação principal
    # para garantir que o log seja salvo mesmo se a operação principal falhar.
    try:
        db.session.commit()
    except Exception as e:
        # Em caso de falha no commit do log, é melhor apenas registrar o erro
        # sem impedir a execução do resto da aplicação.
        print(f"ERRO AO SALVAR LOG: {e}")
        db.session.rollback()