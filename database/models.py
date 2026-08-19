from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.orm import Base


class AgenteIbama(Base):
    __tablename__ = "agente ibama"

    matricula: Mapped[int] = mapped_column(Integer, primary_key=True)
    senha: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    nome_agente: Mapped[str] = mapped_column(String(45), nullable=False)
    cpf: Mapped[str] = mapped_column(String(45), nullable=False, unique=True)
    telefone: Mapped[str | None] = mapped_column(Text)
    login: Mapped[str] = mapped_column(String(45), nullable=False, unique=True)
    perfil: Mapped[str] = mapped_column(String(50), nullable=False, default="agente")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ativo")
    cadastrado_por: Mapped[str | None] = mapped_column(String(45))
    atualizado_por: Mapped[str | None] = mapped_column(String(45))


class Infrator(Base):
    __tablename__ = "infrator"

    id_infrator: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    senha: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_infrator: Mapped[str] = mapped_column(String(45), nullable=False)
    telefone_infrator: Mapped[str | None] = mapped_column(Text)


class Tccm(Base):
    __tablename__ = "tccm"

    processo: Mapped[str] = mapped_column(String(100), primary_key=True)
    agente_matricula: Mapped[int] = mapped_column("agente ibama_matricula", Integer, primary_key=True)
    infrator_id: Mapped[int] = mapped_column("infrator_id_infrator", Integer, primary_key=True)
    total_pago: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    total_validado: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    data_validade: Mapped[date | None] = mapped_column(Date)
    intervalo: Mapped[int] = mapped_column(Integer, nullable=False)
    total_devido: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pendente")
    documento_sei: Mapped[str | None] = mapped_column(Text)
    data_inicio: Mapped[date | None] = mapped_column(Date)
    semestres: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class NotaFiscal(Base):
    __tablename__ = "nota fiscal"

    nota_fiscal: Mapped[str] = mapped_column(String(50), primary_key=True)
    agente_matricula: Mapped[int] = mapped_column("agente ibama_matricula", Integer, primary_key=True)
    semestre: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    chave_de_acesso: Mapped[str] = mapped_column(String(44), nullable=False, unique=True)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    status_nota: Mapped[str | None] = mapped_column(String(30), default="Pendente")
    processo: Mapped[str | None] = mapped_column(String(100))
    arquivo: Mapped[str | None] = mapped_column(Text)


class Produto(Base):
    __tablename__ = "produtos"

    lote: Mapped[str] = mapped_column(String(255), primary_key=True)
    nota_fiscal: Mapped[str] = mapped_column("nota fiscal_nota_fiscal", String(50), primary_key=True)
    agente_matricula: Mapped[int] = mapped_column("nota fiscal_agente ibama_matricula", Integer, primary_key=True)
    status_entrega: Mapped[str] = mapped_column(Text, nullable=False, default="pendente")
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    data_validade: Mapped[date | None] = mapped_column(Date)
    itens_id: Mapped[int | None] = mapped_column(Integer)
    nome_item: Mapped[str | None] = mapped_column(String(200))


class Item(Base):
    __tablename__ = "itens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str | None] = mapped_column(String(200))
    descricao: Mapped[str] = mapped_column(String(200), nullable=False)
    codigo_interno: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    categoria: Mapped[str | None] = mapped_column(String(100))
    tipo: Mapped[str | None] = mapped_column(String(50))
    justificativa: Mapped[str | None] = mapped_column(Text)
    unidade_medida: Mapped[str | None] = mapped_column(String(50))
    semestre: Mapped[str | None] = mapped_column(String(20))
    quantidade_prevista: Mapped[int | None] = mapped_column(Integer, default=0)
    status: Mapped[str | None] = mapped_column(String(30), default="Ativo")
    notas_fiscais: Mapped[str | None] = mapped_column(String(100))
    processo: Mapped[str | None] = mapped_column(String(100))
    criado_em: Mapped[datetime | None] = mapped_column(DateTime)


class ItemSemestre(Base):
    __tablename__ = "item_semestre"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    itens_id: Mapped[int] = mapped_column(Integer, nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    semestre: Mapped[int] = mapped_column(Integer, nullable=False)
    quantidade_prevista: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processo: Mapped[str | None] = mapped_column(String(100))


class Local(Base):
    __tablename__ = "locais"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cep: Mapped[str] = mapped_column(String(10), nullable=False)
    endereco: Mapped[str] = mapped_column(String(255), nullable=False)
    instituicao: Mapped[str] = mapped_column(String(200), nullable=False)
    responsavel: Mapped[str] = mapped_column(String(100), nullable=False)
    telefone: Mapped[str | None] = mapped_column(String(20))
    criado_em: Mapped[datetime | None] = mapped_column(DateTime)


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario: Mapped[str] = mapped_column(String(100), nullable=False)
    acao: Mapped[str] = mapped_column(String(50), nullable=False)
    tabela: Mapped[str] = mapped_column(String(50), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    criado_em: Mapped[datetime | None] = mapped_column(DateTime)


class Insumo(Base):
    __tablename__ = "insumo"

    id_insumo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    justificativa: Mapped[str | None] = mapped_column(Text)
    link: Mapped[str | None] = mapped_column(Text)
    preco_orcado: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    infrator_id: Mapped[int] = mapped_column("infrator_id_infrator", Integer, nullable=False)
    produto_lote: Mapped[str] = mapped_column("produtos_lote", String(255), nullable=False)


class InsumoTccm(Base):
    __tablename__ = "insumo_has_TCCM"

    insumo_id: Mapped[int] = mapped_column("insumo_id_insumo", Integer, primary_key=True)
    insumo_infrator_id: Mapped[int] = mapped_column("insumo_infrator_id_infrator", Integer, primary_key=True)
    insumo_produto_lote: Mapped[str] = mapped_column("insumo_produtos_lote", String(255), primary_key=True)
    processo: Mapped[str] = mapped_column("TCCM_processo", String(100), primary_key=True)
    agente_matricula: Mapped[int] = mapped_column("TCCM_agente ibama_matricula", Integer, primary_key=True)
    infrator_id: Mapped[int] = mapped_column("TCCM_infrator_id_infrator", Integer, primary_key=True)