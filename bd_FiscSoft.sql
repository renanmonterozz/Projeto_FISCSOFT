CREATE DATABASE  IF NOT EXISTS `fiscsoft` /*!40100 DEFAULT CHARACTER SET utf8mb3 */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `fiscsoft`;
-- MySQL dump 10.13  Distrib 8.0.33, for Win64 (x86_64)
--
-- Host: localhost    Database: fiscsoft
-- ------------------------------------------------------
-- Server version	8.0.31

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `agente ibama`
--

DROP TABLE IF EXISTS `agente ibama`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agente ibama` (
  `matricula` int NOT NULL,
  `login` varchar(50) NOT NULL,
  `senha` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  `nome_agente` varchar(45) NOT NULL,
  `status` varchar(20) DEFAULT 'ativo',
  `perfil` varchar(30) DEFAULT 'Agente',
  `cpf` varchar(45) NOT NULL,
  `telefone` char(11) DEFAULT NULL,
  PRIMARY KEY (`matricula`),
  UNIQUE KEY `matricula_UNIQUE` (`matricula`),
  UNIQUE KEY `email senha_UNIQUE` (`email`),
  UNIQUE KEY `cpf_UNIQUE` (`cpf`),
  UNIQUE KEY `login` (`login`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `agente ibama`
--

LOCK TABLES `agente ibama` WRITE;
/*!40000 ALTER TABLE `agente ibama` DISABLE KEYS */;
INSERT INTO `agente ibama` VALUES (0,'admin','123456','admin@ibama.gov.br','Carlos Silva','ativo','Administrador','12345678901',NULL);
/*!40000 ALTER TABLE `agente ibama` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `infrator`
--

DROP TABLE IF EXISTS `infrator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `infrator` (
  `cpf` varchar(11) NOT NULL,
  `email` varchar(100) NOT NULL,
  `senha` varchar(255) NOT NULL,
  `id_infrator` int NOT NULL AUTO_INCREMENT,
  `nome_infrator` varchar(45) NOT NULL,
  `telefone_infrator` char(11) DEFAULT NULL,
  PRIMARY KEY (`id_infrator`),
  UNIQUE KEY `cpf_UNIQUE` (`cpf`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `id_infrator_UNIQUE` (`id_infrator`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `infrator`
--

LOCK TABLES `infrator` WRITE;
/*!40000 ALTER TABLE `infrator` DISABLE KEYS */;
INSERT INTO `infrator` VALUES ('12345678901','joao@email.com','senha123',1,'João Silva','11987654321'),('23456789012','maria@email.com','senha456',2,'Maria Oliveira','11976543210'),('34567890123','pedro@email.com','senha789',3,'Pedro Santos','11965432109'),('45678901234','ana@email.com','senha321',4,'Ana Costa','11954321098');
/*!40000 ALTER TABLE `infrator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insumo`
--

DROP TABLE IF EXISTS `insumo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insumo` (
  `nome` varchar(255) NOT NULL,
  `tipo` varchar(255) NOT NULL,
  `descrição` text,
  `justificativa` text,
  `link` tinytext,
  `preço_orcado` decimal(8,2) NOT NULL,
  `id_insumo` int NOT NULL AUTO_INCREMENT,
  `infrator_id_infrator` int NOT NULL,
  `produtos_lote` varchar(255) NOT NULL,
  PRIMARY KEY (`id_insumo`,`infrator_id_infrator`,`produtos_lote`),
  UNIQUE KEY `id_insumo_UNIQUE` (`id_insumo`),
  KEY `fk_insumo_infrator1_idx` (`infrator_id_infrator`),
  KEY `fk_insumo_produtos1_idx` (`produtos_lote`),
  CONSTRAINT `fk_insumo_infrator1` FOREIGN KEY (`infrator_id_infrator`) REFERENCES `infrator` (`id_infrator`),
  CONSTRAINT `fk_insumo_produtos1` FOREIGN KEY (`produtos_lote`) REFERENCES `produtos` (`lote`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insumo`
--

LOCK TABLES `insumo` WRITE;
/*!40000 ALTER TABLE `insumo` DISABLE KEYS */;
/*!40000 ALTER TABLE `insumo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insumo_has_tccm`
--

DROP TABLE IF EXISTS `insumo_has_tccm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insumo_has_tccm` (
  `insumo_id_insumo` int NOT NULL,
  `insumo_infrator_id_infrator` int NOT NULL,
  `insumo_produtos_lote` varchar(255) NOT NULL,
  `TCCM_processo` char(20) NOT NULL,
  `TCCM_agente ibama_matricula` int NOT NULL,
  `TCCM_infrator_id_infrator` int NOT NULL,
  PRIMARY KEY (`insumo_id_insumo`,`insumo_infrator_id_infrator`,`insumo_produtos_lote`,`TCCM_processo`,`TCCM_agente ibama_matricula`,`TCCM_infrator_id_infrator`),
  KEY `fk_insumo_has_TCCM_TCCM1_idx` (`TCCM_processo`,`TCCM_agente ibama_matricula`,`TCCM_infrator_id_infrator`),
  KEY `fk_insumo_has_TCCM_insumo1_idx` (`insumo_id_insumo`,`insumo_infrator_id_infrator`,`insumo_produtos_lote`),
  CONSTRAINT `fk_insumo_has_TCCM_insumo1` FOREIGN KEY (`insumo_id_insumo`, `insumo_infrator_id_infrator`, `insumo_produtos_lote`) REFERENCES `insumo` (`id_insumo`, `infrator_id_infrator`, `produtos_lote`),
  CONSTRAINT `fk_insumo_has_TCCM_TCCM1` FOREIGN KEY (`TCCM_processo`, `TCCM_agente ibama_matricula`, `TCCM_infrator_id_infrator`) REFERENCES `tccm` (`processo`, `agente ibama_matricula`, `infrator_id_infrator`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insumo_has_tccm`
--

LOCK TABLES `insumo_has_tccm` WRITE;
/*!40000 ALTER TABLE `insumo_has_tccm` DISABLE KEYS */;
/*!40000 ALTER TABLE `insumo_has_tccm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `itens`
--

DROP TABLE IF EXISTS `itens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `itens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(200) DEFAULT NULL,
  `descricao` varchar(200) NOT NULL,
  `codigo_interno` varchar(50) NOT NULL,
  `categoria` varchar(100) DEFAULT NULL,
  `semestre` varchar(20) DEFAULT NULL,
  `quantidade_prevista` int DEFAULT '0',
  `status` varchar(30) DEFAULT 'Ativo',
  `tipo` varchar(50) DEFAULT NULL,
  `notas_fiscais` varchar(100) DEFAULT NULL,
  `criado_em` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo_interno` (`codigo_interno`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `itens`
--

LOCK TABLES `itens` WRITE;
/*!40000 ALTER TABLE `itens` DISABLE KEYS */;
INSERT INTO `itens` VALUES (1,'Monitor Dell 24\"','Monitor Dell 24\"','IT-001','Eletrônicos',NULL,0,'Ativo','Equipamento','NF-001234','2026-06-26 23:05:18'),(2,'Cadeira Ergonômica','Cadeira Ergonômica','IT-002','Mobiliário',NULL,0,'Ativo','Móvel','NF-001235','2026-06-26 23:05:18'),(3,'Notebook Lenovo','Notebook Lenovo','IT-003','Eletrônicos',NULL,0,'Pendente','Equipamento','NF-001236','2026-06-26 23:05:18'),(4,'Mesa de Escritório','Mesa de Escritório','IT-004','Mobiliário',NULL,0,'Ativo','Móvel','NF-001234','2026-06-26 23:05:18'),(5,'Impressora HP','Impressora HP','IT-005','Eletrônicos',NULL,0,'Inativo','Equipamento','NF-001235','2026-06-26 23:05:18'),(6,'Teclado USB','Teclado USB','IT-006','Eletrônicos',NULL,0,'Ativo','Periférico','NF-001236','2026-06-26 23:05:18'),(7,'Cadeira Executiva','Cadeira Executiva','IT-007','Mobiliário',NULL,0,'Ativo','Móvel','NF-001234','2026-06-26 23:05:18'),(8,'computador','dell','',NULL,'3',100,'Ativo',NULL,NULL,'2026-06-27 00:11:24');
/*!40000 ALTER TABLE `itens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nota fiscal`
--

DROP TABLE IF EXISTS `nota fiscal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nota fiscal` (
  `nota_fiscal` varchar(50) NOT NULL,
  `semestre` tinyint NOT NULL,
  `data` date NOT NULL,
  `chave_de_acesso` varchar(44) NOT NULL,
  `valor_total` decimal(8,2) NOT NULL,
  `agente ibama_matricula` int NOT NULL,
  PRIMARY KEY (`nota_fiscal`,`agente ibama_matricula`),
  UNIQUE KEY `Nº nota-fiscal_UNIQUE` (`nota_fiscal`),
  UNIQUE KEY `chave_de_acesso_UNIQUE` (`chave_de_acesso`),
  KEY `fk_nota fiscal_agente ibama1_idx` (`agente ibama_matricula`),
  CONSTRAINT `fk_nota fiscal_agente ibama1` FOREIGN KEY (`agente ibama_matricula`) REFERENCES `agente ibama` (`matricula`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nota fiscal`
--

LOCK TABLES `nota fiscal` WRITE;
/*!40000 ALTER TABLE `nota fiscal` DISABLE KEYS */;
/*!40000 ALTER TABLE `nota fiscal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `produtos`
--

DROP TABLE IF EXISTS `produtos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `produtos` (
  `lote` varchar(255) NOT NULL,
  `status_entrega` enum('pendente','entregue','parcial') NOT NULL DEFAULT 'pendente',
  `quantidade` int NOT NULL DEFAULT '0',
  `preço_unitário` decimal(10,2) NOT NULL,
  `data_validade` date DEFAULT NULL,
  `nota fiscal_nota_fiscal` varchar(50) NOT NULL,
  `nota fiscal_agente ibama_matricula` int NOT NULL,
  PRIMARY KEY (`lote`,`nota fiscal_nota_fiscal`,`nota fiscal_agente ibama_matricula`),
  UNIQUE KEY `lote_UNIQUE` (`lote`),
  KEY `fk_produtos_nota fiscal1_idx` (`nota fiscal_nota_fiscal`,`nota fiscal_agente ibama_matricula`),
  CONSTRAINT `fk_produtos_nota fiscal1` FOREIGN KEY (`nota fiscal_nota_fiscal`, `nota fiscal_agente ibama_matricula`) REFERENCES `nota fiscal` (`nota_fiscal`, `agente ibama_matricula`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `produtos`
--

LOCK TABLES `produtos` WRITE;
/*!40000 ALTER TABLE `produtos` DISABLE KEYS */;
/*!40000 ALTER TABLE `produtos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tccm`
--

DROP TABLE IF EXISTS `tccm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tccm` (
  `processo` char(20) NOT NULL,
  `total_pago` decimal(12,2) NOT NULL DEFAULT '0.00',
  `total_validado` decimal(12,2) NOT NULL,
  `data_validade` date DEFAULT NULL,
  `intervalo` tinyint NOT NULL,
  `total_devido` decimal(12,2) NOT NULL,
  `status` enum('pendente','concluido','atrasado') NOT NULL DEFAULT 'pendente',
  `agente ibama_matricula` int NOT NULL,
  `infrator_id_infrator` int NOT NULL,
  PRIMARY KEY (`processo`,`agente ibama_matricula`,`infrator_id_infrator`),
  UNIQUE KEY `processo_UNIQUE` (`processo`),
  KEY `fk_TCCM_agente ibama_idx` (`agente ibama_matricula`),
  KEY `fk_TCCM_infrator1_idx` (`infrator_id_infrator`),
  CONSTRAINT `fk_TCCM_agente ibama` FOREIGN KEY (`agente ibama_matricula`) REFERENCES `agente ibama` (`matricula`),
  CONSTRAINT `fk_TCCM_infrator1` FOREIGN KEY (`infrator_id_infrator`) REFERENCES `infrator` (`id_infrator`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tccm`
--

LOCK TABLES `tccm` WRITE;
/*!40000 ALTER TABLE `tccm` DISABLE KEYS */;
/*!40000 ALTER TABLE `tccm` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-02 20:06:09
