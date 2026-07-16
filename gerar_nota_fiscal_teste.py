from fpdf import FPDF
import random
import string


def gerar_chave_acesso():
    return ''.join(random.choices(string.digits, k=44))


def gerar_cnpj():
    return ''.join(random.choices(string.digits, k=14))


def gerar_cpf():
    return ''.join(random.choices(string.digits, k=11))


def gerar_numero_nf():
    return ''.join(random.choices(string.digits, k=9))


class NotaFiscalPDF(FPDF):
    def header(self):
        self.set_fill_color(0, 100, 0)
        self.rect(10, 10, 190, 25, 'F')
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(255, 255, 255)
        self.set_y(14)
        self.cell(0, 8, 'NOTA FISCAL ELETRONICA', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_font('Helvetica', '', 9)
        self.cell(0, 6, 'Autorizacao de uso concedida pela SEFAZ', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_y(40)

    def footer(self):
        self.set_y(-20)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, f'Chave de Acesso: {self.chave_acesso}', align='C', new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 5, f'Consulte a autenticidade em: www.nfe.fazenda.gov.br', align='C', new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 5, f'Pagina {self.page_no()}/{{nb}}', align='C')


def gerar_nota_fiscal(caminho_saida=None):
    numero_nf = gerar_numero_nf()
    chave_acesso = gerar_chave_acesso()
    cnpj_emitente = gerar_cnpj()
    cnpj_destinatario = gerar_cnpj()

    pdf = NotaFiscalPDF()
    pdf.chave_acesso = chave_acesso
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f'NFe N. {numero_nf}   -   Serie 1', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 7, 'DADOS DO EMITENTE', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 5, f'Razao Social: IBAMA - Instituto Brasileiro do Meio Ambiente', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 5, f'CNPJ: {cnpj_emitente[:2]}.{cnpj_emitente[2:5]}.{cnpj_emitente[5:8]}/{cnpj_emitente[8:12]}-{cnpj_emitente[12:]}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 5, 'Endereco: Esplanada dos Ministerios, Bloco D, Brasilia - DF', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 5, 'Telefone: (61) 3674-7000   -   Email: contato@ibama.gov.br', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 5, 'CNAE: 8421-4/00   -   Regime Tributario: Simples Nacional', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(3)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 7, 'DADOS DO DESTINATARIO', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 9)
    cpf = gerar_cpf()
    pdf.cell(0, 5, f'Razao Social / Nome: Empresa Comercial ABC Ltda', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 5, f'CPF/CNPJ: {cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 5, 'Endereco: Av. Paulista, 1578, Bela Vista, Sao Paulo - SP', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 5, 'CEP: 01310-100   -   Telefone: (11) 3015-5000', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(3)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 7, 'DADOS DA NOTA FISCAL', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(95, 5, f'Numero: {numero_nf}', new_x='RIGHT')
    pdf.cell(95, 5, 'Serie: 001', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(95, 5, f'Data de Emissao: 15/07/2026', new_x='RIGHT')
    pdf.cell(95, 5, f'Data de Entrada/Saida: 15/07/2026', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(95, 5, 'Tipo de Operacao: Venda', new_x='RIGHT')
    pdf.cell(95, 5, 'Modalidade do Frete: Por conta do Emitente', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(3)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 7, 'PRODUTOS / SERVICOS', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(1)

    produtos = [
        {
            'codigo': '1.001.0001',
            'descricao': 'Monitor Dell 24" UltraSharp',
            'ncm': '8528.52.00',
            'cfop': '5102',
            'unidade': 'UN',
            'qtde': 5,
            'valor_unit': 1850.00,
        },
        {
            'codigo': '1.001.0002',
            'descricao': 'Cadeira Ergonomica Executive',
            'ncm': '9401.30.00',
            'cfop': '5102',
            'unidade': 'UN',
            'qtde': 10,
            'valor_unit': 1200.00,
        },
        {
            'codigo': '1.001.0003',
            'descricao': 'Notebook Lenovo ThinkPad T14',
            'ncm': '8471.30.12',
            'cfop': '5102',
            'unidade': 'UN',
            'qtde': 3,
            'valor_unit': 7500.00,
        },
        {
            'codigo': '1.001.0004',
            'descricao': 'Teclado USB Mecanico ABNT2',
            'ncm': '8471.60.50',
            'cfop': '5102',
            'unidade': 'UN',
            'qtde': 15,
            'valor_unit': 350.00,
        },
        {
            'codigo': '1.001.0005',
            'descricao': 'Mesa de Escritorio Ajustavel',
            'ncm': '9403.30.00',
            'cfop': '5102',
            'unidade': 'UN',
            'qtde': 8,
            'valor_unit': 2100.00,
        },
    ]

    pdf.set_font('Helvetica', 'B', 8)
    col_w = [22, 50, 18, 12, 14, 14, 16, 22, 22]
    headers = ['Codigo', 'Descricao', 'NCM/SH', 'CFOP', 'Unid.', 'Qtde', 'Vl.Unit.', 'Vl.Total', 'Desc.(%)']
    pdf.set_fill_color(240, 240, 240)
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 6, h, border=1, align='C', fill=True)
    pdf.ln()

    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(0, 0, 0)
    total_geral = 0
    for p in produtos:
        valor_total_item = p['qtde'] * p['valor_unit']
        total_geral += valor_total_item
        desconto = 0
        pdf.cell(col_w[0], 6, p['codigo'], border=1, align='C')
        pdf.cell(col_w[1], 6, p['descricao'][:28], border=1, align='L')
        pdf.cell(col_w[2], 6, p['ncm'], border=1, align='C')
        pdf.cell(col_w[3], 6, p['cfop'], border=1, align='C')
        pdf.cell(col_w[4], 6, p['unidade'], border=1, align='C')
        pdf.cell(col_w[5], 6, str(p['qtde']), border=1, align='C')
        pdf.cell(col_w[6], 6, f'{p["valor_unit"]:.2f}', border=1, align='R')
        pdf.cell(col_w[7], 6, f'{valor_total_item:.2f}', border=1, align='R')
        pdf.cell(col_w[8], 6, f'{desconto:.2f}', border=1, align='R')
        pdf.ln()

    pdf.ln(4)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 7, 'VALORES TOTAIS', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(95, 5, f'Base de Calculo do ICMS: R$ {total_geral:,.2f}', new_x='RIGHT')
    pdf.cell(95, 5, f'Valor do ICMS: R$ 0,00', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(95, 5, f'Valor do IPI: R$ 0,00', new_x='RIGHT')
    pdf.cell(95, 5, f'Valor Total dos Produtos: R$ {total_geral:,.2f}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(95, 5, f'Valor do Frete: R$ 0,00', new_x='RIGHT')
    pdf.cell(95, 5, f'Valor do Seguro: R$ 0,00', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(95, 5, f'Outras Despesas: R$ 0,00', new_x='RIGHT')
    pdf.cell(95, 5, f'Valor do Desconto: R$ 0,00', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 100, 0)
    pdf.cell(95, 8, '', new_x='RIGHT')
    pdf.cell(95, 8, f'VALOR TOTAL DA NOTA: R$ {total_geral:,.2f}', new_x='LMARGIN', new_y='NEXT')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 7, 'INFORMACOES ADICIONAIS', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 9)
    pdf.multi_cell(0, 5,
        'Nota fiscal referente a aquisicao de equipamentos de TI para modernizacao '
        'da infraestrutura tecnologica do IBAMA. Projeto FISCSOFT - Sistema de '
        'Fiscalizacao. Documento gerado automaticamente para fins de teste.'
    )
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 7, 'PROTOCOLO DE AUTORIZACAO DE USO', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(95, 5, f'Protocolo: {random.randint(100000000000, 999999999999)}', new_x='RIGHT')
    pdf.cell(95, 5, f'Data/Hora: 15/07/2026 14:32:17', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(95, 5, 'Situacao: Autorizada', new_x='RIGHT')
    pdf.cell(95, 5, 'UF: DF', new_x='LMARGIN', new_y='NEXT')

    if caminho_saida is None:
        caminho_saida = 'nota_fiscal_teste.pdf'
    pdf.output(caminho_saida)
    print(f'Nota fiscal gerada: {caminho_saida}')
    print(f'Numero: {numero_nf}')
    print(f'Chave de Acesso: {chave_acesso}')
    print(f'Valor Total: R$ {total_geral:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'))
    return caminho_saida, numero_nf, chave_acesso


if __name__ == '__main__':
    gerar_nota_fiscal()
