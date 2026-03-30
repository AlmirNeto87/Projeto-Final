const chatArea = document.getElementById("chat-area");
const input = document.getElementById("inputPergunta");
const btn = document.getElementById("btnEnviar");

function addMsg(texto, tipo="bot"){
    const div = document.createElement("div");
    div.className = tipo === "user" ? "text-end mb-2" : "text-start mb-2";
    div.innerHTML = `<span class="badge bg-${tipo==="user"?"primary":"secondary"}">${texto}</span>`;
    chatArea.appendChild(div);
    chatArea.scrollTop = chatArea.scrollHeight;
}

btn.onclick = async () => {
    const pergunta = input.value.trim();
    if(!pergunta) return;

    addMsg(pergunta, "user");
    input.value = "";

    const res = await fetch("/chatbot/perguntar", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({pergunta})
    });

    const data = await res.json();
    addMsg(data.resposta, "bot");
};

input.addEventListener("keypress", e=>{
    if(e.key === "Enter") btn.click();
});