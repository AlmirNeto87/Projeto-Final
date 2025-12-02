
# Remova ou adicione as importações conforme a organização real do seu projeto:
from models.usuario_model import Usuario, PerfilEnum 


def criar_dados_mock_usuarios(app, db):
    """
    Cria 3 usuários de cada perfil (Funcionário, Gerente, Admin) se eles não existirem.
    """
    
    with app.app_context():
        print("--- Verificando e criando dados mock de usuários ---")
        
        # Lista de usuários mock para ser criada
        usuarios_mock_data = [
            # 1. ADMIN_SEGURANCA (Senha padrão: admin123)
            {"name": "Admin Principal", "email": "admin1@seguranca.com", "perfil": PerfilEnum.ADMIN_SEGURANCA},
            {"name": "Admin Secundário", "email": "admin2@seguranca.com", "perfil": PerfilEnum.ADMIN_SEGURANCA},
            {"name": "Admin de Testes", "email": "admin3@seguranca.com", "perfil": PerfilEnum.ADMIN_SEGURANCA},

            # 2. GERENTE (Senha padrão: gerente123)
            {"name": "Gerente Geral", "email": "gerente1@empresa.com", "perfil": PerfilEnum.GERENTE},
            {"name": "Gerente de Projetos", "email": "gerente2@empresa.com", "perfil": PerfilEnum.GERENTE},
            {"name": "Gerente Operacional", "email": "gerente3@empresa.com", "perfil": PerfilEnum.GERENTE},

            # 3. FUNCIONARIO (Senha padrão: func123)
            {"name": "Funcionário A", "email": "func1@empresa.com", "perfil": PerfilEnum.FUNCIONARIO},
            {"name": "Funcionário B", "email": "func2@empresa.com", "perfil": PerfilEnum.FUNCIONARIO},
            {"name": "Funcionário C", "email": "func3@empresa.com", "perfil": PerfilEnum.FUNCIONARIO},
        ]
        
        # Cria um conjunto para rastrear os e-mails que já estão no banco
        existing_emails = set(u.email for u in Usuario.query.all())
        
        novos_usuarios = []
        
        for data in usuarios_mock_data:
            if data["email"] not in existing_emails:
                usuario = Usuario(
                    name=data["name"], 
                    email=data["email"], 
                    perfil=data["perfil"]
                )
                
                # Define a senha com base no perfil
                if data["perfil"] == PerfilEnum.ADMIN_SEGURANCA:
                    usuario.set_senha("admin123")
                elif data["perfil"] == PerfilEnum.GERENTE:
                    usuario.set_senha("gerente123")
                else: # FUNCIONARIO
                    usuario.set_senha("func123")
                    
                novos_usuarios.append(usuario)
                print(f"- Criado: {usuario}")

        if novos_usuarios:
            db.session.add_all(novos_usuarios)
            print(f"\n- Total de {len(novos_usuarios)} novos usuários adicionados à sessão.")
        else:
            print("- Todos os usuários mock já existem no banco de dados.")

        try:
            if novos_usuarios:
                db.session.commit()
                print("--- Dados mock de usuários processados e commitados com sucesso. ---")
            else:
                 print("--- Verificação de dados mock concluída. Nenhuma alteração realizada. ---")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar dados mock: {e}. Rollback executado.")