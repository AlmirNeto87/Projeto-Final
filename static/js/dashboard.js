// Acesso aos dados iniciais enviados pela página
const DATA = window.dashboardData || {};

// DOM Elements (certifique-se que existem estes elementos no template)
const elTituloPrincipal = document.getElementById("titulo-grafico-principal");
const elTituloSecundario = document.getElementById("titulo-grafico-secundario");
const elTituloTabela = document.getElementById("titulo-tabela");

const tabelaHead = document.getElementById("tabela-head");
const tabelaBody = document.getElementById("tabela-body");

// ===================================================================
// HELPERS
// ===================================================================

function safe(v) { return v || []; }

// converte qualquer label em string segura que o Chart.js vai aceitar
function toLabelString(x) {
    if (x === null || x === undefined) return "Não informado";
    // Date -> formato legível
    if (Object.prototype.toString.call(x) === "[object Date]" || (typeof x === "string" && /^\d{4}-\d{2}-\d{2}/.test(x))) {
        try {
            const d = new Date(x);
            if (!isNaN(d.getTime())) return d.toLocaleString();
        } catch {}
    }
    // força string e remove espaços estranhos / normaliza acentos
    return String(x).normalize("NFKD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, " ").trim();
}

function normalizeLabels(labels) {
    if (!labels) return [];
    return labels.map(l => toLabelString(l));
}

// cria opções diferentes dependendo do tipo (garante axis/legend)
function chartOptionsForType(type) {
    const base = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: (type === "pie" || type === "doughnut") }
        }
    };

    if (type === "bar" || type === "line") {
        base.scales = {
            x: { display: true, ticks: { autoSkip: false } },
            y: { display: true, beginAtZero: true }
        };
        // se line, ativar tension/pointRadius se quiser
        if (type === "line") {
            base.elements = { line: { tension: 0.3 } };
        }
    }

    return base;
}

function createChart(ctx, type, labels, values) {
    const normalizedLabels = normalizeLabels(labels);
    const opts = chartOptionsForType(type);
    return new Chart(ctx, {
        type,
        data: {
            labels: normalizedLabels,
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
        options: opts
    });
}

function updateChart(chart, type, labels, values) {
    // coerção + debug
    const before = chart.config.type;
    const normLabels = normalizeLabels(labels);
    console.log("[dashboard] atualizando chart:", { beforeType: before, afterType: type, rawLabels: labels, normLabels });

    // trocar tipo (Chart.js v3+ aceita mudar config.type e chamar update())
    chart.config.type = type;
    chart.options = chartOptionsForType(type);

    // assegura dataset[0] existir
    if (!chart.data.datasets || chart.data.datasets.length === 0) {
        chart.data.datasets = [{ data: [], backgroundColor: [], borderColor: "rgba(0,0,0,0.05)" }];
    }

    chart.data.labels = normLabels;
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
// CONFIGURAÇÃO INICIAL DOS GRÁFICOS
// ===================================================================

const grafPrincipalCtx = document.getElementById("grafPrincipal").getContext("2d");
const grafSecundarioCtx = document.getElementById("grafSecundario").getContext("2d");

let chartPrincipal = createChart(
    grafPrincipalCtx,
    DATA.chart ? DATA.chart.type || "pie" : "pie",
    DATA.chart ? DATA.chart.labels || [] : (DATA.usuariosLabels || []),
    DATA.chart ? DATA.chart.values || [] : (DATA.usuariosValores || [])
);

let chartSecundario = createChart(
    grafSecundarioCtx,
    DATA.chart2 ? DATA.chart2.type || "line" : "line",
    DATA.chart2 ? DATA.chart2.labels || [] : (DATA.loginLabels || []),
    DATA.chart2 ? DATA.chart2.values || [] : (DATA.loginValores || [])
);

// Render inicial da tabela (últimos logs)
renderTable(tabelaHead, tabelaBody, DATA.logsIniciais || []);

// ===================================================================
// API - Buscar dados por entidade
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
// MOSTRAR ENTIDADE SELECIONADA
// ===================================================================

async function showEntity(entity) {
    const data = await fetchEntity(entity);
    if (!data) return;

    // títulos
    elTituloPrincipal.textContent = (data.chart && data.chart.title) || "Gráfico Principal";
    elTituloSecundario.textContent = (data.chart2 && data.chart2.title) || "Segundo Gráfico";

    // tabela título
    if (entity === "usuarios") elTituloTabela.textContent = "Lista de Usuários";
    else if (entity === "veiculos") elTituloTabela.textContent = "Tabela de Veículos";
    else if (entity === "equipamentos") elTituloTabela.textContent = "Tabela de Equipamentos";

    // atualiza charts
    updateChart(chartPrincipal, (data.chart && data.chart.type) || "bar", (data.chart && data.chart.labels) || [], (data.chart && data.chart.values) || []);
    updateChart(chartSecundario, (data.chart2 && data.chart2.type) || "line", (data.chart2 && data.chart2.labels) || [], (data.chart2 && data.chart2.values) || []);

    // debug – mostra no console o que está chegando
    console.log("[dashboard] Chart1 labels recebidos:", data.chart && data.chart.labels);
    console.log("[dashboard] Chart2 labels recebidos:", data.chart2 && data.chart2.labels);

    // tabela
    renderTable(tabelaHead, tabelaBody, data.table || []);
}

// ===================================================================
// EVENTOS DOS CARDS
// ===================================================================

document.querySelectorAll(".clickable-card").forEach(card => {
    card.addEventListener("click", () => {
        document.querySelectorAll(".clickable-card").forEach(c => c.classList.remove("border-primary"));
        card.classList.add("border-primary");
        showEntity(card.dataset.entity);
    });
});

// ===================================================================
// MOSTRAR TUDO
// ===================================================================

document.getElementById("btnMostrarTudo").addEventListener("click", () => {
    elTituloPrincipal.textContent = "Gráfico Principal";
    elTituloSecundario.textContent = "Segundo Gráfico";
    elTituloTabela.textContent = "Tabela";

    updateChart(chartPrincipal, "pie", DATA.usuariosLabels || [], DATA.usuariosValores || []);
    updateChart(chartSecundario, "line", DATA.loginLabels || [], DATA.loginValores || []);

    renderTable(tabelaHead, tabelaBody, DATA.logsIniciais || []);

    document.querySelectorAll(".clickable-card").forEach(c => c.classList.remove("border-primary"));
});
