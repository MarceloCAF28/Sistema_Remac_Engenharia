from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

# ========== MODELO DE FORMA DE PAGAMENTO ==========
class FormaPagamento(db.Model):
    __tablename__ = 'formas_pagamento'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    descricao = db.Column(db.String(200))
    permite_parcelamento = db.Column(db.Boolean, default=True)
    parcelas_maximas = db.Column(db.Integer, default=12)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relacionamentos
    receitas = db.relationship('Receita', back_populates='forma_pagamento', lazy=True)
    despesas = db.relationship('Despesa', back_populates='forma_pagamento', lazy=True)
    parcelas_receita = db.relationship('ParcelaReceita', back_populates='forma_pagamento', lazy=True)
    parcelas_despesa = db.relationship('ParcelaDespesa', back_populates='forma_pagamento', lazy=True)
    parcelas_obra = db.relationship('ParcelaObra', back_populates='forma_pagamento', lazy=True)

# ========== MODELO DE CONTA BANCÁRIA ==========
class ContaBancaria(db.Model):
    __tablename__ = 'contas_bancarias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    banco = db.Column(db.String(100))
    agencia = db.Column(db.String(20))
    numero_conta = db.Column(db.String(20))
    tipo = db.Column(db.String(50))
    saldo_inicial = db.Column(db.Float, default=0)
    saldo_atual = db.Column(db.Float, default=0)
    observacao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    movimentacoes = db.relationship('MovimentacaoConta', back_populates='conta', lazy=True, cascade='all, delete-orphan')
    receitas = db.relationship('Receita', back_populates='conta', lazy=True)
    despesas = db.relationship('Despesa', back_populates='conta', lazy=True)
    materiais = db.relationship('Material', back_populates='conta', lazy=True)
    mao_obra = db.relationship('MaoObra', back_populates='conta', lazy=True)
    obras = db.relationship('Obra', back_populates='conta_recebimento', lazy=True)
    parcelas_receita = db.relationship('ParcelaReceita', back_populates='conta', lazy=True)
    parcelas_despesa = db.relationship('ParcelaDespesa', back_populates='conta', lazy=True)
    parcelas_obra = db.relationship('ParcelaObra', back_populates='conta', lazy=True)
    
    def calcular_saldo(self):
        entradas = sum(m.valor for m in self.movimentacoes if m.tipo == 'ENTRADA')
        saidas = sum(m.valor for m in self.movimentacoes if m.tipo == 'SAIDA')
        self.saldo_atual = self.saldo_inicial + entradas - saidas
        return self.saldo_atual

# ========== MODELO DE MOVIMENTAÇÃO DE CONTA ==========
class MovimentacaoConta(db.Model):
    __tablename__ = 'movimentacoes_conta'
    
    id = db.Column(db.Integer, primary_key=True)
    conta_id = db.Column(db.Integer, db.ForeignKey('contas_bancarias.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20))
    valor = db.Column(db.Float, default=0)
    categoria = db.Column(db.String(50))
    referencia_id = db.Column(db.Integer)
    parcela_id = db.Column(db.Integer)
    observacao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relacionamentos
    conta = db.relationship('ContaBancaria', back_populates='movimentacoes')

# ========== MODELO DE CATEGORIA DE DESPESA ==========
class CategoriaDespesa(db.Model):
    __tablename__ = 'categorias_despesa'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.String(200))
    tipo = db.Column(db.String(50), default='VARIÁVEL')
    
    despesas = db.relationship('Despesa', back_populates='categoria', lazy=True)

# ========== MODELO DE ITEM ABC ==========
class ItemABC(db.Model):
    __tablename__ = 'itens_abc'
    
    id = db.Column(db.Integer, primary_key=True)
    obra_id = db.Column(db.Integer, db.ForeignKey('obras.id'), nullable=False)
    codigo = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    unidade = db.Column(db.String(20))
    quantidade_prevista = db.Column(db.Float, default=0)
    valor_unitario = db.Column(db.Float, default=0)
    valor_total_previsto = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relacionamentos
    obra = db.relationship('Obra', back_populates='itens_abc')
    materiais = db.relationship('Material', back_populates='item_abc', lazy=True)
    mao_obra = db.relationship('MaoObra', back_populates='item_abc', lazy=True)
    
    @property
    def valor_total_real(self):
        materiais_valor = sum(m.valor_total or 0 for m in self.materiais)
        mao_obra_valor = sum(m.valor_total or 0 for m in self.mao_obra)
        return materiais_valor + mao_obra_valor
    
    @property
    def desvio(self):
        return self.valor_total_real - self.valor_total_previsto
    
    @property
    def percentual_desvio(self):
        if self.valor_total_previsto > 0:
            return (self.desvio / self.valor_total_previsto) * 100
        return 0

# ========== MODELO OBRA (COM CONTA ID) ==========
class Obra(db.Model):
    __tablename__ = 'obras'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    cliente = db.Column(db.String(200), nullable=False)
    contrato = db.Column(db.String(100), unique=True)
    descricao = db.Column(db.Text)
    data_inicio = db.Column(db.Date)
    data_fim = db.Column(db.Date)
    status = db.Column(db.String(50), default='EM ANDAMENTO')
    
    # Dados de parcelamento do contrato
    valor_total_contrato = db.Column(db.Float, default=0)
    quantidade_parcelas = db.Column(db.Integer, default=1)
    forma_pagamento_id = db.Column(db.Integer, db.ForeignKey('formas_pagamento.id'))
    conta_id = db.Column(db.Integer, db.ForeignKey('contas_bancarias.id'))  # CONTA DE RECEBIMENTO
    data_primeira_parcela = db.Column(db.Date)
    observacao_parcelas = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    receitas = db.relationship('Receita', back_populates='obra', lazy=True, cascade='all, delete-orphan')
    despesas = db.relationship('Despesa', back_populates='obra', lazy=True, cascade='all, delete-orphan')
    materiais = db.relationship('Material', back_populates='obra', lazy=True, cascade='all, delete-orphan')
    mao_obra = db.relationship('MaoObra', back_populates='obra', lazy=True, cascade='all, delete-orphan')
    itens_abc = db.relationship('ItemABC', back_populates='obra', lazy=True, cascade='all, delete-orphan')
    parcelas = db.relationship('ParcelaObra', back_populates='obra', lazy=True, cascade='all, delete-orphan')
    forma_pagamento = db.relationship('FormaPagamento', foreign_keys=[forma_pagamento_id])
    conta_recebimento = db.relationship('ContaBancaria', foreign_keys=[conta_id], back_populates='obras')
    
    @property
    def total_receitas(self):
        """Total de receitas recebidas (incluindo parcelas do contrato)"""
        receitas_recebidas = sum(r.valor_recebido or 0 for r in self.receitas)
        parcelas_recebidas = sum(p.valor_recebido or 0 for p in self.parcelas)
        return receitas_recebidas + parcelas_recebidas
    
    @property
    def total_despesas(self):
        """Total de despesas pagas"""
        despesas_pagas = sum(d.valor_pago or 0 for d in self.despesas)
        materiais_pagos = sum(m.valor_pago or 0 for m in self.materiais)
        mao_obra_paga = sum(m.valor_pago or 0 for m in self.mao_obra)
        return despesas_pagas + materiais_pagos + mao_obra_paga
    
    @property
    def total_materiais(self):
        return sum(m.valor_total or 0 for m in self.materiais)
    
    @property
    def total_mao_obra(self):
        return sum(m.valor_total or 0 for m in self.mao_obra)
    
    @property
    def lucro(self):
        return self.total_receitas - self.total_despesas
    
    @property
    def margem_lucro(self):
        if self.total_receitas > 0:
            return (self.lucro / self.total_receitas) * 100
        return 0
    
    @property
    def total_a_receber(self):
        """Total de parcelas do contrato ainda não recebidas"""
        return sum(p.valor - (p.valor_recebido or 0) for p in self.parcelas if p.status != 'RECEBIDO')
    
    @property
    def analise_abc(self):
        """Gera análise ABC dos itens da obra"""
        itens = []
        for item in self.itens_abc:
            itens.append({
                'id': item.id,
                'codigo': item.codigo,
                'descricao': item.descricao,
                'unidade': item.unidade,
                'previsto': item.valor_total_previsto,
                'realizado': item.valor_total_real,
                'desvio': item.desvio,
                'percentual_desvio': round(item.percentual_desvio, 2)
            })
        
        # Ordenar por valor realizado (maior para menor)
        itens.sort(key=lambda x: x['realizado'], reverse=True)
        total = sum(item['realizado'] for item in itens)
        acumulado = 0
        
        for item in itens:
            acumulado += item['realizado']
            item['percentual'] = (item['realizado'] / total * 100) if total > 0 else 0
            item['percentual_acumulado'] = (acumulado / total * 100) if total > 0 else 0
            
            # Classificação ABC
            if item['percentual_acumulado'] <= 80:
                item['classificacao'] = 'A'
            elif item['percentual_acumulado'] <= 95:
                item['classificacao'] = 'B'
            else:
                item['classificacao'] = 'C'
        
        return itens

# ========== MODELO DE PARCELA DE OBRA ==========
class ParcelaObra(db.Model):
    __tablename__ = 'parcelas_obra'
    
    id = db.Column(db.Integer, primary_key=True)
    obra_id = db.Column(db.Integer, db.ForeignKey('obras.id'), nullable=False)
    numero_parcela = db.Column(db.Integer, nullable=False)
    total_parcelas = db.Column(db.Integer, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    data_recebimento = db.Column(db.Date)
    valor = db.Column(db.Float, default=0)
    valor_recebido = db.Column(db.Float, default=0)
    forma_pagamento_id = db.Column(db.Integer, db.ForeignKey('formas_pagamento.id'))
    conta_id = db.Column(db.Integer, db.ForeignKey('contas_bancarias.id'))
    status = db.Column(db.String(20), default='PENDENTE')
    observacao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    obra = db.relationship('Obra', back_populates='parcelas')
    conta = db.relationship('ContaBancaria', back_populates='parcelas_obra')
    forma_pagamento = db.relationship('FormaPagamento', back_populates='parcelas_obra')
    
    @property
    def dias_atraso(self):
        if self.status in ['PENDENTE', 'PARCIAL'] and self.data_vencimento < date.today():
            return (date.today() - self.data_vencimento).days
        return 0
    
    def atualizar_status(self):
        """Atualiza o status baseado na data de vencimento e recebimento"""
        if self.valor_recebido >= self.valor:
            self.status = 'RECEBIDO'
        elif self.valor_recebido > 0:
            self.status = 'PARCIAL'
        elif self.data_vencimento < date.today():
            self.status = 'ATRASADO'
        else:
            self.status = 'PENDENTE'

# ========== MODELO DE RECEITA ==========
class Receita(db.Model):
    __tablename__ = 'receitas'
    
    id = db.Column(db.Integer, primary_key=True)
    obra_id = db.Column(db.Integer, db.ForeignKey('obras.id'), nullable=False)
    conta_id = db.Column(db.Integer, db.ForeignKey('contas_bancarias.id'))
    forma_pagamento_id = db.Column(db.Integer, db.ForeignKey('formas_pagamento.id'))
    data = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    valor_total = db.Column(db.Float, default=0)
    quantidade_parcelas = db.Column(db.Integer, default=1)
    valor_parcela = db.Column(db.Float, default=0)
    data_primeira_parcela = db.Column(db.Date)
    tipo = db.Column(db.String(50))
    centro_custo = db.Column(db.String(100))
    observacao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    obra = db.relationship('Obra', back_populates='receitas')
    conta = db.relationship('ContaBancaria', back_populates='receitas')
    forma_pagamento = db.relationship('FormaPagamento', back_populates='receitas')
    parcelas = db.relationship('ParcelaReceita', back_populates='receita', lazy=True, cascade='all, delete-orphan')
    
    @property
    def valor_recebido(self):
        return sum(p.valor_recebido or 0 for p in self.parcelas)
    
    @property
    def status(self):
        if self.valor_recebido >= self.valor_total:
            return 'RECEBIDO'
        elif self.valor_recebido > 0:
            return 'PARCIAL'
        else:
            return 'PENDENTE'

# ========== MODELO DE PARCELA DE RECEITA ==========
class ParcelaReceita(db.Model):
    __tablename__ = 'parcelas_receita'
    
    id = db.Column(db.Integer, primary_key=True)
    receita_id = db.Column(db.Integer, db.ForeignKey('receitas.id'), nullable=False)
    numero_parcela = db.Column(db.Integer, nullable=False)
    total_parcelas = db.Column(db.Integer, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    data_recebimento = db.Column(db.Date)
    valor = db.Column(db.Float, default=0)
    valor_recebido = db.Column(db.Float, default=0)
    forma_pagamento_id = db.Column(db.Integer, db.ForeignKey('formas_pagamento.id'))
    conta_id = db.Column(db.Integer, db.ForeignKey('contas_bancarias.id'))
    status = db.Column(db.String(20), default='PENDENTE')
    observacao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    receita = db.relationship('Receita', back_populates='parcelas')
    conta = db.relationship('ContaBancaria', back_populates='parcelas_receita')
    forma_pagamento = db.relationship('FormaPagamento', back_populates='parcelas_receita')
    
    @property
    def dias_atraso(self):
        if self.status in ['PENDENTE', 'PARCIAL'] and self.data_vencimento < date.today():
            return (date.today() - self.data_vencimento).days
        return 0
    
    def atualizar_status(self):
        """Atualiza o status baseado na data de vencimento e recebimento"""
        if self.valor_recebido >= self.valor:
            self.status = 'RECEBIDO'
        elif self.valor_recebido > 0:
            self.status = 'PARCIAL'
        elif self.data_vencimento < date.today():
            self.status = 'ATRASADO'
        else:
            self.status = 'PENDENTE'

# ========== MODELO DE DESPESA ==========
class Despesa(db.Model):
    __tablename__ = 'despesas'
    
    id = db.Column(db.Integer, primary_key=True)
    obra_id = db.Column(db.Integer, db.ForeignKey('obras.id'), nullable=False)
    conta_id = db.Column(db.Integer, db.ForeignKey('contas_bancarias.id'))
    forma_pagamento_id = db.Column(db.Integer, db.ForeignKey('formas_pagamento.id'))
    data = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    fornecedor = db.Column(db.String(200))
    valor_total = db.Column(db.Float, default=0)
    quantidade_parcelas = db.Column(db.Integer, default=1)
    valor_parcela = db.Column(db.Float, default=0)
    data_primeira_parcela = db.Column(db.Date)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_despesa.id'))
    centro_custo = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    observacao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    obra = db.relationship('Obra', back_populates='despesas')
    conta = db.relationship('ContaBancaria', back_populates='despesas')
    forma_pagamento = db.relationship('FormaPagamento', back_populates='despesas')
    categoria = db.relationship('CategoriaDespesa', back_populates='despesas')
    parcelas = db.relationship('ParcelaDespesa', back_populates='despesa', lazy=True, cascade='all, delete-orphan')
    
    @property
    def valor_pago(self):
        return sum(p.valor_pago or 0 for p in self.parcelas)
    
    @property
    def status(self):
        if self.valor_pago >= self.valor_total:
            return 'PAGO'
        elif self.valor_pago > 0:
            return 'PARCIAL'
        else:
            return 'PENDENTE'

# ========== MODELO DE PARCELA DE DESPESA ==========
class ParcelaDespesa(db.Model):
    __tablename__ = 'parcelas_despesa'
    
    id = db.Column(db.Integer, primary_key=True)
    despesa_id = db.Column(db.Integer, db.ForeignKey('despesas.id'), nullable=False)
    numero_parcela = db.Column(db.Integer, nullable=False)
    total_parcelas = db.Column(db.Integer, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    data_pagamento = db.Column(db.Date)
    valor = db.Column(db.Float, default=0)
    valor_pago = db.Column(db.Float, default=0)
    forma_pagamento_id = db.Column(db.Integer, db.ForeignKey('formas_pagamento.id'))
    conta_id = db.Column(db.Integer, db.ForeignKey('contas_bancarias.id'))
    status = db.Column(db.String(20), default='PENDENTE')
    observacao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    despesa = db.relationship('Despesa', back_populates='parcelas')
    conta = db.relationship('ContaBancaria', back_populates='parcelas_despesa')
    forma_pagamento = db.relationship('FormaPagamento', back_populates='parcelas_despesa')
    
    @property
    def dias_atraso(self):
        if self.status in ['PENDENTE', 'PARCIAL'] and self.data_vencimento < date.today():
            return (date.today() - self.data_vencimento).days
        return 0
    
    def atualizar_status(self):
        """Atualiza o status baseado na data de vencimento e pagamento"""
        if self.valor_pago >= self.valor:
            self.status = 'PAGO'
        elif self.valor_pago > 0:
            self.status = 'PARCIAL'
        elif self.data_vencimento < date.today():
            self.status = 'ATRASADO'
        else:
            self.status = 'PENDENTE'

# ========== MODELO DE MATERIAL ==========
class Material(db.Model):
    __tablename__ = 'materiais'
    
    id = db.Column(db.Integer, primary_key=True)
    obra_id = db.Column(db.Integer, db.ForeignKey('obras.id'), nullable=False)
    conta_id = db.Column(db.Integer, db.ForeignKey('contas_bancarias.id'))
    forma_pagamento_id = db.Column(db.Integer, db.ForeignKey('formas_pagamento.id'))
    item_abc_id = db.Column(db.Integer, db.ForeignKey('itens_abc.id'))
    data = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    fornecedor = db.Column(db.String(200))
    quantidade = db.Column(db.Float)
    unidade = db.Column(db.String(20))
    valor_unitario = db.Column(db.Float)
    valor_total = db.Column(db.Float, default=0)
    quantidade_parcelas = db.Column(db.Integer, default=1)
    data_primeira_parcela = db.Column(db.Date)
    valor_pago = db.Column(db.Float, default=0)
    data_pagamento = db.Column(db.Date)
    item_associado = db.Column(db.String(50))
    centro_custo = db.Column(db.String(100))
    observacao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    obra = db.relationship('Obra', back_populates='materiais')
    conta = db.relationship('ContaBancaria', back_populates='materiais')
    forma_pagamento = db.relationship('FormaPagamento', foreign_keys=[forma_pagamento_id])
    item_abc = db.relationship('ItemABC', back_populates='materiais')
    
    @property
    def status(self):
        if self.valor_pago >= self.valor_total:
            return 'PAGO'
        elif self.valor_pago > 0:
            return 'PARCIAL'
        else:
            return 'PENDENTE'

# ========== MODELO DE MÃO DE OBRA ==========
class MaoObra(db.Model):
    __tablename__ = 'mao_obra'
    
    id = db.Column(db.Integer, primary_key=True)
    obra_id = db.Column(db.Integer, db.ForeignKey('obras.id'), nullable=False)
    conta_id = db.Column(db.Integer, db.ForeignKey('contas_bancarias.id'))
    forma_pagamento_id = db.Column(db.Integer, db.ForeignKey('formas_pagamento.id'))
    item_abc_id = db.Column(db.Integer, db.ForeignKey('itens_abc.id'))
    data = db.Column(db.Date, nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    funcionario = db.Column(db.String(200))
    funcao = db.Column(db.String(100))
    horas_trabalhadas = db.Column(db.Float)
    valor_hora = db.Column(db.Float)
    valor_total = db.Column(db.Float, default=0)
    quantidade_parcelas = db.Column(db.Integer, default=1)
    data_primeira_parcela = db.Column(db.Date)
    valor_pago = db.Column(db.Float, default=0)
    data_pagamento = db.Column(db.Date)
    item_associado = db.Column(db.String(50))
    centro_custo = db.Column(db.String(100))
    observacao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    obra = db.relationship('Obra', back_populates='mao_obra')
    conta = db.relationship('ContaBancaria', back_populates='mao_obra')
    forma_pagamento = db.relationship('FormaPagamento', foreign_keys=[forma_pagamento_id])
    item_abc = db.relationship('ItemABC', back_populates='mao_obra')
    
    @property
    def status(self):
        if self.valor_pago >= self.valor_total:
            return 'PAGO'
        elif self.valor_pago > 0:
            return 'PARCIAL'
        else:
            return 'PENDENTE'