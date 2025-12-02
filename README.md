# 🐍 Super Módulo Flask - Aula 03  

Bem-vindo ao **Super Módulo Flask Aula 03**, um projeto em Python utilizando a biblioteca Flask.  
Nesta etapa, avançamos bastante em relação à Aula 02:  
organizamos o projeto em uma estrutura mais **profissional e escalável**, separamos os controladores , implementamos **login com sessão** e aplicamos o **Bootstrap** em todas as páginas HTML para uma interface moderna e responsiva.  

Projeto baseado na 3ª Aula do Prof. Robson – creditado mais abaixo no texto.  

---

## 📚 Conteúdo da Aula  

### Revisão da Aula Anterior  
- CRUD de Produtos completo.  
- CRUD de Usuários completo.  
- Login básico com sessão.  
- Integração inicial do Bootstrap.  

### Organização do Projeto  
- Estrutura em **camadas** para deixar o código mais limpo:  
  - `controllers/` → lógica das rotas separada em Blueprints.  
  - `models/` → modelos de dados e futuras integrações com banco.  
  - `templates/` → páginas HTML organizadas em pastas.  
  - `app.py` → ponto central de inicialização do projeto.  


### Login e Sessão (refinado)  
- Proteção de rotas com decorador `@login_obrigatorio`.  
- Barra de navegação exibida apenas quando o usuário está logado.  
- Logout remove os dados da sessão de forma segura.  

### Bootstrap aplicado em toda a aplicação  
- Layout responsivo em todas as páginas.  
- Barra de navegação estilizada.  
- Formulários e tabelas organizados.  

---

## 🚀 Tecnologias Utilizadas  
- Python 3.x  
- Flask  
- HTML/CSS  
- Bootstrap (via CDN)  

---

## ▶️ Como Executar o Projeto  

Clone este repositório:  
```bash
git clone https://github.com/seu-usuario/super-modulo-flask-aula03.git
cd super-modulo-flask-aula03
```

Crie um ambiente virtual (opcional, mas recomendado):  
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

Instale as dependências:  
```bash
pip install flask
pip install flask_sqlalchemy
```

Execute a aplicação:  
```bash
python app.py
```

Abra no navegador:  
[http://127.0.0.1:5000](http://127.0.0.1:5000)  

---

## 🎨 Como usar o Bootstrap via CDN  

Para adicionar o Bootstrap às páginas HTML, insira o link CDN dentro da tag `<head>` do seu arquivo:  

```html
<head>
    <meta charset="UTF-8">
    <title>Minha Página Flask</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1 class="text-center">Minha Página com Bootstrap</h1>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
```

💡 Com isso, todas as suas páginas Flask podem aproveitar a máxima responsividade e estilo do Bootstrap.  

---

## 🔒 Funcionalidades de Login e Sessão  

- O login é a primeira rota antes de acessar a aplicação.  
- Usuário logado permanece ativo enquanto a sessão existir.  
- Logout encerra a sessão e protege as rotas `/produtos` e `/usuarios`.  
- A barra de navegação só aparece quando o usuário está autenticado.  
- Todas as rotas críticas agora estão protegidas com `@login_obrigatorio`.  

---

## 👨‍🏫 Créditos  

Projeto desenvolvido a partir da aula do **Prof. Robson – Escola Infinity Fortaleza/CE**  
👉 GitHub do Prof. Robson: [https://github.com/robson400](https://github.com/robson400)  
