# FISCSOFT - Correções Pendentes

Data: 19/08/2026

---

## I. BUGS (Corrigir primeiro)

### B1 - crash cadastrar_infrator.py
- [ ] `screens/cadastrar_infrator.py:44` — trocar `colors` por `COLORS`

### B2 - imports duplicados notas_fiscais_externo.py
- [ ] `screens/notas_fiscais_externo.py:11` — remover import duplicado de `ComboBoxComSeta`
- [ ] `screens/notas_fiscais_externo.py:19` — remover import duplicado de `ASSETS_DIR`

### B3 - requirements.txt conflitante
- [ ] Remover `dotenv==0.9.9` (conflita com `python-dotenv==1.2.2`)
- [ ] Remover `six==1.17.0` (compat Python 2 desnecessário)
- [ ] Remover `mysql-connector-python==9.7.0` (não usa mais MySQL)

---

## II. SEGURANÇA

### S1 - Senha hardcoded
- [ ] `utils.py:34` — remover `"admin123"` hardcoded, usar variável de ambiente ou config

### S2 - Hash legado
- [ ] `utils.py:68-80` — migrar senhas SHA-256 para bcrypt automaticamente no primeiro login

### S3 - Sem lockout
- [ ] `main.py` — adicionar contador de tentativas falhas (bloquear após 5 tentativas)

### S4 - Permissões opcionais
- [ ] `config/permissoes.py` — considerar decorator ou middleware que aplique `pode_acao()` automaticamente

---

## III. QUALIDADE DE CÓDIGO

### Q1 - Função duplicada: carregar_icone()
- [ ] Extrair de `screens/sidebar.py` e `screens/sidebar_externo.py` para `utils.py` ou `config/styles.py`

### Q2 - Função duplicada: _fmt_date()
- [ ] Extrair de `tccm_dashboard.py`, `notas_fiscais.py`, `destinacao.py`, `notas_fiscais_externo.py` para `utils.py`

### Q3 - main.py gigante
- [ ] Separar lógica de login em `screens/login.py` ou `auth.py`
- [ ] Manter apenas App shell e navegação em `main.py`

### Q4 - tccm_dashboard.py gigante
- [ ] Decompor em módulos menores (cadastro, listagem, detalhes)

### Q5 - Sem type hints
- [ ] Adicionar type hints em `utils.py`, `permissoes.py`, `conexaodb.py`

### Q6 - Sem testes
- [ ] Criar `tests/` com testes para: hash_password, verify_password, pode_acao, criar_schema

### Q7 - Nomes misturados PT/EN
- [ ] Padronizar: manter PT para constantes de negócio (`COR_PRIMARIA`), EN para técnicas (`TILE_SIZE`)

---

## IV. FUNCIONALIDADES AUSENTES

### F1 - Validação de entrada
- [ ] CPF: validar 11 dígitos + dígitos verificadores
- [ ] Campos obrigatórios: marcar visualmente
- [ ] Duplicatas: checar login/email/matricula antes de inserir

### F2 - Tratamento de erros DB
- [ ] Adicionar try/except em queries das telas que não tratam

### F3 - Backup SQLite
- [ ] Criar função de backup incremental (copiar .db com timestamp)

### F4 - Exportação unificada
- [ ] openpyxl e pandas já estão no requirements — padronizar exportação de relatórios

---

## V. ARQUITETURA

- [ ] Criar `config/helpers.py` para funções utilitárias compartilhadas
- [ ] Considerar logging estruturado (arquivo + console) além dos logs no DB
- [ ] Adicionar `.editorconfig` e `pyproject.toml` com linter/formatter
