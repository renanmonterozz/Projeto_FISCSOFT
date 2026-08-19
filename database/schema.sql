-- Schema fiscsoft (unificado)
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `fiscsoft` DEFAULT CHARACTER SET utf8;
USE `fiscsoft`;

-- -----------------------------------------------------
-- Table `fiscsoft`.`agente ibama`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fiscsoft`.`agente ibama` (
  `matricula` INT NOT NULL,
  `senha` VARCHAR(255) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `nome_agente` VARCHAR(45) NOT NULL,
  `cpf` VARCHAR(45) NOT NULL,
  `telefone` CHAR(11) NULL,
  `login` VARCHAR(45) NOT NULL,
  `perfil` ENUM("agente", "operador", "admin") NOT NULL DEFAULT "agente",
  `status` ENUM("ativo", "inativo") NOT NULL DEFAULT "ativo",
  `cadastrado_por` VARCHAR(45) NULL,
  `atualizado_por` VARCHAR(45) NULL,
  UNIQUE INDEX `matricula_UNIQUE` (`matricula` ASC) VISIBLE,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE,
  UNIQUE INDEX `login_UNIQUE` (`login` ASC) VISIBLE,
  PRIMARY KEY (`matricula`),
  UNIQUE INDEX `cpf_UNIQUE` (`cpf` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fiscsoft`.`infrator`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fiscsoft`.`infrator` (
  `cpf` VARCHAR(11) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `senha` VARCHAR(255) NOT NULL,
  `id_infrator` INT NOT NULL AUTO_INCREMENT,
  `nome_infrator` VARCHAR(45) NOT NULL,
  `telefone_infrator` CHAR(11) NULL,
  UNIQUE INDEX `cpf_UNIQUE` (`cpf` ASC) VISIBLE,
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE,
  UNIQUE INDEX `id_infrator_UNIQUE` (`id_infrator` ASC) VISIBLE,
  PRIMARY KEY (`id_infrator`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fiscsoft`.`TCCM`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fiscsoft`.`TCCM` (
  `processo` CHAR(20) NOT NULL,
  `documento_sei` TEXT NULL,
  `data_inicio` DATE NULL,
  `semestres` INT NOT NULL DEFAULT 1,
  `total_pago` DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  `total_validado` DECIMAL(12,2) NOT NULL,
  `data_validade` DATE NULL,
  `intervalo` TINYINT(2) NOT NULL,
  `total_devido` DECIMAL(12,2) NOT NULL,
  `status` ENUM("pendente", "concluido", "atrasado") NOT NULL DEFAULT 'pendente',
  `agente ibama_matricula` INT NOT NULL,
  `infrator_id_infrator` INT NOT NULL,
  UNIQUE INDEX `processo_UNIQUE` (`processo` ASC) VISIBLE,
  PRIMARY KEY (`processo`, `agente ibama_matricula`, `infrator_id_infrator`),
  INDEX `fk_TCCM_agente ibama_idx` (`agente ibama_matricula` ASC) VISIBLE,
  INDEX `fk_TCCM_infrator1_idx` (`infrator_id_infrator` ASC) VISIBLE,
  CONSTRAINT `fk_TCCM_agente ibama`
    FOREIGN KEY (`agente ibama_matricula`)
    REFERENCES `fiscsoft`.`agente ibama` (`matricula`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_TCCM_infrator1`
    FOREIGN KEY (`infrator_id_infrator`)
    REFERENCES `fiscsoft`.`infrator` (`id_infrator`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fiscsoft`.`nota fiscal`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fiscsoft`.`nota fiscal` (
  `nota_fiscal` VARCHAR(50) NOT NULL,
  `semestre` TINYINT(2) NOT NULL,
  `data` DATE NOT NULL,
  `chave_de_acesso` VARCHAR(44) NOT NULL,
  `valor_total` DECIMAL(8,2) NOT NULL,
  `agente ibama_matricula` INT NOT NULL,
  `status_nota` VARCHAR(30) NULL DEFAULT 'Pendente',
  `processo` TEXT NULL,
  UNIQUE INDEX `nota_fiscal_UNIQUE` (`nota_fiscal` ASC) VISIBLE,
  UNIQUE INDEX `chave_de_acesso_UNIQUE` (`chave_de_acesso` ASC) VISIBLE,
  PRIMARY KEY (`nota_fiscal`, `agente ibama_matricula`),
  INDEX `fk_nota fiscal_agente ibama1_idx` (`agente ibama_matricula` ASC) VISIBLE,
  INDEX `fk_nota fiscal_tccm_idx` (`processo` ASC) VISIBLE,
  CONSTRAINT `fk_nota fiscal_agente ibama1`
    FOREIGN KEY (`agente ibama_matricula`)
    REFERENCES `fiscsoft`.`agente ibama` (`matricula`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_nota fiscal_tccm`
    FOREIGN KEY (`processo`)
    REFERENCES `fiscsoft`.`TCCM` (`processo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fiscsoft`.`produtos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fiscsoft`.`produtos` (
  `lote` VARCHAR(255) NOT NULL,
  `status_entrega` ENUM("pendente", "entregue", "parcial") NOT NULL DEFAULT 'pendente',
  `quantidade` INT NOT NULL DEFAULT 0,
  `preco_unitario` DECIMAL(10,2) NOT NULL,
  `data_validade` DATE NULL,
  `nota fiscal_nota_fiscal` VARCHAR(50) NOT NULL,
  `nota fiscal_agente ibama_matricula` INT NOT NULL,
  `itens_id` INT NULL,
  `nome_item` VARCHAR(200) NULL,
  PRIMARY KEY (`lote`, `nota fiscal_nota_fiscal`, `nota fiscal_agente ibama_matricula`),
  UNIQUE INDEX `lote_UNIQUE` (`lote` ASC) VISIBLE,
  INDEX `fk_produtos_nota fiscal1_idx` (`nota fiscal_nota_fiscal` ASC, `nota fiscal_agente ibama_matricula` ASC) VISIBLE,
  INDEX `fk_produtos_itens_idx` (`itens_id` ASC) VISIBLE,
  CONSTRAINT `fk_produtos_nota fiscal1`
    FOREIGN KEY (`nota fiscal_nota_fiscal` , `nota fiscal_agente ibama_matricula`)
    REFERENCES `fiscsoft`.`nota fiscal` (`nota_fiscal` , `agente ibama_matricula`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_produtos_itens`
    FOREIGN KEY (`itens_id`)
    REFERENCES `fiscsoft`.`itens` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fiscsoft`.`itens`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fiscsoft`.`itens` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(200) NULL,
  `descricao` VARCHAR(200) NOT NULL,
  `codigo_interno` VARCHAR(50) NOT NULL,
  `categoria` VARCHAR(100) NULL,
  `tipo` VARCHAR(50) NULL,
  `justificativa` TEXT NULL,
  `unidade_medida` VARCHAR(50) NULL,
  `semestre` VARCHAR(20) NULL,
  `quantidade_prevista` INT DEFAULT 0,
  `status` VARCHAR(30) DEFAULT 'Ativo',
  `notas_fiscais` VARCHAR(100) NULL,
  `processo` VARCHAR(100) NULL,
  `criado_em` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE INDEX `codigo_interno_UNIQUE` (`codigo_interno` ASC) VISIBLE,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fiscsoft`.`locais`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fiscsoft`.`locais` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `cep` VARCHAR(10) NOT NULL,
  `endereco` VARCHAR(255) NOT NULL,
  `instituicao` VARCHAR(200) NOT NULL,
  `responsavel` VARCHAR(100) NOT NULL,
  `telefone` VARCHAR(20) NULL,
  `criado_em` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fiscsoft`.`logs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fiscsoft`.`logs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `usuario` VARCHAR(100) NOT NULL,
  `acao` VARCHAR(50) NOT NULL,
  `tabela` VARCHAR(50) NOT NULL,
  `descricao` TEXT NOT NULL,
  `criado_em` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fiscsoft`.`item_semestre`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fiscsoft`.`item_semestre` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `itens_id` INT NOT NULL,
  `ano` INT NOT NULL,
  `semestre` INT NOT NULL,
  `quantidade_prevista` INT NOT NULL DEFAULT 0,
  `processo` TEXT NULL,
  UNIQUE INDEX `uk_item_semestre` (`itens_id` ASC, `ano` ASC, `semestre` ASC) VISIBLE,
  PRIMARY KEY (`id`),
  INDEX `fk_item_semestre_itens_idx` (`itens_id` ASC) VISIBLE,
  CONSTRAINT `fk_item_semestre_itens`
    FOREIGN KEY (`itens_id`)
    REFERENCES `fiscsoft`.`itens` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fiscsoft`.`schema_migrations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fiscsoft`.`schema_migrations` (
  `name` TEXT NOT NULL,
  `applied_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE INDEX `uk_schema_migrations` (`name`(255) ASC) VISIBLE)
ENGINE = InnoDB;
