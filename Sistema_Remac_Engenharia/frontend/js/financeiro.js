// ============================================
// GESTÃO FINANCEIRA
// ============================================

let mesesDisponiveis = [];
let mesAtual = null;
let anoAtual = null;
let dadosFinanceiros = null;

let graficoPizza, graficoBarras, graficoEvolucao;

document.addEventListener('DOMContentLoaded', function() {
    console.log('💰 Módulo financeiro iniciado');
    
    // Carregar meses disponíveis
    carregarMesesDisponiveis();
});

// ========== CARREGAR MESES DISPONÍVEIS ==========
async function carregarMesesDisponiveis() {
    try {
        mesesDisponiveis = await api.get('/financeiro/meses-disponiveis');
        console.log('📅 Meses disponíveis:', mesesDisponiveis);
        
        const seletor = document.getElementById('seletorMes');
        if (seletor) {
            let options = '';
            mesesDisponiveis.forEach(m => {
                options += `<option value="${m.valor}">${m.nome}</option>`;
            });
            seletor.innerHTML = options;
            
            // Se houver meses, selecionar o primeiro (mais recente)
            if (mesesDisponiveis.length > 0) {
                const primeiro = mesesDisponiveis[0];
                seletor.value = primeiro.valor;
                const [ano, mes] = primeiro.valor.split('-').map(Number);
                carregarResumoMensal(ano, mes);
            } else {
                // Se não houver dados, carregar mês atual
                const hoje = new Date();
                carregarResumoMensal(hoje.getFullYear(), hoje.getMonth() + 1);
            }
        }
    } catch (error) {
        console.error('❌ Erro ao carregar meses:', error);
        // Carregar mês atual como fallback
        const hoje = new Date();
        carregarResumoMensal(hoje.getFullYear(), hoje.getMonth() + 1);
    }
}

// ========== CARREGAR RESUMO MENSAL ==========
async function carregarResumoMensal(ano, mes) {
    console.log(`📊 Carregando resumo de ${mes}/${ano}`);
    
    mesAtual = mes;
    anoAtual = ano;
    
    try {
        dadosFinanceiros = await api.get(`/financeiro/resumo-mensal?ano=${ano}&mes=${mes}`);
        console.log('📊 Dados carregados:', dadosFinanceiros);
        
        atualizarInterface();
        carregarEvolucaoAnual(ano);
    } catch (error) {
        console.error('❌ Erro ao carregar resumo mensal:', error);
        mostrarNotificacao('❌ Erro ao carregar dados financeiros', 'danger');
    }
}

// ========== ATUALIZAR INTERFACE ==========
function atualizarInterface() {
    if (!dadosFinanceiros) return;
    
    // Atualizar cabeçalho
    document.getElementById('mesAno').innerHTML = `${dadosFinanceiros.mes}/${dadosFinanceiros.ano}`;
    document.getElementById('nomeMes').innerHTML = dadosFinanceiros.nome_mes;
    
    // Atualizar cards
    document.getElementById('totalEntradas').innerHTML = `R$ ${formatarMoeda(dadosFinanceiros.resumo.total_entradas)}`;
    document.getElementById('totalSaidas').innerHTML = `R$ ${formatarMoeda(dadosFinanceiros.resumo.total_saidas)}`;
    document.getElementById('saldoMes').innerHTML = `R$ ${formatarMoeda(dadosFinanceiros.resumo.saldo)}`;
    
    const qtdReceitas = dadosFinanceiros.resumo.qtd_receitas || 0;
    const qtdDespesas = dadosFinanceiros.resumo.qtd_despesas || 0;
    const qtdMateriais = dadosFinanceiros.resumo.qtd_materiais || 0;
    const qtdMaoObra = dadosFinanceiros.resumo.qtd_mao_obra || 0;
    
    document.getElementById('qtdReceitas').innerHTML = `${qtdReceitas} receitas`;
    document.getElementById('qtdDespesas').innerHTML = `${qtdDespesas + qtdMateriais + qtdMaoObra} despesas (${qtdDespesas} gerais, ${qtdMateriais} materiais, ${qtdMaoObra} MO)`;
    
    // Atualizar cor do card de saldo
    const cardSaldo = document.getElementById('cardSaldo');
    const saldo = dadosFinanceiros.resumo.saldo;
    const status = dadosFinanceiros.resumo.status;
    
    cardSaldo.classList.remove('bg-success', 'bg-danger', 'bg-secondary');
    if (saldo > 0) {
        cardSaldo.classList.add('bg-success');
        document.getElementById('statusMes').innerHTML = '✅ Mês POSITIVO';
    } else if (saldo < 0) {
        cardSaldo.classList.add('bg-danger');
        document.getElementById('statusMes').innerHTML = '❌ Mês NEGATIVO';
    } else {
        cardSaldo.classList.add('bg-secondary');
        document.getElementById('statusMes').innerHTML = '⚪ Mês NEUTRO';
    }
    cardSaldo.classList.add('text-white');
    
    // Atualizar gráficos
    atualizarGraficos();
}

// ========== ATUALIZAR GRÁFICOS ==========
function atualizarGraficos() {
    if (!dadosFinanceiros) return;
    
    const totalEntradas = dadosFinanceiros.resumo.total_entradas;
    const totalSaidas = dadosFinanceiros.resumo.total_saidas;
    
    // Gráfico de Pizza (Receitas vs Despesas)
    const ctxPizza = document.getElementById('graficoPizza')?.getContext('2d');
    if (ctxPizza) {
        if (graficoPizza) graficoPizza.destroy();
        
        graficoPizza = new Chart(ctxPizza, {
            type: 'pie',
            data: {
                labels: ['Receitas', 'Despesas'],
                datasets: [{
                    data: [totalEntradas, totalSaidas],
                    backgroundColor: ['#28a745', '#dc3545'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
}

// ========== CARREGAR EVOLUÇÃO ANUAL ==========
async function carregarEvolucaoAnual(ano) {
    try {
        const dados = await api.get(`/financeiro/evolucao-anual?ano=${ano}`);
        console.log('📈 Evolução anual:', dados);
        
        document.getElementById('anoEvolucao').innerHTML = ano;
        
        const ctxEvolucao = document.getElementById('graficoEvolucao')?.getContext('2d');
        if (ctxEvolucao) {
            if (graficoEvolucao) graficoEvolucao.destroy();
            
            graficoEvolucao = new Chart(ctxEvolucao, {
                type: 'line',
                data: {
                    labels: dados.map(d => d.nome_mes.substring(0, 3)),
                    datasets: [
                        {
                            label: 'Receitas',
                            data: dados.map(d => d.receitas),
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'Despesas',
                            data: dados.map(d => d.despesas),
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            tension: 0.4,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: `Evolução Financeira ${ano}`
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('❌ Erro ao carregar evolução anual:', error);
    }
}

// ========== NAVEGAÇÃO ENTRE MESES ==========
function mudarMes() {
    const seletor = document.getElementById('seletorMes');
    const valor = seletor.value;
    
    if (valor) {
        const [ano, mes] = valor.split('-').map(Number);
        carregarResumoMensal(ano, mes);
    }
}

function carregarMesAnterior() {
    if (!mesAtual || !anoAtual) return;
    
    let novoMes = mesAtual - 1;
    let novoAno = anoAtual;
    
    if (novoMes < 1) {
        novoMes = 12;
        novoAno -= 1;
    }
    
    carregarResumoMensal(novoAno, novoMes);
    // Atualizar seletor
    const seletor = document.getElementById('seletorMes');
    seletor.value = `${novoAno}-${novoMes.toString().padStart(2, '0')}`;
}

function carregarProximoMes() {
    if (!mesAtual || !anoAtual) return;
    
    let novoMes = mesAtual + 1;
    let novoAno = anoAtual;
    
    if (novoMes > 12) {
        novoMes = 1;
        novoAno += 1;
    }
    
    carregarResumoMensal(novoAno, novoMes);
    // Atualizar seletor
    const seletor = document.getElementById('seletorMes');
    seletor.value = `${novoAno}-${novoMes.toString().padStart(2, '0')}`;
}

// Exportar funções
window.carregarMesAnterior = carregarMesAnterior;
window.carregarProximoMes = carregarProximoMes;
window.mudarMes = mudarMes;
window.formatarMoeda = formatarMoeda;