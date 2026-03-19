// ============================================
// DASHBOARD
// ============================================

let obras = [];
let graficoPizza, graficoBarras;

document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Dashboard iniciado');
    carregarDados();
});

// ========== CARREGAR DADOS ==========
async function carregarDados() {
    try {
        obras = await api.get('/obras');
        console.log('📋 Obras carregadas:', obras.length);
        
        atualizarCards();
        renderizarTabela();
        criarGraficos();
    } catch (error) {
        console.error('❌ Erro ao carregar dados:', error);
        mostrarNotificacao('❌ Erro ao carregar dashboard', 'danger');
    }
}

// ========== ATUALIZAR CARDS ==========
function atualizarCards() {
    let totalObras = obras.length;
    let obrasAndamento = obras.filter(o => o.status === 'EM ANDAMENTO').length;
    let totalReceitas = 0;
    let totalDespesas = 0;
    
    obras.forEach(obra => {
        totalReceitas += obra.total_receitas || 0;
        totalDespesas += obra.total_despesas || 0;
    });
    
    let lucroTotal = totalReceitas - totalDespesas;
    let margemMedia = totalReceitas > 0 ? (lucroTotal / totalReceitas * 100).toFixed(2) : 0;
    
    document.getElementById('totalObras').innerHTML = totalObras;
    document.getElementById('obrasAndamento').innerHTML = `${obrasAndamento} em andamento`;
    document.getElementById('totalReceitas').innerHTML = `R$ ${formatarMoeda(totalReceitas)}`;
    document.getElementById('totalDespesas').innerHTML = `R$ ${formatarMoeda(totalDespesas)}`;
    document.getElementById('lucroTotal').innerHTML = `R$ ${formatarMoeda(lucroTotal)}`;
    document.getElementById('margemMedia').innerHTML = `${margemMedia}%`;
}

// ========== RENDERIZAR TABELA ==========
function renderizarTabela() {
    const tbody = document.getElementById('tabelaObras');
    
    if (obras.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Nenhuma obra cadastrada</td></tr>';
        return;
    }
    
    let html = '';
    obras.slice(0, 10).forEach(obra => {
        const statusClass = obra.status === 'EM ANDAMENTO' ? 'bg-primary' : (obra.status === 'CONCLUIDA' ? 'bg-success' : 'bg-warning');
        const statusText = obra.status === 'EM ANDAMENTO' ? 'Em Andamento' : (obra.status === 'CONCLUIDA' ? 'Concluída' : 'Paralisada');
        const lucroClass = obra.lucro < 0 ? 'text-danger' : 'text-success';
        
        html += `
            <tr>
                <td><strong>${obra.nome}</strong></td>
                <td>${obra.cliente}</td>
                <td><span class="badge ${statusClass}">${statusText}</span></td>
                <td class="text-end">R$ ${formatarMoeda(obra.total_receitas)}</td>
                <td class="text-end">R$ ${formatarMoeda(obra.total_despesas)}</td>
                <td class="text-end ${lucroClass}">R$ ${formatarMoeda(obra.lucro)}</td>
                <td class="text-end">${obra.margem_lucro}%</td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// ========== CRIAR GRÁFICOS ==========
function criarGraficos() {
    // Gráfico de Pizza - Material vs Mão de Obra
    let totalMateriais = 0;
    let totalMaoObra = 0;
    
    obras.forEach(obra => {
        totalMateriais += obra.total_materiais || 0;
        totalMaoObra += obra.total_mao_obra || 0;
    });
    
    const ctxPizza = document.getElementById('graficoPizza')?.getContext('2d');
    if (ctxPizza) {
        if (graficoPizza) graficoPizza.destroy();
        
        graficoPizza = new Chart(ctxPizza, {
            type: 'pie',
            data: {
                labels: ['Materiais', 'Mão de Obra'],
                datasets: [{
                    data: [totalMateriais, totalMaoObra],
                    backgroundColor: ['#48bb78', '#4299e1'],
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
    
    // Gráfico de Barras - Top 5 Obras por Lucro
    const obrasLucro = [...obras].sort((a, b) => b.lucro - a.lucro).slice(0, 5);
    
    const ctxBarras = document.getElementById('graficoBarras')?.getContext('2d');
    if (ctxBarras) {
        if (graficoBarras) graficoBarras.destroy();
        
        graficoBarras = new Chart(ctxBarras, {
            type: 'bar',
            data: {
                labels: obrasLucro.map(o => o.nome.length > 15 ? o.nome.substring(0, 15) + '...' : o.nome),
                datasets: [{
                    label: 'Lucro (R$)',
                    data: obrasLucro.map(o => o.lucro),
                    backgroundColor: '#48bb78'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}

// Exportar funções
window.formatarMoeda = formatarMoeda;