// ============================================
// GERENCIAMENTO DE CONTAS BANCÁRIAS
// ============================================

let contas = [];
let modalNovaConta, modalEditarConta, modalExtrato;

document.addEventListener('DOMContentLoaded', function() {
    console.log('🏦 Módulo de contas iniciado');
    
    modalNovaConta = new bootstrap.Modal(document.getElementById('modalNovaConta'));
    modalEditarConta = new bootstrap.Modal(document.getElementById('modalEditarConta'));
    modalExtrato = new bootstrap.Modal(document.getElementById('modalExtrato'));
    
    carregarContas();
});

// ========== CARREGAR CONTAS ==========
async function carregarContas() {
    const tbody = document.getElementById('listaContas');
    
    try {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">🔄 Carregando...</td></tr>';
        
        contas = await api.get('/contas');
        
        renderizarTabela(contas);
        atualizarResumo(contas);
        
    } catch (error) {
        console.error('❌ Erro ao carregar contas:', error);
        tbody.innerHTML = '<tr><td colspan="9" class="text-center text-danger">❌ Erro ao carregar contas</td></tr>';
    }
}

// ========== RENDERIZAR TABELA ==========
function renderizarTabela(contasFiltradas) {
    const tbody = document.getElementById('listaContas');
    
    if (contasFiltradas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">📭 Nenhuma conta cadastrada</td></tr>';
        return;
    }
    
    let html = '';
    contasFiltradas.forEach(c => {
        const saldoClass = c.saldo_atual >= 0 ? 'text-success' : 'text-danger';
        
        html += `
            <tr>
                <td>${c.id}</td>
                <td><strong>${c.nome}</strong></td>
                <td>${c.banco || '-'}</td>
                <td>${c.agencia || '-'}</td>
                <td>${c.numero_conta || '-'}</td>
                <td>${c.tipo || '-'}</td>
                <td class="text-end">R$ ${formatarMoeda(c.saldo_inicial)}</td>
                <td class="text-end ${saldoClass}">R$ ${formatarMoeda(c.saldo_atual)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-info" onclick="verExtrato(${c.id})" title="Extrato">
                        <i class="bi bi-receipt"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-primary" onclick="editarConta(${c.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deletarConta(${c.id}, '${c.nome.replace(/'/g, "\\'")}')" title="Deletar">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// ========== ATUALIZAR RESUMO ==========
function atualizarResumo(contasFiltradas) {
    let saldoTotal = 0;
    let totalContas = contasFiltradas.length;
    
    contasFiltradas.forEach(c => {
        saldoTotal += c.saldo_atual || 0;
    });
    
    const mediaContas = totalContas > 0 ? saldoTotal / totalContas : 0;
    
    document.getElementById('saldoTotal').innerHTML = `R$ ${formatarMoeda(saldoTotal)}`;
    document.getElementById('totalContas').innerHTML = totalContas;
    document.getElementById('mediaContas').innerHTML = `R$ ${formatarMoeda(mediaContas)}`;
}

// ========== NOVA CONTA ==========
function abrirModalNovaConta() {
    document.getElementById('nome').value = '';
    document.getElementById('banco').value = '';
    document.getElementById('agencia').value = '';
    document.getElementById('numero_conta').value = '';
    document.getElementById('tipo').value = 'CORRENTE';
    document.getElementById('saldo_inicial').value = '0';
    document.getElementById('observacao').value = '';
    
    modalNovaConta.show();
}

async function salvarNovaConta() {
    const nome = document.getElementById('nome').value.trim();
    
    if (!nome) {
        mostrarNotificacao('❌ Nome da conta é obrigatório', 'danger');
        return;
    }
    
    const dados = {
        nome: nome,
        banco: document.getElementById('banco').value.trim() || null,
        agencia: document.getElementById('agencia').value.trim() || null,
        numero_conta: document.getElementById('numero_conta').value.trim() || null,
        tipo: document.getElementById('tipo').value,
        saldo_inicial: parseFloat(document.getElementById('saldo_inicial').value) || 0,
        observacao: document.getElementById('observacao').value.trim() || null
    };
    
    try {
        const result = await api.post('/contas', dados);
        if (result.success) {
            mostrarNotificacao('✅ Conta criada com sucesso!', 'success');
            modalNovaConta.hide();
            await carregarContas();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao criar conta', 'danger');
    }
}

// ========== EDITAR CONTA ==========
async function editarConta(contaId) {
    const conta = contas.find(c => c.id === contaId);
    if (!conta) return;
    
    document.getElementById('edit_id').value = conta.id;
    document.getElementById('edit_nome').value = conta.nome;
    document.getElementById('edit_banco').value = conta.banco || '';
    document.getElementById('edit_agencia').value = conta.agencia || '';
    document.getElementById('edit_numero_conta').value = conta.numero_conta || '';
    document.getElementById('edit_tipo').value = conta.tipo || 'CORRENTE';
    document.getElementById('edit_saldo_inicial').value = conta.saldo_inicial;
    document.getElementById('edit_observacao').value = conta.observacao || '';
    
    modalEditarConta.show();
}

async function atualizarConta() {
    const id = document.getElementById('edit_id').value;
    const nome = document.getElementById('edit_nome').value.trim();
    
    if (!nome) {
        mostrarNotificacao('❌ Nome da conta é obrigatório', 'danger');
        return;
    }
    
    const dados = {
        nome: nome,
        banco: document.getElementById('edit_banco').value.trim() || null,
        agencia: document.getElementById('edit_agencia').value.trim() || null,
        numero_conta: document.getElementById('edit_numero_conta').value.trim() || null,
        tipo: document.getElementById('edit_tipo').value,
        saldo_inicial: parseFloat(document.getElementById('edit_saldo_inicial').value) || 0,
        observacao: document.getElementById('edit_observacao').value.trim() || null
    };
    
    try {
        const result = await api.put('/contas/' + id, dados);
        if (result.success) {
            mostrarNotificacao('✅ Conta atualizada com sucesso!', 'success');
            modalEditarConta.hide();
            await carregarContas();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao atualizar conta', 'danger');
    }
}

// ========== VER EXTRATO ==========
async function verExtrato(contaId) {
    try {
        const movimentacoes = await api.get(`/contas/${contaId}/extrato`);
        const conta = contas.find(c => c.id === contaId);
        
        let html = `
            <h4>Extrato - ${conta.nome}</h4>
            <p>Saldo Atual: R$ ${formatarMoeda(conta.saldo_atual)}</p>
            <hr>
            <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                <table class="table table-sm table-striped">
                    <thead class="sticky-top bg-light">
                        <tr>
                            <th>Data</th>
                            <th>Descrição</th>
                            <th>Tipo</th>
                            <th class="text-end">Valor</th>
                            <th>Categoria</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        if (movimentacoes.length === 0) {
            html += '<tr><td colspan="5" class="text-center">Nenhuma movimentação encontrada</td></tr>';
        } else {
            movimentacoes.forEach(m => {
                const valorClass = m.tipo === 'ENTRADA' ? 'text-success' : 'text-danger';
                html += `
                    <tr>
                        <td>${m.data}</td>
                        <td>${m.descricao}</td>
                        <td>${m.tipo}</td>
                        <td class="text-end ${valorClass}">R$ ${formatarMoeda(m.valor)}</td>
                        <td>${m.categoria || '-'}</td>
                    </tr>
                `;
            });
        }
        
        html += '</tbody></table></div>';
        
        document.getElementById('extratoContent').innerHTML = html;
        modalExtrato.show();
        
    } catch (error) {
        console.error('❌ Erro ao carregar extrato:', error);
        mostrarNotificacao('❌ Erro ao carregar extrato', 'danger');
    }
}

// ========== DELETAR CONTA ==========
async function deletarConta(contaId, nomeConta) {
    if (!confirm(`🗑️ Deseja realmente deletar a conta "${nomeConta}"?`)) return;
    
    try {
        const result = await api.delete('/contas/' + contaId);
        if (result.success) {
            mostrarNotificacao('✅ Conta deletada com sucesso!', 'success');
            await carregarContas();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao deletar conta', 'danger');
    }
}

// Exportar funções
window.abrirModalNovaConta = abrirModalNovaConta;
window.salvarNovaConta = salvarNovaConta;
window.editarConta = editarConta;
window.atualizarConta = atualizarConta;
window.verExtrato = verExtrato;
window.deletarConta = deletarConta;
window.formatarMoeda = formatarMoeda;