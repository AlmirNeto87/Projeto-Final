const socket = io();

// ID do usuário atualmente selecionado para o chat
let usuarioAtual = null;
let usuarioAtualNome = null;

// Elementos DOM
const listaUsuarios = document.getElementById("lista-usuarios");
const areaMensagens = document.getElementById("area-mensagens");
const tituloChat = document.getElementById("titulo-chat");
const btnEnviar = document.getElementById("btnEnviar");
const inputMsg = document.getElementById("msg");


// ======================================================
// FUNÇÕES AUXILIARES
// ======================================================

// Adiciona usuário na lista lateral
function adicionarUsuarioLista(id, nome) {
    // evitar duplicação
    if (document.getElementById(`contato-${id}`)) return;

    const li = document.createElement("li");
    li.className = "list-group-item list-group-item-action";
    li.id = `contato-${id}`;
    li.style.cursor = "pointer";
    li.textContent = nome;

    // clique para abrir chat
    li.onclick = () => selecionarUsuario(id, nome);

    listaUsuarios.appendChild(li);
}

// Remove usuário da lista lateral
function removerUsuarioLista(id) {
    const el = document.getElementById(`contato-${id}`);
    if (el) el.remove();

    // se o chat aberto era dele → resetar
    if (usuarioAtual === id) {
        usuarioAtual = null;
        usuarioAtualNome = null;
        tituloChat.textContent = "Selecione alguém";
        areaMensagens.innerHTML = "";
    }
}

// Rolagem automática no final da área de mensagens
function autoScroll() {
    areaMensagens.scrollTo({
        top: areaMensagens.scrollHeight,
        behavior: "smooth"
    });
}

// Inserir mensagem enviada pelo próprio usuário
function adicionarMensagemEnviada(texto) {
    const div = document.createElement("div");
    div.className = "text-end mb-2";
    div.innerHTML = `
        <span class="badge bg-primary p-2">
            ${texto}
        </span>
    `;
    areaMensagens.appendChild(div);
    autoScroll();
}

// Inserir mensagem recebida
function adicionarMensagemRecebida(texto, nome) {
    const div = document.createElement("div");
    div.className = "text-start mb-2";
    div.innerHTML = `
        <span class="badge bg-secondary p-2">
            <strong>${nome}:</strong> ${texto}
        </span>
    `;
    areaMensagens.appendChild(div);
    autoScroll();
}


// ======================================================
// SELEÇÃO DO USUÁRIO NO CHAT
// ======================================================
function selecionarUsuario(id, nome) {
    usuarioAtual = id;
    usuarioAtualNome = nome;

    tituloChat.textContent = `Conversando com ${nome}`;
    areaMensagens.innerHTML = ""; // limpa histórico

    // destacar selecionado
    document.querySelectorAll("#lista-usuarios li")
        .forEach(li => li.classList.remove("active"));

    const ativo = document.getElementById(`contato-${id}`);
    if (ativo) ativo.classList.add("active");

    // solicitar mensagens antigas
    socket.emit("load_messages", { para: id });
}


// ======================================================
// SOCKET.IO — EVENTOS
// ======================================================

// Usuário entrou
socket.on("user_online", data => {
    adicionarUsuarioLista(data.id, data.nome);
});

// Usuário saiu
socket.on("user_offline", data => {
    removerUsuarioLista(data.id);
});

// Receber mensagem em tempo real
socket.on("receive_message", data => {
    // só mostrar se a conversa aberta é com o remetente atual
    if (data.de === usuarioAtual) {
        adicionarMensagemRecebida(data.texto, data.nome);
    }
});

// Carregar histórico de mensagens (quando troca de usuário)
socket.on("load_messages_response", lista => {
    areaMensagens.innerHTML = "";

    lista.forEach(msg => {
        if (msg.de === usuarioAtual) {
            adicionarMensagemRecebida(msg.texto, usuarioAtualNome);
        } else {
            adicionarMensagemEnviada(msg.texto);
        }
    });

    autoScroll();
});


// ======================================================
// EVENTO DE ENVIAR MENSAGEM
// ======================================================
btnEnviar.onclick = () => {
    const texto = inputMsg.value.trim();

    if (!texto || !usuarioAtual) return;

    socket.emit("send_message", {
        para: usuarioAtual,
        texto: texto
    });

    adicionarMensagemEnviada(texto);
    inputMsg.value = "";
};


// ENTER envia também
inputMsg.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        btnEnviar.click();
    }
});
