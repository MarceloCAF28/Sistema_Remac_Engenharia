// ============================================
// GERENCIAMENTO DE RECEITAS
// ============================================

let receitas = [];
let obras = [];
let contas = [];
let formasPagamento = [];
let modalNovaReceita, modalVisualizarParcelas, modalReceberParcela;

document.addEventListener('DOMContentLoaded', function() {
    console.log('💰 Módulo de receitas iniciado');
    
    modalNovaReceita = new bootstrap.Modal(document.getElementById('modalNovaReceita'));
    modalVisualizarParcelas = new bootstrap.Modal(document.getElementById('modalVisualizarParcelas'));
    modalReceberParcela = new bootstrap.Modal(document.getElementById('modalReceberParcela'));
    
    carregarFormasPagamento();
    carregarObras();
    carregarContas();
    carregarReceitas();
    document.getElementById('data').value = new Date().toISOString().split('T')[0];
});

// ========== CARREGAR OBRAS ==========
async function carregarObras() {
    try {
        obras = await api.get('/obras');
        const options = '<option value="">Selecione...</option>' + obras.map(o => `<option value="${o.id}">${o.nome}</option>`).join('');
        document.getElementById('obra_id').innerHTML = options;
        document.getElementById('filtroObra').innerHTML = '<option value="">Todas as Obras</option>' + obras.map(o => `<option value="${o.id}">${o.nome}</option>`).join('');
    } catch (error) {
        console.error('❌ Erro ao carregar obras:', error);
    }
}

// ========== CARREGAR CONTAS ==========
async function carregarContas() {
    try {
        contas = await api.get('/contas');
        const options = '<option value="">Selecione uma conta...</option>' + contas.map(c => `<option value="${c.id}">${c.nome}</option>`).join('');
        document.getElementById('conta_id').innerHTML = options;
        document.getElementById('rec_conta_id').innerHTML = '<option value="">Selecione...</option>' + contas.map(c => `<option value="${c.id}">${c.nome}</option>`).join('');
    } catch (error) {
        console.error('❌ Erro ao carregar contas:', error);
    }
}

// ========== CARREGAR FORMAS DE PAGAMENTO ==========
async function carregarFormasPagamento() {
    try {
        formasPagamento = await api.get('/formas-pagamento');
        const options = '<option value="">Selecione...</option>' + 
            formasPagamento.map(f => `<option value="${f.id}">${f.nome}</option>`).join('');
        document.getElementById('forma_pagamento_id').innerHTML = options;
        document.getElementById('rec_forma_pagamento_id').innerHTML = options;
    } catch (error) {
        console.error('❌ Erro ao carregar formas de pagamento:', error);
    }
}

// ========== CARREGAR RECEITAS ==========
async function carregarReceitas() {
    const tbody = document.getElementById('listaReceitas');
    try {
        tbody.innerHTML = '<tr><td colspan="12" class="text-center">🔄 Carregando...</td></tr>';
        
        const params = [];
        if (document.getElementById('filtroObra').value) params.push(`obra_id=${document.getElementById('filtroObra').value}`);
        if (document.getElementById('filtroMes').value) params.push(`mes=${document.getElementById('filtroMes').value}`);
        if (document.getElementById('filtroAno').value) params.push(`ano=${document.getElementById('filtroAno').value}`);
        
        const url = '/receitas' + (params.length ? '?' + params.join('&') : '');
        receitas = await api.get(url);
        
        const status = document.getElementById('filtroStatus').value;
        let filtradas = receitas;
        if (status) filtradas = receitas.filter(r => r.status === status);
        
        renderizarTabela(filtradas);
        atualizarResumo(filtradas);
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="12" class="text-center text-danger">❌ Erro ao carregar receitas</td></tr>';
    }
}

// ========== RENDERIZAR TABELA ==========
function renderizarTabela(receitasFiltradas) {
    const tbody = document.getElementById('listaReceitas');
    if (!receitasFiltradas.length) {
        tbody.innerHTML = '<tr><td colspan="12" class="text-center">📭 Nenhuma receita encontrada</td></tr>';
        return;
    }
    
    let html = '';
    receitasFiltradas.forEach(r => {
        const statusClass = r.status === 'RECEBIDO' ? 'bg-success' : (r.status === 'PARCIAL' ? 'bg-warning' : 'bg-secondary');
        const parcelasText = r.quantidade_parcelas > 1 ? r.quantidade_parcelas + 'x' : 'À vista';
        const formaPagto = r.forma_pagamento_nome || '-';
        
        html += `
            <tr>
                <td>${r.id}</td>
                <td>${r.data_br || r.data}</td>
                <td>${r.obra_nome || '-'}</td>
                <td>${r.descricao}</td>
                <td>${r.tipo || '-'}</td>
                <td>${formaPagto}</td>
                <td class="text-center">${parcelasText}</td>
                <td class="text-end">R$ ${formatarMoeda(r.valor_total)}</td>
                <td class="text-end">R$ ${formatarMoeda(r.valor_recebido)}</td>
                <td><span class="badge ${statusClass}">${r.status}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-warning" onclick="verParcelasReceita(${r.id})" title="Ver Parcelas">
                        <i class="bi bi-credit-card"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deletarReceita(${r.id}, '${r.descricao.replace(/'/g, "\\'")}')" title="Deletar">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

// ========== ATUALIZAR RESUMO ==========
function atualizarResumo(receitasFiltradas) {
    let totalPrevisto = 0, totalRecebido = 0;
    receitasFiltradas.forEach(r => {
        totalPrevisto += r.valor_total || 0;
        totalRecebido += r.valor_recebido || 0;
    });
    document.getElementById('totalPrevisto').innerHTML = `R$ ${formatarMoeda(totalPrevisto)}`;
    document.getElementById('totalRecebido').innerHTML = `R$ ${formatarMoeda(totalRecebido)}`;
    document.getElementById('totalAReceber').innerHTML = `R$ ${formatarMoeda(totalPrevisto - totalRecebido)}`;
}

// ========== APLICAR FILTROS ==========
function aplicarFiltros() { carregarReceitas(); }
function limparFiltros() {
    document.getElementById('filtroObra').value = '';
    document.getElementById('filtroMes').value = '';
    document.getElementById('filtroAno').value = '';
    document.getElementById('filtroStatus').value = '';
    carregarReceitas();
}

// ========== CALCULAR VALOR DA PARCELA ==========
function calcularValorParcelaReceita() {
    const valorTotal = parseFloat(document.getElementById('valor_total').value) || 0;
    const quantidadeParcelas = parseInt(document.getElementById('quantidade_parcelas').value) || 1;
    
    const divValorParcela = document.getElementById('div_valor_parcela');
    const avisoDiv = document.getElementById('div_aviso_parcelamento_receita');
    const aviso = document.getElementById('aviso_parcelamento_receita');
    const dataPrimeiraParcela = document.getElementById('data_primeira_parcela');
    
    if (quantidadeParcelas > 1 && valorTotal > 0) {
        const valorParcela = valorTotal / quantidadeParcelas;
        if (document.getElementById('valor_parcela')) {
            document.getElementById('valor_parcela').value = `R$ ${formatarMoeda(valorParcela)} (${quantidadeParcelas}x)`;
        }
        if (divValorParcela) {
            divValorParcela.style.display = 'block';
        }
        if (avisoDiv && aviso) {
            aviso.innerHTML = `Serão geradas ${quantidadeParcelas} parcelas de R$ ${formatarMoeda(valorParcela)} com vencimento mensal a partir da data informada.`;
            avisoDiv.style.display = 'block';
        }
        if (dataPrimeiraParcela) {
            dataPrimeiraParcela.required = true;
        }
    } else {
        if (divValorParcela) {
            divValorParcela.style.display = 'none';
        }
        if (avisoDiv) {
            avisoDiv.style.display = 'none';
        }
        if (dataPrimeiraParcela) {
            dataPrimeiraParcela.required = false;
        }
    }
}

// ========== NOVA RECEITA ==========
function abrirModalNovaReceita() {
    document.getElementById('obra_id').value = '';
    document.getElementById('data').value = new Date().toISOString().split('T')[0];
    document.getElementById('descricao').value = '';
    document.getElementById('tipo').value = 'ENTRADA';
    document.getElementById('centro_custo').value = '';
    document.getElementById('valor_total').value = '';
    document.getElementById('quantidade_parcelas').value = '1';
    document.getElementById('forma_pagamento_id').value = '';
    document.getElementById('conta_id').value = '';
    document.getElementById('data_primeira_parcela').value = '';
    document.getElementById('observacao').value = '';
    
    document.getElementById('div_valor_parcela').style.display = 'none';
    document.getElementById('div_aviso_parcelamento_receita').style.display = 'none';
    
    modalNovaReceita.show();
}

async function salvarNovaReceita() {
    const obraId = document.getElementById('obra_id').value;
    const descricao = document.getElementById('descricao').value.trim();
    const valorTotal = parseFloat(document.getElementById('valor_total').value);
    
    if (!obraId) {
        mostrarNotificacao('❌ Selecione uma obra', 'danger');
        return;
    }
    if (!descricao) {
        mostrarNotificacao('❌ Descrição é obrigatória', 'danger');
        return;
    }
    if (!valorTotal || valorTotal <= 0) {
        mostrarNotificacao('❌ Valor total deve ser maior que zero', 'danger');
        return;
    }
    
    const quantidadeParcelas = parseInt(document.getElementById('quantidade_parcelas').value) || 1;
    const dataPrimeiraParcela = document.getElementById('data_primeira_parcela').value;
    
    // Validar parcelamento
    if (quantidadeParcelas > 1 && !dataPrimeiraParcela) {
        mostrarNotificacao('❌ Para parcelamento, informe a data da primeira parcela', 'danger');
        return;
    }
    
    const dados = {
        obra_id: parseInt(obraId),
        data: document.getElementById('data').value,
        descricao: descricao,
        tipo: document.getElementById('tipo').value,
        centro_custo: document.getElementById('centro_custo').value.trim() || null,
        valor_total: valorTotal,
        quantidade_parcelas: quantidadeParcelas,
        forma_pagamento_id: document.getElementById('forma_pagamento_id').value || null,
        conta_id: document.getElementById('conta_id').value || null,
        data_primeira_parcela: dataPrimeiraParcela || null,
        observacao: document.getElementById('observacao').value.trim() || null
    };
    
    try {
        const result = await api.post('/receitas', dados);
        if (result.success) {
            const msgParcelamento = quantidadeParcelas > 1 ? ` (parcelado em ${quantidadeParcelas}x)` : '';
            mostrarNotificacao(`✅ Receita cadastrada com sucesso${msgParcelamento}!`, 'success');
            modalNovaReceita.hide();
            await carregarReceitas();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao cadastrar receita', 'danger');
    }
}

// ========== VER PARCELAS DA RECEITA ==========
async function verParcelasReceita(receitaId) {
    try {
        const parcelas = await api.get(`/parcelas/receita/${receitaId}`);
        const receita = receitas.find(r => r.id === receitaId);
        
        if (!parcelas || parcelas.length === 0) {
            document.getElementById('listaParcelas').innerHTML = '<p class="text-center">Nenhuma parcela encontrada</p>';
            modalVisualizarParcelas.show();
            return;
        }
        
        // Calcular totais
        const totalRecebido = parcelas.reduce((sum, p) => sum + p.valor_recebido, 0);
        const totalAReceber = parcelas.reduce((sum, p) => sum + (p.valor - p.valor_recebido), 0);
        
        let html = `
            <h6>Receita: ${receita.descricao}</h6>
            <p><strong>Valor Total:</strong> R$ ${formatarMoeda(receita.valor_total)}</p>
            <p><strong>Total Recebido:</strong> R$ ${formatarMoeda(totalRecebido)}</p>
            <p><strong>Total a Receber:</strong> R$ ${formatarMoeda(totalAReceber)}</p>
            <hr>
            <div class="table-responsive">
                <table class="table table-sm table-striped">
                    <thead>
                        <tr>
                            <th>Parcela</th>
                            <th>Vencimento</th>
                            <th>Valor</th>
                            <th>Recebido</th>
                            <th>Saldo</th>
                            <th>Status</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        parcelas.forEach(p => {
            const statusClass = p.status === 'RECEBIDO' ? 'success' : 
                               (p.status === 'ATRASADO' ? 'danger' : 
                                (p.status === 'PARCIAL' ? 'warning' : 'warning'));
            const statusText = p.status === 'RECEBIDO' ? 'Recebido' : 
                              (p.status === 'ATRASADO' ? `Atrasado (${p.dias_atraso}d)` : 
                               (p.status === 'PARCIAL' ? 'Parcial' : 'Pendente'));
            const saldo = p.valor - p.valor_recebido;
            
            html += `
                <tr>
                    <td>${p.numero_parcela}/${p.total_parcelas}</td>
                    <td>${p.data_vencimento}</td>
                    <td class="text-end">R$ ${formatarMoeda(p.valor)}</td>
                    <td class="text-end">R$ ${formatarMoeda(p.valor_recebido)}</td>
                    <td class="text-end">R$ ${formatarMoeda(saldo)}</td>
                    <td><span class="badge bg-${statusClass}">${statusText}</span></td>
                    <td>
                        ${p.status !== 'RECEBIDO' ? 
                            `<button class="btn btn-sm btn-success" onclick="abrirModalReceberParcela(${p.id}, ${p.valor}, ${saldo})">
                                <i class="bi bi-cash"></i> Receber
                            </button>` : 
                            '<span class="text-success"><i class="bi bi-check-circle"></i> Pago</span>'}
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        document.getElementById('listaParcelas').innerHTML = html;
        modalVisualizarParcelas.show();
    } catch (error) {
        console.error('❌ Erro ao carregar parcelas:', error);
        mostrarNotificacao('❌ Erro ao carregar parcelas', 'danger');
    }
}

// ========== ABRIR MODAL RECEBER PARCELA ==========
function abrirModalReceberParcela(parcelaId, valorParcela, saldo) {
    document.getElementById('rec_parcela_id').value = parcelaId;
    document.getElementById('rec_valor_parcela').value = `R$ ${formatarMoeda(valorParcela)}`;
    document.getElementById('rec_valor_recebido').value = saldo.toFixed(2);
    document.getElementById('rec_data_recebimento').value = new Date().toISOString().split('T')[0];
    document.getElementById('rec_conta_id').value = '';
    document.getElementById('rec_forma_pagamento_id').value = '';
    document.getElementById('rec_observacao').value = '';
    
    modalReceberParcela.show();
}

// ========== CONFIRMAR RECEBIMENTO DE PARCELA ==========
async function confirmarRecebimentoParcela() {
    const parcelaId = document.getElementById('rec_parcela_id').value;
    const valorRecebido = parseFloat(document.getElementById('rec_valor_recebido').value);
    const dataRecebimento = document.getElementById('rec_data_recebimento').value;
    const contaId = document.getElementById('rec_conta_id').value;
    
    if (!valorRecebido || valorRecebido <= 0) {
        mostrarNotificacao('❌ Informe o valor recebido', 'danger');
        return;
    }
    
    if (!dataRecebimento) {
        mostrarNotificacao('❌ Informe a data de recebimento', 'danger');
        return;
    }
    
    if (!contaId) {
        mostrarNotificacao('❌ Selecione a conta de recebimento', 'danger');
        return;
    }
    
    const data = {
        valor_recebido: valorRecebido,
        data_recebimento: dataRecebimento,
        conta_id: parseInt(contaId),
        forma_pagamento_id: document.getElementById('rec_forma_pagamento_id').value || null,
        observacao: document.getElementById('rec_observacao').value.trim() || null
    };
    
    try {
        const result = await api.post(`/parcelas/receita/${parcelaId}/receber`, data);
        if (result.success) {
            mostrarNotificacao('✅ Recebimento registrado com sucesso!', 'success');
            modalReceberParcela.hide();
            await carregarReceitas();
            
            // Recarregar parcelas
            modalVisualizarParcelas.hide();
            setTimeout(() => {
                const receitaId = receitas.find(r => r.id === parseInt(document.getElementById('rec_parcela_id').value))?.id;
                if (receitaId) verParcelasReceita(receitaId);
            }, 300);
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao registrar recebimento', 'danger');
    }
}

// ========== DELETAR RECEITA ==========
async function deletarReceita(receitaId, descricao) {
    if (!confirm(`🗑️ Deseja realmente deletar a receita "${descricao}"?`)) return;
    try {
        const result = await api.delete('/receitas/' + receitaId);
        if (result.success) {
            mostrarNotificacao('✅ Receita deletada com sucesso!', 'success');
            await carregarReceitas();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao deletar receita', 'danger');
    }
}

// Exportar funções
window.abrirModalNovaReceita = abrirModalNovaReceita;
window.salvarNovaReceita = salvarNovaReceita;
window.verParcelasReceita = verParcelasReceita;
window.abrirModalReceberParcela = abrirModalReceberParcela;
window.confirmarRecebimentoParcela = confirmarRecebimentoParcela;
window.deletarReceita = deletarReceita;
window.aplicarFiltros = aplicarFiltros;
window.limparFiltros = limparFiltros;
window.calcularValorParcelaReceita = calcularValorParcelaReceita;