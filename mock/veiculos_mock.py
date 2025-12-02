from models.veiculo_model import Veiculo
from random import choice, randint
from datetime import datetime, timedelta

# Definição de uma lista FIXA de 20 veículos mock para garantir placas únicas e consistência
VEICULOS_MOCK_DATA_FIXA = [
    # Carros Militares (Placas M-XXXX)
    {"modelo": "Humvee", "marca": "AM General", "ano_fabricacao": 2018, "cor": "Verde Oliva", "placa": "M-1001", "situacao": "Ativo", "descricao": "Veículo de reconhecimento leve."},
    {"modelo": "Guarani", "marca": "Iveco", "ano_fabricacao": 2021, "cor": "Camuflado", "placa": "M-1002", "situacao": "Ativo", "descricao": "Transporte de tropas blindado."},
    {"modelo": "Jipe Troller T4", "marca": "Troller", "ano_fabricacao": 2019, "cor": "Preto Fosco", "placa": "M-1003", "situacao": "Manutencao", "descricao": "Veículo de patrulha todo-terreno."},

    # Carros Comerciais (Placas C-XXXX)
    {"modelo": "Ford Ranger", "marca": "Ford", "ano_fabricacao": 2022, "cor": "Prata", "placa": "C-2001", "situacao": "Ativo", "descricao": "Caminhonete para transporte de suprimentos."},
    {"modelo": "Toyota Corolla", "marca": "Toyota", "ano_fabricacao": 2023, "cor": "Branco", "placa": "C-2002", "situacao": "Ativo", "descricao": "Carro de uso administrativo."},
    {"modelo": "Chevrolet S10", "marca": "Chevrolet", "ano_fabricacao": 2020, "cor": "Cinza", "placa": "C-2003", "situacao": "Defeituoso", "descricao": "Veículo de logística, motor com problema."},

    # Motos (Placas T-XXXX)
    {"modelo": "Triumph Tiger 900", "marca": "Triumph", "ano_fabricacao": 2022, "cor": "Laranja", "placa": "T-3001", "situacao": "Ativo", "descricao": "Moto de uso rápido e escolta."},
    {"modelo": "Harley-Davidson Road King", "marca": "Harley-Davidson", "ano_fabricacao": 2019, "cor": "Preto", "placa": "T-3002", "situacao": "Manutencao", "descricao": "Moto de grande porte para longas distâncias."},
    {"modelo": "Yamaha Lander XTZ 250", "marca": "Yamaha", "ano_fabricacao": 2023, "cor": "Azul", "placa": "T-3003", "situacao": "Ativo", "descricao": "Moto para terrenos mistos."},

    # Iates (Placas N-XXXX)
    {"modelo": "Azimut Grande", "marca": "Azimut", "ano_fabricacao": 2017, "cor": "Branco", "placa": "N-4001", "situacao": "Ativo", "descricao": "Iate de patrulha costeira e resgate."},
    {"modelo": "Sunseeker Predator", "marca": "Sunseeker", "ano_fabricacao": 2015, "cor": "Azul Marinho", "placa": "N-4002", "situacao": "Manutencao", "descricao": "Embarcação de alta velocidade."},
    {"modelo": "Ferretti Yachts", "marca": "Ferretti", "ano_fabricacao": 2020, "cor": "Bege", "placa": "N-4003", "situacao": "Ativo", "descricao": "Veículo naval de apoio logístico."},

    # Helicópteros (Placas H-XXXX)
    {"modelo": "Bell 429 Global Ranger", "marca": "Bell", "ano_fabricacao": 2021, "cor": "Vermelho", "placa": "H-5001", "situacao": "Ativo", "descricao": "Aeronave de multi-missão."},
    {"modelo": "Airbus H145", "marca": "Airbus", "ano_fabricacao": 2019, "cor": "Amarelo", "placa": "H-5002", "situacao": "Defeituoso", "descricao": "Helicóptero leve, aguardando peças."},
    {"modelo": "Sikorsky S-70", "marca": "Sikorsky", "ano_fabricacao": 2016, "cor": "Verde", "placa": "H-5003", "situacao": "Ativo", "descricao": "Helicóptero de transporte pesado."},

    # Aviões (Placas A-XXXX)
    {"modelo": "Embraer Phenom 300", "marca": "Embraer", "ano_fabricacao": 2022, "cor": "Cinza Claro", "placa": "A-6001", "situacao": "Ativo", "descricao": "Jato executivo de médio alcance."},
    {"modelo": "Cessna Caravan", "marca": "Cessna", "ano_fabricacao": 2018, "cor": "Branco", "placa": "A-6002", "situacao": "Manutencao", "descricao": "Aeronave turboélice de transporte."},
    {"modelo": "Boeing 737", "marca": "Boeing", "ano_fabricacao": 2015, "cor": "Branco/Azul", "placa": "A-6003", "situacao": "Ativo", "descricao": "Aeronave de transporte de grande capacidade."},
    
    # Extra (Placas E-XXXX)
    {"modelo": "Veículo Submersível", "marca": "DeepSea", "ano_fabricacao": 2023, "cor": "Azul Escuro", "placa": "E-7001", "situacao": "Ativo", "descricao": "Submersível para operações secretas."},
    {"modelo": "Quadriciclo", "marca": "Polaris", "ano_fabricacao": 2021, "cor": "Vermelho", "placa": "E-7002", "situacao": "Defeituoso", "descricao": "Veículo para terreno acidentado."},
]


def criar_dados_mock_veiculos(app, db):
    """
    Cria 20 veículos com placas fixas, verificando a existência pela placa.
    """
    
    with app.app_context():
        print("\n--- Verificando e criando dados mock de veículos ---")
        
        # 1. Coleta todas as placas existentes no banco de dados
        # Assumimos que 'placa' é um identificador único de veículos.
        existing_plates = set(v.placa for v in Veiculo.query.all())
        
        novos_veiculos = []
        local_arm_counter = 1 # Para definir o local de armazenamento sequencialmente
        
        for data in VEICULOS_MOCK_DATA_FIXA:
            placa = data["placa"]
            
            if placa not in existing_plates:
                
                # Define o local de armazenamento (para ter alguma variação)
                local_armazenamento = f"Armazém {local_arm_counter}"
                local_arm_counter = local_arm_counter % 5 + 1 # Gira de 1 a 5
                
                veiculo = Veiculo(
                    modelo=data["modelo"],
                    marca=data["marca"],
                    ano_fabricacao=data["ano_fabricacao"],
                    cor=data["cor"],
                    placa=placa,
                    local_armazenamento=local_armazenamento,
                    situacao=data["situacao"],
                    descricao=data["descricao"]
                )
                novos_veiculos.append(veiculo)
                print(f"- Criado: {veiculo.placa} ({veiculo.modelo})")

        if novos_veiculos:
            db.session.add_all(novos_veiculos)
            print(f"\n- Total de {len(novos_veiculos)} novos veículos adicionados à sessão.")
        else:
            print("- Todos os veículos mock já existem no banco de dados.")

        try:
            if novos_veiculos:
                db.session.commit()
                print("--- Dados mock de veículos processados e commitados com sucesso. ---")
            else:
                 print("--- Verificação de dados mock de veículos concluída. Nenhuma alteração realizada. ---")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar dados mock de veículos: {e}. Rollback executado.")