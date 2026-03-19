// ============================================
// SISTEMA DE PARCELAMENTO - FUNÇÕES GLOBAIS
// ============================================

// ========== FUNÇÃO PARA VER FLUXO DE PARCELAS ==========
async function verFluxoParcelas() {
    try {
        const meses = prompt('Quantos meses à frente deseja visualizar? (ex: 6)', '6');
        if (!meses) return;
        
        const data = await api.get(`/parcelas/fluxo?meses=${meses}`);
        
        // Calcular totais
        const totalReceber = data.a_receber.reduce((sum, p) => sum + p.saldo, 0);
        const totalPagar = data.a_pagar.reduce((sum, p) => sum + p.saldo, 0);
        
        let html = `
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="card bg-success text-white">
                        <div class="card-body">
                            <h6>Total a Receber</h6>
                            <h4>R$ ${formatarMoeda(totalReceber)}</h4>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card bg-danger text-white">
                        <div class="card-body">
                            <h6>Total a Pagar</h6>
                            <h4>R$ ${formatarMoeda(totalPagar)}</h4>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <h5 class="text-success"><i class="bi bi-arrow-down-circle"></i> A Receber (${data.a_receber.length})</h5>
                    <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                        <table class="table table-sm table-striped">
                            <thead class="sticky-top bg-light">
                                <tr>
                                    <th>Vencimento</th>
                                    <th>Descrição</th>
                                    <th>Obra</th>
                                    <th>Parcela</th>
                                    <th class="text-end">Valor</th>
                                    <th class="text-end">Saldo</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
        `;
        
        if (data.a_receber.length === 0) {
            html += '<tr><td colspan="7" class="text-center">Nenhuma parcela a receber</td></tr>';
        } else {
            data.a_receber.forEach(p => {
                const statusClass = p.status === 'ATRASADO' ? 'danger' : 
                                   (p.status === 'PARCIAL' ? 'warning' : 'warning');
                const statusText = p.status === 'ATRASADO' ? `Atrasado (${p.dias_atraso}d)` : 
                                  (p.status === 'PARCIAL' ? 'Parcial' : 'Pendente');
                html += `
                    <tr>
                        <td>${p.data_vencimento}</td>
                        <td>${p.descricao}</td>
                        <td>${p.obra}</td>
                        <td class="text-center">${p.parcela}</td>
                        <td class="text-end">R$ ${formatarMoeda(p.valor)}</td>
                        <td class="text-end">R$ ${formatarMoeda(p.saldo)}</td>
                        <td><span class="badge bg-${statusClass}">${statusText}</span></td>
                    </tr>
                `;
            });
        }
        
        html += `
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="col-md-6">
                    <h5 class="text-danger"><i class="bi bi-arrow-up-circle"></i> A Pagar (${data.a_pagar.length})</h5>
                    <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                        <table class="table table-sm table-striped">
                            <thead class="sticky-top bg-light">
                                <tr>
                                    <th>Vencimento</th>
                                    <th>Descrição</th>
                                    <th>Obra</th>
                                    <th>Parcela</th>
                                    <th class="text-end">Valor</th>
                                    <th class="text-end">Saldo</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
        `;
        
        if (data.a_pagar.length === 0) {
            html += '<tr><td colspan="7" class="text-center">Nenhuma parcela a pagar</td></tr>';
        } else {
            data.a_pagar.forEach(p => {
                const statusClass = p.status === 'ATRASADO' ? 'danger' : 
                                   (p.status === 'PARCIAL' ? 'warning' : 'warning');
                const statusText = p.status === 'ATRASADO' ? `Atrasado (${p.dias_atraso}d)` : 
                                  (p.status === 'PARCIAL' ? 'Parcial' : 'Pendente');
                html += `
                    <tr>
                        <td>${p.data_vencimento}</td>
                        <td>${p.descricao}</td>
                        <td>${p.obra}</td>
                        <td class="text-center">${p.parcela}</td>
                        <td class="text-end">R$ ${formatarMoeda(p.valor)}</td>
                        <td class="text-end">R$ ${formatarMoeda(p.saldo)}</td>
                        <td><span class="badge bg-${statusClass}">${statusText}</span></td>
                    </tr>
                `;
            });
        }
        
        html += `
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        // Criar ou atualizar modal
        let modal = document.getElementById('modalFluxoParcelas');
        if (!modal) {
            modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = 'modalFluxoParcelas';
            modal.innerHTML = `
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header bg-dark text-white">
                            <h5 class="modal-title"><i class="bi bi-calendar-check"></i> Fluxo de Parcelas - Próximos ${meses} Meses</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="conteudoFluxoParcelas"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }
        
        document.getElementById('conteudoFluxoParcelas').innerHTML = html;
        new bootstrap.Modal(document.getElementById('modalFluxoParcelas')).show();
        
    } catch (error) {
        console.error('❌ Erro ao carregar fluxo:', error);
        mostrarNotificacao('❌ Erro ao carregar fluxo de parcelas', 'danger');
    }
}

// ========== FUNÇÕES DE UTILITÁRIOS ==========
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
window.verFluxoParcelas = verFluxoParcelas;
window.formatarMoeda = formatarMoeda;
window.mostrarNotificacao = mostrarNotificacao;