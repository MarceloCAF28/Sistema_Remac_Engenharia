// ============================================
// GERENCIAMENTO DE OBRAS
// ============================================

let obras = [];
let formasPagamento = [];
let contas = [];
let modalNovaObra, modalEditarObra, modalVisualizarObra, modalParcelasObra, modalReceberParcela;

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Módulo de obras iniciado');
    
    modalNovaObra = new bootstrap.Modal(document.getElementById('modalNovaObra'));
    modalEditarObra = new bootstrap.Modal(document.getElementById('modalEditarObra'));
    modalVisualizarObra = new bootstrap.Modal(document.getElementById('modalVisualizarObra'));
    modalParcelasObra = new bootstrap.Modal(document.getElementById('modalParcelasObra'));
    modalReceberParcela = new bootstrap.Modal(document.getElementById('modalReceberParcela'));
    
    carregarFormasPagamento();
    carregarContas();
    carregarObras();
});

// ========== CARREGAR OBRAS ==========
async function carregarObras() {
    const tbody = document.getElementById('listaObras');
    try {
        tbody.innerHTML = '<tr><td colspan="16" class="text-center">🔄 Carregando...</td></tr>';
        obras = await api.get('/obras');
        renderizarTabela(obras);
    } catch (error) {
        console.error('❌ Erro ao carregar obras:', error);
        tbody.innerHTML = '<tr><td colspan="16" class="text-center text-danger">❌ Erro ao carregar obras</td></tr>';
    }
}

// ========== CARREGAR FORMAS DE PAGAMENTO ==========
async function carregarFormasPagamento() {
    try {
        formasPagamento = await api.get('/formas-pagamento');
        const options = '<option value="">Selecione...</option>' + 
            formasPagamento.map(f => `<option value="${f.id}">${f.nome}</option>`).join('');
        
        document.getElementById('forma_pagamento_id').innerHTML = options;
        document.getElementById('rec_forma_pagamento_id').innerHTML = '<option value="">Selecione...</option>' + options;
    } catch (error) {
        console.error('❌ Erro ao carregar formas de pagamento:', error);
    }
}

// ========== CARREGAR CONTAS ==========
async function carregarContas() {
    try {
        contas = await api.get('/contas');
        const options = '<option value="">Selecione uma conta...</option>' + 
            contas.map(c => `<option value="${c.id}">${c.nome}</option>`).join('');
        
        document.getElementById('conta_id').innerHTML = options;
        document.getElementById('rec_conta_id').innerHTML = '<option value="">Selecione...</option>' + 
            contas.map(c => `<option value="${c.id}">${c.nome}</option>`).join('');
    } catch (error) {
        console.error('❌ Erro ao carregar contas:', error);
    }
}

// ========== RENDERIZAR TABELA ==========
function renderizarTabela(obrasFiltradas) {
    const tbody = document.getElementById('listaObras');
    if (obrasFiltradas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="16" class="text-center">📭 Nenhuma obra encontrada</td></tr>';
        return;
    }
    
    let html = '';
    obrasFiltradas.forEach(obra => {
        const lucroClass = obra.lucro < 0 ? 'text-danger' : 'text-success';
        const statusClass = obra.status === 'EM ANDAMENTO' ? 'bg-primary' : 
                           (obra.status === 'CONCLUIDA' ? 'bg-success' : 'bg-warning');
        const statusText = obra.status === 'EM ANDAMENTO' ? 'Em Andamento' : 
                          (obra.status === 'CONCLUIDA' ? 'Concluída' : 'Paralisada');
        const parcelasText = obra.quantidade_parcelas > 1 ? obra.quantidade_parcelas + 'x' : 'À vista';
        const contaNome = obra.conta_nome || '-';
        
        html += `
            <tr>
                <td>${obra.id}</td>
                <td><strong>${obra.nome || '-'}</strong></td>
                <td>${obra.cliente || '-'}</td>
                <td>${obra.contrato || '-'}</td>
                <td>${obra.data_inicio || '-'}</td>
                <td><span class="badge ${statusClass}">${statusText}</span></td>
                <td class="text-end">R$ ${formatarMoeda(obra.valor_total_contrato)}</td>
                <td class="text-center">
                    <span class="badge bg-info">${parcelasText}</span>
                </td>
                <td class="text-end">R$ ${formatarMoeda(obra.total_receitas)}</td>
                <td class="text-end">R$ ${formatarMoeda(obra.total_despesas)}</td>
                <td class="text-end ${lucroClass}">R$ ${formatarMoeda(obra.lucro)}</td>
                <td class="text-end">${obra.margem_lucro}%</td>
                <td class="text-center">
                    <span class="badge bg-info">${obra.qtd_itens_abc || 0} itens</span>
                </td>
                <td class="text-center">
                    <span class="badge bg-warning">R$ ${formatarMoeda(obra.total_a_receber)}</span>
                </td>
                <td>${contaNome}</td>
                <td>
                    <button class="btn btn-sm btn-outline-info" onclick="visualizarObra(${obra.id})" title="Visualizar">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-warning" onclick="verParcelasObra(${obra.id})" title="Ver Parcelas">
                        <i class="bi bi-credit-card"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-primary" onclick="editarObra(${obra.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deletarObra(${obra.id}, '${obra.nome.replace(/'/g, "\\'")}')" title="Deletar">
                        <i class="bi bi-trash"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-warning" onclick="window.location.href='abc.html?obra=${obra.id}'" title="Ver Curva ABC">
                        <i class="bi bi-bar-chart-steps"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

// ========== APLICAR FILTROS ==========
function aplicarFiltros() {
    const status = document.getElementById('filtroStatus').value;
    const busca = document.getElementById('filtroBusca').value.toLowerCase();
    
    let filtradas = obras;
    if (status !== 'todos') filtradas = filtradas.filter(obra => obra.status === status);
    if (busca) filtradas = filtradas.filter(obra => 
        (obra.nome && obra.nome.toLowerCase().includes(busca)) ||
        (obra.cliente && obra.cliente.toLowerCase().includes(busca)) ||
        (obra.contrato && obra.contrato.toLowerCase().includes(busca))
    );
    renderizarTabela(filtradas);
}

// ========== CALCULAR VALOR DA PARCELA ==========
function calcularValorParcelaObra() {
    const valorTotal = parseFloat(document.getElementById('valor_total_contrato').value) || 0;
    const quantidadeParcelas = parseInt(document.getElementById('quantidade_parcelas').value) || 1;
    
    const divValorParcela = document.getElementById('div_valor_parcela_obra');
    const avisoDiv = document.getElementById('div_aviso_parcelamento_obra');
    const aviso = document.getElementById('aviso_parcelamento_obra');
    const dataPrimeiraParcela = document.getElementById('data_primeira_parcela');
    
    if (quantidadeParcelas > 1 && valorTotal > 0) {
        const valorParcela = valorTotal / quantidadeParcelas;
        if (document.getElementById('valor_parcela_obra')) {
            document.getElementById('valor_parcela_obra').value = `R$ ${formatarMoeda(valorParcela)} (${quantidadeParcelas}x)`;
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

// ========== NOVA OBRA ==========
function abrirModalNovaObra() {
    document.getElementById('nome').value = '';
    document.getElementById('cliente').value = '';
    document.getElementById('contrato').value = '';
    document.getElementById('data_inicio').value = '';
    document.getElementById('status').value = 'EM ANDAMENTO';
    document.getElementById('descricao').value = '';
    document.getElementById('valor_total_contrato').value = '0';
    document.getElementById('quantidade_parcelas').value = '1';
    document.getElementById('forma_pagamento_id').value = '';
    document.getElementById('conta_id').value = '';
    document.getElementById('data_primeira_parcela').value = '';
    document.getElementById('observacao_parcelas').value = '';
    document.getElementById('div_valor_parcela_obra').style.display = 'none';
    document.getElementById('div_aviso_parcelamento_obra').style.display = 'none';
    
    modalNovaObra.show();
}

async function salvarNovaObra() {
    const nome = document.getElementById('nome').value.trim();
    const cliente = document.getElementById('cliente').value.trim();
    
    if (!nome) {
        mostrarNotificacao('❌ Nome da obra é obrigatório', 'danger');
        return;
    }
    if (!cliente) {
        mostrarNotificacao('❌ Cliente é obrigatório', 'danger');
        return;
    }
    
    const quantidadeParcelas = parseInt(document.getElementById('quantidade_parcelas').value) || 1;
    const dataPrimeiraParcela = document.getElementById('data_primeira_parcela').value;
    
    // Validar parcelamento
    if (quantidadeParcelas > 1 && !dataPrimeiraParcela) {
        mostrarNotificacao('❌ Para parcelamento, informe a data da primeira parcela', 'danger');
        return;
    }
    
    const data = {
        nome: nome,
        cliente: cliente,
        contrato: document.getElementById('contrato').value.trim() || null,
        data_inicio: document.getElementById('data_inicio').value || null,
        status: document.getElementById('status').value,
        descricao: document.getElementById('descricao').value.trim() || null,
        valor_total_contrato: parseFloat(document.getElementById('valor_total_contrato').value) || 0,
        quantidade_parcelas: quantidadeParcelas,
        forma_pagamento_id: document.getElementById('forma_pagamento_id').value || null,
        conta_id: document.getElementById('conta_id').value || null,
        data_primeira_parcela: dataPrimeiraParcela || null,
        observacao_parcelas: document.getElementById('observacao_parcelas').value.trim() || null
    };
    
    try {
        const result = await api.post('/obras', data);
        if (result.success) {
            const msgParcelamento = quantidadeParcelas > 1 ? ` (parcelado em ${quantidadeParcelas}x)` : '';
            mostrarNotificacao(`✅ Obra criada com sucesso${msgParcelamento}!`, 'success');
            modalNovaObra.hide();
            await carregarObras();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao criar obra', 'danger');
    }
}

// ========== EDITAR OBRA ==========
async function editarObra(obraId) {
    try {
        const obra = obras.find(o => o.id === obraId);
        if (!obra) return;
        
        document.getElementById('edit_id').value = obra.id;
        document.getElementById('edit_nome').value = obra.nome || '';
        document.getElementById('edit_cliente').value = obra.cliente || '';
        document.getElementById('edit_contrato').value = obra.contrato || '';
        
        if (obra.data_inicio) {
            const partes = obra.data_inicio.split('/');
            document.getElementById('edit_data_inicio').value = `${partes[2]}-${partes[1]}-${partes[0]}`;
        }
        if (obra.data_fim) {
            const partes = obra.data_fim.split('/');
            document.getElementById('edit_data_fim').value = `${partes[2]}-${partes[1]}-${partes[0]}`;
        }
        
        document.getElementById('edit_status').value = obra.status || 'EM ANDAMENTO';
        document.getElementById('edit_descricao').value = obra.descricao || '';
        document.getElementById('edit_valor_total_contrato').value = obra.valor_total_contrato || 0;
        document.getElementById('edit_quantidade_parcelas').value = obra.quantidade_parcelas || 1;
        
        modalEditarObra.show();
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao carregar dados da obra', 'danger');
    }
}

async function atualizarObra() {
    const id = document.getElementById('edit_id').value;
    const nome = document.getElementById('edit_nome').value.trim();
    const cliente = document.getElementById('edit_cliente').value.trim();
    
    if (!nome || !cliente) {
        mostrarNotificacao('❌ Nome e Cliente são obrigatórios', 'danger');
        return;
    }
    
    const data = {
        nome: nome,
        cliente: cliente,
        contrato: document.getElementById('edit_contrato').value.trim() || null,
        data_inicio: document.getElementById('edit_data_inicio').value || null,
        data_fim: document.getElementById('edit_data_fim').value || null,
        status: document.getElementById('edit_status').value,
        descricao: document.getElementById('edit_descricao').value.trim() || null,
        valor_total_contrato: parseFloat(document.getElementById('edit_valor_total_contrato').value) || 0
    };
    
    try {
        const result = await api.put('/obras/' + id, data);
        if (result.success) {
            mostrarNotificacao('✅ Obra atualizada com sucesso!', 'success');
            modalEditarObra.hide();
            await carregarObras();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao atualizar obra', 'danger');
    }
}

// ========== VER PARCELAS DA OBRA ==========
async function verParcelasObra(obraId) {
    try {
        const parcelas = await api.get(`/parcelas/obra/${obraId}`);
        const obra = obras.find(o => o.id === obraId);
        
        if (!parcelas || parcelas.length === 0) {
            document.getElementById('listaParcelasObra').innerHTML = '<p class="text-center">Nenhuma parcela encontrada para esta obra</p>';
            modalParcelasObra.show();
            return;
        }
        
        // Calcular totais
        const totalRecebido = parcelas.reduce((sum, p) => sum + p.valor_recebido, 0);
        const totalAReceber = parcelas.reduce((sum, p) => sum + (p.valor - p.valor_recebido), 0);
        
        let html = `
            <h6>Obra: ${obra.nome}</h6>
            <p><strong>Valor Total do Contrato:</strong> R$ ${formatarMoeda(obra.valor_total_contrato)}</p>
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
                            `<button class="btn btn-sm btn-success" onclick="abrirModalReceberParcelaObra(${p.id}, ${p.valor}, ${saldo})">
                                <i class="bi bi-cash"></i> Receber
                            </button>` : 
                            '<span class="text-success"><i class="bi bi-check-circle"></i> Pago</span>'}
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
        document.getElementById('listaParcelasObra').innerHTML = html;
        modalParcelasObra.show();
    } catch (error) {
        console.error('❌ Erro ao carregar parcelas da obra:', error);
        mostrarNotificacao('❌ Erro ao carregar parcelas da obra', 'danger');
    }
}

// ========== ABRIR MODAL RECEBER PARCELA ==========
function abrirModalReceberParcelaObra(parcelaId, valorParcela, saldo) {
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
async function confirmarRecebimentoParcelaObra() {
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
        const result = await api.post(`/parcelas/obra/${parcelaId}/receber`, data);
        if (result.success) {
            mostrarNotificacao('✅ Recebimento registrado com sucesso!', 'success');
            modalReceberParcela.hide();
            await carregarObras();
            
            // Recarregar parcelas
            const obraId = obras.find(o => o.id === parseInt(document.getElementById('rec_parcela_id').value))?.id;
            if (obraId) {
                modalParcelasObra.hide();
                setTimeout(() => verParcelasObra(obraId), 300);
            }
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao registrar recebimento', 'danger');
    }
}

// ========== VISUALIZAR OBRA ==========
async function visualizarObra(obraId) {
    try {
        const response = await api.get('/obras/' + obraId);
        const obra = response.resumo;
        
        let html = `
            <div class="row">
                <div class="col-md-8">
                    <h4>${obra.nome}</h4>
                    <p><strong>Cliente:</strong> ${obra.cliente}</p>
                    <p><strong>Contrato:</strong> ${obra.contrato || '-'}</p>
                    <p><strong>Período:</strong> ${obra.data_inicio || '?'} até ${obra.data_fim || '?'}</p>
                    <p><strong>Status:</strong> <span class="badge bg-${obra.status === 'EM ANDAMENTO' ? 'primary' : (obra.status === 'CONCLUIDA' ? 'success' : 'warning')}">${obra.status}</span></p>
                    <p><strong>Valor do Contrato:</strong> R$ ${formatarMoeda(obra.valor_total_contrato)}</p>
                    <p><strong>Parcelas:</strong> ${obra.quantidade_parcelas > 1 ? obra.quantidade_parcelas + 'x' : 'À vista'}</p>
                    <p><strong>Forma de Pagamento:</strong> ${obra.forma_pagamento_nome || '-'}</p>
                    <p><strong>Conta de Recebimento:</strong> ${obra.conta_nome || '-'}</p>
                    <p><strong>Total a Receber:</strong> R$ ${formatarMoeda(obra.total_a_receber)}</p>
                    <p><strong>Descrição:</strong> ${obra.descricao || '-'}</p>
                </div>
                <div class="col-md-4">
                    <div class="card bg-primary text-white mb-3">
                        <div class="card-body">
                            <h6>Total Receitas</h6>
                            <h3>R$ ${formatarMoeda(obra.total_receitas)}</h3>
                        </div>
                    </div>
                    <div class="card bg-danger text-white mb-3">
                        <div class="card-body">
                            <h6>Total Despesas</h6>
                            <h3>R$ ${formatarMoeda(obra.total_despesas)}</h3>
                        </div>
                    </div>
                    <div class="card bg-${obra.lucro >= 0 ? 'success' : 'secondary'} text-white">
                        <div class="card-body">
                            <h6>Lucro / Margem</h6>
                            <h3>R$ ${formatarMoeda(obra.lucro)}</h3>
                            <small>Margem: ${obra.margem_lucro}%</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <ul class="nav nav-tabs mt-4">
                <li class="nav-item"><a class="nav-link active" data-bs-toggle="tab" href="#receitas">Receitas</a></li>
                <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#despesas">Despesas</a></li>
                <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#materiais">Materiais</a></li>
                <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#mao-obra">Mão de Obra</a></li>
                <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#parcelas">Parcelas do Contrato</a></li>
                <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#abc">Curva ABC</a></li>
            </ul>
            
            <div class="tab-content mt-3">
                <div class="tab-pane fade show active" id="receitas">${renderizarTabelaReceitas(response.receitas)}</div>
                <div class="tab-pane fade" id="despesas">${renderizarTabelaDespesas(response.despesas)}</div>
                <div class="tab-pane fade" id="materiais">${renderizarTabelaMateriais(response.materiais)}</div>
                <div class="tab-pane fade" id="mao-obra">${renderizarTabelaMaoObra(response.mao_obra)}</div>
                <div class="tab-pane fade" id="parcelas">
                    <div class="text-center mb-3">
                        <button class="btn btn-warning" onclick="verParcelasObra(${obra.id})">
                            <i class="bi bi-credit-card"></i> Ver Parcelas Detalhadas
                        </button>
                    </div>
                </div>
                <div class="tab-pane fade" id="abc">
                    <div class="text-center">
                        <button class="btn btn-warning" onclick="window.location.href='abc.html?obra=${obra.id}'">
                            <i class="bi bi-bar-chart-steps"></i> Ver Curva ABC Completa
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('detalhesObra').innerHTML = html;
        modalVisualizarObra.show();
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao carregar detalhes da obra', 'danger');
    }
}

// ========== RENDERIZAR TABELAS ==========
function renderizarTabelaReceitas(receitas) {
    if (!receitas || !receitas.length) return '<p class="text-center">Nenhuma receita cadastrada</p>';
    let html = '<table class="table table-sm table-striped"><thead><tr><th>Data</th><th>Descrição</th><th>Forma Pagto</th><th class="text-end">Previsto</th><th class="text-end">Recebido</th><th>Status</th></tr></thead><tbody>';
    receitas.forEach(r => {
        const statusClass = r.status === 'RECEBIDO' ? 'bg-success' : (r.status === 'PARCIAL' ? 'bg-warning' : 'bg-secondary');
        html += `<tr><td>${r.data}</td><td>${r.descricao}</td><td>${r.forma_pagamento_nome || '-'}</td><td class="text-end">R$ ${formatarMoeda(r.valor_total)}</td><td class="text-end">R$ ${formatarMoeda(r.valor_recebido)}</td><td><span class="badge ${statusClass}">${r.status}</span></td></tr>`;
    });
    return html + '</tbody></table>';
}

function renderizarTabelaDespesas(despesas) {
    if (!despesas || !despesas.length) return '<p class="text-center">Nenhuma despesa cadastrada</p>';
    let html = '<table class="table table-sm table-striped"><thead><tr><th>Data</th><th>Descrição</th><th>Categoria</th><th class="text-end">Previsto</th><th class="text-end">Pago</th><th>Status</th></tr></thead><tbody>';
    despesas.forEach(d => {
        const statusClass = d.status === 'PAGO' ? 'bg-success' : (d.status === 'PARCIAL' ? 'bg-warning' : 'bg-secondary');
        html += `<tr><td>${d.data}</td><td>${d.descricao}</td><td>${d.categoria || '-'}</td><td class="text-end">R$ ${formatarMoeda(d.valor_total)}</td><td class="text-end">R$ ${formatarMoeda(d.valor_pago)}</td><td><span class="badge ${statusClass}">${d.status}</span></td></tr>`;
    });
    return html + '</tbody></table>';
}

function renderizarTabelaMateriais(materiais) {
    if (!materiais || !materiais.length) return '<p class="text-center">Nenhum material cadastrado</p>';
    let html = '<table class="table table-sm table-striped"><thead><tr><th>Data</th><th>Descrição</th><th>Item ABC</th><th class="text-end">Total</th><th class="text-end">Pago</th><th>Status</th></tr></thead><tbody>';
    materiais.forEach(m => {
        const statusClass = m.status === 'PAGO' ? 'bg-success' : (m.status === 'PARCIAL' ? 'bg-warning' : 'bg-secondary');
        html += `<tr><td>${m.data}</td><td>${m.descricao}</td><td>${m.item_abc_codigo || '-'}</td><td class="text-end">R$ ${formatarMoeda(m.valor_total)}</td><td class="text-end">R$ ${formatarMoeda(m.valor_pago)}</td><td><span class="badge ${statusClass}">${m.status}</span></td></tr>`;
    });
    return html + '</tbody></table>';
}

function renderizarTabelaMaoObra(maoObra) {
    if (!maoObra || !maoObra.length) return '<p class="text-center">Nenhuma mão de obra cadastrada</p>';
    let html = '<table class="table table-sm table-striped"><thead><tr><th>Data</th><th>Descrição</th><th>Item ABC</th><th class="text-end">Total</th><th class="text-end">Pago</th><th>Status</th></tr></thead><tbody>';
    maoObra.forEach(m => {
        const statusClass = m.status === 'PAGO' ? 'bg-success' : (m.status === 'PARCIAL' ? 'bg-warning' : 'bg-secondary');
        html += `<tr><td>${m.data}</td><td>${m.descricao}</td><td>${m.item_abc_codigo || '-'}</td><td class="text-end">R$ ${formatarMoeda(m.valor_total)}</td><td class="text-end">R$ ${formatarMoeda(m.valor_pago)}</td><td><span class="badge ${statusClass}">${m.status}</span></td></tr>`;
    });
    return html + '</tbody></table>';
}

// ========== DELETAR OBRA ==========
async function deletarObra(obraId, nomeObra) {
    if (!confirm(`🗑️ Deseja realmente deletar a obra "${nomeObra}"?`)) return;
    try {
        const result = await api.delete('/obras/' + obraId);
        if (result.success) {
            mostrarNotificacao('✅ Obra deletada com sucesso!', 'success');
            await carregarObras();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao deletar obra', 'danger');
    }
}

// ========== UTILITÁRIOS ==========
function formatarMoeda(valor) {
    if (valor === undefined || valor === null) return '0,00';
    return valor.toFixed(2).replace('.', ',');
}

function mostrarNotificacao(mensagem, tipo = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${tipo} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '9999';
    notification.style.maxWidth = '400px';
    notification.innerHTML = `
        ${mensagem}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}

// Exportar funções
window.abrirModalNovaObra = abrirModalNovaObra;
window.salvarNovaObra = salvarNovaObra;
window.editarObra = editarObra;
window.atualizarObra = atualizarObra;
window.visualizarObra = visualizarObra;
window.verParcelasObra = verParcelasObra;
window.abrirModalReceberParcelaObra = abrirModalReceberParcelaObra;
window.confirmarRecebimentoParcelaObra = confirmarRecebimentoParcelaObra;
window.deletarObra = deletarObra;
window.aplicarFiltros = aplicarFiltros;
window.calcularValorParcelaObra = calcularValorParcelaObra;
window.formatarMoeda = formatarMoeda;
window.mostrarNotificacao = mostrarNotificacao;