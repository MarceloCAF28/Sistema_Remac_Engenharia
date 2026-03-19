from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime, timedelta, date
import os
import pandas as pd
from io import BytesIO
import traceback
import os
from flask import Flask
from flask_cors import CORS

# Importar db e modelos
from database import db
from models import *

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configurações
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, '..', 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ========== FUNÇÕES DE INICIALIZAÇÃO ==========
def criar_categorias_padrao():
    """Cria categorias de despesa padrão"""
    categorias = [
        {'nome': 'COMPRAS DE OBRA', 'tipo': 'VARIÁVEL'},
        {'nome': 'MÃO DE OBRA', 'tipo': 'VARIÁVEL'},
        {'nome': 'IMPOSTOS OBRAS', 'tipo': 'VARIÁVEL'},
        {'nome': 'IMPOSTOS ESCRITÓRIO', 'tipo': 'FIXA'},
        {'nome': 'ÁGUA/ENERGIA', 'tipo': 'FIXA'},
        {'nome': 'IPTU IMÓVEIS/TAXAS', 'tipo': 'FIXA'},
        {'nome': 'COLABORADORES - ESC', 'tipo': 'FIXA'},
        {'nome': 'PRÓ LABORE - SÓCIO', 'tipo': 'FIXA'},
        {'nome': 'CONTADOR', 'tipo': 'FIXA'},
        {'nome': 'CAPACITAÇÃO', 'tipo': 'VARIÁVEL'},
        {'nome': 'LIMPEZA ESCRITÓRIO', 'tipo': 'FIXA'},
        {'nome': 'CUSTOS COM ESCRITÓRIO', 'tipo': 'VARIÁVEL'},
        {'nome': 'EQUIPAMENTOS / NOVOS', 'tipo': 'VARIÁVEL'},
        {'nome': 'ANUIDADES/ FILIAÇÕES', 'tipo': 'FIXA'},
        {'nome': 'DESLOCAMENTO / ESTACIONAMENTO', 'tipo': 'VARIÁVEL'},
        {'nome': 'CUSTOS COM VEICULO', 'tipo': 'VARIÁVEL'},
        {'nome': 'PAGAMENTO DE CLIENTE', 'tipo': 'VARIÁVEL'},
        {'nome': 'INVESTIMENTO', 'tipo': 'VARIÁVEL'},
        {'nome': 'MARKETING', 'tipo': 'VARIÁVEL'},
        {'nome': 'ALUGUEL DE EQUIPAMENTO', 'tipo': 'VARIÁVEL'},
        {'nome': 'MANUTENÇÃO EQUIPAMENTOS', 'tipo': 'VARIÁVEL'},
    ]
    
    with app.app_context():
        for cat in categorias:
            if not CategoriaDespesa.query.filter_by(nome=cat['nome']).first():
                nova_cat = CategoriaDespesa(nome=cat['nome'], tipo=cat['tipo'])
                db.session.add(nova_cat)
        db.session.commit()
        print("✅ Categorias padrão criadas")

def criar_contas_padrao():
    """Cria contas bancárias padrão"""
    contas = [
        {'nome': 'Caixa', 'banco': 'Dinheiro em espécie', 'tipo': 'CAIXA', 'saldo_inicial': 0},
        {'nome': 'Banco do Brasil', 'banco': 'Banco do Brasil', 'tipo': 'CORRENTE', 'saldo_inicial': 0},
        {'nome': 'Caixa Econômica', 'banco': 'Caixa Econômica Federal', 'tipo': 'CORRENTE', 'saldo_inicial': 0},
        {'nome': 'Bradesco', 'banco': 'Bradesco', 'tipo': 'CORRENTE', 'saldo_inicial': 0},
        {'nome': 'Itaú', 'banco': 'Itaú', 'tipo': 'CORRENTE', 'saldo_inicial': 0},
        {'nome': 'PagBank', 'banco': 'PagBank', 'tipo': 'DIGITAL', 'saldo_inicial': 0},
        {'nome': 'Mercado Pago', 'banco': 'Mercado Pago', 'tipo': 'DIGITAL', 'saldo_inicial': 0},
    ]
    
    with app.app_context():
        for conta in contas:
            if not ContaBancaria.query.filter_by(nome=conta['nome']).first():
                nova_conta = ContaBancaria(
                    nome=conta['nome'],
                    banco=conta['banco'],
                    tipo=conta['tipo'],
                    saldo_inicial=conta['saldo_inicial'],
                    saldo_atual=conta['saldo_inicial']
                )
                db.session.add(nova_conta)
        db.session.commit()
        print("✅ Contas bancárias padrão criadas")

def criar_formas_pagamento_padrao():
    """Cria formas de pagamento padrão"""
    formas = [
        {'nome': 'DINHEIRO', 'descricao': 'Pagamento em espécie', 'permite_parcelamento': False, 'parcelas_maximas': 1},
        {'nome': 'PIX', 'descricao': 'Pagamento via PIX', 'permite_parcelamento': False, 'parcelas_maximas': 1},
        {'nome': 'BOLETO', 'descricao': 'Boleto bancário', 'permite_parcelamento': True, 'parcelas_maximas': 12},
        {'nome': 'CARTÃO DE CRÉDITO', 'descricao': 'Cartão de crédito', 'permite_parcelamento': True, 'parcelas_maximas': 12},
        {'nome': 'CARTÃO DE DÉBITO', 'descricao': 'Cartão de débito', 'permite_parcelamento': False, 'parcelas_maximas': 1},
        {'nome': 'TRANSFERÊNCIA', 'descricao': 'Transferência bancária', 'permite_parcelamento': False, 'parcelas_maximas': 1},
        {'nome': 'CHEQUE', 'descricao': 'Cheque', 'permite_parcelamento': True, 'parcelas_maximas': 6},
    ]
    
    with app.app_context():
        for forma in formas:
            if not FormaPagamento.query.filter_by(nome=forma['nome']).first():
                nova_forma = FormaPagamento(
                    nome=forma['nome'],
                    descricao=forma['descricao'],
                    permite_parcelamento=forma['permite_parcelamento'],
                    parcelas_maximas=forma['parcelas_maximas']
                )
                db.session.add(nova_forma)
        db.session.commit()
        print("✅ Formas de pagamento padrão criadas")

with app.app_context():
    db.create_all()
    print("✅ Banco de dados criado")
    criar_categorias_padrao()
    criar_contas_padrao()
    criar_formas_pagamento_padrao()

# ========== FUNÇÃO PARA ATUALIZAR STATUS DAS PARCELAS ==========
def atualizar_status_parcelas():
    """Atualiza o status de todas as parcelas baseado na data atual"""
    try:
        hoje = date.today()
        atualizacoes = 0
        
        # Atualizar parcelas de receita
        parcelas_receita = ParcelaReceita.query.filter(
            ParcelaReceita.status.in_(['PENDENTE', 'PARCIAL'])
        ).all()
        
        for p in parcelas_receita:
            status_antigo = p.status
            p.atualizar_status()
            if status_antigo != p.status:
                atualizacoes += 1
        
        # Atualizar parcelas de despesa
        parcelas_despesa = ParcelaDespesa.query.filter(
            ParcelaDespesa.status.in_(['PENDENTE', 'PARCIAL'])
        ).all()
        
        for p in parcelas_despesa:
            status_antigo = p.status
            p.atualizar_status()
            if status_antigo != p.status:
                atualizacoes += 1
        
        # Atualizar parcelas de obra
        parcelas_obra = ParcelaObra.query.filter(
            ParcelaObra.status.in_(['PENDENTE', 'PARCIAL'])
        ).all()
        
        for p in parcelas_obra:
            status_antigo = p.status
            p.atualizar_status()
            if status_antigo != p.status:
                atualizacoes += 1
        
        db.session.commit()
        if atualizacoes > 0:
            print(f"✅ {atualizacoes} parcelas tiveram status atualizado para {hoje.strftime('%d/%m/%Y')}")
    except Exception as e:
        print(f"❌ Erro ao atualizar status das parcelas: {e}")
        traceback.print_exc()

# ========== FUNÇÃO AUXILIAR PARA REGISTRAR MOVIMENTAÇÃO ==========
def registrar_movimentacao_conta(conta_id, data, descricao, tipo, valor, categoria, referencia_id=None, parcela_id=None, observacao=None):
    """Função auxiliar para registrar movimentação em conta"""
    try:
        mov = MovimentacaoConta(
            conta_id=conta_id,
            data=data,
            descricao=descricao,
            tipo=tipo,
            valor=valor,
            categoria=categoria,
            referencia_id=referencia_id,
            parcela_id=parcela_id,
            observacao=observacao
        )
        db.session.add(mov)
        
        # Atualizar saldo da conta
        conta = ContaBancaria.query.get(conta_id)
        if conta:
            if tipo == 'ENTRADA':
                conta.saldo_atual += valor
                print(f"💰 Saldo da conta {conta.nome} aumentou em R$ {valor}")
            else:
                conta.saldo_atual -= valor
                print(f"💰 Saldo da conta {conta.nome} diminuiu em R$ {valor}")
        
        return mov
    except Exception as e:
        print(f"❌ Erro ao registrar movimentação: {e}")
        traceback.print_exc()
        return None

# ========== FUNÇÃO PARA GERAR PARCELAS ==========
def gerar_parcelas_receita(receita_id, total_parcelas, valor_total, data_primeira_parcela, forma_pagamento_id=None, conta_id=None):
    """Gera as parcelas de uma receita"""
    try:
        receita = Receita.query.get(receita_id)
        if not receita:
            return False
        
        valor_parcela = valor_total / total_parcelas
        
        for i in range(1, total_parcelas + 1):
            # Calcular data de vencimento (adicionar meses)
            data_vencimento = data_primeira_parcela
            if i > 1:
                mes = data_primeira_parcela.month + (i - 1)
                ano = data_primeira_parcela.year
                while mes > 12:
                    mes -= 12
                    ano += 1
                try:
                    data_vencimento = date(ano, mes, data_primeira_parcela.day)
                except ValueError:
                    ultimo_dia = (date(ano, mes + 1, 1) - timedelta(days=1)).day if mes < 12 else 31
                    data_vencimento = date(ano, mes, min(data_primeira_parcela.day, ultimo_dia))
            
            parcela = ParcelaReceita(
                receita_id=receita_id,
                numero_parcela=i,
                total_parcelas=total_parcelas,
                data_vencimento=data_vencimento,
                valor=valor_parcela,
                forma_pagamento_id=forma_pagamento_id,
                conta_id=conta_id,
                status='PENDENTE'
            )
            db.session.add(parcela)
        
        return True
    except Exception as e:
        print(f"❌ Erro ao gerar parcelas da receita: {e}")
        traceback.print_exc()
        return False

def gerar_parcelas_despesa(despesa_id, total_parcelas, valor_total, data_primeira_parcela, forma_pagamento_id=None, conta_id=None):
    """Gera as parcelas de uma despesa"""
    try:
        despesa = Despesa.query.get(despesa_id)
        if not despesa:
            return False
        
        valor_parcela = valor_total / total_parcelas
        
        for i in range(1, total_parcelas + 1):
            data_vencimento = data_primeira_parcela
            if i > 1:
                mes = data_primeira_parcela.month + (i - 1)
                ano = data_primeira_parcela.year
                while mes > 12:
                    mes -= 12
                    ano += 1
                try:
                    data_vencimento = date(ano, mes, data_primeira_parcela.day)
                except ValueError:
                    ultimo_dia = (date(ano, mes + 1, 1) - timedelta(days=1)).day if mes < 12 else 31
                    data_vencimento = date(ano, mes, min(data_primeira_parcela.day, ultimo_dia))
            
            parcela = ParcelaDespesa(
                despesa_id=despesa_id,
                numero_parcela=i,
                total_parcelas=total_parcelas,
                data_vencimento=data_vencimento,
                valor=valor_parcela,
                forma_pagamento_id=forma_pagamento_id,
                conta_id=conta_id,
                status='PENDENTE'
            )
            db.session.add(parcela)
        
        return True
    except Exception as e:
        print(f"❌ Erro ao gerar parcelas da despesa: {e}")
        traceback.print_exc()
        return False

def gerar_parcelas_obra(obra_id, total_parcelas, valor_total, data_primeira_parcela, forma_pagamento_id=None, conta_id=None):
    """Gera as parcelas do contrato de uma obra"""
    try:
        obra = Obra.query.get(obra_id)
        if not obra:
            return False
        
        valor_parcela = valor_total / total_parcelas
        
        for i in range(1, total_parcelas + 1):
            data_vencimento = data_primeira_parcela
            if i > 1:
                mes = data_primeira_parcela.month + (i - 1)
                ano = data_primeira_parcela.year
                while mes > 12:
                    mes -= 12
                    ano += 1
                try:
                    data_vencimento = date(ano, mes, data_primeira_parcela.day)
                except ValueError:
                    ultimo_dia = (date(ano, mes + 1, 1) - timedelta(days=1)).day if mes < 12 else 31
                    data_vencimento = date(ano, mes, min(data_primeira_parcela.day, ultimo_dia))
            
            parcela = ParcelaObra(
                obra_id=obra_id,
                numero_parcela=i,
                total_parcelas=total_parcelas,
                data_vencimento=data_vencimento,
                valor=valor_parcela,
                forma_pagamento_id=forma_pagamento_id,
                conta_id=conta_id,
                status='PENDENTE'
            )
            db.session.add(parcela)
        
        return True
    except Exception as e:
        print(f"❌ Erro ao gerar parcelas da obra: {e}")
        traceback.print_exc()
        return False

# ========== ROTAS DE FORMAS DE PAGAMENTO ==========

@app.route('/api/formas-pagamento', methods=['GET'])
def listar_formas_pagamento():
    """Lista todas as formas de pagamento cadastradas"""
    try:
        formas = FormaPagamento.query.order_by(FormaPagamento.nome).all()
        resultado = [{
            'id': f.id,
            'nome': f.nome,
            'descricao': f.descricao,
            'permite_parcelamento': f.permite_parcelamento,
            'parcelas_maximas': f.parcelas_maximas
        } for f in formas]
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao listar formas de pagamento:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/formas-pagamento', methods=['POST'])
def criar_forma_pagamento():
    """Cria uma nova forma de pagamento"""
    try:
        data = request.json
        if FormaPagamento.query.filter_by(nome=data.get('nome')).first():
            return jsonify({'error': 'Forma de pagamento já existe'}), 400
        
        forma = FormaPagamento(
            nome=data.get('nome'),
            descricao=data.get('descricao'),
            permite_parcelamento=data.get('permite_parcelamento', True),
            parcelas_maximas=data.get('parcelas_maximas', 12)
        )
        db.session.add(forma)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Forma de pagamento criada com sucesso!', 'forma_id': forma.id})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao criar forma de pagamento:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/formas-pagamento/<int:forma_id>', methods=['PUT'])
def atualizar_forma_pagamento(forma_id):
    try:
        forma = FormaPagamento.query.get_or_404(forma_id)
        data = request.json
        forma.nome = data.get('nome', forma.nome)
        forma.descricao = data.get('descricao', forma.descricao)
        forma.permite_parcelamento = data.get('permite_parcelamento', forma.permite_parcelamento)
        forma.parcelas_maximas = data.get('parcelas_maximas', forma.parcelas_maximas)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Forma de pagamento atualizada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao atualizar forma de pagamento:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/formas-pagamento/<int:forma_id>', methods=['DELETE'])
def deletar_forma_pagamento(forma_id):
    try:
        forma = FormaPagamento.query.get_or_404(forma_id)
        db.session.delete(forma)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Forma de pagamento deletada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao deletar forma de pagamento:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ========== ROTAS DE CONTAS BANCÁRIAS ==========

@app.route('/api/contas', methods=['GET'])
def listar_contas():
    try:
        contas = ContaBancaria.query.order_by(ContaBancaria.nome).all()
        for conta in contas:
            conta.calcular_saldo()
        db.session.commit()
        
        resultado = [{
            'id': c.id,
            'nome': c.nome,
            'banco': c.banco,
            'agencia': c.agencia,
            'numero_conta': c.numero_conta,
            'tipo': c.tipo,
            'saldo_inicial': c.saldo_inicial,
            'saldo_atual': c.saldo_atual,
            'observacao': c.observacao
        } for c in contas]
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao listar contas:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas', methods=['POST'])
def criar_conta():
    try:
        data = request.json
        conta = ContaBancaria(
            nome=data.get('nome'),
            banco=data.get('banco'),
            agencia=data.get('agencia'),
            numero_conta=data.get('numero_conta'),
            tipo=data.get('tipo'),
            saldo_inicial=float(data.get('saldo_inicial', 0)),
            saldo_atual=float(data.get('saldo_inicial', 0)),
            observacao=data.get('observacao')
        )
        db.session.add(conta)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Conta criada com sucesso!', 'conta_id': conta.id})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao criar conta:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas/<int:conta_id>', methods=['GET'])
def detalhe_conta(conta_id):
    try:
        conta = ContaBancaria.query.get_or_404(conta_id)
        conta.calcular_saldo()
        return jsonify({
            'id': conta.id,
            'nome': conta.nome,
            'banco': conta.banco,
            'agencia': conta.agencia,
            'numero_conta': conta.numero_conta,
            'tipo': conta.tipo,
            'saldo_inicial': conta.saldo_inicial,
            'saldo_atual': conta.saldo_atual,
            'observacao': conta.observacao
        })
    except Exception as e:
        print("❌ Erro ao buscar conta:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas/<int:conta_id>/extrato', methods=['GET'])
def extrato_conta(conta_id):
    try:
        print(f"🔍 Buscando extrato para conta ID: {conta_id}")
        
        conta = ContaBancaria.query.get_or_404(conta_id)
        print(f"✅ Conta encontrada: {conta.nome}")
        
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        
        query = MovimentacaoConta.query.filter_by(conta_id=conta_id)
        
        if mes and ano:
            query = query.filter(
                db.extract('month', MovimentacaoConta.data) == mes,
                db.extract('year', MovimentacaoConta.data) == ano
            )
        
        movimentacoes = query.order_by(MovimentacaoConta.data.desc()).all()
        print(f"📊 Encontradas {len(movimentacoes)} movimentações")
        
        resultado = [{
            'id': m.id,
            'data': m.data.strftime('%d/%m/%Y'),
            'descricao': m.descricao,
            'tipo': m.tipo,
            'valor': m.valor,
            'categoria': m.categoria,
            'observacao': m.observacao
        } for m in movimentacoes]
        
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao gerar extrato:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas/<int:conta_id>', methods=['PUT'])
def atualizar_conta(conta_id):
    try:
        conta = ContaBancaria.query.get_or_404(conta_id)
        data = request.json
        
        conta.nome = data.get('nome', conta.nome)
        conta.banco = data.get('banco', conta.banco)
        conta.agencia = data.get('agencia', conta.agencia)
        conta.numero_conta = data.get('numero_conta', conta.numero_conta)
        conta.tipo = data.get('tipo', conta.tipo)
        conta.observacao = data.get('observacao', conta.observacao)
        
        if 'saldo_inicial' in data:
            diferenca = float(data['saldo_inicial']) - conta.saldo_inicial
            conta.saldo_inicial = float(data['saldo_inicial'])
            conta.saldo_atual += diferenca
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Conta atualizada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao atualizar conta:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contas/<int:conta_id>', methods=['DELETE'])
def deletar_conta(conta_id):
    try:
        conta = ContaBancaria.query.get_or_404(conta_id)
        db.session.delete(conta)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Conta deletada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao deletar conta:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ========== ROTAS DE CATEGORIAS ==========

@app.route('/api/categorias', methods=['GET'])
def listar_categorias():
    try:
        categorias = CategoriaDespesa.query.all()
        resultado = [{'id': c.id, 'nome': c.nome, 'tipo': c.tipo} for c in categorias]
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao listar categorias:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ========== ROTAS DE ITENS ABC ==========

@app.route('/api/abc', methods=['GET'])
def listar_itens_abc():
    try:
        obra_id = request.args.get('obra_id')
        query = ItemABC.query
        if obra_id:
            query = query.filter_by(obra_id=obra_id)
        
        itens = query.order_by(ItemABC.codigo).all()
        
        resultado = [{
            'id': i.id,
            'obra_id': i.obra_id,
            'obra_nome': i.obra.nome if i.obra else '',
            'codigo': i.codigo,
            'descricao': i.descricao,
            'unidade': i.unidade,
            'quantidade_prevista': i.quantidade_prevista,
            'valor_unitario': i.valor_unitario,
            'valor_total_previsto': i.valor_total_previsto,
            'valor_total_real': i.valor_total_real,
            'desvio': i.desvio,
            'percentual_desvio': round(i.percentual_desvio, 2)
        } for i in itens]
        
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao listar itens ABC:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/abc', methods=['POST'])
def criar_item_abc():
    try:
        data = request.json
        
        if not data.get('obra_id'):
            return jsonify({'error': 'Obra é obrigatória'}), 400
        if not data.get('codigo'):
            return jsonify({'error': 'Código é obrigatório'}), 400
        if not data.get('descricao'):
            return jsonify({'error': 'Descrição é obrigatória'}), 400
        
        item = ItemABC(
            obra_id=int(data.get('obra_id')),
            codigo=data.get('codigo'),
            descricao=data.get('descricao'),
            unidade=data.get('unidade'),
            quantidade_prevista=float(data.get('quantidade_prevista', 0)),
            valor_unitario=float(data.get('valor_unitario', 0)),
            valor_total_previsto=float(data.get('quantidade_prevista', 0)) * float(data.get('valor_unitario', 0))
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Item ABC criado com sucesso!', 'item_id': item.id})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao criar item ABC:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/abc/<int:item_id>', methods=['PUT'])
def atualizar_item_abc(item_id):
    try:
        item = ItemABC.query.get_or_404(item_id)
        data = request.json
        
        item.codigo = data.get('codigo', item.codigo)
        item.descricao = data.get('descricao', item.descricao)
        item.unidade = data.get('unidade', item.unidade)
        item.quantidade_prevista = float(data.get('quantidade_prevista', item.quantidade_prevista))
        item.valor_unitario = float(data.get('valor_unitario', item.valor_unitario))
        item.valor_total_previsto = item.quantidade_prevista * item.valor_unitario
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item ABC atualizado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao atualizar item ABC:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/abc/<int:item_id>', methods=['DELETE'])
def deletar_item_abc(item_id):
    try:
        item = ItemABC.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item ABC deletado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao deletar item ABC:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/obras/<int:obra_id>/analise-abc', methods=['GET'])
def analise_abc_obra(obra_id):
    try:
        obra = Obra.query.get_or_404(obra_id)
        analise = obra.analise_abc
        return jsonify({'obra_id': obra.id, 'obra_nome': obra.nome, 'itens': analise})
    except Exception as e:
        print("❌ Erro ao gerar análise ABC:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ========== ROTAS DE OBRAS ==========

@app.route('/api/obras', methods=['GET'])
def listar_obras():
    try:
        atualizar_status_parcelas()
        
        obras = Obra.query.order_by(Obra.created_at.desc()).all()
        resultado = []
        for obra in obras:
            forma_pagto = None
            if obra.forma_pagamento_id:
                forma = FormaPagamento.query.get(obra.forma_pagamento_id)
                forma_pagto = forma.nome if forma else None
            
            conta_nome = None
            if obra.conta_id:
                conta = ContaBancaria.query.get(obra.conta_id)
                conta_nome = conta.nome if conta else None
            
            resultado.append({
                'id': obra.id,
                'nome': obra.nome,
                'cliente': obra.cliente,
                'contrato': obra.contrato,
                'descricao': obra.descricao,
                'data_inicio': obra.data_inicio.strftime('%d/%m/%Y') if obra.data_inicio else '',
                'data_fim': obra.data_fim.strftime('%d/%m/%Y') if obra.data_fim else '',
                'status': obra.status,
                'valor_total_contrato': obra.valor_total_contrato,
                'quantidade_parcelas': obra.quantidade_parcelas,
                'forma_pagamento_id': obra.forma_pagamento_id,
                'forma_pagamento_nome': forma_pagto,
                'conta_id': obra.conta_id,
                'conta_nome': conta_nome,
                'data_primeira_parcela': obra.data_primeira_parcela.strftime('%Y-%m-%d') if obra.data_primeira_parcela else None,
                'total_receitas': obra.total_receitas,
                'total_despesas': obra.total_despesas,
                'lucro': obra.lucro,
                'margem_lucro': round(obra.margem_lucro, 2),
                'total_materiais': obra.total_materiais,
                'total_mao_obra': obra.total_mao_obra,
                'total_a_receber': obra.total_a_receber,
                'qtd_itens_abc': len(obra.itens_abc),
                'created_at': obra.created_at.strftime('%d/%m/%Y')
            })
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao listar obras:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/obras', methods=['POST'])
def criar_obra():
    try:
        data = request.json
        print(f"📥 Dados recebidos: {data}")
        
        if not data.get('nome'):
            return jsonify({'error': 'Nome da obra é obrigatório'}), 400
        if not data.get('cliente'):
            return jsonify({'error': 'Cliente é obrigatório'}), 400
        
        quantidade_parcelas = int(data.get('quantidade_parcelas', 1))
        if quantidade_parcelas > 1 and not data.get('data_primeira_parcela'):
            return jsonify({'error': 'Para parcelamento, informe a data da primeira parcela'}), 400
        
        obra = Obra(
            nome=data.get('nome'),
            cliente=data.get('cliente'),
            contrato=data.get('contrato'),
            descricao=data.get('descricao'),
            data_inicio=datetime.strptime(data.get('data_inicio'), '%Y-%m-%d').date() if data.get('data_inicio') else None,
            status=data.get('status', 'EM ANDAMENTO'),
            valor_total_contrato=float(data.get('valor_total_contrato', 0)),
            quantidade_parcelas=quantidade_parcelas,
            forma_pagamento_id=int(data.get('forma_pagamento_id')) if data.get('forma_pagamento_id') else None,
            conta_id=int(data.get('conta_id')) if data.get('conta_id') else None,
            data_primeira_parcela=datetime.strptime(data.get('data_primeira_parcela'), '%Y-%m-%d').date() if data.get('data_primeira_parcela') else None,
            observacao_parcelas=data.get('observacao_parcelas')
        )
        
        db.session.add(obra)
        db.session.flush()
        
        # Gerar parcelas do contrato
        if obra.quantidade_parcelas > 1 and obra.valor_total_contrato > 0 and obra.data_primeira_parcela:
            print(f"📊 Gerando {obra.quantidade_parcelas} parcelas para obra ID {obra.id}")
            gerar_parcelas_obra(
                obra_id=obra.id,
                total_parcelas=obra.quantidade_parcelas,
                valor_total=obra.valor_total_contrato,
                data_primeira_parcela=obra.data_primeira_parcela,
                forma_pagamento_id=obra.forma_pagamento_id,
                conta_id=obra.conta_id
            )
        elif obra.valor_total_contrato > 0:
            # Se for à vista, criar uma única parcela
            data_vencimento = obra.data_inicio if obra.data_inicio else obra.data_primeira_parcela if obra.data_primeira_parcela else date.today()
            parcela = ParcelaObra(
                obra_id=obra.id,
                numero_parcela=1,
                total_parcelas=1,
                data_vencimento=data_vencimento,
                valor=obra.valor_total_contrato,
                forma_pagamento_id=obra.forma_pagamento_id,
                conta_id=obra.conta_id,
                status='PENDENTE'
            )
            db.session.add(parcela)
            print(f"📊 Gerada 1 parcela à vista para obra ID {obra.id}")
        
        db.session.commit()
        print(f"✅ Obra criada com sucesso! ID: {obra.id}")
        
        return jsonify({'success': True, 'message': 'Obra criada com sucesso!', 'obra_id': obra.id})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao criar obra:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/obras/<int:obra_id>', methods=['GET'])
def detalhe_obra(obra_id):
    try:
        obra = Obra.query.get_or_404(obra_id)
        
        forma_pagto = None
        if obra.forma_pagamento_id:
            forma = FormaPagamento.query.get(obra.forma_pagamento_id)
            forma_pagto = forma.nome if forma else None
        
        conta_nome = None
        if obra.conta_id:
            conta = ContaBancaria.query.get(obra.conta_id)
            conta_nome = conta.nome if conta else None
        
        resumo = {
            'id': obra.id,
            'nome': obra.nome,
            'cliente': obra.cliente,
            'contrato': obra.contrato,
            'descricao': obra.descricao,
            'data_inicio': obra.data_inicio.strftime('%d/%m/%Y') if obra.data_inicio else '',
            'data_fim': obra.data_fim.strftime('%d/%m/%Y') if obra.data_fim else '',
            'status': obra.status,
            'valor_total_contrato': obra.valor_total_contrato,
            'quantidade_parcelas': obra.quantidade_parcelas,
            'forma_pagamento_id': obra.forma_pagamento_id,
            'forma_pagamento_nome': forma_pagto,
            'conta_id': obra.conta_id,
            'conta_nome': conta_nome,
            'data_primeira_parcela': obra.data_primeira_parcela.strftime('%Y-%m-%d') if obra.data_primeira_parcela else None,
            'total_receitas': obra.total_receitas,
            'total_despesas': obra.total_despesas,
            'total_materiais': obra.total_materiais,
            'total_mao_obra': obra.total_mao_obra,
            'total_a_receber': obra.total_a_receber,
            'lucro': obra.lucro,
            'margem_lucro': round(obra.margem_lucro, 2)
        }
        
        receitas = []
        for r in obra.receitas:
            forma = FormaPagamento.query.get(r.forma_pagamento_id) if r.forma_pagamento_id else None
            conta = ContaBancaria.query.get(r.conta_id) if r.conta_id else None
            
            receitas.append({
                'id': r.id,
                'data': r.data.strftime('%d/%m/%Y') if r.data else '',
                'descricao': r.descricao,
                'valor_total': r.valor_total,
                'valor_recebido': r.valor_recebido,
                'quantidade_parcelas': r.quantidade_parcelas,
                'status': r.status,
                'tipo': r.tipo,
                'forma_pagamento_nome': forma.nome if forma else None,
                'conta_nome': conta.nome if conta else None,
                'centro_custo': r.centro_custo
            })
        
        despesas = []
        for d in obra.despesas:
            forma = FormaPagamento.query.get(d.forma_pagamento_id) if d.forma_pagamento_id else None
            conta = ContaBancaria.query.get(d.conta_id) if d.conta_id else None
            categoria = CategoriaDespesa.query.get(d.categoria_id) if d.categoria_id else None
            
            despesas.append({
                'id': d.id,
                'data': d.data.strftime('%d/%m/%Y') if d.data else '',
                'descricao': d.descricao,
                'fornecedor': d.fornecedor,
                'valor_total': d.valor_total,
                'valor_pago': d.valor_pago,
                'quantidade_parcelas': d.quantidade_parcelas,
                'status': d.status,
                'categoria': categoria.nome if categoria else '',
                'tipo': d.tipo,
                'forma_pagamento_nome': forma.nome if forma else None,
                'conta_nome': conta.nome if conta else None,
                'centro_custo': d.centro_custo
            })
        
        materiais = []
        for m in obra.materiais:
            forma = FormaPagamento.query.get(m.forma_pagamento_id) if m.forma_pagamento_id else None
            conta = ContaBancaria.query.get(m.conta_id) if m.conta_id else None
            item_abc = ItemABC.query.get(m.item_abc_id) if m.item_abc_id else None
            
            materiais.append({
                'id': m.id,
                'data': m.data.strftime('%d/%m/%Y') if m.data else '',
                'descricao': m.descricao,
                'fornecedor': m.fornecedor,
                'quantidade': m.quantidade,
                'unidade': m.unidade,
                'valor_unitario': m.valor_unitario,
                'valor_total': m.valor_total,
                'valor_pago': m.valor_pago,
                'item_abc_id': m.item_abc_id,
                'item_abc_codigo': item_abc.codigo if item_abc else None,
                'forma_pagamento_nome': forma.nome if forma else None,
                'conta_nome': conta.nome if conta else None,
                'centro_custo': m.centro_custo
            })
        
        mao_obra = []
        for mo in obra.mao_obra:
            forma = FormaPagamento.query.get(mo.forma_pagamento_id) if mo.forma_pagamento_id else None
            conta = ContaBancaria.query.get(mo.conta_id) if mo.conta_id else None
            item_abc = ItemABC.query.get(mo.item_abc_id) if mo.item_abc_id else None
            
            mao_obra.append({
                'id': mo.id,
                'data': mo.data.strftime('%d/%m/%Y') if mo.data else '',
                'descricao': mo.descricao,
                'funcionario': mo.funcionario,
                'funcao': mo.funcao,
                'horas_trabalhadas': mo.horas_trabalhadas,
                'valor_hora': mo.valor_hora,
                'valor_total': mo.valor_total,
                'valor_pago': mo.valor_pago,
                'item_abc_id': mo.item_abc_id,
                'item_abc_codigo': item_abc.codigo if item_abc else None,
                'forma_pagamento_nome': forma.nome if forma else None,
                'conta_nome': conta.nome if conta else None,
                'centro_custo': mo.centro_custo
            })
        
        return jsonify({'resumo': resumo, 'receitas': receitas, 'despesas': despesas, 'materiais': materiais, 'mao_obra': mao_obra})
    except Exception as e:
        print("❌ Erro ao carregar detalhes da obra:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/obras/<int:obra_id>', methods=['PUT'])
def atualizar_obra(obra_id):
    try:
        obra = Obra.query.get_or_404(obra_id)
        data = request.json
        
        obra.nome = data.get('nome', obra.nome)
        obra.cliente = data.get('cliente', obra.cliente)
        obra.contrato = data.get('contrato', obra.contrato)
        obra.descricao = data.get('descricao', obra.descricao)
        obra.status = data.get('status', obra.status)
        obra.valor_total_contrato = float(data.get('valor_total_contrato', obra.valor_total_contrato))
        
        if data.get('data_inicio'):
            obra.data_inicio = datetime.strptime(data.get('data_inicio'), '%Y-%m-%d').date()
        if data.get('data_fim'):
            obra.data_fim = datetime.strptime(data.get('data_fim'), '%Y-%m-%d').date()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Obra atualizada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao atualizar obra:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/obras/<int:obra_id>', methods=['DELETE'])
def deletar_obra(obra_id):
    try:
        obra = Obra.query.get_or_404(obra_id)
        db.session.delete(obra)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Obra deletada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao deletar obra:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
# ========== ROTAS DE RECEITAS ==========

@app.route('/api/receitas', methods=['GET'])
def listar_receitas():
    try:
        atualizar_status_parcelas()
        
        obra_id = request.args.get('obra_id')
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        
        query = Receita.query
        if obra_id:
            query = query.filter_by(obra_id=obra_id)
        if mes and ano:
            query = query.filter(
                db.extract('month', Receita.data) == mes,
                db.extract('year', Receita.data) == ano
            )
        
        receitas = query.order_by(Receita.data.desc()).all()
        resultado = []
        
        for r in receitas:
            forma_pagto = None
            if r.forma_pagamento_id:
                forma = FormaPagamento.query.get(r.forma_pagamento_id)
                forma_pagto = forma.nome if forma else None
            
            conta_nome = None
            if r.conta_id:
                conta = ContaBancaria.query.get(r.conta_id)
                conta_nome = conta.nome if conta else None
            
            resultado.append({
                'id': r.id,
                'obra_id': r.obra_id,
                'obra_nome': r.obra.nome if r.obra else '',
                'conta_id': r.conta_id,
                'conta_nome': conta_nome,
                'forma_pagamento_id': r.forma_pagamento_id,
                'forma_pagamento_nome': forma_pagto,
                'data': r.data.strftime('%Y-%m-%d'),
                'data_br': r.data.strftime('%d/%m/%Y'),
                'descricao': r.descricao,
                'valor_total': r.valor_total,
                'quantidade_parcelas': r.quantidade_parcelas,
                'valor_parcela': r.valor_parcela,
                'valor_recebido': r.valor_recebido,
                'status': r.status,
                'tipo': r.tipo,
                'centro_custo': r.centro_custo,
                'observacao': r.observacao
            })
        
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao listar receitas:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/receitas', methods=['POST'])
def criar_receita():
    try:
        data = request.json
        print(f"📥 Dados recebidos: {data}")
        
        if not data.get('obra_id'):
            return jsonify({'error': 'Obra é obrigatória'}), 400
        if not data.get('descricao'):
            return jsonify({'error': 'Descrição é obrigatória'}), 400
        if not data.get('valor_total') or float(data.get('valor_total')) <= 0:
            return jsonify({'error': 'Valor total deve ser maior que zero'}), 400
        
        quantidade_parcelas = int(data.get('quantidade_parcelas', 1))
        valor_total = float(data.get('valor_total'))
        
        if quantidade_parcelas > 1 and not data.get('data_primeira_parcela'):
            return jsonify({'error': 'Para parcelamento, informe a data da primeira parcela'}), 400
        
        receita = Receita(
            obra_id=int(data.get('obra_id')),
            conta_id=int(data.get('conta_id')) if data.get('conta_id') else None,
            forma_pagamento_id=int(data.get('forma_pagamento_id')) if data.get('forma_pagamento_id') else None,
            data=datetime.strptime(data.get('data'), '%Y-%m-%d').date(),
            descricao=data.get('descricao'),
            valor_total=valor_total,
            quantidade_parcelas=quantidade_parcelas,
            valor_parcela=valor_total / quantidade_parcelas if quantidade_parcelas > 0 else valor_total,
            data_primeira_parcela=datetime.strptime(data.get('data_primeira_parcela'), '%Y-%m-%d').date() if data.get('data_primeira_parcela') else None,
            tipo=data.get('tipo'),
            centro_custo=data.get('centro_custo'),
            observacao=data.get('observacao')
        )
        
        db.session.add(receita)
        db.session.flush()
        
        if quantidade_parcelas > 1 and receita.data_primeira_parcela:
            print(f"📊 Gerando {quantidade_parcelas} parcelas para receita ID {receita.id}")
            gerar_parcelas_receita(
                receita_id=receita.id,
                total_parcelas=quantidade_parcelas,
                valor_total=valor_total,
                data_primeira_parcela=receita.data_primeira_parcela,
                forma_pagamento_id=receita.forma_pagamento_id,
                conta_id=receita.conta_id
            )
        else:
            parcela = ParcelaReceita(
                receita_id=receita.id,
                numero_parcela=1,
                total_parcelas=1,
                data_vencimento=receita.data,
                valor=valor_total,
                forma_pagamento_id=receita.forma_pagamento_id,
                conta_id=receita.conta_id,
                status='PENDENTE'
            )
            db.session.add(parcela)
        
        db.session.commit()
        print(f"✅ Receita criada com sucesso! ID: {receita.id}")
        
        return jsonify({'success': True, 'message': 'Receita cadastrada com sucesso!', 'receita_id': receita.id})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao criar receita:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/receitas/<int:receita_id>', methods=['PUT'])
def atualizar_receita(receita_id):
    try:
        receita = Receita.query.get_or_404(receita_id)
        data = request.json
        
        receita.obra_id = int(data.get('obra_id'))
        receita.conta_id = int(data.get('conta_id')) if data.get('conta_id') else None
        receita.forma_pagamento_id = int(data.get('forma_pagamento_id')) if data.get('forma_pagamento_id') else None
        receita.data = datetime.strptime(data.get('data'), '%Y-%m-%d').date()
        receita.descricao = data.get('descricao')
        receita.valor_total = float(data.get('valor_total', 0))
        receita.tipo = data.get('tipo')
        receita.centro_custo = data.get('centro_custo')
        receita.observacao = data.get('observacao')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Receita atualizada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao atualizar receita:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/receitas/<int:receita_id>', methods=['DELETE'])
def deletar_receita(receita_id):
    try:
        receita = Receita.query.get_or_404(receita_id)
        db.session.delete(receita)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Receita deletada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao deletar receita:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ========== ROTAS DE DESPESAS ==========

@app.route('/api/despesas', methods=['GET'])
def listar_despesas():
    try:
        atualizar_status_parcelas()
        
        obra_id = request.args.get('obra_id')
        categoria_id = request.args.get('categoria_id')
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        tipo = request.args.get('tipo')
        
        query = Despesa.query
        
        if obra_id:
            query = query.filter_by(obra_id=obra_id)
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        if tipo:
            query = query.filter_by(tipo=tipo)
        if mes and ano:
            query = query.filter(
                db.extract('month', Despesa.data) == mes,
                db.extract('year', Despesa.data) == ano
            )
        
        despesas = query.order_by(Despesa.data.desc()).all()
        resultado = []
        
        for d in despesas:
            forma_pagto = None
            if d.forma_pagamento_id:
                forma = FormaPagamento.query.get(d.forma_pagamento_id)
                forma_pagto = forma.nome if forma else None
            
            conta_nome = None
            if d.conta_id:
                conta = ContaBancaria.query.get(d.conta_id)
                conta_nome = conta.nome if conta else None
            
            categoria_nome = None
            if d.categoria_id:
                categoria = CategoriaDespesa.query.get(d.categoria_id)
                categoria_nome = categoria.nome if categoria else None
            
            resultado.append({
                'id': d.id,
                'obra_id': d.obra_id,
                'obra_nome': d.obra.nome if d.obra else '',
                'conta_id': d.conta_id,
                'conta_nome': conta_nome,
                'forma_pagamento_id': d.forma_pagamento_id,
                'forma_pagamento_nome': forma_pagto,
                'data': d.data.strftime('%Y-%m-%d'),
                'data_br': d.data.strftime('%d/%m/%Y'),
                'descricao': d.descricao,
                'fornecedor': d.fornecedor,
                'valor_total': d.valor_total,
                'quantidade_parcelas': d.quantidade_parcelas,
                'valor_parcela': d.valor_parcela,
                'valor_pago': d.valor_pago,
                'status': d.status,
                'categoria_id': d.categoria_id,
                'categoria_nome': categoria_nome,
                'centro_custo': d.centro_custo,
                'tipo': d.tipo,
                'observacao': d.observacao
            })
        
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao listar despesas:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/despesas', methods=['POST'])
def criar_despesa():
    try:
        data = request.json
        print(f"📥 Dados recebidos: {data}")
        
        if not data.get('obra_id'):
            return jsonify({'error': 'Obra é obrigatória'}), 400
        if not data.get('descricao'):
            return jsonify({'error': 'Descrição é obrigatória'}), 400
        if not data.get('valor_total') or float(data.get('valor_total')) <= 0:
            return jsonify({'error': 'Valor total deve ser maior que zero'}), 400
        
        quantidade_parcelas = int(data.get('quantidade_parcelas', 1))
        valor_total = float(data.get('valor_total'))
        
        if quantidade_parcelas > 1 and not data.get('data_primeira_parcela'):
            return jsonify({'error': 'Para parcelamento, informe a data da primeira parcela'}), 400
        
        despesa = Despesa(
            obra_id=int(data.get('obra_id')),
            conta_id=int(data.get('conta_id')) if data.get('conta_id') else None,
            forma_pagamento_id=int(data.get('forma_pagamento_id')) if data.get('forma_pagamento_id') else None,
            data=datetime.strptime(data.get('data'), '%Y-%m-%d').date(),
            descricao=data.get('descricao'),
            fornecedor=data.get('fornecedor'),
            valor_total=valor_total,
            quantidade_parcelas=quantidade_parcelas,
            valor_parcela=valor_total / quantidade_parcelas if quantidade_parcelas > 0 else valor_total,
            data_primeira_parcela=datetime.strptime(data.get('data_primeira_parcela'), '%Y-%m-%d').date() if data.get('data_primeira_parcela') else None,
            categoria_id=int(data.get('categoria_id')) if data.get('categoria_id') else None,
            centro_custo=data.get('centro_custo'),
            tipo=data.get('tipo', 'OUTROS'),
            observacao=data.get('observacao')
        )
        
        db.session.add(despesa)
        db.session.flush()
        
        if quantidade_parcelas > 1 and despesa.data_primeira_parcela:
            print(f"📊 Gerando {quantidade_parcelas} parcelas para despesa ID {despesa.id}")
            gerar_parcelas_despesa(
                despesa_id=despesa.id,
                total_parcelas=quantidade_parcelas,
                valor_total=valor_total,
                data_primeira_parcela=despesa.data_primeira_parcela,
                forma_pagamento_id=despesa.forma_pagamento_id,
                conta_id=despesa.conta_id
            )
        else:
            parcela = ParcelaDespesa(
                despesa_id=despesa.id,
                numero_parcela=1,
                total_parcelas=1,
                data_vencimento=despesa.data,
                valor=valor_total,
                forma_pagamento_id=despesa.forma_pagamento_id,
                conta_id=despesa.conta_id,
                status='PENDENTE'
            )
            db.session.add(parcela)
        
        db.session.commit()
        print(f"✅ Despesa criada com sucesso! ID: {despesa.id}")
        
        return jsonify({'success': True, 'message': 'Despesa cadastrada com sucesso!', 'despesa_id': despesa.id})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao criar despesa:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/despesas/<int:despesa_id>', methods=['PUT'])
def atualizar_despesa(despesa_id):
    try:
        despesa = Despesa.query.get_or_404(despesa_id)
        data = request.json
        
        despesa.obra_id = int(data.get('obra_id'))
        despesa.conta_id = int(data.get('conta_id')) if data.get('conta_id') else None
        despesa.forma_pagamento_id = int(data.get('forma_pagamento_id')) if data.get('forma_pagamento_id') else None
        despesa.data = datetime.strptime(data.get('data'), '%Y-%m-%d').date()
        despesa.descricao = data.get('descricao')
        despesa.fornecedor = data.get('fornecedor')
        despesa.valor_total = float(data.get('valor_total', 0))
        despesa.categoria_id = int(data.get('categoria_id')) if data.get('categoria_id') else None
        despesa.centro_custo = data.get('centro_custo')
        despesa.tipo = data.get('tipo')
        despesa.observacao = data.get('observacao')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Despesa atualizada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao atualizar despesa:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/despesas/<int:despesa_id>', methods=['DELETE'])
def deletar_despesa(despesa_id):
    try:
        despesa = Despesa.query.get_or_404(despesa_id)
        db.session.delete(despesa)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Despesa deletada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao deletar despesa:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ========== ROTAS DE MATERIAIS ==========

@app.route('/api/materiais', methods=['GET'])
def listar_materiais():
    try:
        obra_id = request.args.get('obra_id')
        
        query = Material.query
        if obra_id:
            query = query.filter_by(obra_id=obra_id)
        
        materiais = query.order_by(Material.data.desc()).all()
        resultado = []
        
        for m in materiais:
            forma_pagto = None
            if m.forma_pagamento_id:
                forma = FormaPagamento.query.get(m.forma_pagamento_id)
                forma_pagto = forma.nome if forma else None
            
            conta_nome = None
            if m.conta_id:
                conta = ContaBancaria.query.get(m.conta_id)
                conta_nome = conta.nome if conta else None
            
            item_abc_codigo = None
            item_abc_descricao = None
            if m.item_abc_id:
                item_abc = ItemABC.query.get(m.item_abc_id)
                if item_abc:
                    item_abc_codigo = item_abc.codigo
                    item_abc_descricao = item_abc.descricao
            
            resultado.append({
                'id': m.id,
                'obra_id': m.obra_id,
                'obra_nome': m.obra.nome if m.obra else '',
                'conta_id': m.conta_id,
                'conta_nome': conta_nome,
                'forma_pagamento_id': m.forma_pagamento_id,
                'forma_pagamento_nome': forma_pagto,
                'item_abc_id': m.item_abc_id,
                'item_abc_codigo': item_abc_codigo,
                'item_abc_descricao': item_abc_descricao,
                'data': m.data.strftime('%Y-%m-%d'),
                'data_br': m.data.strftime('%d/%m/%Y'),
                'descricao': m.descricao,
                'fornecedor': m.fornecedor,
                'quantidade': m.quantidade,
                'unidade': m.unidade,
                'valor_unitario': m.valor_unitario,
                'valor_total': m.valor_total,
                'quantidade_parcelas': m.quantidade_parcelas,
                'data_primeira_parcela': m.data_primeira_parcela.strftime('%Y-%m-%d') if m.data_primeira_parcela else None,
                'valor_pago': m.valor_pago,
                'data_pagamento': m.data_pagamento.strftime('%Y-%m-%d') if m.data_pagamento else None,
                'item_associado': m.item_associado,
                'centro_custo': m.centro_custo,
                'observacao': m.observacao,
                'status': m.status
            })
        
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao listar materiais:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/materiais', methods=['POST'])
def criar_material():
    try:
        data = request.json
        print(f"📥 Dados recebidos: {data}")
        
        if not data.get('obra_id'):
            return jsonify({'error': 'Obra é obrigatória'}), 400
        if not data.get('descricao'):
            return jsonify({'error': 'Descrição é obrigatória'}), 400
        if not data.get('valor_total') or float(data.get('valor_total')) <= 0:
            return jsonify({'error': 'Valor total deve ser maior que zero'}), 400
        
        quantidade_parcelas = int(data.get('quantidade_parcelas', 1))
        data_primeira_parcela = data.get('data_primeira_parcela')
        
        if quantidade_parcelas > 1 and not data_primeira_parcela:
            return jsonify({'error': 'Para parcelamento, informe a data da primeira parcela'}), 400
        
        material = Material(
            obra_id=int(data.get('obra_id')),
            conta_id=int(data.get('conta_id')) if data.get('conta_id') else None,
            forma_pagamento_id=int(data.get('forma_pagamento_id')) if data.get('forma_pagamento_id') else None,
            item_abc_id=int(data.get('item_abc_id')) if data.get('item_abc_id') else None,
            data=datetime.strptime(data.get('data'), '%Y-%m-%d').date(),
            descricao=data.get('descricao'),
            fornecedor=data.get('fornecedor'),
            quantidade=float(data.get('quantidade')) if data.get('quantidade') else None,
            unidade=data.get('unidade'),
            valor_unitario=float(data.get('valor_unitario')) if data.get('valor_unitario') else None,
            valor_total=float(data.get('valor_total', 0)),
            quantidade_parcelas=quantidade_parcelas,
            data_primeira_parcela=datetime.strptime(data_primeira_parcela, '%Y-%m-%d').date() if data_primeira_parcela else None,
            valor_pago=float(data.get('valor_pago', 0)),
            data_pagamento=datetime.strptime(data.get('data_pagamento'), '%Y-%m-%d').date() if data.get('data_pagamento') else None,
            item_associado=data.get('item_associado'),
            centro_custo=data.get('centro_custo'),
            observacao=data.get('observacao')
        )
        
        db.session.add(material)
        db.session.commit()
        
        # Se tiver valor pago, registrar movimentação
        if material.valor_pago > 0 and material.conta_id:
            registrar_movimentacao_conta(
                conta_id=material.conta_id,
                data=material.data_pagamento or material.data,
                descricao=f"Pagamento Material: {material.descricao}",
                tipo='SAIDA',
                valor=material.valor_pago,
                categoria='MATERIAL',
                referencia_id=material.id,
                observacao=material.observacao
            )
        
        return jsonify({'success': True, 'message': 'Material cadastrado com sucesso!', 'material_id': material.id})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao cadastrar material:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/materiais/<int:material_id>', methods=['PUT'])
def atualizar_material(material_id):
    try:
        material = Material.query.get_or_404(material_id)
        data = request.json
        
        material.obra_id = int(data.get('obra_id'))
        material.conta_id = int(data.get('conta_id')) if data.get('conta_id') else None
        material.forma_pagamento_id = int(data.get('forma_pagamento_id')) if data.get('forma_pagamento_id') else None
        material.item_abc_id = int(data.get('item_abc_id')) if data.get('item_abc_id') else None
        material.data = datetime.strptime(data.get('data'), '%Y-%m-%d').date()
        material.descricao = data.get('descricao')
        material.fornecedor = data.get('fornecedor')
        material.quantidade = float(data.get('quantidade')) if data.get('quantidade') else None
        material.unidade = data.get('unidade')
        material.valor_unitario = float(data.get('valor_unitario')) if data.get('valor_unitario') else None
        material.valor_total = float(data.get('valor_total', 0))
        material.valor_pago = float(data.get('valor_pago', 0))
        material.data_pagamento = datetime.strptime(data.get('data_pagamento'), '%Y-%m-%d').date() if data.get('data_pagamento') else None
        material.item_associado = data.get('item_associado')
        material.centro_custo = data.get('centro_custo')
        material.observacao = data.get('observacao')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Material atualizado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao atualizar material:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/materiais/<int:material_id>', methods=['DELETE'])
def deletar_material(material_id):
    try:
        material = Material.query.get_or_404(material_id)
        db.session.delete(material)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Material deletado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao deletar material:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ========== ROTAS DE MÃO DE OBRA ==========

@app.route('/api/mao-obra', methods=['GET'])
def listar_mao_obra():
    try:
        obra_id = request.args.get('obra_id')
        
        query = MaoObra.query
        if obra_id:
            query = query.filter_by(obra_id=obra_id)
        
        mao_obra = query.order_by(MaoObra.data.desc()).all()
        resultado = []
        
        for m in mao_obra:
            forma_pagto = None
            if m.forma_pagamento_id:
                forma = FormaPagamento.query.get(m.forma_pagamento_id)
                forma_pagto = forma.nome if forma else None
            
            conta_nome = None
            if m.conta_id:
                conta = ContaBancaria.query.get(m.conta_id)
                conta_nome = conta.nome if conta else None
            
            item_abc_codigo = None
            item_abc_descricao = None
            if m.item_abc_id:
                item_abc = ItemABC.query.get(m.item_abc_id)
                if item_abc:
                    item_abc_codigo = item_abc.codigo
                    item_abc_descricao = item_abc.descricao
            
            resultado.append({
                'id': m.id,
                'obra_id': m.obra_id,
                'obra_nome': m.obra.nome if m.obra else '',
                'conta_id': m.conta_id,
                'conta_nome': conta_nome,
                'forma_pagamento_id': m.forma_pagamento_id,
                'forma_pagamento_nome': forma_pagto,
                'item_abc_id': m.item_abc_id,
                'item_abc_codigo': item_abc_codigo,
                'item_abc_descricao': item_abc_descricao,
                'data': m.data.strftime('%Y-%m-%d'),
                'data_br': m.data.strftime('%d/%m/%Y'),
                'descricao': m.descricao,
                'funcionario': m.funcionario,
                'funcao': m.funcao,
                'horas_trabalhadas': m.horas_trabalhadas,
                'valor_hora': m.valor_hora,
                'valor_total': m.valor_total,
                'quantidade_parcelas': m.quantidade_parcelas,
                'data_primeira_parcela': m.data_primeira_parcela.strftime('%Y-%m-%d') if m.data_primeira_parcela else None,
                'valor_pago': m.valor_pago,
                'data_pagamento': m.data_pagamento.strftime('%Y-%m-%d') if m.data_pagamento else None,
                'item_associado': m.item_associado,
                'centro_custo': m.centro_custo,
                'observacao': m.observacao,
                'status': m.status
            })
        
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao listar mão de obra:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/mao-obra', methods=['POST'])
def criar_mao_obra():
    try:
        data = request.json
        print(f"📥 Dados recebidos: {data}")
        
        if not data.get('obra_id'):
            return jsonify({'error': 'Obra é obrigatória'}), 400
        if not data.get('descricao'):
            return jsonify({'error': 'Descrição é obrigatória'}), 400
        if not data.get('valor_total') or float(data.get('valor_total')) <= 0:
            return jsonify({'error': 'Valor total deve ser maior que zero'}), 400
        
        quantidade_parcelas = int(data.get('quantidade_parcelas', 1))
        data_primeira_parcela = data.get('data_primeira_parcela')
        
        if quantidade_parcelas > 1 and not data_primeira_parcela:
            return jsonify({'error': 'Para parcelamento, informe a data da primeira parcela'}), 400
        
        mao_obra = MaoObra(
            obra_id=int(data.get('obra_id')),
            conta_id=int(data.get('conta_id')) if data.get('conta_id') else None,
            forma_pagamento_id=int(data.get('forma_pagamento_id')) if data.get('forma_pagamento_id') else None,
            item_abc_id=int(data.get('item_abc_id')) if data.get('item_abc_id') else None,
            data=datetime.strptime(data.get('data'), '%Y-%m-%d').date(),
            descricao=data.get('descricao'),
            funcionario=data.get('funcionario'),
            funcao=data.get('funcao'),
            horas_trabalhadas=float(data.get('horas_trabalhadas')) if data.get('horas_trabalhadas') else None,
            valor_hora=float(data.get('valor_hora')) if data.get('valor_hora') else None,
            valor_total=float(data.get('valor_total', 0)),
            quantidade_parcelas=quantidade_parcelas,
            data_primeira_parcela=datetime.strptime(data_primeira_parcela, '%Y-%m-%d').date() if data_primeira_parcela else None,
            valor_pago=float(data.get('valor_pago', 0)),
            data_pagamento=datetime.strptime(data.get('data_pagamento'), '%Y-%m-%d').date() if data.get('data_pagamento') else None,
            item_associado=data.get('item_associado'),
            centro_custo=data.get('centro_custo'),
            observacao=data.get('observacao')
        )
        
        db.session.add(mao_obra)
        db.session.commit()
        
        if mao_obra.valor_pago > 0 and mao_obra.conta_id:
            registrar_movimentacao_conta(
                conta_id=mao_obra.conta_id,
                data=mao_obra.data_pagamento or mao_obra.data,
                descricao=f"Pagamento Mão de Obra: {mao_obra.descricao}",
                tipo='SAIDA',
                valor=mao_obra.valor_pago,
                categoria='MAO_OBRA',
                referencia_id=mao_obra.id,
                observacao=mao_obra.observacao
            )
        
        return jsonify({'success': True, 'message': 'Mão de obra cadastrada com sucesso!', 'mao_obra_id': mao_obra.id})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao cadastrar mão de obra:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/mao-obra/<int:mao_obra_id>', methods=['PUT'])
def atualizar_mao_obra(mao_obra_id):
    try:
        mao_obra = MaoObra.query.get_or_404(mao_obra_id)
        data = request.json
        
        mao_obra.obra_id = int(data.get('obra_id'))
        mao_obra.conta_id = int(data.get('conta_id')) if data.get('conta_id') else None
        mao_obra.forma_pagamento_id = int(data.get('forma_pagamento_id')) if data.get('forma_pagamento_id') else None
        mao_obra.item_abc_id = int(data.get('item_abc_id')) if data.get('item_abc_id') else None
        mao_obra.data = datetime.strptime(data.get('data'), '%Y-%m-%d').date()
        mao_obra.descricao = data.get('descricao')
        mao_obra.funcionario = data.get('funcionario')
        mao_obra.funcao = data.get('funcao')
        mao_obra.horas_trabalhadas = float(data.get('horas_trabalhadas')) if data.get('horas_trabalhadas') else None
        mao_obra.valor_hora = float(data.get('valor_hora')) if data.get('valor_hora') else None
        mao_obra.valor_total = float(data.get('valor_total', 0))
        mao_obra.valor_pago = float(data.get('valor_pago', 0))
        mao_obra.data_pagamento = datetime.strptime(data.get('data_pagamento'), '%Y-%m-%d').date() if data.get('data_pagamento') else None
        mao_obra.item_associado = data.get('item_associado')
        mao_obra.centro_custo = data.get('centro_custo')
        mao_obra.observacao = data.get('observacao')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Mão de obra atualizada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao atualizar mão de obra:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/mao-obra/<int:mao_obra_id>', methods=['DELETE'])
def deletar_mao_obra(mao_obra_id):
    try:
        mao_obra = MaoObra.query.get_or_404(mao_obra_id)
        db.session.delete(mao_obra)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Mão de obra deletada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao deletar mão de obra:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
# ========== ROTAS DE PARCELAS ==========

@app.route('/api/parcelas/receita/<int:receita_id>', methods=['GET'])
def listar_parcelas_receita(receita_id):
    """Lista todas as parcelas de uma receita"""
    try:
        print(f"🔍 Buscando parcelas para receita ID: {receita_id}")
        
        receita = Receita.query.get(receita_id)
        if not receita:
            return jsonify({'error': 'Receita não encontrada'}), 404
        
        atualizar_status_parcelas()
        
        parcelas = ParcelaReceita.query.filter_by(receita_id=receita_id).order_by(ParcelaReceita.numero_parcela).all()
        print(f"✅ Encontradas {len(parcelas)} parcelas")
        
        resultado = []
        for p in parcelas:
            forma_nome = None
            if p.forma_pagamento_id:
                forma = FormaPagamento.query.get(p.forma_pagamento_id)
                forma_nome = forma.nome if forma else None
            
            conta_nome = None
            if p.conta_id:
                conta = ContaBancaria.query.get(p.conta_id)
                conta_nome = conta.nome if conta else None
            
            resultado.append({
                'id': p.id,
                'receita_id': p.receita_id,
                'numero_parcela': p.numero_parcela,
                'total_parcelas': p.total_parcelas,
                'data_vencimento': p.data_vencimento.strftime('%d/%m/%Y'),
                'data_vencimento_iso': p.data_vencimento.strftime('%Y-%m-%d'),
                'data_recebimento': p.data_recebimento.strftime('%d/%m/%Y') if p.data_recebimento else None,
                'valor': p.valor,
                'valor_recebido': p.valor_recebido,
                'forma_pagamento_id': p.forma_pagamento_id,
                'forma_pagamento_nome': forma_nome,
                'conta_id': p.conta_id,
                'conta_nome': conta_nome,
                'status': p.status,
                'dias_atraso': p.dias_atraso,
                'observacao': p.observacao
            })
        
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao listar parcelas da receita:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/parcelas/despesa/<int:despesa_id>', methods=['GET'])
def listar_parcelas_despesa(despesa_id):
    """Lista todas as parcelas de uma despesa"""
    try:
        print(f"🔍 Buscando parcelas para despesa ID: {despesa_id}")
        
        despesa = Despesa.query.get(despesa_id)
        if not despesa:
            return jsonify({'error': 'Despesa não encontrada'}), 404
        
        atualizar_status_parcelas()
        
        parcelas = ParcelaDespesa.query.filter_by(despesa_id=despesa_id).order_by(ParcelaDespesa.numero_parcela).all()
        print(f"✅ Encontradas {len(parcelas)} parcelas")
        
        resultado = []
        for p in parcelas:
            forma_nome = None
            if p.forma_pagamento_id:
                forma = FormaPagamento.query.get(p.forma_pagamento_id)
                forma_nome = forma.nome if forma else None
            
            conta_nome = None
            if p.conta_id:
                conta = ContaBancaria.query.get(p.conta_id)
                conta_nome = conta.nome if conta else None
            
            resultado.append({
                'id': p.id,
                'despesa_id': p.despesa_id,
                'numero_parcela': p.numero_parcela,
                'total_parcelas': p.total_parcelas,
                'data_vencimento': p.data_vencimento.strftime('%d/%m/%Y'),
                'data_vencimento_iso': p.data_vencimento.strftime('%Y-%m-%d'),
                'data_pagamento': p.data_pagamento.strftime('%d/%m/%Y') if p.data_pagamento else None,
                'valor': p.valor,
                'valor_pago': p.valor_pago,
                'forma_pagamento_id': p.forma_pagamento_id,
                'forma_pagamento_nome': forma_nome,
                'conta_id': p.conta_id,
                'conta_nome': conta_nome,
                'status': p.status,
                'dias_atraso': p.dias_atraso,
                'observacao': p.observacao
            })
        
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao listar parcelas da despesa:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/parcelas/obra/<int:obra_id>', methods=['GET'])
def listar_parcelas_obra(obra_id):
    """Lista todas as parcelas do contrato de uma obra"""
    try:
        print(f"🔍 Buscando parcelas para obra ID: {obra_id}")
        
        obra = Obra.query.get(obra_id)
        if not obra:
            print(f"❌ Obra {obra_id} não encontrada")
            return jsonify({'error': 'Obra não encontrada'}), 404
        
        atualizar_status_parcelas()
        
        parcelas = ParcelaObra.query.filter_by(obra_id=obra_id).order_by(ParcelaObra.numero_parcela).all()
        print(f"✅ Encontradas {len(parcelas)} parcelas")
        
        resultado = []
        for p in parcelas:
            forma_nome = None
            if p.forma_pagamento_id:
                forma = FormaPagamento.query.get(p.forma_pagamento_id)
                forma_nome = forma.nome if forma else None
            
            conta_nome = None
            if p.conta_id:
                conta = ContaBancaria.query.get(p.conta_id)
                conta_nome = conta.nome if conta else None
            
            resultado.append({
                'id': p.id,
                'obra_id': p.obra_id,
                'numero_parcela': p.numero_parcela,
                'total_parcelas': p.total_parcelas,
                'data_vencimento': p.data_vencimento.strftime('%d/%m/%Y'),
                'data_vencimento_iso': p.data_vencimento.strftime('%Y-%m-%d'),
                'data_recebimento': p.data_recebimento.strftime('%d/%m/%Y') if p.data_recebimento else None,
                'valor': p.valor,
                'valor_recebido': p.valor_recebido,
                'forma_pagamento_id': p.forma_pagamento_id,
                'forma_pagamento_nome': forma_nome,
                'conta_id': p.conta_id,
                'conta_nome': conta_nome,
                'status': p.status,
                'dias_atraso': p.dias_atraso,
                'observacao': p.observacao
            })
        
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao listar parcelas da obra:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/parcelas/receita/<int:parcela_id>/receber', methods=['POST'])
def receber_parcela(parcela_id):
    """Registra o recebimento de uma parcela"""
    try:
        print(f"🔍 Recebendo parcela ID: {parcela_id}")
        
        parcela = ParcelaReceita.query.get_or_404(parcela_id)
        data = request.json
        
        valor_recebido = float(data.get('valor_recebido', parcela.valor))
        data_recebimento = datetime.strptime(data.get('data_recebimento'), '%Y-%m-%d').date() if data.get('data_recebimento') else date.today()
        conta_id = data.get('conta_id')
        
        if not conta_id:
            return jsonify({'error': 'Conta de recebimento é obrigatória'}), 400
        
        print(f"💰 Valor: R$ {valor_recebido}")
        print(f"📅 Data: {data_recebimento}")
        print(f"🏦 Conta ID: {conta_id}")
        
        parcela.valor_recebido = valor_recebido
        parcela.data_recebimento = data_recebimento
        
        if data.get('forma_pagamento_id'):
            parcela.forma_pagamento_id = int(data.get('forma_pagamento_id'))
        if conta_id:
            parcela.conta_id = int(conta_id)
        if data.get('observacao'):
            parcela.observacao = data.get('observacao')
        
        parcela.atualizar_status()
        print(f"✅ Status atualizado: {parcela.status}")
        
        if conta_id and valor_recebido > 0:
            registrar_movimentacao_conta(
                conta_id=int(conta_id),
                data=data_recebimento,
                descricao=f"Recebimento - Parcela {parcela.numero_parcela}/{parcela.total_parcelas} - {parcela.receita.descricao}",
                tipo='ENTRADA',
                valor=valor_recebido,
                categoria='RECEITA',
                referencia_id=parcela.receita_id,
                parcela_id=parcela.id,
                observacao=parcela.observacao
            )
        
        db.session.commit()
        print("✅ Transação concluída com sucesso")
        
        return jsonify({'success': True, 'message': 'Recebimento registrado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao registrar recebimento da parcela:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/parcelas/despesa/<int:parcela_id>/pagar', methods=['POST'])
def pagar_parcela(parcela_id):
    """Registra o pagamento de uma parcela"""
    try:
        print(f"🔍 Pagando parcela ID: {parcela_id}")
        
        parcela = ParcelaDespesa.query.get_or_404(parcela_id)
        data = request.json
        
        valor_pago = float(data.get('valor_pago', parcela.valor))
        data_pagamento = datetime.strptime(data.get('data_pagamento'), '%Y-%m-%d').date() if data.get('data_pagamento') else date.today()
        conta_id = data.get('conta_id')
        
        if not conta_id:
            return jsonify({'error': 'Conta de pagamento é obrigatória'}), 400
        
        print(f"💰 Valor: R$ {valor_pago}")
        print(f"📅 Data: {data_pagamento}")
        print(f"🏦 Conta ID: {conta_id}")
        
        parcela.valor_pago = valor_pago
        parcela.data_pagamento = data_pagamento
        
        if data.get('forma_pagamento_id'):
            parcela.forma_pagamento_id = int(data.get('forma_pagamento_id'))
        if conta_id:
            parcela.conta_id = int(conta_id)
        if data.get('observacao'):
            parcela.observacao = data.get('observacao')
        
        parcela.atualizar_status()
        print(f"✅ Status atualizado: {parcela.status}")
        
        if conta_id and valor_pago > 0:
            registrar_movimentacao_conta(
                conta_id=int(conta_id),
                data=data_pagamento,
                descricao=f"Pagamento - Parcela {parcela.numero_parcela}/{parcela.total_parcelas} - {parcela.despesa.descricao}",
                tipo='SAIDA',
                valor=valor_pago,
                categoria='DESPESA',
                referencia_id=parcela.despesa_id,
                parcela_id=parcela.id,
                observacao=parcela.observacao
            )
        
        db.session.commit()
        print("✅ Transação concluída com sucesso")
        
        return jsonify({'success': True, 'message': 'Pagamento registrado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao registrar pagamento da parcela:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/parcelas/obra/<int:parcela_id>/receber', methods=['POST'])
def receber_parcela_obra(parcela_id):
    """Registra o recebimento de uma parcela do contrato da obra"""
    try:
        print(f"🔍 Recebendo parcela de obra ID: {parcela_id}")
        
        parcela = ParcelaObra.query.get_or_404(parcela_id)
        data = request.json
        
        valor_recebido = float(data.get('valor_recebido', parcela.valor))
        data_recebimento = datetime.strptime(data.get('data_recebimento'), '%Y-%m-%d').date() if data.get('data_recebimento') else date.today()
        conta_id = data.get('conta_id')
        
        if not conta_id:
            return jsonify({'error': 'Conta de recebimento é obrigatória'}), 400
        
        print(f"💰 Valor: R$ {valor_recebido}")
        print(f"📅 Data: {data_recebimento}")
        print(f"🏦 Conta ID: {conta_id}")
        
        parcela.valor_recebido = valor_recebido
        parcela.data_recebimento = data_recebimento
        
        if data.get('forma_pagamento_id'):
            parcela.forma_pagamento_id = int(data.get('forma_pagamento_id'))
        if conta_id:
            parcela.conta_id = int(conta_id)
        if data.get('observacao'):
            parcela.observacao = data.get('observacao')
        
        parcela.atualizar_status()
        print(f"✅ Status atualizado: {parcela.status}")
        
        if conta_id and valor_recebido > 0:
            registrar_movimentacao_conta(
                conta_id=int(conta_id),
                data=data_recebimento,
                descricao=f"Recebimento Contrato - Parcela {parcela.numero_parcela}/{parcela.total_parcelas} - {parcela.obra.nome}",
                tipo='ENTRADA',
                valor=valor_recebido,
                categoria='PARCELA_OBRA',
                referencia_id=parcela.obra_id,
                parcela_id=parcela.id,
                observacao=parcela.observacao
            )
        
        db.session.commit()
        print("✅ Transação concluída com sucesso")
        
        return jsonify({'success': True, 'message': 'Recebimento registrado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro ao registrar recebimento da parcela da obra:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/parcelas/fluxo', methods=['GET'])
def fluxo_parcelas():
    """Retorna o fluxo de parcelas a receber/pagar"""
    try:
        atualizar_status_parcelas()
        
        meses = int(request.args.get('meses', 6))
        
        data_inicio = date.today()
        data_fim = data_inicio + timedelta(days=30*meses)
        
        resultado = {
            'a_receber': [],
            'a_pagar': []
        }
        
        # Parcelas de receita a receber
        parcelas_receita = ParcelaReceita.query.filter(
            ParcelaReceita.status.in_(['PENDENTE', 'PARCIAL']),
            ParcelaReceita.data_vencimento <= data_fim
        ).order_by(ParcelaReceita.data_vencimento).all()
        
        for p in parcelas_receita:
            resultado['a_receber'].append({
                'id': p.id,
                'tipo': 'receita',
                'descricao': p.receita.descricao,
                'obra': p.receita.obra.nome if p.receita.obra else 'Sem obra',
                'parcela': f"{p.numero_parcela}/{p.total_parcelas}",
                'data_vencimento': p.data_vencimento.strftime('%d/%m/%Y'),
                'valor': p.valor,
                'valor_recebido': p.valor_recebido,
                'saldo': p.valor - p.valor_recebido,
                'status': p.status,
                'dias_atraso': p.dias_atraso
            })
        
        # Parcelas de obra a receber
        parcelas_obra = ParcelaObra.query.filter(
            ParcelaObra.status.in_(['PENDENTE', 'PARCIAL']),
            ParcelaObra.data_vencimento <= data_fim
        ).order_by(ParcelaObra.data_vencimento).all()
        
        for p in parcelas_obra:
            resultado['a_receber'].append({
                'id': p.id,
                'tipo': 'contrato',
                'descricao': f"Contrato - {p.obra.nome}",
                'obra': p.obra.nome,
                'parcela': f"{p.numero_parcela}/{p.total_parcelas}",
                'data_vencimento': p.data_vencimento.strftime('%d/%m/%Y'),
                'valor': p.valor,
                'valor_recebido': p.valor_recebido,
                'saldo': p.valor - p.valor_recebido,
                'status': p.status,
                'dias_atraso': p.dias_atraso
            })
        
        # Parcelas de despesa a pagar
        parcelas_despesa = ParcelaDespesa.query.filter(
            ParcelaDespesa.status.in_(['PENDENTE', 'PARCIAL']),
            ParcelaDespesa.data_vencimento <= data_fim
        ).order_by(ParcelaDespesa.data_vencimento).all()
        
        for p in parcelas_despesa:
            resultado['a_pagar'].append({
                'id': p.id,
                'tipo': 'despesa',
                'descricao': p.despesa.descricao,
                'obra': p.despesa.obra.nome if p.despesa.obra else 'Sem obra',
                'parcela': f"{p.numero_parcela}/{p.total_parcelas}",
                'data_vencimento': p.data_vencimento.strftime('%d/%m/%Y'),
                'valor': p.valor,
                'valor_pago': p.valor_pago,
                'saldo': p.valor - p.valor_pago,
                'status': p.status,
                'dias_atraso': p.dias_atraso
            })
        
        # Ordenar por data
        resultado['a_receber'].sort(key=lambda x: x['data_vencimento'])
        resultado['a_pagar'].sort(key=lambda x: x['data_vencimento'])
        
        print(f"📊 Fluxo gerado: {len(resultado['a_receber'])} a receber, {len(resultado['a_pagar'])} a pagar")
        
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao gerar fluxo de parcelas:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
# ========== ROTAS DE GESTÃO FINANCEIRA ==========

@app.route('/api/financeiro/meses-disponiveis', methods=['GET'])
def financeiro_meses_disponiveis():
    """Retorna lista de meses com dados cadastrados"""
    try:
        atualizar_status_parcelas()
        
        # Buscar meses das receitas
        meses_receitas = db.session.query(
            db.extract('year', Receita.data).label('ano'),
            db.extract('month', Receita.data).label('mes')
        ).distinct().all()
        
        # Buscar meses das despesas
        meses_despesas = db.session.query(
            db.extract('year', Despesa.data).label('ano'),
            db.extract('month', Despesa.data).label('mes')
        ).distinct().all()
        
        # Buscar meses das parcelas de receita (vencimento)
        meses_parcelas_receita = db.session.query(
            db.extract('year', ParcelaReceita.data_vencimento).label('ano'),
            db.extract('month', ParcelaReceita.data_vencimento).label('mes')
        ).distinct().all()
        
        # Buscar meses das parcelas de despesa (vencimento)
        meses_parcelas_despesa = db.session.query(
            db.extract('year', ParcelaDespesa.data_vencimento).label('ano'),
            db.extract('month', ParcelaDespesa.data_vencimento).label('mes')
        ).distinct().all()
        
        # Buscar meses das parcelas de obra (vencimento)
        meses_parcelas_obra = db.session.query(
            db.extract('year', ParcelaObra.data_vencimento).label('ano'),
            db.extract('month', ParcelaObra.data_vencimento).label('mes')
        ).distinct().all()
        
        # Combinar todos os meses
        todos_meses = set()
        for item in meses_receitas + meses_despesas + meses_parcelas_receita + meses_parcelas_despesa + meses_parcelas_obra:
            if item.ano and item.mes:
                todos_meses.add((int(item.ano), int(item.mes)))
        
        # Ordenar do mais recente para o mais antigo
        meses_ordenados = sorted(list(todos_meses), key=lambda x: (x[0], x[1]), reverse=True)
        
        resultado = [{
            'ano': ano,
            'mes': mes,
            'nome': date(ano, mes, 1).strftime('%B/%Y').capitalize(),
            'valor': f"{ano}-{mes:02d}"
        } for ano, mes in meses_ordenados]
        
        print(f"📅 Meses disponíveis: {len(resultado)}")
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao buscar meses disponíveis:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/financeiro/resumo-mensal', methods=['GET'])
def financeiro_resumo_mensal():
    """Retorna resumo financeiro de um mês específico"""
    try:
        atualizar_status_parcelas()
        
        ano = request.args.get('ano', type=int)
        mes = request.args.get('mes', type=int)
        
        if not ano or not mes:
            hoje = date.today()
            ano = hoje.year
            mes = hoje.month
        
        data_inicio = date(ano, mes, 1)
        if mes == 12:
            data_fim = date(ano + 1, 1, 1) - timedelta(days=1)
        else:
            data_fim = date(ano, mes + 1, 1) - timedelta(days=1)
        
        print(f"📅 Período analisado: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
        
        # ===== ENTRADAS RECEBIDAS (já pagas) =====
        # Parcelas de receita recebidas no período
        parcelas_recebidas = ParcelaReceita.query.filter(
            ParcelaReceita.data_recebimento >= data_inicio,
            ParcelaReceita.data_recebimento <= data_fim
        ).all()
        
        total_recebido = sum(p.valor_recebido for p in parcelas_recebidas)
        print(f"💰 Recebido de receitas: R$ {total_recebido:.2f} ({len(parcelas_recebidas)} parcelas)")
        
        # Parcelas de obras recebidas no período
        parcelas_obra_recebidas = ParcelaObra.query.filter(
            ParcelaObra.data_recebimento >= data_inicio,
            ParcelaObra.data_recebimento <= data_fim
        ).all()
        
        total_recebido_obra = sum(p.valor_recebido for p in parcelas_obra_recebidas)
        print(f"🏗️ Recebido de contratos: R$ {total_recebido_obra:.2f} ({len(parcelas_obra_recebidas)} parcelas)")
        
        total_entradas = total_recebido + total_recebido_obra
        
        # ===== SAÍDAS PAGAS (já pagas) =====
        # Parcelas de despesa pagas no período
        parcelas_pagas = ParcelaDespesa.query.filter(
            ParcelaDespesa.data_pagamento >= data_inicio,
            ParcelaDespesa.data_pagamento <= data_fim
        ).all()
        
        total_pago = sum(p.valor_pago for p in parcelas_pagas)
        print(f"💳 Pago de despesas: R$ {total_pago:.2f} ({len(parcelas_pagas)} parcelas)")
        
        # Materiais pagos no período
        materiais_pagos = Material.query.filter(
            Material.data_pagamento >= data_inicio,
            Material.data_pagamento <= data_fim
        ).all()
        
        total_materiais = sum(m.valor_pago for m in materiais_pagos)
        print(f"📦 Materiais pagos: R$ {total_materiais:.2f} ({len(materiais_pagos)} itens)")
        
        # Mão de obra paga no período
        mao_obra_paga = MaoObra.query.filter(
            MaoObra.data_pagamento >= data_inicio,
            MaoObra.data_pagamento <= data_fim
        ).all()
        
        total_mao_obra = sum(m.valor_pago for m in mao_obra_paga)
        print(f"👷 Mão de obra paga: R$ {total_mao_obra:.2f} ({len(mao_obra_paga)} itens)")
        
        total_saidas = total_pago + total_materiais + total_mao_obra
        
        # ===== PROJEÇÕES (a receber/pagar no período) =====
        # Parcelas de receita com vencimento no período (ainda não recebidas)
        parcelas_a_receber = ParcelaReceita.query.filter(
            ParcelaReceita.status.in_(['PENDENTE', 'PARCIAL']),
            ParcelaReceita.data_vencimento >= data_inicio,
            ParcelaReceita.data_vencimento <= data_fim
        ).all()
        
        total_a_receber = sum(p.valor - p.valor_recebido for p in parcelas_a_receber)
        print(f"📅 Receitas a receber: R$ {total_a_receber:.2f} ({len(parcelas_a_receber)} parcelas)")
        
        # Parcelas de obras com vencimento no período (ainda não recebidas)
        parcelas_obra_a_receber = ParcelaObra.query.filter(
            ParcelaObra.status.in_(['PENDENTE', 'PARCIAL']),
            ParcelaObra.data_vencimento >= data_inicio,
            ParcelaObra.data_vencimento <= data_fim
        ).all()
        
        total_a_receber_obra = sum(p.valor - p.valor_recebido for p in parcelas_obra_a_receber)
        print(f"📅 Contratos a receber: R$ {total_a_receber_obra:.2f} ({len(parcelas_obra_a_receber)} parcelas)")
        
        total_a_receber += total_a_receber_obra
        
        # Parcelas de despesa com vencimento no período (ainda não pagas)
        parcelas_a_pagar = ParcelaDespesa.query.filter(
            ParcelaDespesa.status.in_(['PENDENTE', 'PARCIAL']),
            ParcelaDespesa.data_vencimento >= data_inicio,
            ParcelaDespesa.data_vencimento <= data_fim
        ).all()
        
        total_a_pagar = sum(p.valor - p.valor_pago for p in parcelas_a_pagar)
        print(f"📅 Despesas a pagar: R$ {total_a_pagar:.2f} ({len(parcelas_a_pagar)} parcelas)")
        
        saldo = total_entradas - total_saidas
        
        return jsonify({
            'mes': mes,
            'ano': ano,
            'nome_mes': data_inicio.strftime('%B/%Y').capitalize(),
            'resumo': {
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'saldo': saldo,
                'status': 'POSITIVO' if saldo >= 0 else 'NEGATIVO',
                'total_a_receber': total_a_receber,
                'total_a_pagar': total_a_pagar,
                'qtd_parcelas_recebidas': len(parcelas_recebidas) + len(parcelas_obra_recebidas),
                'qtd_parcelas_pagas': len(parcelas_pagas),
                'qtd_materiais': len(materiais_pagos),
                'qtd_mao_obra': len(mao_obra_paga),
                'qtd_a_receber': len(parcelas_a_receber) + len(parcelas_obra_a_receber),
                'qtd_a_pagar': len(parcelas_a_pagar)
            }
        })
    except Exception as e:
        print("❌ Erro ao gerar resumo mensal:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/financeiro/evolucao-anual', methods=['GET'])
def financeiro_evolucao_anual():
    """Retorna evolução mensal de receitas e despesas do ano"""
    try:
        atualizar_status_parcelas()
        
        ano = request.args.get('ano', type=int)
        if not ano:
            ano = date.today().year
        
        print(f"📈 Gerando evolução anual para {ano}")
        
        resultado = []
        for mes in range(1, 13):
            data_inicio = date(ano, mes, 1)
            if mes == 12:
                data_fim = date(ano + 1, 1, 1) - timedelta(days=1)
            else:
                data_fim = date(ano, mes + 1, 1) - timedelta(days=1)
            
            # Recebimentos no mês
            recebido = db.session.query(db.func.sum(ParcelaReceita.valor_recebido)).filter(
                ParcelaReceita.data_recebimento >= data_inicio,
                ParcelaReceita.data_recebimento <= data_fim
            ).scalar() or 0
            
            recebido_obra = db.session.query(db.func.sum(ParcelaObra.valor_recebido)).filter(
                ParcelaObra.data_recebimento >= data_inicio,
                ParcelaObra.data_recebimento <= data_fim
            ).scalar() or 0
            
            # Pagamentos no mês
            pago = db.session.query(db.func.sum(ParcelaDespesa.valor_pago)).filter(
                ParcelaDespesa.data_pagamento >= data_inicio,
                ParcelaDespesa.data_pagamento <= data_fim
            ).scalar() or 0
            
            materiais = db.session.query(db.func.sum(Material.valor_pago)).filter(
                Material.data_pagamento >= data_inicio,
                Material.data_pagamento <= data_fim
            ).scalar() or 0
            
            mao_obra = db.session.query(db.func.sum(MaoObra.valor_pago)).filter(
                MaoObra.data_pagamento >= data_inicio,
                MaoObra.data_pagamento <= data_fim
            ).scalar() or 0
            
            total_receitas = recebido + recebido_obra
            total_despesas = pago + materiais + mao_obra
            saldo = total_receitas - total_despesas
            
            resultado.append({
                'mes': mes,
                'nome_mes': data_inicio.strftime('%B').capitalize(),
                'receitas': total_receitas,
                'despesas': total_despesas,
                'saldo': saldo
            })
        
        return jsonify(resultado)
    except Exception as e:
        print("❌ Erro ao gerar evolução anual:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ========== ROTAS DE RELATÓRIOS ==========

@app.route('/api/relatorio/obras', methods=['GET'])
def relatorio_obras():
    """Gera relatório Excel de todas as obras"""
    try:
        atualizar_status_parcelas()
        
        obras = Obra.query.all()
        
        dados = []
        for obra in obras:
            dados.append({
                'ID': obra.id,
                'Obra': obra.nome,
                'Cliente': obra.cliente,
                'Contrato': obra.contrato,
                'Status': obra.status,
                'Data Início': obra.data_inicio.strftime('%d/%m/%Y') if obra.data_inicio else '',
                'Data Fim': obra.data_fim.strftime('%d/%m/%Y') if obra.data_fim else '',
                'Valor Contrato': obra.valor_total_contrato,
                'Parcelas': obra.quantidade_parcelas,
                'Total Receitas': obra.total_receitas,
                'Total Despesas': obra.total_despesas,
                'Lucro': obra.lucro,
                'Margem (%)': round(obra.margem_lucro, 2)
            })
        
        df = pd.DataFrame(dados)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Obras', index=False)
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'relatorio_obras_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
        )
    except Exception as e:
        print("❌ Erro ao gerar relatório de obras:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/relatorio/receitas', methods=['GET'])
def relatorio_receitas():
    """Gera relatório Excel de receitas com filtros"""
    try:
        atualizar_status_parcelas()
        
        obra_id = request.args.get('obra_id')
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        
        query = Receita.query
        
        if obra_id:
            query = query.filter_by(obra_id=obra_id)
        if mes and ano:
            query = query.filter(
                db.extract('month', Receita.data) == mes,
                db.extract('year', Receita.data) == ano
            )
        
        receitas = query.order_by(Receita.data).all()
        
        dados = []
        for r in receitas:
            forma_nome = None
            if r.forma_pagamento_id:
                forma = FormaPagamento.query.get(r.forma_pagamento_id)
                forma_nome = forma.nome if forma else None
            
            conta_nome = None
            if r.conta_id:
                conta = ContaBancaria.query.get(r.conta_id)
                conta_nome = conta.nome if conta else None
            
            dados.append({
                'ID': r.id,
                'Data': r.data.strftime('%d/%m/%Y'),
                'Obra': r.obra.nome if r.obra else '',
                'Descrição': r.descricao,
                'Tipo': r.tipo,
                'Forma Pagamento': forma_nome,
                'Conta': conta_nome,
                'Parcelas': f"{r.quantidade_parcelas}x" if r.quantidade_parcelas > 1 else 'À vista',
                'Valor Total': r.valor_total,
                'Valor Recebido': r.valor_recebido,
                'Status': r.status
            })
        
        df = pd.DataFrame(dados)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Receitas', index=False)
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'relatorio_receitas_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
        )
    except Exception as e:
        print("❌ Erro ao gerar relatório de receitas:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/relatorio/despesas', methods=['GET'])
def relatorio_despesas():
    """Gera relatório Excel de despesas com filtros"""
    try:
        atualizar_status_parcelas()
        
        obra_id = request.args.get('obra_id')
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        tipo = request.args.get('tipo')
        
        # Despesas gerais
        query_despesas = Despesa.query
        if obra_id:
            query_despesas = query_despesas.filter_by(obra_id=obra_id)
        if tipo:
            query_despesas = query_despesas.filter_by(tipo=tipo)
        if mes and ano:
            query_despesas = query_despesas.filter(
                db.extract('month', Despesa.data) == mes,
                db.extract('year', Despesa.data) == ano
            )
        despesas = query_despesas.all()
        
        # Materiais
        query_materiais = Material.query
        if obra_id:
            query_materiais = query_materiais.filter_by(obra_id=obra_id)
        if mes and ano:
            query_materiais = query_materiais.filter(
                db.extract('month', Material.data) == mes,
                db.extract('year', Material.data) == ano
            )
        materiais = query_materiais.all()
        
        # Mão de obra
        query_mao_obra = MaoObra.query
        if obra_id:
            query_mao_obra = query_mao_obra.filter_by(obra_id=obra_id)
        if mes and ano:
            query_mao_obra = query_mao_obra.filter(
                db.extract('month', MaoObra.data) == mes,
                db.extract('year', MaoObra.data) == ano
            )
        mao_obra = query_mao_obra.all()
        
        dados = []
        
        # Adicionar despesas gerais
        for d in despesas:
            forma_nome = None
            if d.forma_pagamento_id:
                forma = FormaPagamento.query.get(d.forma_pagamento_id)
                forma_nome = forma.nome if forma else None
            
            conta_nome = None
            if d.conta_id:
                conta = ContaBancaria.query.get(d.conta_id)
                conta_nome = conta.nome if conta else None
            
            categoria_nome = None
            if d.categoria_id:
                categoria = CategoriaDespesa.query.get(d.categoria_id)
                categoria_nome = categoria.nome if categoria else None
            
            dados.append({
                'Tipo': 'Despesa Geral',
                'ID': d.id,
                'Data': d.data.strftime('%d/%m/%Y'),
                'Obra': d.obra.nome if d.obra else '',
                'Descrição': d.descricao,
                'Fornecedor': d.fornecedor,
                'Categoria': categoria_nome,
                'Forma Pagamento': forma_nome,
                'Conta': conta_nome,
                'Parcelas': f"{d.quantidade_parcelas}x" if d.quantidade_parcelas > 1 else 'À vista',
                'Valor Total': d.valor_total,
                'Valor Pago': d.valor_pago,
                'Status': d.status
            })
        
        # Adicionar materiais
        for m in materiais:
            forma_nome = None
            if m.forma_pagamento_id:
                forma = FormaPagamento.query.get(m.forma_pagamento_id)
                forma_nome = forma.nome if forma else None
            
            conta_nome = None
            if m.conta_id:
                conta = ContaBancaria.query.get(m.conta_id)
                conta_nome = conta.nome if conta else None
            
            dados.append({
                'Tipo': 'Material',
                'ID': m.id,
                'Data': m.data.strftime('%d/%m/%Y'),
                'Obra': m.obra.nome if m.obra else '',
                'Descrição': m.descricao,
                'Fornecedor': m.fornecedor,
                'Categoria': 'Material',
                'Forma Pagamento': forma_nome,
                'Conta': conta_nome,
                'Parcelas': f"{m.quantidade_parcelas}x" if m.quantidade_parcelas > 1 else 'À vista',
                'Valor Total': m.valor_total,
                'Valor Pago': m.valor_pago,
                'Status': m.status
            })
        
        # Adicionar mão de obra
        for mo in mao_obra:
            forma_nome = None
            if mo.forma_pagamento_id:
                forma = FormaPagamento.query.get(mo.forma_pagamento_id)
                forma_nome = forma.nome if forma else None
            
            conta_nome = None
            if mo.conta_id:
                conta = ContaBancaria.query.get(mo.conta_id)
                conta_nome = conta.nome if conta else None
            
            dados.append({
                'Tipo': 'Mão de Obra',
                'ID': mo.id,
                'Data': mo.data.strftime('%d/%m/%Y'),
                'Obra': mo.obra.nome if mo.obra else '',
                'Descrição': mo.descricao,
                'Fornecedor': mo.funcionario,
                'Categoria': 'Mão de Obra',
                'Forma Pagamento': forma_nome,
                'Conta': conta_nome,
                'Parcelas': f"{mo.quantidade_parcelas}x" if mo.quantidade_parcelas > 1 else 'À vista',
                'Valor Total': mo.valor_total,
                'Valor Pago': mo.valor_pago,
                'Status': mo.status
            })
        
        df = pd.DataFrame(dados)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Despesas', index=False)
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'relatorio_despesas_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
        )
    except Exception as e:
        print("❌ Erro ao gerar relatório de despesas:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/relatorio/parcelas', methods=['GET'])
def relatorio_parcelas():
    """Gera relatório Excel de parcelas a receber/pagar"""
    try:
        atualizar_status_parcelas()
        
        tipo = request.args.get('tipo', 'todas')  # receber, pagar, todas
        
        dados = []
        
        if tipo in ['todas', 'receber']:
            # Parcelas de receitas
            parcelas_receita = ParcelaReceita.query.filter(
                ParcelaReceita.status.in_(['PENDENTE', 'PARCIAL'])
            ).order_by(ParcelaReceita.data_vencimento).all()
            
            for p in parcelas_receita:
                forma_nome = None
                if p.forma_pagamento_id:
                    forma = FormaPagamento.query.get(p.forma_pagamento_id)
                    forma_nome = forma.nome if forma else None
                
                dados.append({
                    'Tipo': 'A Receber - Receita',
                    'ID Parcela': p.id,
                    'Descrição': p.receita.descricao,
                    'Obra': p.receita.obra.nome if p.receita.obra else 'Sem obra',
                    'Parcela': f"{p.numero_parcela}/{p.total_parcelas}",
                    'Data Vencimento': p.data_vencimento.strftime('%d/%m/%Y'),
                    'Valor': p.valor,
                    'Valor Recebido': p.valor_recebido,
                    'Saldo': p.valor - p.valor_recebido,
                    'Status': p.status,
                    'Dias Atraso': p.dias_atraso,
                    'Forma Pagamento': forma_nome
                })
            
            # Parcelas de contratos de obras
            parcelas_obra = ParcelaObra.query.filter(
                ParcelaObra.status.in_(['PENDENTE', 'PARCIAL'])
            ).order_by(ParcelaObra.data_vencimento).all()
            
            for p in parcelas_obra:
                forma_nome = None
                if p.forma_pagamento_id:
                    forma = FormaPagamento.query.get(p.forma_pagamento_id)
                    forma_nome = forma.nome if forma else None
                
                dados.append({
                    'Tipo': 'A Receber - Contrato',
                    'ID Parcela': p.id,
                    'Descrição': f"Contrato - {p.obra.nome}",
                    'Obra': p.obra.nome,
                    'Parcela': f"{p.numero_parcela}/{p.total_parcelas}",
                    'Data Vencimento': p.data_vencimento.strftime('%d/%m/%Y'),
                    'Valor': p.valor,
                    'Valor Recebido': p.valor_recebido,
                    'Saldo': p.valor - p.valor_recebido,
                    'Status': p.status,
                    'Dias Atraso': p.dias_atraso,
                    'Forma Pagamento': forma_nome
                })
        
        if tipo in ['todas', 'pagar']:
            # Parcelas de despesas
            parcelas_despesa = ParcelaDespesa.query.filter(
                ParcelaDespesa.status.in_(['PENDENTE', 'PARCIAL'])
            ).order_by(ParcelaDespesa.data_vencimento).all()
            
            for p in parcelas_despesa:
                forma_nome = None
                if p.forma_pagamento_id:
                    forma = FormaPagamento.query.get(p.forma_pagamento_id)
                    forma_nome = forma.nome if forma else None
                
                dados.append({
                    'Tipo': 'A Pagar',
                    'ID Parcela': p.id,
                    'Descrição': p.despesa.descricao,
                    'Obra': p.despesa.obra.nome if p.despesa.obra else 'Sem obra',
                    'Parcela': f"{p.numero_parcela}/{p.total_parcelas}",
                    'Data Vencimento': p.data_vencimento.strftime('%d/%m/%Y'),
                    'Valor': p.valor,
                    'Valor Pago': p.valor_pago,
                    'Saldo': p.valor - p.valor_pago,
                    'Status': p.status,
                    'Dias Atraso': p.dias_atraso,
                    'Forma Pagamento': forma_nome
                })
        
        # Ordenar por data de vencimento
        dados.sort(key=lambda x: x['Data Vencimento'])
        
        df = pd.DataFrame(dados)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Parcelas', index=False)
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'relatorio_parcelas_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
        )
    except Exception as e:
        print("❌ Erro ao gerar relatório de parcelas:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/relatorio/abc', methods=['GET'])
def relatorio_abc():
    """Gera relatório Excel da curva ABC"""
    try:
        atualizar_status_parcelas()
        
        obra_id = request.args.get('obra_id')
        
        if obra_id:
            obra = Obra.query.get(obra_id)
            itens = obra.analise_abc if obra else []
            
            dados = []
            for item in itens:
                dados.append({
                    'Código': item['codigo'],
                    'Descrição': item['descricao'],
                    'Unidade': item.get('unidade', '-'),
                    'Previsto': item['previsto'],
                    'Realizado': item['realizado'],
                    'Desvio': item['desvio'],
                    '% Desvio': f"{item['percentual_desvio']:.2f}%",
                    '% do Total': f"{item.get('percentual', 0):.2f}%",
                    '% Acumulado': f"{item.get('percentual_acumulado', 0):.2f}%",
                    'Classificação': item.get('classificacao', '-')
                })
        else:
            # Relatório ABC consolidado de todas as obras
            todas_obras = Obra.query.all()
            todos_itens = []
            
            for obra in todas_obras:
                itens = obra.analise_abc
                for item in itens:
                    item['obra_nome'] = obra.nome
                    todos_itens.append(item)
            
            # Ordenar por valor realizado
            todos_itens.sort(key=lambda x: x['realizado'], reverse=True)
            
            dados = []
            for item in todos_itens:
                dados.append({
                    'Obra': item['obra_nome'],
                    'Código': item['codigo'],
                    'Descrição': item['descricao'],
                    'Unidade': item.get('unidade', '-'),
                    'Previsto': item['previsto'],
                    'Realizado': item['realizado'],
                    'Desvio': item['desvio'],
                    '% Desvio': f"{item['percentual_desvio']:.2f}%",
                    '% do Total': f"{item.get('percentual', 0):.2f}%",
                    'Classificação': item.get('classificacao', '-')
                })
        
        df = pd.DataFrame(dados)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Curva ABC', index=False)
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'relatorio_abc_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
        )
    except Exception as e:
        print("❌ Erro ao gerar relatório ABC:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/relatorio/contas', methods=['GET'])
def relatorio_contas():
    """Gera relatório Excel de contas bancárias"""
    try:
        contas = ContaBancaria.query.all()
        
        dados = []
        for conta in contas:
            conta.calcular_saldo()
            
            dados.append({
                'ID': conta.id,
                'Nome': conta.nome,
                'Banco': conta.banco,
                'Agência': conta.agencia,
                'Conta': conta.numero_conta,
                'Tipo': conta.tipo,
                'Saldo Inicial': conta.saldo_inicial,
                'Saldo Atual': conta.saldo_atual,
                'Observação': conta.observacao
            })
        
        df = pd.DataFrame(dados)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Contas', index=False)
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'relatorio_contas_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
        )
    except Exception as e:
        print("❌ Erro ao gerar relatório de contas:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/relatorio/financeiro', methods=['GET'])
def relatorio_financeiro():
    """Gera relatório Excel financeiro mensal"""
    try:
        atualizar_status_parcelas()
        
        mes = request.args.get('mes', type=int)
        ano = request.args.get('ano', type=int)
        
        if not mes or not ano:
            hoje = date.today()
            mes = hoje.month
            ano = hoje.year
        
        # Definir intervalo do mês
        data_inicio = date(ano, mes, 1)
        if mes == 12:
            data_fim = date(ano + 1, 1, 1) - timedelta(days=1)
        else:
            data_fim = date(ano, mes + 1, 1) - timedelta(days=1)
        
        dados = []
        
        # Parcelas de receita com vencimento no mês
        parcelas_receita = ParcelaReceita.query.filter(
            ParcelaReceita.data_vencimento >= data_inicio,
            ParcelaReceita.data_vencimento <= data_fim
        ).order_by(ParcelaReceita.data_vencimento).all()
        
        for p in parcelas_receita:
            dados.append({
                'Tipo': 'Parcela a Receber',
                'Data': p.data_vencimento.strftime('%d/%m/%Y'),
                'Descrição': f"{p.receita.descricao} - Parcela {p.numero_parcela}/{p.total_parcelas}",
                'Obra': p.receita.obra.nome if p.receita.obra else '',
                'Valor': p.valor,
                'Recebido': p.valor_recebido,
                'Saldo': p.valor - p.valor_recebido,
                'Status': p.status
            })
        
        # Parcelas de obra com vencimento no mês
        parcelas_obra = ParcelaObra.query.filter(
            ParcelaObra.data_vencimento >= data_inicio,
            ParcelaObra.data_vencimento <= data_fim
        ).order_by(ParcelaObra.data_vencimento).all()
        
        for p in parcelas_obra:
            dados.append({
                'Tipo': 'Parcela de Contrato',
                'Data': p.data_vencimento.strftime('%d/%m/%Y'),
                'Descrição': f"Contrato {p.obra.nome} - Parcela {p.numero_parcela}/{p.total_parcelas}",
                'Obra': p.obra.nome,
                'Valor': p.valor,
                'Recebido': p.valor_recebido,
                'Saldo': p.valor - p.valor_recebido,
                'Status': p.status
            })
        
        # Parcelas de despesa com vencimento no mês
        parcelas_despesa = ParcelaDespesa.query.filter(
            ParcelaDespesa.data_vencimento >= data_inicio,
            ParcelaDespesa.data_vencimento <= data_fim
        ).order_by(ParcelaDespesa.data_vencimento).all()
        
        for p in parcelas_despesa:
            dados.append({
                'Tipo': 'Parcela a Pagar',
                'Data': p.data_vencimento.strftime('%d/%m/%Y'),
                'Descrição': f"{p.despesa.descricao} - Parcela {p.numero_parcela}/{p.total_parcelas}",
                'Obra': p.despesa.obra.nome if p.despesa.obra else '',
                'Valor': p.valor,
                'Pago': p.valor_pago,
                'Saldo': p.valor - p.valor_pago,
                'Status': p.status
            })
        
        # Ordenar por data
        dados.sort(key=lambda x: x['Data'])
        
        df = pd.DataFrame(dados)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=f'{mes:02d}/{ano}', index=False)
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'relatorio_financeiro_{ano}{mes:02d}_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
        )
    except Exception as e:
        print("❌ Erro ao gerar relatório financeiro:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ========== HEALTH CHECK ==========

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'API funcionando!', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SISTEMA DE GESTÃO DE ENGENHARIA - REMAC")
    print("=" * 60)
    print("✅ API rodando em:")
    print("   - http://localhost:5000")
    print("✅ Módulos carregados:")
    print("   - Obras (CRUD completo + Parcelamento 2-12x)")
    print("   - Receitas (CRUD completo + Parcelamento 2-12x)")
    print("   - Despesas (CRUD completo + Parcelamento 2-12x)")
    print("   - Materiais (CRUD completo + Parcelamento 2-12x)")
    print("   - Mão de Obra (CRUD completo + Parcelamento 2-12x)")
    print("   - Contas Bancárias (CRUD completo)")
    print("   - Formas de Pagamento (CRUD completo)")
    print("   - Parcelas (Geração automática + Recebimento/Pagamento)")
    print("   - Fluxo de Caixa por Parcelas")
    print("   - Itens ABC (Curva ABC)")
    print("   - Relatórios Excel")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
