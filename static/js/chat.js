// ====== CHAT.JS — VERSÃO COMPLETA E ATUALIZADA ======

const socket = io();

// estado do chat
let usuarioAtual = null;
let usuarioAtualNome = null;
let meuId = parseInt(document.body.dataset.usuarioId || "0");

// cache dos contatos: { id: { id, nome, perfil, online, preview } }
let listaCache = {};

// elementos
const listaUsuarios = document.getElementById("lista-usuarios");
const areaMensagens = document.getElementById("area-mensagens");
const tituloChat = document.getElementById("titulo-chat");
const btnEnviar = document.getElementById("btnEnviar");
const inputMsg = document.getElementById("msg");
const btnFecharSessaoTopo = document.getElementById("btnFecharSessao");


// =======================================================
// UTIL / FORMATAÇÃO
// =======================================================
function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

function formatHorarioIso(iso) {
    try {
        return new Date(iso).toLocaleString();
    } catch {
        return iso;
    }
}

function autoScroll() {
    areaMensagens.scrollTop = areaMensagens.scrollHeight;
}

function clearSelectionUI() {
    document.querySelectorAll("#lista-usuarios li")
        .forEach(li => li.classList.remove("active"));
}

function criarBadgeOnline(online) {
    const span = document.createElement("span");
    span.className = `badge ms-2 ${online ? "bg-success" : "bg-secondary"}`;
    span.textContent = online ? "online" : "offline";
    return span;
}


// =======================================================
// RENDER LISTA DE CONTATOS
// =======================================================
function renderLista() {
    listaUsuarios.innerHTML = "";

    const contatos = Object.values(listaCache)
        .filter(c => c.online) // SOMENTE ONLINE
        .sort((a,b) => a.nome.localeCompare(b.nome));

    if (contatos.length === 0) {
        const li = document.createElement("li");
        li.className = "list-group-item text-muted";
        li.textContent = "Nenhum contato online disponível.";
        listaUsuarios.appendChild(li);
        return;
    }

    contatos.forEach(u => {
        const li = document.createElement("li");
        li.id = `contato-${u.id}`;
        li.className = "list-group-item list-group-item-action d-flex justify-content-between align-items-start";
        li.style.cursor = "pointer";

        // ESQUERDA
        const left = document.createElement("div");
        left.className = "ms-2 me-auto";
        const title = document.createElement("div");
        title.className = "fw-bold";
        title.textContent = u.nome;

        const sub = document.createElement("small");
        sub.className = "text-muted";
        sub.textContent = u.perfil || "";

        left.appendChild(title);
        left.appendChild(sub);

        // DIREITA
        const right = document.createElement("div");
        right.className = "d-flex flex-column align-items-end";

        // online
        const online = criarBadgeOnline(u.online);
        online.id = `online-badge-${u.id}`;

        // preview
        const preview = document.createElement("small");
        preview.className = "text-muted";
        preview.id = `preview-${u.id}`;
        preview.textContent = u.preview || "";

        // botão fechar conversa
        const btnClose = document.createElement("button");
        btnClose.id = `btn-fechar-${u.id}`;
        btnClose.className = "btn btn-sm btn-outline-danger mt-1 d-none";
        btnClose.textContent = "Fechar";
        btnClose.onclick = (e) => {
            e.stopPropagation();
            fecharSessao(u.id);
        };

        right.appendChild(online);
        right.appendChild(preview);
        right.appendChild(btnClose);

        li.appendChild(left);
        li.appendChild(right);

        li.onclick = () => selecionarUsuario(u.id, u.nome);

        listaUsuarios.appendChild(li);
    });

    if (usuarioAtual) {
        const ativo = document.getElementById(`contato-${usuarioAtual}`);
        if (ativo) ativo.classList.add("active");
    }
}


// =======================================================
// ATUALIZAR / REMOVER CONTATO
// =======================================================
function upsertContato(data) {
    listaCache[data.id] = Object.assign({}, listaCache[data.id] || {}, data);
    renderLista();
}

function removerContato(id) {
    delete listaCache[id];
    const el = document.getElementById(`contato-${id}`);
    if (el) el.remove();

    if (usuarioAtual === id) {
        usuarioAtual = null;
        usuarioAtualNome = null;
        tituloChat.textContent = "Selecione alguém";
        areaMensagens.innerHTML = "";
        btnFecharSessaoTopo.classList.add("d-none");
    }
}


// =======================================================
// RENDER DAS MENSAGENS
// =======================================================
function adicionarMensagemEnviada(texto, horario) {
    const div = document.createElement("div");
    div.className = "d-flex justify-content-end mb-2";

    const bubble = document.createElement("div");
    bubble.className = "p-2 bg-primary text-white rounded";
    bubble.style.maxWidth = "75%";
    bubble.innerHTML = `
        <div>${escapeHtml(texto)}</div>
        <small class="d-block text-end text-light-50">${formatHorarioIso(horario)}</small>
    `;

    div.appendChild(bubble);
    areaMensagens.appendChild(div);
    autoScroll();
}

function adicionarMensagemRecebida(texto, nome, horario) {
    const div = document.createElement("div");
    div.className = "d-flex justify-content-start mb-2";

    const bubble = document.createElement("div");
    bubble.className = "p-2 bg-secondary text-dark rounded";
    bubble.style.maxWidth = "75%";
    bubble.innerHTML = `
        <div><strong>${escapeHtml(nome)}:</strong> ${escapeHtml(texto)}</div>
        <small class="d-block text-start text-muted">${formatHorarioIso(horario)}</small>
    `;

    div.appendChild(bubble);
    areaMensagens.appendChild(div);
    autoScroll();
}


// =======================================================
// FETCH CONTATOS
// =======================================================
async function fetchContatos() {
    try {
        const res = await fetch("/chat/contatos");
        const data = await res.json();
        data.forEach(c => upsertContato(c));
    } catch (e) {
        console.error("Erro ao buscar contatos:", e);
    }
}


// =======================================================
// SELECIONAR USUÁRIO
// =======================================================
function selecionarUsuario(id, nome) {
    usuarioAtual = id;
    usuarioAtualNome = nome;

    tituloChat.textContent = `Conversando com ${nome}`;
    areaMensagens.innerHTML = "";
    clearSelectionUI();

    const ativo = document.getElementById(`contato-${id}`);
    if (ativo) ativo.classList.add("active");

    // solicitar histórico ao backend via socket
    socket.emit("load_messages", { para: id });

    // mostrar botão de fechar
    const btnClose = document.getElementById(`btn-fechar-${id}`);
    if (btnClose) btnClose.classList.remove("d-none");

    btnFecharSessaoTopo.classList.remove("d-none");
}


// =======================================================
// FECHAR SESSÃO (REST + socket)
// =======================================================
async function fecharSessao(contatoId) {
    try {
        const res = await fetch(`/chat/fechar/${contatoId}`, { method: "POST" });
        if (!res.ok) throw new Error("Erro ao fechar sessão.");

        // esconder botões
        const btnClose = document.getElementById(`btn-fechar-${contatoId}`);
        if (btnClose) btnClose.classList.add("d-none");

        if (usuarioAtual === contatoId) {
            usuarioAtual = null;
            usuarioAtualNome = null;
            tituloChat.textContent = "Selecione alguém";
            areaMensagens.innerHTML = "";
            clearSelectionUI();
            btnFecharSessaoTopo.classList.add("d-none");
        }

        // avisar outro usuário
        socket.emit("fechar_sessao", { para: contatoId });

    } catch (e) {
        console.error("fecharSessao:", e);
    }
}


// =======================================================
// SOCKET EVENTS
// =======================================================

// ao conectar → carregar contatos
socket.on("connect", () => {
    fetchContatos();
});

// ONLINE
socket.on("user_online", data => {
    upsertContato({
        id: data.id,
        nome: data.nome,
        perfil: data.perfil || "",
        online: true
    });
});

// OFFLINE
socket.on("user_offline", data => {
    if (listaCache[data.id]) {
        listaCache[data.id].online = false;
        renderLista();
    }
});

// RECEBER MENSAGEM
socket.on("receive_message", data => {
    if (usuarioAtual === data.de) {
        adicionarMensagemRecebida(data.texto, data.nome, data.horario);
    } else {
        if (listaCache[data.de]) {
            listaCache[data.de].preview = `${data.nome}: ${data.texto}`;
            renderLista();
        }
    }
});

// CONFIRMAÇÃO PARA O REMETENTE
socket.on("message_sent", data => {
    if (usuarioAtual === data.para) {
        adicionarMensagemEnviada(data.texto, data.horario);
    }
});

// HISTÓRICO
socket.on("load_messages_response", lista => {
    areaMensagens.innerHTML = "";
    lista.forEach(msg => {
        if (msg.de === usuarioAtual) {
            adicionarMensagemRecebida(msg.texto, listaCache[msg.de]?.nome || "Contato", msg.horario);
        } else {
            adicionarMensagemEnviada(msg.texto, msg.horario);
        }
    });
    autoScroll();
});

// SESSÃO FECHADA EM TEMPO REAL
socket.on("sessao_fechada", data => {
    const contatoId = data.de;

    const btnClose = document.getElementById(`btn-fechar-${contatoId}`);
    if (btnClose) btnClose.classList.add("d-none");

    if (usuarioAtual === contatoId) {
        usuarioAtual = null;
        usuarioAtualNome = null;
        tituloChat.textContent = "Selecione alguém";
        areaMensagens.innerHTML = "";
        clearSelectionUI();
        btnFecharSessaoTopo.classList.add("d-none");
    }
});


// =======================================================
// ENVIAR MENSAGEM
// =======================================================
btnEnviar.onclick = () => {
    const texto = inputMsg.value.trim();
    if (!texto || !usuarioAtual) return;

    socket.emit("send_message", {
        para: usuarioAtual,
        texto: texto
    });

    inputMsg.value = "";
};

// ENTER envia
inputMsg.addEventListener("keypress", e => {
    if (e.key === "Enter") {
        btnEnviar.click();
        e.preventDefault();
    }
});


// =======================================================
// Fallback inicial
// =======================================================
fetchContatos().catch(() => {});
