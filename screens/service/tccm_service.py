from __future__ import annotations

import calendar
from datetime import datetime

from screens.repository.tccm_repository import TccmRepository


class RegraTccmError(ValueError):
    """Erro de regra de negocio do cadastro de TCCM."""


class TccmService:
    def __init__(self, repository=None):
        self.repository = repository or TccmRepository()

    def listar_agentes(self):
        return self.repository.listar_agentes()

    def listar_infratores(self):
        return self.repository.listar_infratores()

    def listar_itens_processo(self, processo):
        return self.repository.listar_itens_processo(processo)

    def salvar(self, dados, itens):
        return self.repository.criar_com_itens(dados, itens)

    def criar_infrator(self, dados):
        return self.repository.criar_infrator(dados)

    def criar_agente(self, dados):
        return self.repository.criar_agente(dados)

    def listar_dashboard(self):
        return self.repository.listar_dashboard()

    def buscar_detalhes(self, processo):
        return self.repository.buscar_detalhes(processo)


def calcular_data_validade(data_inicio, semestres):
    try:
        if isinstance(data_inicio, str):
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        total_meses = int(semestres) * 6
        mes_indice = data_inicio.month - 1 + total_meses
        ano = data_inicio.year + mes_indice // 12
        mes = mes_indice % 12 + 1
        dia = min(data_inicio.day, calendar.monthrange(ano, mes)[1])
        return data_inicio.replace(year=ano, month=mes, day=dia)
    except (AttributeError, TypeError, ValueError):
        return None


def validar_item_tccm(nome, descricao, justificativa, quantidade):
    dados = {
        "nome": (nome or "").strip(),
        "descricao": (descricao or "").strip(),
        "justificativa": (justificativa or "").strip(),
        "quantidade": (quantidade or "").strip(),
    }
    if not all((dados["nome"], dados["descricao"], dados["justificativa"], dados["quantidade"])):
        raise RegraTccmError(
            "Preencha nome, descricao, justificativa e quantidade!"
        )
    try:
        dados["quantidade"] = int(dados["quantidade"])
    except ValueError as exc:
        raise RegraTccmError("Quantidade deve ser um numero inteiro!") from exc
    return dados


def validar_cadastro_tccm(
    processo,
    documento_sei,
    data_inicio,
    semestres,
    total_devido,
    agente,
    infrator,
):
    processo = (processo or "").strip()
    documento_sei = (documento_sei or "").strip()
    data_inicio = (data_inicio or "").strip()
    semestres = (semestres or "").strip()
    total_devido = (total_devido or "").strip()
    agente = (agente or "").strip()
    infrator = (infrator or "").strip()

    if not all((processo, data_inicio, semestres, total_devido)):
        raise RegraTccmError(
            "Preencha todos os campos obrigatorios na aba 'Dados do TCCM'!"
        )
    if " - " not in agente:
        raise RegraTccmError("Selecione um agente na aba 'Agente Responsavel'!")
    if " - " not in infrator:
        raise RegraTccmError("Selecione um infrator na aba 'Infrator'!")

    try:
        semestres_val = int(semestres)
    except ValueError as exc:
        raise RegraTccmError("Semestres deve ser um numero inteiro!") from exc

    try:
        total_devido_val = float(total_devido.replace(",", "."))
    except ValueError as exc:
        raise RegraTccmError("Total a ser pago invalido!") from exc

    try:
        data_inicio_dt = datetime.strptime(data_inicio, "%d/%m/%Y")
    except ValueError as exc:
        raise RegraTccmError(
            "Data invalida! Use o formato DD/MM/AAAA."
        ) from exc

    try:
        agente_matricula = int(agente.split(" - ", 1)[0])
        infrator_id = int(infrator.split(" - ", 1)[0])
    except ValueError as exc:
        raise RegraTccmError("Agente ou infrator invalido!") from exc

    return {
        "processo": processo,
        "documento_sei": documento_sei,
        "data_inicio": data_inicio,
        "data_inicio_db": data_inicio_dt.strftime("%Y-%m-%d"),
        "semestres": semestres_val,
        "total_devido": total_devido_val,
        "agente_matricula": agente_matricula,
        "infrator_id": infrator_id,
    }
