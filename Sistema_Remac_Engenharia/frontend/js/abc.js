// ============================================
// GERENCIAMENTO DA CURVA ABC
// ============================================

let itensABC = [];
let obras = [];
let modalNovoItem, modalEditarItem;

document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Módulo ABC iniciado');
    
    modalNovoItem = new bootstrap.Modal(document.getElementById('modalNovoItemABC'));
    modalEditarItem = new bootstrap.Modal(document.getElementById('modalEditarItemABC'));
    
    carregarObras();
    carregarItensABC();
    
    // Preview do total
    document.getElementById('item_quantidade')?.addEventListener('input', atualizarPreview);
    document.getElementById('item_valor_unitario')?.addEventListener('input', atualizarPreview);
});

// ========== ATUALIZAR PREVIEW ==========
function atualizarPreview() {
    const qtd = parseFloat(document.getElementById('item_quantidade').value) || 0;
    const valor = parseFloat(document.getElementById('item_valor_unitario').value) || 0;
    const total = qtd * valor;
    document.getElementById('previewTotal').textContent = formatarMoeda(total);
}

// ========== CARREGAR OBRAS ==========
async function carregarObras() {
    try {
        obras = await api.get('/obras');
        
        const selects = ['filtroObra', 'item_obra_id', 'edit_item_obra_id'];
        
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

// ========== CARREGAR ITENS ABC ==========
async function carregarItensABC() {
    const tbody = document.getElementById('listaItensABC');
    
    try {
        tbody.innerHTML = '<tr><td colspan="11" class="text-center">🔄 Carregando...</td></tr>';
        
        const obraId = document.getElementById('filtroObra')?.value;
        const url = obraId ? `/abc?obra_id=${obraId}` : '/abc';
        
        itensABC = await api.get(url);
        
        // Se tiver obra selecionada, fazer análise ABC completa
        if (obraId) {
            await carregarAnaliseABC(obraId);
        } else {
            renderizarTabela(itensABC);
            atualizarResumo(itensABC);
        }
        
    } catch (error) {
        console.error('❌ Erro ao carregar itens ABC:', error);
        tbody.innerHTML = '<tr><td colspan="11" class="text-center text-danger">❌ Erro ao carregar itens</td></tr>';
    }
}

// ========== CARREGAR ANÁLISE ABC DA OBRA ==========
async function carregarAnaliseABC(obraId) {
    try {
        const analise = await api.get(`/obras/${obraId}/analise-abc`);
        
        renderizarTabelaComClassificacao(analise.itens);
        
        // Calcular totais por classe
        let totalA = 0, totalB = 0, totalC = 0;
        let qtdA = 0, qtdB = 0, qtdC = 0;
        
        analise.itens.forEach(item => {
            if (item.classificacao === 'A') {
                totalA += item.realizado;
                qtdA++;
            } else if (item.classificacao === 'B') {
                totalB += item.realizado;
                qtdB++;
            } else {
                totalC += item.realizado;
                qtdC++;
            }
        });
        
        document.getElementById('totalClasseA').innerHTML = `R$ ${formatarMoeda(totalA)}`;
        document.getElementById('totalClasseB').innerHTML = `R$ ${formatarMoeda(totalB)}`;
        document.getElementById('totalClasseC').innerHTML = `R$ ${formatarMoeda(totalC)}`;
        document.getElementById('qtdClasseA').innerHTML = `${qtdA} itens`;
        document.getElementById('qtdClasseB').innerHTML = `${qtdB} itens`;
        document.getElementById('qtdClasseC').innerHTML = `${qtdC} itens`;
        
    } catch (error) {
        console.error('❌ Erro ao carregar análise ABC:', error);
    }
}

// ========== RENDERIZAR TABELA ==========
function renderizarTabela(itens) {
    const tbody = document.getElementById('listaItensABC');
    
    if (itens.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" class="text-center">📭 Nenhum item encontrado</td></tr>';
        return;
    }
    
    let html = '';
    itens.forEach(item => {
        const desvioClass = item.desvio > 0 ? 'text-danger' : (item.desvio < 0 ? 'text-success' : '');
        
        html += `
            <tr>
                <td>${item.id}</td>
                <td><strong>${item.codigo}</strong></td>
                <td>${item.descricao}</td>
                <td>${item.unidade || '-'}</td>
                <td class="text-end">R$ ${formatarMoeda(item.valor_total_previsto)}</td>
                <td class="text-end">R$ ${formatarMoeda(item.valor_total_real)}</td>
                <td class="text-end ${desvioClass}">R$ ${formatarMoeda(item.desvio)}</td>
                <td class="text-end ${desvioClass}">${item.percentual_desvio}%</td>
                <td>-</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editarItemABC(${item.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deletarItemABC(${item.id}, '${item.descricao.replace(/'/g, "\\'")}')" title="Deletar">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// ========== RENDERIZAR TABELA COM CLASSIFICAÇÃO ==========
function renderizarTabelaComClassificacao(itens) {
    const tbody = document.getElementById('listaItensABC');
    
    if (itens.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" class="text-center">📭 Nenhum item encontrado</td></tr>';
        return;
    }
    
    let html = '';
    itens.forEach(item => {
        const desvioClass = item.desvio > 0 ? 'text-danger' : (item.desvio < 0 ? 'text-success' : '');
        const classeClass = item.classificacao === 'A' ? 'bg-danger' : 
                           (item.classificacao === 'B' ? 'bg-warning' : 'bg-success');
        
        html += `
            <tr>
                <td>${item.id || '-'}</td>
                <td><strong>${item.codigo || '-'}</strong></td>
                <td>${item.descricao || '-'}</td>
                <td>${item.unidade || '-'}</td>
                <td class="text-end">R$ ${formatarMoeda(item.previsto || 0)}</td>
                <td class="text-end">R$ ${formatarMoeda(item.realizado || 0)}</td>
                <td class="text-end ${desvioClass}">R$ ${formatarMoeda(item.desvio || 0)}</td>
                <td class="text-end ${desvioClass}">${item.percentual_desvio?.toFixed(2) || 0}%</td>
                <td><span class="badge ${classeClass} text-white">${item.classificacao || '-'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editarItemABC(${item.id})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deletarItemABC(${item.id}, '${item.descricao?.replace(/'/g, "\\'")}')" title="Deletar">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// ========== ATUALIZAR RESUMO ==========
function atualizarResumo(itens) {
    let totalPrevisto = 0, totalRealizado = 0;
    
    itens.forEach(item => {
        totalPrevisto += item.valor_total_previsto || 0;
        totalRealizado += item.valor_total_real || 0;
    });
    
    document.getElementById('totalClasseA').innerHTML = `R$ ${formatarMoeda(totalRealizado)}`;
    document.getElementById('totalClasseB').innerHTML = `R$ 0,00`;
    document.getElementById('totalClasseC').innerHTML = `R$ 0,00`;
    document.getElementById('qtdClasseA').innerHTML = `${itens.length} itens`;
    document.getElementById('qtdClasseB').innerHTML = `0 itens`;
    document.getElementById('qtdClasseC').innerHTML = `0 itens`;
}

// ========== NOVO ITEM ABC ==========
function abrirModalNovoItem() {
    document.getElementById('item_obra_id').value = '';
    document.getElementById('item_codigo').value = '';
    document.getElementById('item_descricao').value = '';
    document.getElementById('item_unidade').value = 'UN';
    document.getElementById('item_quantidade').value = '1';
    document.getElementById('item_valor_unitario').value = '0';
    atualizarPreview();
    
    modalNovoItem.show();
}

async function salvarNovoItemABC() {
    const obra_id = document.getElementById('item_obra_id').value;
    const codigo = document.getElementById('item_codigo').value.trim();
    const descricao = document.getElementById('item_descricao').value.trim();
    
    if (!obra_id) {
        mostrarNotificacao('❌ Selecione uma obra', 'danger');
        return;
    }
    if (!codigo) {
        mostrarNotificacao('❌ Código do item é obrigatório', 'danger');
        return;
    }
    if (!descricao) {
        mostrarNotificacao('❌ Descrição é obrigatória', 'danger');
        return;
    }
    
    const dados = {
        obra_id: parseInt(obra_id),
        codigo: codigo,
        descricao: descricao,
        unidade: document.getElementById('item_unidade').value,
        quantidade_prevista: parseFloat(document.getElementById('item_quantidade').value) || 0,
        valor_unitario: parseFloat(document.getElementById('item_valor_unitario').value) || 0
    };
    
    try {
        const result = await api.post('/abc', dados);
        if (result.success) {
            mostrarNotificacao('✅ Item ABC criado com sucesso!', 'success');
            modalNovoItem.hide();
            await carregarItensABC();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao criar item', 'danger');
    }
}

// ========== EDITAR ITEM ABC ==========
async function editarItemABC(itemId) {
    const item = itensABC.find(i => i.id === itemId);
    if (!item) return;
    
    document.getElementById('edit_item_id').value = item.id;
    document.getElementById('edit_item_obra_id').value = item.obra_id;
    document.getElementById('edit_item_codigo').value = item.codigo;
    document.getElementById('edit_item_descricao').value = item.descricao;
    document.getElementById('edit_item_unidade').value = item.unidade || 'UN';
    document.getElementById('edit_item_quantidade').value = item.quantidade_prevista;
    document.getElementById('edit_item_valor_unitario').value = item.valor_unitario;
    
    modalEditarItem.show();
}

async function atualizarItemABC() {
    const id = document.getElementById('edit_item_id').value;
    
    const dados = {
        obra_id: parseInt(document.getElementById('edit_item_obra_id').value),
        codigo: document.getElementById('edit_item_codigo').value.trim(),
        descricao: document.getElementById('edit_item_descricao').value.trim(),
        unidade: document.getElementById('edit_item_unidade').value,
        quantidade_prevista: parseFloat(document.getElementById('edit_item_quantidade').value) || 0,
        valor_unitario: parseFloat(document.getElementById('edit_item_valor_unitario').value) || 0
    };
    
    try {
        const result = await api.put('/abc/' + id, dados);
        if (result.success) {
            mostrarNotificacao('✅ Item ABC atualizado com sucesso!', 'success');
            modalEditarItem.hide();
            await carregarItensABC();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao atualizar item', 'danger');
    }
}

// ========== DELETAR ITEM ABC ==========
async function deletarItemABC(itemId, descricao) {
    if (!confirm(`🗑️ Deseja realmente deletar o item "${descricao}"?`)) return;
    
    try {
        const result = await api.delete('/abc/' + itemId);
        if (result.success) {
            mostrarNotificacao('✅ Item deletado com sucesso!', 'success');
            await carregarItensABC();
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        mostrarNotificacao('❌ Erro ao deletar item', 'danger');
    }
}

// Exportar funções
window.abrirModalNovoItem = abrirModalNovoItem;
window.salvarNovoItemABC = salvarNovoItemABC;
window.editarItemABC = editarItemABC;
window.atualizarItemABC = atualizarItemABC;
window.deletarItemABC = deletarItemABC;
window.carregarItensABC = carregarItensABC;
window.formatarMoeda = formatarMoeda;