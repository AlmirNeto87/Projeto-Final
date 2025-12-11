# 🦇 Sistema WayneCorp – Plataforma de Gerenciamento  
**Aplicação Flask completa com Dashboard, Logs, CRUDs, Autenticação, Exportação de Logs, Lockdown, Chat Interno em Tempo Real e UI Moderna**

Este projeto é um sistema profissional desenvolvido em **Flask**, com uma estrutura organizada em **camadas**, uso avançado de **Blueprints**, autenticação com perfis, página de **Dashboard com gráficos**, **sistema de logs detalhados**, exportação CSV/JSON, cards responsivos e **Chat Interno em Tempo Real** com Socket.IO e sessões privadas..

Além disso, o projeto utiliza um diretório /mock com dados fictícios usados apenas para inicialização e testes.

Inspirado e expandido a partir das aulas do Prof. Robson – Infinity School.

---

# 📌 Funcionalidades Principais

## 🔐 Autenticação e Perfis de Usuário
✔ Login com sessão  
✔ Logout seguro  
✔ Perfis com permissões:

- **Funcionário** → Equipamentos  
- **Gerente** → Equipamentos + Veículos  
- **Administrador de Segurança** → Todos os módulos + Logs  +        Dashboard  + Lockdown + Chat completo

✔ Rotas protegidas com:
- `@login_obrigatorio`
- `@perfil_obrigatorio(...)`
- `@verificar_lockdown`
---

## 🛑 Modo LOCKDOWN (Controle de Emergência)

O projeto inclui um sistema de Lockdown, permitindo ao Administrador de Segurança bloquear o uso do sistema para todos os outros usuários.

Como funciona

Quando LOCKDOWN está ativo:

- Apenas Administrador de Segurança tem acesso às rotas protegidas por `@verificar_lockdown.`

- Funcionários e Gerentes são redirecionados para a página `/bloqueio.`

- Ações bloqueadas são registradas no sistema de logs.

- Possui interface visual no Dashboard para ativar/desativar.
---

Rotas

- Ativar Lockdown:
`GET /admin/lockdown/ativar`

- Desativar Lockdown:
`GET /admin/lockdown/desativar`

- Página exibida aos bloqueados:
`GET /bloqueio`

Observação

O estado de Lockdown fica em `app.config["LOCKDOWN_ATIVO"]`.
É ideal para ambientes de desenvolvimento ou testes. Em produção, você pode persistir o estado no banco.

---

## 💬 Chat Interno em Tempo Real (com Socket.IO)

O sistema possui um chat completo, privado e seguro, totalmente integrado ao controle de perfis e lockdown.

Recursos do Chat

✔ Comunicação em tempo real com Flask-SocketIO

✔ Apenas usuários online aparecem na lista

✔ Cada conversa possui uma sessão exclusiva:
- A sessão é criada ao enviar a primeira mensagem
- Pode ser fechada manualmente pelo botão Fechar Conversa
- A conversa some da lista em tempo real

  ✔ Previews de últimas mensagens
  
  ✔ Histórico carregado via WebSocket
  
  ✔ Perfil respeita regras de contato:

- Funcionário ↔ Funcionário
- Gerente ↔ Gerente + Funcionário
- Administrador ↔ todos

Tecnologias envolvidas
- Socket.IO 4.x
- Eventos: `connect, disconnect, send_message, receive_message, load_messages, message_sent`
- Sessões armazenadas em `chat_sessao_model.py`
- Mensagens armazenadas em `chat_message_model.py`



## 📊 Dashboard Inteligente
Página dedicada a análise de dados, com:

### **Gráficos**
- Quantidade por tipo (usuários, veículos, equipamentos)
- Gráficos dinâmicos filtráveis
- Renderização baseada no card selecionado

### **Tabelas Dinâmicas**
- Listagem recente
- Visão geral filtrável

---

## 📝 Sistema de Logs Completo
Tudo o que acontece no sistema é registrado:

✔ Usuário responsável  
✔ Tipo de operação  
✔ Modelo afetado  
✔ Descrição  
✔ Data e hora com timezone  
✔ Modificações (JSON)

### **Filtros**
- Usuário  
- Operação  
- Intervalo de datas  

### **Exportação**
- **CSV**  
- **JSON**

---

## 📦 CRUDs Completos
- Usuários  
- Equipamentos  
- Veículos  

Cada módulo inclui:

✔ Listagem  
✔ Cadastro  
✔ Edição  
✔ Exclusão  
✔ Logs automáticos

---

# 🧱 Estrutura do Projeto
    /controllers
    auth_controller.py
    usuario_controller.py
    veiculo_controller.py
    equipamento_controller.py
    log_controller.py
    dashboard_controller.py
    chat_controller.py

    /models
    usuario_model.py
    veiculo_model.py
    equipamento_model.py
    log_model.py
    chat_message_model.py
    chat_sessao_model.py

    /templates
    base.html
    index.html
    dashboard.html
    logs.html
    ...

    /mock -< Dados Ficticios
    usuario_mock.py
    veiculo_mock.py
    equipamento_mock.py
    
    /static
    /js
    chat.js
    /css

    /utils
    decorators.py

    config.py
    app.py
    README.md


---

# 🚀 Tecnologias Utilizadas

### **Backend**
- Python 3.x
- Flask
- Flask SQLAlchemy
- Blueprints
- Manipulação JSON e CSV
- Flask SocketIO
- Eventlet (server realtime)
- CSV/JSON export

### **Frontend**
- HTML5
- Bootstrap 5 (CDN)
- Chart.js
- Cards responsivos
- Navbar com menu hambúrguer

### **Banco de Dados**
- SQLite (padrão)
- Suporte simples para MySQL/PostgreSQL

---

# ▶️ Como Executar o Projeto

## 1️⃣ Clonar o repositório
 ```bash
    git clone https://github.com/AlmirNeto87/Projeto-Final.git
    cd Projeto-Final
 ```
## 2️⃣ Criar ambiente virtual (opcional, recomendado)
```bash
    python -m venv venv
```
 Ativar Windows
```bash
   venv\Scripts\activate
```
## 3️⃣ Instalar dependências
```bash
    pip install flask flask_sqlalchemy 
    pip install flask-socketio
    pip install eventlet
    pip install tzdata

```
## 4️⃣ Executar o servidor
```bash
   python app.py
```
## 5️⃣ Acessar no navegador
👉 http://127.0.0.1:5000

## 🖼 Interface e Navegação
✔ Navbar Responsiva
- Ícone hambúrguer para mobile
-    Links exibidos de acordo com o perfil do usuário

✔ Página Inicial com Cards Responsivos

✔ Design moderno e padronizado com:
- Usuários
- Veículos
- Equipamentos
- Logs
- Dashboard
- Lockkdonw
- Chat Interno

#   🔒 Segurança
- Sessões protegidas
- Permissões por perfil
- Logs completos (incluindo acessos negados)
- Bloqueio de Lockdown para acesso crítico
- Rotas críticas protegidas por decoradores

