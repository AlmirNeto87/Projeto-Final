# 🦇 Sistema WayneCorp – Plataforma de Gerenciamento  
**Aplicação Flask completa com Dashboard, Logs, CRUDs, Autenticação, Exportação e Interface Responsiva**

Este projeto é um sistema profissional desenvolvido em **Flask**, com uma estrutura organizada em **camadas**, uso avançado de **Blueprints**, autenticação com perfis, página de **Dashboard com gráficos**, **sistema de logs detalhados**, exportação CSV/JSON, cards responsivos e muito mais.

Inspirado e expandido a partir das aulas do Prof. Robson – Infinity School.

---

# 📌 Funcionalidades Principais

## 🔐 Autenticação e Perfis de Usuário
✔ Login com sessão  
✔ Logout seguro  
✔ Perfis com permissões:

- **Funcionário** → Equipamentos  
- **Gerente** → Equipamentos + Veículos  
- **Administrador de Segurança** → Todos os módulos + Logs + Dashboard  

✔ Rotas protegidas com:
- `@login_obrigatorio`
- `@perfil_obrigatorio(...)`

---

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

    /models
    usuario_model.py
    veiculo_model.py
    equipamento_model.py
    log_model.py

    /templates
    base.html
    index.html
    dashboard.html
    logs.html
    ...

    /static
    /js
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
    git clone https://github.com/seu-usuario/wayncorp-flask.git
    cd wayncorp-flask
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
```
## 4️⃣ Executar o servidor
```bash
   python app.py
```
## 5️⃣ Acessar no navegador
👉 http://127.0.0.1:5000

# 🖼 Interface e Navegação
    ✔ Navbar Responsiva
        Ícone hambúrguer para mobile
        Links exibidos de acordo com o perfil do usuário
    ✔ Página Inicial com Cards Responsivos
        Design moderno e padronizado com:
        Usuários
        Veículos
        Equipamentos
        Logs
        Dashboard

#   🔒 Segurança
         Sessões protegidas
        Permissões por perfil
        Logs completos (incluindo acessos negados)
        Rotas críticas protegidas por decoradores

