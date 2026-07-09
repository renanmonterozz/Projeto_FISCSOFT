
-- Schema fiscsoft
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `fiscsoft` DEFAULT CHARACTER SET utf8 ;
USE `fiscsoft` ;

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
  UNIQUE INDEX `Nº nota-fiscal_UNIQUE` (`nota_fiscal` ASC) VISIBLE,
  UNIQUE INDEX `chave_de_acesso_UNIQUE` (`chave_de_acesso` ASC) VISIBLE,
  PRIMARY KEY (`nota_fiscal`, `agente ibama_matricula`),
  INDEX `fk_nota fiscal_agente ibama1_idx` (`agente ibama_matricula` ASC) VISIBLE,
  CONSTRAINT `fk_nota fiscal_agente ibama1`
    FOREIGN KEY (`agente ibama_matricula`)
    REFERENCES `fiscsoft`.`agente ibama` (`matricula`)
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
  `preço_unitário` DECIMAL(10,2) NOT NULL,
  `data_validade` DATE NULL,
  `nota fiscal_nota_fiscal` VARCHAR(50) NOT NULL,
  `nota fiscal_agente ibama_matricula` INT NOT NULL,
  PRIMARY KEY (`lote`, `nota fiscal_nota_fiscal`, `nota fiscal_agente ibama_matricula`),
  UNIQUE INDEX `lote_UNIQUE` (`lote` ASC) VISIBLE,
  INDEX `fk_produtos_nota fiscal1_idx` (`nota fiscal_nota_fiscal` ASC, `nota fiscal_agente ibama_matricula` ASC) VISIBLE,
  CONSTRAINT `fk_produtos_nota fiscal1`
    FOREIGN KEY (`nota fiscal_nota_fiscal` , `nota fiscal_agente ibama_matricula`)
    REFERENCES `fiscsoft`.`nota fiscal` (`nota_fiscal` , `agente ibama_matricula`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fiscsoft`.`insumo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fiscsoft`.`insumo` (
  `nome` VARCHAR(255) NOT NULL,
  `tipo` VARCHAR(255) NOT NULL,
  `descrição` TEXT(255) NULL,
  `justificativa` TEXT(255) NULL,
  `link` TINYTEXT NULL,
  `preço_orcado` DECIMAL(8,2) NOT NULL,
  `id_insumo` INT NOT NULL AUTO_INCREMENT,
  `infrator_id_infrator` INT NOT NULL,
  `produtos_lote` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id_insumo`, `infrator_id_infrator`, `produtos_lote`),
  UNIQUE INDEX `id_insumo_UNIQUE` (`id_insumo` ASC) VISIBLE,
  INDEX `fk_insumo_infrator1_idx` (`infrator_id_infrator` ASC) VISIBLE,
  INDEX `fk_insumo_produtos1_idx` (`produtos_lote` ASC) VISIBLE,
  CONSTRAINT `fk_insumo_infrator1`
    FOREIGN KEY (`infrator_id_infrator`)
    REFERENCES `fiscsoft`.`infrator` (`id_infrator`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_insumo_produtos1`
    FOREIGN KEY (`produtos_lote`)
    REFERENCES `fiscsoft`.`produtos` (`lote`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `fiscsoft`.`insumo_has_TCCM`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fiscsoft`.`insumo_has_TCCM` (
  `insumo_id_insumo` INT NOT NULL,
  `insumo_infrator_id_infrator` INT NOT NULL,
  `insumo_produtos_lote` VARCHAR(255) NOT NULL,
  `TCCM_processo` CHAR(20) NOT NULL,
  `TCCM_agente ibama_matricula` INT NOT NULL,
  `TCCM_infrator_id_infrator` INT NOT NULL,
  PRIMARY KEY (`insumo_id_insumo`, `insumo_infrator_id_infrator`, `insumo_produtos_lote`, `TCCM_processo`, `TCCM_agente ibama_matricula`, `TCCM_infrator_id_infrator`),
  INDEX `fk_insumo_has_TCCM_TCCM1_idx` (`TCCM_processo` ASC, `TCCM_agente ibama_matricula` ASC, `TCCM_infrator_id_infrator` ASC) VISIBLE,
  INDEX `fk_insumo_has_TCCM_insumo1_idx` (`insumo_id_insumo` ASC, `insumo_infrator_id_infrator` ASC, `insumo_produtos_lote` ASC) VISIBLE,
  CONSTRAINT `fk_insumo_has_TCCM_insumo1`
    FOREIGN KEY (`insumo_id_insumo` , `insumo_infrator_id_infrator` , `insumo_produtos_lote`)
    REFERENCES `fiscsoft`.`insumo` (`id_insumo` , `infrator_id_infrator` , `produtos_lote`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_insumo_has_TCCM_TCCM1`
    FOREIGN KEY (`TCCM_processo` , `TCCM_agente ibama_matricula` , `TCCM_infrator_id_infrator`)
    REFERENCES `fiscsoft`.`TCCM` (`processo` , `agente ibama_matricula` , `infrator_id_infrator`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


