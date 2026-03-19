// ============================================
// GERENCIAMENTO DE DESPESAS - VERSÃO COMPLETA
// ============================================

let despesas = [];
let materiais = [];
let maoObra = [];
let obras = [];
let categorias = [];
let contas = [];
let formasPagamento = [];
let itensABC = [];

let modalNovaDespesaMaterial, modalNovaDespesaMaoObra, modalNovaDespesaOutros;
let modalVisualizarDespesa, modalVisualizarParcelasDespesa, modalPagarParcela;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    console.log('💰 Módulo de despesas iniciado - Versão completa');
    
    if (typeof bootstrap === 'undefined') {
        console.error('❌ Bootstrap não carregado!');
        alert('Erro: Bootstrap não carregado. Recarregue a página.');
        return;
    }
    
    try {
        const modalMaterial = document.getElementById('modalNovaDespesaMaterial');
        const modalMaoObra = document.getElementById('modalNovaDespesaMaoObra');
        const modalOutros = document.getElementById('modalNovaDespesaOutros');
        const modalVisualizar = document.getElementById('modalVisualizarDespesa');
        const modalParcelas = document.getElementById('modalVisualizarParcelasDespesa');
        const modalPagar = document.getElementById('modalPagarParcela');
        
        if (modalMaterial) modalNovaDespesaMaterial = new bootstrap.Modal(modalMaterial);
        if (modalMaoObra) modalNovaDespesaMaoObra = new bootstrap.Modal(modalMaoObra);
        if (modalOutros) modalNovaDespesaOutros = new bootstrap.Modal(modalOutros);
        if (modalVisualizar) modalVisualizarDespesa = new bootstrap.Modal(modalVisualizar);
        if (modalParcelas) modalVisualizarParcelasDespesa = new bootstrap.Modal(modalParcelas);
        if (modalPagar) modalPagarParcela = new bootstrap.Modal(modalPagar);
        
        console.log('✅ Modais inicializados');
    } catch (error) {
        console.error('❌ Erro ao inicializar modais:', error);
    }
    
    carregarFormasPagamento();
    carregarObras();
    carregarCategorias();
    carregarContas();
    carregarItensABC();  // Carregar itens ABC primeiro
    carregarDespesas();
    carregarMateriais();
    carregarMaoObra();
    
    const hoje = new Date().toISOString().split('T')[0];
    if (document.getElementById('mat_data')) document.getElementById('mat_data').value = hoje;
    if (document.getElementById('mo_data')) document.getElementById('mo_data').value = hoje;
    if (document.getElementById('out_data')) document.getElementById('out_data').value = hoje;
});

// ========== CARREGAR FORMAS DE PAGAMENTO ==========
async function carregarFormasPagamento() {
    try {
        formasPagamento = await api.get('/formas-pagamento');
        console.log('💳 Formas de pagamento carregadas:', formasPagamento.length);
        
        const options = '<option value="">Selecione...</option>' + 
            formasPagamento.map(f => `<option value="${f.id}">${f.nome}</option>`).join('');
        
        // Preencher todos os selects de forma de pagamento
        const matSelect = document.getElementById('mat_forma_pagamento_id');
        const moSelect = document.getElementById('mo_forma_pagamento_id');
        const outSelect = document.getElementById('out_forma_pagamento_id');
        const pagSelect = document.getElementById('pag_forma_pagamento_id');
        
        if (matSelect) matSelect.innerHTML = options;
        if (moSelect) moSelect.innerHTML = options;
        if (outSelect) outSelect.innerHTML = options;
        if (pagSelect) pagSelect.innerHTML = options;
        
    } catch (error) {
        console.error('❌ Erro ao carregar formas de pagamento:', error);
    }
}

// ========== CARREGAR OBRAS ==========
async function carregarObras() {
    try {
        obras = await api.get('/obras');
        console.log('📋 Obras carregadas:', obras.length);
        
        const selects = [
            'filtroObra', 'mat_obra_id', 'mo_obra_id', 'out_obra_id'
        ];
        
        selects.forEach(id => {
            const select = document.getElementById(id);
            if (select) {
                let options = id === 'filtroObra' 
                    ? '<option value="">Todas as Obras</option>'
                    : '<option value="">Selecione...</option>';
                
                obras.forEach(obra => {
                    options += `<option value="${obra.id}">${obra.nome}</option>`;
                });
                select.innerHTML = options;
            }
        });
    } catch (error) {
        console.error('❌ Erro ao carregar obras:', error);
    }
}

// ========== CARREGAR CATEGORIAS ==========
async function carregarCategorias() {
    try {
        categorias = await api.get('/categorias');
        console.log('📋 Categorias carregadas:', categorias.length);
        
        const select = document.getElementById('out_categoria_id');
        if (select) {
            let options = '<option value="">Selecione...</option>';
            categorias.forEach(cat => {
                options += `<option value="${cat.id}">${cat.nome}</option>`;
            });
            select.innerHTML = options;
        }
    } catch (error) {
        console.error('❌ Erro ao carregar categorias:', error);
    }
}

// ========== CARREGAR CONTAS ==========
async function carregarContas() {
    try {
        contas = await api.get('/contas');
        console.log('🏦 Contas carregadas:', contas.length);
        
        const selects = ['mat_conta_id', 'mo_conta_id', 'out_conta_id', 'pag_conta_id'];
        
        selects.forEach(id => {
            const select = document.getElementById(id);
            if (select) {
                let options = '<option value="">Selecione uma conta...</option>';
                contas.forEach(conta => {
                    options += `<option value="${conta.id}">${conta.nome}</option>`;
                });
                select.innerHTML = options;
            }
        });
    } catch (error) {
        console.error('❌ Erro ao carregar contas:', error);
    }
}

// ========== CARREGAR ITENS ABC ==========
async function carregarItensABC() {
    try {
        itensABC = await api.get('/abc');
        console.log('📊 Itens ABC carregados:', itensABC.length);
        
        // Preencher select de itens ABC para MATERIAL
        const matSelect = document.getElementById('mat_item_abc_id');
        if (matSelect) {
            let options = '<option value="">Não vincular</option>';
            itensABC.forEach(item => {
                options += `<option value="${item.id}">${item.codigo} - ${item.descricao.substring(0, 50)}</option>`;
            });
            matSelect.innerHTML = options;
            console.log('✅ Select de material preenchido com', itensABC.length, 'itens');
        }
        
        // Preencher select de itens ABC para MÃO DE OBRA
        const moSelect = document.getElementById('mo_item_abc_id');
        if (moSelect) {
            let options = '<option value="">Não vincular</option>';
            itensABC.forEach(item => {
                options += `<option value="${item.id}">${item.codigo} - ${item.descricao.substring(0, 50)}</option>`;
            });
            moSelect.innerHTML = options;
            console.log('✅ Select de mão de obra preenchido com', itensABC.length, 'itens');
        }
    } catch (error) {
        console.error('❌ Erro ao carregar itens ABC:', error);
    }
}

// ========== CARREGAR DESPESAS ==========
async function carregarDespesas() {
    const tbody = document.getElementById('listaDespesas');
    if (!tbody) return;
    
    try {
        tbody.innerHTML = '<tr><td colspan="12" class="text-center">🔄 Carregando...</td></tr>';
        
        const params = [];
        if (document.getElementById('filtroObra')?.value) params.push(`obra_id=${document.getElementById('filtroObra').value}`);
        if (document.getElementById('filtroTipo')?.value) params.push(`tipo=${document.getElementById('filtroTipo').value}`);
        if (document.getElementById('filtroMes')?.value) params.push(`mes=${document.getElementById('filtroMes').value}`);
        if (document.getElementById('filtroAno')?.value) params.push(`ano=${document.getElementById('filtroAno').value}`);
        
        const url = '/despesas' + (params.length ? '?' + params.join('&') : '');
        console.log('📥 Carregando despesas:', url);
        
        despesas = await api.get(url);
        console.log('📋 Despesas carregadas:', despesas.length);
        
        const status = document.getElementById('filtroStatus')?.value;
        let filtradas = despesas;
        if (status) filtradas = despesas.filter(d => d.status === status);
        
        renderizarTabelaDespesas(filtradas);
        atualizarResumo();
    } catch (error) {
        console.error('❌ Erro ao carregar despesas:', error);
        tbody.innerHTML = '<tr><td colspan="12" class="text-center text-danger">❌ Erro ao carregar despesas</td></tr>';
    }
}

// ========== CARREGAR MATERIAIS ==========
async function carregarMateriais() {
    const tbody = document.getElementById('listaMateriais');
    if (!tbody) return;
    
    try {
        tbody.innerHTML = '<tr><td colspan="15" class="text-center">🔄 Carregando...</td></tr>';
        
        const obraId = document.getElementById('filtroObra')?.value;
        const url = obraId ? `/materiais?obra_id=${obraId}` : '/materiais';
        console.log('📥 Carregando materiais:', url);
        
        materiais = await api.get(url);
        console.log('📋 Materiais carregados:', materiais.length);
        
        renderizarTabelaMateriais(materiais);
        atualizarResumo();
    } catch (error) {
        console.error('❌ Erro ao carregar materiais:', error);
        tbody.innerHTML = '<tr><td colspan="15" class="text-center text-danger">❌ Erro ao carregar materiais</td></tr>';
    }
}

// ========== CARREGAR MÃO DE OBRA ==========
async function carregarMaoObra() {
    const tbody = document.getElementById('listaMaoObra');
    if (!tbody) return;
    
    try {
        tbody.innerHTML = '<tr><td colspan="15" class="text-center">🔄 Carregando...</td></tr>';
        
        const obraId = document.getElementById('filtroObra')?.value;
        const url = obraId ? `/mao-obra?obra_id=${obraId}` : '/mao-obra';
        console.log('📥 Carregando mão de obra:', url);
        
        maoObra = await api.get(url);
        console.log('📋 Mão de obra carregada:', maoObra.length);
        
        renderizarTabelaMaoObra(maoObra);
        atualizarResumo();
    } catch (error) {
        console.error('❌ Erro ao carregar mão de obra:', error);
        tbody.innerHTML = '<tr><td colspan="15" class="text-center text-danger">❌ Erro ao carregar mão de obra</td></tr>';
    }
}

// ========== RENDERIZAR TABELA DE DESPESAS ==========
function renderizarTabelaDespesas(despesasFiltradas) {
    const tbody = document.getElementById('listaDespesas');
    if (!tbody) return;
    
    if (!despesasFiltradas || despesasFiltradas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="12" class="text-center">📭 Nenhuma despesa encontrada</td></tr>';
        return;
    }
    
    let html = '';
    despesasFiltradas.forEach(d => {
        const statusClass = d.status === 'PAGO' ? 'bg-success' : (d.status === 'PARCIAL' ? 'bg-warning' : 'bg-secondary');
        const tipoIcon = d.tipo === 'MATERIAL' ? '📦' : (d.tipo === 'MÃO DE OBRA' ? '👷' : '📄');
        const parcelasText = d.quantidade_parcelas > 1 ? d.quantidade_parcelas + 'x' : 'À vista';
        const formaPagto = d.forma_pagamento_nome || '-';
        
        html += `
            <tr>
                <td>${d.id}</td>
                <td>${d.data_br || d.data}</td>
                <td>${d.obra_nome || '-'}</td>
                <td>${d.descricao}</td>
                <td>${tipoIcon} ${d.tipo || 'OUTROS'}</td>
                <td>${formaPagto}</td>
                <td class="text-center">${parcelasText}</td>
                <td class="text-end">R$ ${formatarMoeda(d.valor_total)}</td>
                <td class="text-end">R$ ${formatarMoeda(d.valor_pago)}</td>
                <td><span class="badge ${statusClass}">${d.status}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-warning" onclick="verParcelasDespesa(${d.id})" title="Ver Parcelas">
                        <i class="bi bi-credit-card"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deletarDespesa(${d.id}, '${d.descricao.replace(/'/g, "\\'")}')" title="Deletar">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// ========== RENDERIZAR TABELA DE MATERIAIS ==========
function renderizarTabelaMateriais(materiaisFiltrados) {
    const tbody = document.getElementById('listaMateriais');
    if (!tbody) return;
    
    if (!materiaisFiltrados || materiaisFiltrados.length === 0) {
        tbody.innerHTML = '<tr><td colspan="15" class="text-center">📭 Nenhum material encontrado</td></tr>';
        return;
    }
    
    let html = '';
    materiaisFiltrados.forEach(m => {
        const statusClass = m.status === 'PAGO' ? 'bg-success' : (m.status === 'PARCIAL' ? 'bg-warning' : 'bg-secondary');
        const parcelasText = m.quantidade_parcelas > 1 ? m.quantidade_parcelas + 'x' : 'À vista';
        const itemABC = m.item_abc_codigo ? `${m.item_abc_codigo}` : '-';
        const formaPagto = m.forma_pagamento_nome || '-';
        
        html += `
            <tr>
                <td>${m.id}</td>
                <td>${m.data_br || m.data}</td>
                <td>${m.obra_nome || '-'}</td>
                <td>${m.descricao}</td>
                <td>${m.fornecedor || '-'}</td>
                <td>${m.quantidade || '-'}</td>
                <td>${m.unidade || '-'}</td>
                <td>R$ ${formatarMoeda(m.valor_unitario || 0)}</td>
                <td>${formaPagto}</td>
                <td class="text-center">${parcelasText}</td>
                <td>${itemABC}</td>
                <td class="text-end">R$ ${formatarMoeda(m.valor_total)}</td>
                <td class="text-end">R$ ${formatarMoeda(m.valor_pago)}</td>
                <td><span class="badge ${statusClass}">${m.status}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-warning" onclick="verParcelasMaterial(${m.id})" title="Ver Parcelas">
                        <i class="bi bi-credit-card"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deletarMaterial(${m.id}, '${m.descricao.replace(/'/g, "\\'")}')" title="Deletar">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// ========== RENDERIZAR TABELA DE MÃO DE OBRA ==========
function renderizarTabelaMaoObra(maoObraFiltrada) {
    const tbody = document.getElementById('listaMaoObra');
    if (!tbody) return;
    
    if (!maoObraFiltrada || maoObraFiltrada.length === 0) {
        tbody.innerHTML = '<tr><td colspan="15" class="text-center">📭 Nenhuma mão de obra encontrada</td></tr>';
        return;
    }
    
    let html = '';
    maoObraFiltrada.forEach(m => {
        const statusClass = m.status === 'PAGO' ? 'bg-success' : (m.status === 'PARCIAL' ? 'bg-warning' : 'bg-secondary');
        const parcelasText = m.quantidade_parcelas > 1 ? m.quantidade_parcelas + 'x' : 'À vista';
        const itemABC = m.item_abc_codigo ? `${m.item_abc_codigo}` : '-';
        const formaPagto = m.forma_pagamento_nome || '-';
        
        html += `
            <tr>
                <td>${m.id}</td>
                <td>${m.data_br || m.data}</td>
                <td>${m.obra_nome || '-'}</td>
                <td>${m.descricao}</td>
                <td>${m.funcionario || '-'}</td>
                <td>${m.funcao || '-'}</td>
                <td>${m.horas_trabalhadas || '-'}</td>
                <td>R$ ${formatarMoeda(m.valor_hora || 0)}</td>
                <td>${formaPagto}</td>
                <td class="text-center">${parcelasText}</td>
                <td>${itemABC}</td>
                <td class="text-end">R$ ${formatarMoeda(m.valor_total)}</td>
                <td class="text-end">R$ ${formatarMoeda(m.valor_pago)}</td>
                <td><span class="badge ${statusClass}">${m.status}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-warning" onclick="verParcelasMaoObra(${m.id})" title="Ver Parcelas">
                        <i class="bi bi-credit-card"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deletarMaoObra(${m.id}, '${m.descricao.replace(/'/g, "\\'")}')" title="Deletar">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// ========== ATUALIZAR RESUMO ==========
function atualizarResumo() {
    let totalPrevisto = 0;
    let totalPago = 0;
    let totalMateriais = 0;
    let totalMaoObra = 0;
    
    // Despesas gerais
    despesas.forEach(d => {
        totalPrevisto += d.valor_total || 0;
        totalPago += d.valor_pago || 0;
    });
    
    // Materiais
    materiais.forEach(m => {
        totalPrevisto += m.valor_total || 0;
        totalPago += m.valor_pago || 0;
        totalMateriais += m.valor_pago || 0;
    });
    
    // Mão de obra
    maoObra.forEach(m => {
        totalPrevisto += m.valor_total || 0;
        totalPago += m.valor_pago || 0;
        totalMaoObra += m.valor_pago || 0;
    });
    
    if (document.getElementById('totalPrevisto')) {
        document.getElementById('totalPrevisto').innerHTML = `R$ ${formatarMoeda(totalPrevisto)}`;
    }
    if (document.getElementById('totalPago')) {
        document.getElementById('totalPago').innerHTML = `R$ ${formatarMoeda(totalPago)}`;
    }
    if (document.getElementById('totalMateriais')) {
        document.getElementById('totalMateriais').innerHTML = `R$ ${formatarMoeda(totalMateriais)}`;
    }
    if (document.getElementById('totalMaoObra')) {
        document.getElementById('totalMaoObra').innerHTML = `R$ ${formatarMoeda(totalMaoObra)}`;
    }
}

// ========== APLICAR FILTROS ==========
function aplicarFiltros() {
    carregarDespesas();
    carregarMateriais();
    carregarMaoObra();
}

function limparFiltros() {
    if (document.getElementById('filtroObra')) document.getElementById('filtroObra').value = '';
    if (document.getElementById('filtroTipo')) document.getElementById('filtroTipo').value = '';
    if (document.getElementById('filtroMes')) document.getElementById('filtroMes').value = '';
    if (document.getElementById('filtroAno')) document.getElementById('filtroAno').value = '';
    if (document.getElementById('filtroStatus')) document.getElementById('filtroStatus').value = '';
    aplicarFiltros();
}

// ========== CALCULAR VALOR DA PARCELA (MATERIAL) ==========
function calcularValorParcelaMaterial() {
    const valorTotal = parseFloat(document.getElementById('mat_valor_total').value) || 0;
    const quantidadeParcelas = parseInt(document.getElementById('mat_quantidade_parcelas').value) || 1;
    
    const divValorParcela = document.getElementById('mat_div_valor_parcela');
    const avisoDiv = document.getElementById('mat_div_aviso_parcelamento');
    const aviso = document.getElementById('mat_aviso_parcelamento');
    const dataPrimeiraParcela = document.getElementById('mat_data_primeira_parcela');
    
    if (quantidadeParcelas > 1 && valorTotal > 0) {
        const valorParcela = valorTotal / quantidadeParcelas;
        if (document.getElementById('mat_valor_parcela')) {
            document.getElementById('mat_valor_parcela').value = `R$ ${formatarMoeda(valorParcela)} (${quantidadeParcelas}x)`;
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

// ========== CALCULAR VALOR DA PARCELA (MÃO DE OBRA) ==========
function calcularValorParcelaMaoObra() {
    const valorTotal = parseFloat(document.getElementById('mo_valor_total').value) || 0;
    const quantidadeParcelas = parseInt(document.getElementById('mo_quantidade_parcelas').value) || 1;
    
    const divValorParcela = document.getElementById('mo_div_valor_parcela');
    const avisoDiv = document.getElementById('mo_div_aviso_parcelamento');
    const aviso = document.getElementById('mo_aviso_parcelamento');
    const dataPrimeiraParcela = document.getElementById('mo_data_primeira_parcela');
    
    if (quantidadeParcelas > 1 && valorTotal > 0) {
        const valorParcela = valorTotal / quantidadeParcelas;
        if (document.getElementById('mo_valor_parcela')) {
            document.getElementById('mo_valor_parcela').value = `R$ ${formatarMoeda(valorParcela)} (${quantidadeParcelas}x)`;
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

// ========== CALCULAR VALOR DA PARCELA (OUTROS) ==========
function calcularValorParcelaOutros() {
    const valorTotal = parseFloat(document.getElementById('out_valor_total').value) || 0;
    const quantidadeParcelas = parseInt(document.getElementById('out_quantidade_parcelas').value) || 1;
    
    const divValorParcela = document.getElementById('out_div_valor_parcela');
    const avisoDiv = document.getElementById('out_div_aviso_parcelamento');
    const aviso = document.getElementById('out_aviso_parcelamento');
    const dataPrimeiraParcela = document.getElementById('out_data_primeira_parcela');
    
    if (quantidadeParcelas > 1 && valorTotal > 0) {
        const valorParcela = valorTotal / quantidadeParcelas;
        if (document.getElementById('out_valor_parcela')) {
            document.getElementById('out_valor_parcela').value = `R$ ${formatarMoeda(valorParcela)} (${quantidadeParcelas}x)`;
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

// ========== ABRIR MODAIS ==========
function abrirModalNovaDespesaMaterial() {
    console.log('📤 Abrindo modal novo material');
    
    document.getElementById('mat_obra_id').value = '';
    document.getElementById('mat_data').value = new Date().toISOString().split('T')[0];
    document.getElementById('mat_descricao').value = '';
    document.getElementById('mat_fornecedor').value = '';
    document.getElementById('mat_quantidade').value = '';
    document.getElementById('mat_unidade').value = 'UN';
    document.getElementById('mat_valor_unitario').value = '';
    document.getElementById('mat_valor_total').value = '';
    document.getElementById('mat_valor_pago').value = '0';
    document.getElementById('mat_data_pagamento').value = '';
    document.getElementById('mat_quantidade_parcelas').value = '1';
    document.getElementById('mat_forma_pagamento_id').value = '';
    document.getElementById('mat_conta_id').value = '';
    document.getElementById('mat_data_primeira_parcela').value = '';
    document.getElementById('mat_item_abc_id').value = '';
    document.getElementById('mat_observacao').value = '';
    
    document.getElementById('mat_div_valor_parcela').style.display = 'none';
    document.getElementById('mat_div_aviso_parcelamento').style.display = 'none';
    
    // Recarregar itens ABC para garantir que estão atualizados
    carregarItensABC();
    
    if (modalNovaDespesaMaterial) modalNovaDespesaMaterial.show();
}

function abrirModalNovaDespesaMaoObra() {
    console.log('📤 Abrindo modal nova mão de obra');
    
    document.getElementById('mo_obra_id').value = '';
    document.getElementById('mo_data').value = new Date().toISOString().split('T')[0];
    document.getElementById('mo_descricao').value = '';
    document.getElementById('mo_funcionario').value = '';
    document.getElementById('mo_funcao').value = '';
    document.getElementById('mo_horas').value = '';
    document.getElementById('mo_valor_hora').value = '';
    document.getElementById('mo_valor_total').value = '';
    document.getElementById('mo_valor_pago').value = '0';
    document.getElementById('mo_data_pagamento').value = '';
    document.getElementById('mo_quantidade_parcelas').value = '1';
    document.getElementById('mo_forma_pagamento_id').value = '';
    document.getElementById('mo_conta_id').value = '';
    document.getElementById('mo_data_primeira_parcela').value = '';
    document.getElementById('mo_item_abc_id').value = '';
    document.getElementById('mo_observacao').value = '';
    
    document.getElementById('mo_div_valor_parcela').style.display = 'none';
    document.getElementById('mo_div_aviso_parcelamento').style.display = 'none';
    
    // Recarregar itens ABC para garantir que estão atualizados
    carregarItensABC();
    
    if (modalNovaDespesaMaoObra) modalNovaDespesaMaoObra.show();
}

function abrirModalNovaDespesaOutros() {
    console.log('📤 Abrindo modal nova despesa outros');
    
    document.getElementById('out_obra_id').value = '';
    document.getElementById('out_data').value = new Date().toISOString().split('T')[0];
    document.getElementById('out_descricao').value = '';
    document.getElementById('out_fornecedor').value = '';
    document.getElementById('out_categoria_id').value = '';
    document.getElementById('out_valor_total').value = '';
    document.getElementById('out_quantidade_parcelas').value = '1';
    document.getElementById('out_forma_pagamento_id').value = '';
    document.getElementById('out_conta_id').value = '';
    document.getElementById('out_data_primeira_parcela').value = '';
    document.getElementById('out_observacao').value = '';
    
    document.getElementById('out_div_valor_parcela').style.display = 'none';
    document.getElementById('out_div_aviso_parcelamento').style.display = 'none';
    
    carregarCategorias();
    
    if (modalNovaDespesaOutros) modalNovaDespesaOutros.show();
}

// ========== SALVAR NOVA DESPESA MATERIAL ==========
async function salvarNovaDespesaMaterial() {
    const obraId = document.getElementById('mat_obra_id').value;
    const descricao = document.getElementById('mat_descricao').value.trim();
    const valorTotal = parseFloat(document.getElementById('mat_valor_total').value);
    const quantidadeParcelas = parseInt(document.getElementById('mat_quantidade_parcelas').value) || 1;
    const dataPrimeiraParcela = document.getElementById('mat_data_primeira_parcela').value;
    const itemAbcId = document.getElementById('mat_item_abc_id').value;
    
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
    
    // Validar parcelamento
    if (quantidadeParcelas > 1 && !dataPrimeiraParcela) {
        mostrarNotificacao('❌ Para parcelamento, informe a data da primeira parcela', 'danger');
        return;
    }
    
    const dados = {
        obra_id: parseInt(obraId),
        data: document.getElementById('mat_data').value,
        descricao: descricao,
        fornecedor: document.getElementById('mat_fornecedor').value.trim() || null,
        quantidade: parseFloat(document.getElementById('mat_quantidade').value) || null,
        unidade: document.getElementById('mat_unidade').value,
        valor_unitario: parseFloat(document.getElementById('mat_valor_unitario').value) || null,
        valor_total: valorTotal,
        quantidade_parcelas: quantidadeParcelas,
        data_primeira_parcela: dataPrimeiraParcela || null,
        forma_pagamento_id: document.getElementById('mat_forma_pagamento_id').value || null,
        conta_id: document.getElementById('mat_conta_id').value || null,
        item_abc_id: itemAbcId || null,  // Enviar o ID do item ABC selecionado
        valor_pago: parseFloat(document.getElementById('mat_valor_pago').value) || 0,
        data_pagamento: document.getElementById('mat_data_pagamento').value || null,
        observacao: document.getElementById('mat_observacao').value.trim() || null,
        tipo: 'MATERIAL'
    };
    
    console.log('📤 Enviando dados do material:', dados);
    
    try {
        const result = await api.post('/materiais', dados);
        if (result.success) {
            const msgParcelamento = quantidadeParcelas > 1 ? ` (parcelado em ${quantidadeParcelas}x)` : '';
            const msgAbc = itemAbcId ? ' vinculado à curva ABC' : '';
            mostrarNotificacao(`✅ Material cadastrado com sucesso${msgParcelamento}${msgAbc}!`, 'success');
            if (modalNovaDespesaMaterial) modalNovaDespesaMaterial.hide();
            await carregarMateriais();
            await carregarDespesas();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao cadastrar material', 'danger');
    }
}

// ========== SALVAR NOVA DESPESA MÃO DE OBRA ==========
async function salvarNovaDespesaMaoObra() {
    const obraId = document.getElementById('mo_obra_id').value;
    const descricao = document.getElementById('mo_descricao').value.trim();
    const valorTotal = parseFloat(document.getElementById('mo_valor_total').value);
    const quantidadeParcelas = parseInt(document.getElementById('mo_quantidade_parcelas').value) || 1;
    const dataPrimeiraParcela = document.getElementById('mo_data_primeira_parcela').value;
    const itemAbcId = document.getElementById('mo_item_abc_id').value;
    
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
    
    // Validar parcelamento
    if (quantidadeParcelas > 1 && !dataPrimeiraParcela) {
        mostrarNotificacao('❌ Para parcelamento, informe a data da primeira parcela', 'danger');
        return;
    }
    
    const dados = {
        obra_id: parseInt(obraId),
        data: document.getElementById('mo_data').value,
        descricao: descricao,
        funcionario: document.getElementById('mo_funcionario').value.trim() || null,
        funcao: document.getElementById('mo_funcao').value || null,
        horas_trabalhadas: parseFloat(document.getElementById('mo_horas').value) || null,
        valor_hora: parseFloat(document.getElementById('mo_valor_hora').value) || null,
        valor_total: valorTotal,
        quantidade_parcelas: quantidadeParcelas,
        data_primeira_parcela: dataPrimeiraParcela || null,
        forma_pagamento_id: document.getElementById('mo_forma_pagamento_id').value || null,
        conta_id: document.getElementById('mo_conta_id').value || null,
        item_abc_id: itemAbcId || null,  // Enviar o ID do item ABC selecionado
        valor_pago: parseFloat(document.getElementById('mo_valor_pago').value) || 0,
        data_pagamento: document.getElementById('mo_data_pagamento').value || null,
        observacao: document.getElementById('mo_observacao').value.trim() || null,
        tipo: 'MÃO DE OBRA'
    };
    
    console.log('📤 Enviando dados da mão de obra:', dados);
    
    try {
        const result = await api.post('/mao-obra', dados);
        if (result.success) {
            const msgParcelamento = quantidadeParcelas > 1 ? ` (parcelado em ${quantidadeParcelas}x)` : '';
            const msgAbc = itemAbcId ? ' vinculado à curva ABC' : '';
            mostrarNotificacao(`✅ Mão de obra cadastrada com sucesso${msgParcelamento}${msgAbc}!`, 'success');
            if (modalNovaDespesaMaoObra) modalNovaDespesaMaoObra.hide();
            await carregarMaoObra();
            await carregarDespesas();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao cadastrar mão de obra', 'danger');
    }
}

// ========== SALVAR NOVA DESPESA OUTROS ==========
async function salvarNovaDespesaOutros() {
    const obraId = document.getElementById('out_obra_id').value;
    const descricao = document.getElementById('out_descricao').value.trim();
    const valorTotal = parseFloat(document.getElementById('out_valor_total').value);
    const quantidadeParcelas = parseInt(document.getElementById('out_quantidade_parcelas').value) || 1;
    const dataPrimeiraParcela = document.getElementById('out_data_primeira_parcela').value;
    
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
    
    // Validar parcelamento
    if (quantidadeParcelas > 1 && !dataPrimeiraParcela) {
        mostrarNotificacao('❌ Para parcelamento, informe a data da primeira parcela', 'danger');
        return;
    }
    
    const dados = {
        obra_id: parseInt(obraId),
        data: document.getElementById('out_data').value,
        descricao: descricao,
        fornecedor: document.getElementById('out_fornecedor').value.trim() || null,
        categoria_id: document.getElementById('out_categoria_id').value || null,
        valor_total: valorTotal,
        quantidade_parcelas: quantidadeParcelas,
        forma_pagamento_id: document.getElementById('out_forma_pagamento_id').value || null,
        conta_id: document.getElementById('out_conta_id').value || null,
        data_primeira_parcela: dataPrimeiraParcela || null,
        observacao: document.getElementById('out_observacao').value.trim() || null,
        tipo: 'OUTROS'
    };
    
    console.log('📤 Enviando dados da despesa:', dados);
    
    try {
        const result = await api.post('/despesas', dados);
        if (result.success) {
            const msgParcelamento = quantidadeParcelas > 1 ? ` (parcelado em ${quantidadeParcelas}x)` : '';
            mostrarNotificacao(`✅ Despesa cadastrada com sucesso${msgParcelamento}!`, 'success');
            if (modalNovaDespesaOutros) modalNovaDespesaOutros.hide();
            await carregarDespesas();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao cadastrar despesa', 'danger');
    }
}

// ========== VER PARCELAS DE MATERIAL ==========
async function verParcelasMaterial(materialId) {
    try {
        // Mostrar mensagem informativa
        mostrarNotificacao('Parcelamento para materiais será implementado na versão 2.0', 'info');
    } catch (error) {
        console.error('❌ Erro ao carregar parcelas:', error);
        mostrarNotificacao('Erro ao carregar parcelas', 'danger');
    }
}

// ========== VER PARCELAS DE MÃO DE OBRA ==========
async function verParcelasMaoObra(maoObraId) {
    try {
        // Mostrar mensagem informativa
        mostrarNotificacao('Parcelamento para mão de obra será implementado na versão 2.0', 'info');
    } catch (error) {
        console.error('❌ Erro ao carregar parcelas:', error);
        mostrarNotificacao('Erro ao carregar parcelas', 'danger');
    }
}

// ========== VER PARCELAS DA DESPESA ==========
async function verParcelasDespesa(despesaId) {
    try {
        const parcelas = await api.get(`/parcelas/despesa/${despesaId}`);
        const despesa = despesas.find(d => d.id === despesaId);
        
        if (!parcelas || parcelas.length === 0) {
            document.getElementById('listaParcelasDespesa').innerHTML = '<p class="text-center">Nenhuma parcela encontrada</p>';
            modalVisualizarParcelasDespesa.show();
            return;
        }
        
        // Calcular totais
        const totalPago = parcelas.reduce((sum, p) => sum + p.valor_pago, 0);
        const totalAPagar = parcelas.reduce((sum, p) => sum + (p.valor - p.valor_pago), 0);
        
        let html = `
            <h6>Despesa: ${despesa.descricao}</h6>
            <p><strong>Valor Total:</strong> R$ ${formatarMoeda(despesa.valor_total)}</p>
            <p><strong>Total Pago:</strong> R$ ${formatarMoeda(totalPago)}</p>
            <p><strong>Total a Pagar:</strong> R$ ${formatarMoeda(totalAPagar)}</p>
            <hr>
            <div class="table-responsive">
                <table class="table table-sm table-striped">
                    <thead>
                        <tr>
                            <th>Parcela</th>
                            <th>Vencimento</th>
                            <th>Valor</th>
                            <th>Pago</th>
                            <th>Saldo</th>
                            <th>Status</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        parcelas.forEach(p => {
            const statusClass = p.status === 'PAGO' ? 'success' : 
                               (p.status === 'ATRASADO' ? 'danger' : 
                                (p.status === 'PARCIAL' ? 'warning' : 'warning'));
            const statusText = p.status === 'PAGO' ? 'Pago' : 
                              (p.status === 'ATRASADO' ? `Atrasado (${p.dias_atraso}d)` : 
                               (p.status === 'PARCIAL' ? 'Parcial' : 'Pendente'));
            const saldo = p.valor - p.valor_pago;
            
            html += `
                <tr>
                    <td>${p.numero_parcela}/${p.total_parcelas}</td>
                    <td>${p.data_vencimento}</td>
                    <td class="text-end">R$ ${formatarMoeda(p.valor)}</td>
                    <td class="text-end">R$ ${formatarMoeda(p.valor_pago)}</td>
                    <td class="text-end">R$ ${formatarMoeda(saldo)}</td>
                    <td><span class="badge bg-${statusClass}">${statusText}</span></td>
                    <td>
                        ${p.status !== 'PAGO' ? 
                            `<button class="btn btn-sm btn-success" onclick="abrirModalPagarParcela(${p.id}, ${p.valor}, ${saldo})">
                                <i class="bi bi-cash"></i> Pagar
                            </button>` : 
                            '<span class="text-success"><i class="bi bi-check-circle"></i> Pago</span>'}
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        document.getElementById('listaParcelasDespesa').innerHTML = html;
        modalVisualizarParcelasDespesa.show();
    } catch (error) {
        console.error('❌ Erro ao carregar parcelas:', error);
        mostrarNotificacao('❌ Erro ao carregar parcelas', 'danger');
    }
}

// ========== ABRIR MODAL PAGAR PARCELA ==========
function abrirModalPagarParcela(parcelaId, valorParcela, saldo) {
    document.getElementById('pag_parcela_id').value = parcelaId;
    document.getElementById('pag_valor_parcela').value = `R$ ${formatarMoeda(valorParcela)}`;
    document.getElementById('pag_valor_pago').value = saldo.toFixed(2);
    document.getElementById('pag_data_pagamento').value = new Date().toISOString().split('T')[0];
    document.getElementById('pag_conta_id').value = '';
    document.getElementById('pag_forma_pagamento_id').value = '';
    document.getElementById('pag_observacao').value = '';
    
    modalPagarParcela.show();
}

// ========== CONFIRMAR PAGAMENTO DE PARCELA ==========
async function confirmarPagamentoParcela() {
    const parcelaId = document.getElementById('pag_parcela_id').value;
    const valorPago = parseFloat(document.getElementById('pag_valor_pago').value);
    const dataPagamento = document.getElementById('pag_data_pagamento').value;
    const contaId = document.getElementById('pag_conta_id').value;
    
    if (!valorPago || valorPago <= 0) {
        mostrarNotificacao('❌ Informe o valor pago', 'danger');
        return;
    }
    
    if (!dataPagamento) {
        mostrarNotificacao('❌ Informe a data de pagamento', 'danger');
        return;
    }
    
    if (!contaId) {
        mostrarNotificacao('❌ Selecione a conta de pagamento', 'danger');
        return;
    }
    
    const data = {
        valor_pago: valorPago,
        data_pagamento: dataPagamento,
        conta_id: parseInt(contaId),
        forma_pagamento_id: document.getElementById('pag_forma_pagamento_id').value || null,
        observacao: document.getElementById('pag_observacao').value.trim() || null
    };
    
    try {
        const result = await api.post(`/parcelas/despesa/${parcelaId}/pagar`, data);
        if (result.success) {
            mostrarNotificacao('✅ Pagamento registrado com sucesso!', 'success');
            modalPagarParcela.hide();
            await carregarDespesas();
            
            // Recarregar parcelas
            modalVisualizarParcelasDespesa.hide();
            setTimeout(() => {
                const despesaId = despesas.find(d => d.id === parseInt(document.getElementById('pag_parcela_id').value))?.id;
                if (despesaId) verParcelasDespesa(despesaId);
            }, 300);
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao registrar pagamento', 'danger');
    }
}

// ========== DELETAR DESPESA ==========
async function deletarDespesa(despesaId, descricao) {
    if (!confirm(`🗑️ Deseja realmente deletar a despesa "${descricao}"?`)) return;
    
    try {
        const result = await api.delete('/despesas/' + despesaId);
        if (result.success) {
            mostrarNotificacao('✅ Despesa deletada com sucesso!', 'success');
            await carregarDespesas();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao deletar despesa', 'danger');
    }
}

async function deletarMaterial(materialId, descricao) {
    if (!confirm(`🗑️ Deseja realmente deletar o material "${descricao}"?`)) return;
    
    try {
        const result = await api.delete('/materiais/' + materialId);
        if (result.success) {
            mostrarNotificacao('✅ Material deletado com sucesso!', 'success');
            await carregarMateriais();
            await carregarDespesas();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao deletar material', 'danger');
    }
}

async function deletarMaoObra(maoObraId, descricao) {
    if (!confirm(`🗑️ Deseja realmente deletar a mão de obra "${descricao}"?`)) return;
    
    try {
        const result = await api.delete('/mao-obra/' + maoObraId);
        if (result.success) {
            mostrarNotificacao('✅ Mão de obra deletada com sucesso!', 'success');
            await carregarMaoObra();
            await carregarDespesas();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao deletar mão de obra', 'danger');
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
    notification.innerHTML = `${mensagem}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}

// ========== EXPORTAR FUNÇÕES ==========
window.abrirModalNovaDespesaMaterial = abrirModalNovaDespesaMaterial;
window.abrirModalNovaDespesaMaoObra = abrirModalNovaDespesaMaoObra;
window.abrirModalNovaDespesaOutros = abrirModalNovaDespesaOutros;
window.salvarNovaDespesaMaterial = salvarNovaDespesaMaterial;
window.salvarNovaDespesaMaoObra = salvarNovaDespesaMaoObra;
window.salvarNovaDespesaOutros = salvarNovaDespesaOutros;
window.verParcelasDespesa = verParcelasDespesa;
window.verParcelasMaterial = verParcelasMaterial;
window.verParcelasMaoObra = verParcelasMaoObra;
window.abrirModalPagarParcela = abrirModalPagarParcela;
window.confirmarPagamentoParcela = confirmarPagamentoParcela;
window.deletarDespesa = deletarDespesa;
window.deletarMaterial = deletarMaterial;
window.deletarMaoObra = deletarMaoObra;
window.aplicarFiltros = aplicarFiltros;
window.limparFiltros = limparFiltros;
window.calcularValorParcelaMaterial = calcularValorParcelaMaterial;
window.calcularValorParcelaMaoObra = calcularValorParcelaMaoObra;
window.calcularValorParcelaOutros = calcularValorParcelaOutros;
window.formatarMoeda = formatarMoeda;
window.mostrarNotificacao = mostrarNotificacao;