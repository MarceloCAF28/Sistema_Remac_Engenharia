// ============================================
// GERENCIAMENTO DE RELATÓRIOS
// ============================================

let obras = [];

document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Módulo de relatórios iniciado');
    carregarObras();
    
    // Definir data atual nos selects de mês/ano
    const hoje = new Date();
    document.getElementById('relatorioMes').value = (hoje.getMonth() + 1).toString();
    document.getElementById('relatorioAno').value = hoje.getFullYear().toString();
});

// ========== CARREGAR OBRAS ==========
async function carregarObras() {
    try {
        obras = await api.get('/obras');
        
        const select = document.getElementById('relatorioObra');
        if (select) {
            let options = '<option value="">Todas as Obras</option>';
            obras.forEach(obra => {
                options += `<option value="${obra.id}">${obra.nome}</option>`;
            });
            select.innerHTML = options;
        }
    } catch (error) {
        console.error('❌ Erro ao carregar obras:', error);
    }
}

// ========== GERAR RELATÓRIOS ==========
function gerarRelatorioObras() {
    window.open(API_URL + '/relatorio/obras', '_blank');
    mostrarNotificacao('✅ Relatório de obras gerado com sucesso!', 'success');
}

function gerarRelatorioReceitas() {
    const obraId = document.getElementById('relatorioObra').value;
    const mes = document.getElementById('relatorioMes').value;
    const ano = document.getElementById('relatorioAno').value;
    
    let url = API_URL + '/relatorio/receitas?';
    const params = [];
    if (obraId) params.push(`obra_id=${obraId}`);
    if (mes) params.push(`mes=${mes}`);
    if (ano) params.push(`ano=${ano}`);
    
    window.open(url + params.join('&'), '_blank');
    mostrarNotificacao('✅ Relatório de receitas gerado com sucesso!', 'success');
}

function gerarRelatorioDespesas() {
    const obraId = document.getElementById('relatorioObra').value;
    const mes = document.getElementById('relatorioMes').value;
    const ano = document.getElementById('relatorioAno').value;
    const tipo = document.getElementById('relatorioTipo').value;
    
    let url = API_URL + '/relatorio/despesas?';
    const params = [];
    if (obraId) params.push(`obra_id=${obraId}`);
    if (mes) params.push(`mes=${mes}`);
    if (ano) params.push(`ano=${ano}`);
    if (tipo) params.push(`tipo=${tipo}`);
    
    window.open(url + params.join('&'), '_blank');
    mostrarNotificacao('✅ Relatório de despesas gerado com sucesso!', 'success');
}

function gerarRelatorioABC() {
    const obraId = document.getElementById('relatorioObra').value;
    
    let url = API_URL + '/relatorio/abc';
    if (obraId) {
        url += `?obra_id=${obraId}`;
    }
    
    window.open(url, '_blank');
    mostrarNotificacao('✅ Relatório ABC gerado com sucesso!', 'success');
}

function gerarRelatorioContas() {
    window.open(API_URL + '/relatorio/contas', '_blank');
    mostrarNotificacao('✅ Relatório de contas gerado com sucesso!', 'success');
}

function gerarRelatorioFinanceiro() {
    const mes = document.getElementById('relatorioMes').value;
    const ano = document.getElementById('relatorioAno').value;
    
    let url = API_URL + '/relatorio/financeiro?';
    const params = [];
    if (mes) params.push(`mes=${mes}`);
    if (ano) params.push(`ano=${ano}`);
    
    window.open(url + params.join('&'), '_blank');
    mostrarNotificacao('✅ Relatório financeiro gerado com sucesso!', 'success');
}

function gerarRelatorioParcelas() {
    const tipo = document.getElementById('relatorioTipo').value || 'todas';
    window.open(API_URL + `/relatorio/parcelas?tipo=${tipo}`, '_blank');
    mostrarNotificacao('✅ Relatório de parcelas gerado com sucesso!', 'success');
}

// ========== APLICAR FILTROS ==========
function aplicarFiltrosRelatorio() {
    mostrarNotificacao('✅ Filtros aplicados!', 'success');
}

// Exportar funções
window.gerarRelatorioObras = gerarRelatorioObras;
window.gerarRelatorioReceitas = gerarRelatorioReceitas;
window.gerarRelatorioDespesas = gerarRelatorioDespesas;
window.gerarRelatorioABC = gerarRelatorioABC;
window.gerarRelatorioContas = gerarRelatorioContas;
window.gerarRelatorioFinanceiro = gerarRelatorioFinanceiro;
window.gerarRelatorioParcelas = gerarRelatorioParcelas;
window.aplicarFiltrosRelatorio = aplicarFiltrosRelatorio;