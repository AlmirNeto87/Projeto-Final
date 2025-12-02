from datetime import datetime, timedelta
from models.equipamento_model import Equipamento
from random import choice, randint
import random

def gerar_data_vencimento():
    """Gera uma data de vencimento aleatória dentro de 1 a 3 anos no futuro."""
    return datetime.today() + timedelta(days=randint(365, 1095))

def gerar_descricao(nome):
    """Gera uma descrição aleatória para o equipamento."""
    descricoes = [
        f"Equipamento utilizado para {nome} em operações de segurança.",
        f"Produto de alta qualidade, ideal para {nome}.",
        f"Equipamento essencial para garantir a segurança nas operações.",
        f"Usado principalmente para proteção em ambientes de alto risco."
    ]
    return random.choice(descricoes)

def criar_dados_mock_equipamentos(app, db):
    """
    Cria 20 equipamentos diversos para simulação, com dados aleatórios se não existirem.
    """
    with app.app_context():
        print("--- Verificando e criando dados mock de equipamentos ---")

        # Lista de equipamentos mock com diferentes categorias
        equipamentos_mock_data = [
            {"nome": "Faca Tática", "quantidade": 5, "nivel_perigo": "Alto"},
            {"nome": "Granada de Mão", "quantidade": 10, "nivel_perigo": "Alto"},  
            {"nome": "C4 Explosivo", "quantidade": 3, "nivel_perigo": "Alto"},  
            {"nome": "Colete Balístico", "quantidade": 15, "nivel_perigo": "Médio"},  
            {"nome": "Revólver Calibre .38", "quantidade": 7, "nivel_perigo": "Alto"},
            {"nome": "Pistola Glock 17", "quantidade": 12, "nivel_perigo": "Alto"},
            {"nome": "Taser", "quantidade": 6, "nivel_perigo": "Médio"},  
            {"nome": "Metralhadora M16", "quantidade": 4, "nivel_perigo": "Alto"},  
            {"nome": "Rifle de Assalto AK-47", "quantidade": 5, "nivel_perigo": "Alto"},  
            {"nome": "Espingarda Pump Action", "quantidade": 8, "nivel_perigo": "Alto"},
            {"nome": "Granada de Fumaça", "quantidade": 20, "nivel_perigo": "Baixo"},
            {"nome": "Cinto de Utilidades", "quantidade": 30, "nivel_perigo": "Baixo"},
            {"nome": "Escudo Balístico", "quantidade": 3, "nivel_perigo": "Médio"},  
            {"nome": "Garrafa Tática", "quantidade": 25, "nivel_perigo": "Baixo"},
            {"nome": "Lanterna Tática", "quantidade": 50, "nivel_perigo": "Baixo"},
            {"nome": "Câmera de Segurança", "quantidade": 12, "nivel_perigo": "Baixo"},
            {"nome": "Detector de Metais", "quantidade": 8, "nivel_perigo": "Médio"},  
            {"nome": "Bomba de Fumaça", "quantidade": 10, "nivel_perigo": "Alto"},
            {"nome": "Drone de Vigilância", "quantidade": 2, "nivel_perigo": "Médio"}, 
            {"nome": "Binóculos Noturnos", "quantidade": 15, "nivel_perigo": "Baixo"},
        ]        
        # Cria um conjunto para rastrear os nomes dos equipamentos já existentes
        existing_equipamentos = set(e.nome for e in Equipamento.query.all())
        
        novos_equipamentos = []

        for data in equipamentos_mock_data:
            if data["nome"] not in existing_equipamentos:
                # Gera os dados de cada equipamento
                equipamento = Equipamento(
                    nome=data["nome"],
                    quantidade=data["quantidade"],
                    data_vencimento=gerar_data_vencimento(),
                    descricao=gerar_descricao(data["nome"]),
                    nivel_perigo=data["nivel_perigo"],
                    situacao=choice(Equipamento.SITUACAO_OPCOES)
                )

                novos_equipamentos.append(equipamento)
                print(f"- Criado: {equipamento.nome}, Nível de Perigo: {equipamento.nivel_perigo}, Situação: {equipamento.situacao}")

        if novos_equipamentos:
            db.session.add_all(novos_equipamentos)
            print(f"\n- Total de {len(novos_equipamentos)} novos equipamentos adicionados à sessão.")
        else:
            print("- Todos os equipamentos mock já existem no banco de dados.")

        try:
            if novos_equipamentos:
                db.session.commit()
                print("--- Dados mock de equipamentos processados e commitados com sucesso. ---")
            else:
                print("--- Verificação de dados mock concluída. Nenhuma alteração realizada. ---")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar dados mock: {e}. Rollback executado.")
