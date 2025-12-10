// Acesso aos dados iniciais enviados pela página
const DATA = window.dashboardData || {};

// DOM Elements
const elTituloPrincipal = document.getElementById("titulo-grafico-principal");
const elTituloSecundario = document.getElementById("titulo-grafico-secundario");
const elTituloTabela = document.getElementById("titulo-tabela");

const tabelaHead = document.getElementById("tabela-head");
const tabelaBody = document.getElementById("tabela-body");


// ===================================================================
//  HELPERS
// ===================================================================

function safe(v) {
    return v || [];
}

function createChart(ctx, type, labels, values) {
    return new Chart(ctx, {
        type,
        data: {
            labels: safe(labels),
            datasets: [{
                label: "",
                data: safe(values),
                borderWidth: 1,
                backgroundColor: [
                    "rgba(54,162,235,0.6)",
                    "rgba(255,99,132,0.6)",
                    "rgba(255,205,86,0.6)",
                    "rgba(75,192,192,0.6)",
                    "rgba(153,102,255,0.6)",
                    "rgba(201,203,207,0.6)"
                ],
                borderColor: "rgba(0,0,0,0.05)"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function updateChart(chart, type, labels, values) {
    chart.config.type = type;
    chart.data.labels = safe(labels);
    chart.data.datasets[0].data = safe(values);
    chart.update();
}

function renderTable(headEl, bodyEl, rows) {
    headEl.innerHTML = "";
    bodyEl.innerHTML = "";

    if (!rows || rows.length === 0) {
        headEl.innerHTML = "<tr><th>Nenhum dado disponível</th></tr>";
        return;
    }

    const keys = Object.keys(rows[0]);
    const headRow = document.createElement("tr");

    keys.forEach(key => {
        const th = document.createElement("th");
        th.textContent = key.charAt(0).toUpperCase() + key.slice(1);
        headRow.appendChild(th);
    });

    headEl.appendChild(headRow);

    rows.forEach(row => {
        const tr = document.createElement("tr");

        keys.forEach(key => {
            const td = document.createElement("td");
            td.textContent = row[key] == null ? "" : row[key];
            tr.appendChild(td);
        });

        bodyEl.appendChild(tr);
    });
}


// ===================================================================
//  CONFIGURAÇÃO INICIAL DOS GRÁFICOS
// ===================================================================

const grafPrincipalCtx = document.getElementById("grafPrincipal").getContext("2d");
const grafSecundarioCtx = document.getElementById("grafSecundario").getContext("2d");

let chartPrincipal = createChart(
    grafPrincipalCtx,
    "pie",
    DATA.usuariosLabels,
    DATA.usuariosValores
);

let chartSecundario = createChart(
    grafSecundarioCtx,
    "line",
    DATA.loginLabels,
    DATA.loginValores
);

// Render inicial da tabela (últimos logs)
renderTable(tabelaHead, tabelaBody, DATA.logsIniciais);


// ===================================================================
//  API - Buscar dados por entidade
// ===================================================================

async function fetchEntity(entity) {
    try {
        const res = await fetch(`/dashboard/data/${entity}`);
        if (!res.ok) throw new Error("Erro ao buscar dados do servidor");
        return await res.json();
    } catch (err) {
        console.error("Erro:", err);
        return null;
    }
}


// ===================================================================
//  MOSTRAR ENTIDADE SELECIONADA
// ===================================================================

async function showEntity(entity) {
    const data = await fetchEntity(entity);
    if (!data) return;

    // Atualizar títulos dos gráficos e tabela
    if (entity === "usuarios") {
        elTituloPrincipal.textContent = data.chart.title;
        elTituloSecundario.textContent = data.chart2.title;
        elTituloTabela.textContent = "Lista de Usuários";

        updateChart(chartPrincipal, data.chart.type, data.chart.labels, data.chart.values);
        
        updateChart(chartSecundario, data.chart2.type, data.chart2.labels, data.chart2.values);
        console.log("Chart1 labels recebidos:", data.chart.labels);
        console.log("Chart2 labels recebidos:", data.chart2.labels);
    }

    if (entity === "veiculos") {
        elTituloPrincipal.textContent = data.chart.title;
        elTituloSecundario.textContent = data.chart2.title;
        elTituloTabela.textContent = "Tabela de Veículos";

        updateChart(chartPrincipal, data.chart.type, data.chart.labels, data.chart.values);

        // gráfico secundário customizado
        updateChart(chartSecundario, data.chart2.type, data.chart2.labels, data.chart2.values);
        console.log("Chart1 labels recebidos:", data.chart.labels);
        console.log("Chart2 labels recebidos:", data.chart2.labels);
    }

    if (entity === "equipamentos") {
        elTituloPrincipal.textContent = data.chart.title;
        elTituloSecundario.textContent = data.chart2.title;
        elTituloTabela.textContent = "Tabela de Equipamentos";
        console.log("Chart1 labels recebidos:", data.chart.labels);
        console.log("Chart2 labels recebidos:", data.chart2.labels);
        updateChart(chartPrincipal, data.chart.type, data.chart.labels, data.chart.values);

        updateChart(chartSecundario, data.chart2.type, data.chart2.labels, data.chart2.values);
    }

    // Tabela relacionada à entidade
    renderTable(tabelaHead, tabelaBody, data.table);
}


// ===================================================================
//  EVENTOS DOS CARDS
// ===================================================================

document.querySelectorAll(".clickable-card").forEach(card => {
    card.addEventListener("click", () => {
        document.querySelectorAll(".clickable-card")
            .forEach(c => c.classList.remove("border-primary"));

        card.classList.add("border-primary");

        showEntity(card.dataset.entity);
    });
});


// ===================================================================
//  MOSTRAR TUDO (ESTADO ORIGINAL DO DASHBOARD)
// ===================================================================

document.getElementById("btnMostrarTudo").addEventListener("click", () => {
    elTituloPrincipal.textContent = "Gráfico Principal";
    elTituloSecundario.textContent = "Segundo Gráfico";
    elTituloTabela.textContent = "Tabela";

    updateChart(chartPrincipal, "pie", DATA.usuariosLabels, DATA.usuariosValores);
    updateChart(chartSecundario, "line", DATA.loginLabels, DATA.loginValores);

    renderTable(tabelaHead, tabelaBody, DATA.logsIniciais);

    document.querySelectorAll(".clickable-card").forEach(c => c.classList.remove("border-primary"));
});
