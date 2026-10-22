-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: abarrotes_placencia
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `abarrotes_placencia`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `abarrotes_placencia` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `abarrotes_placencia`;

--
-- Table structure for table `categoria`
--

DROP TABLE IF EXISTS `categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categoria` (
  `ID_Categoria` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Descripcion` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`ID_Categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categoria`
--

LOCK TABLES `categoria` WRITE;
/*!40000 ALTER TABLE `categoria` DISABLE KEYS */;
INSERT INTO `categoria` VALUES (1,'Abarrotes','Productos básicos de despensa',1),(2,'Bebidas','Refrescos, jugos y aguas',1),(3,'Lácteos','Leche, queso y yogurt',1),(4,'Panadería','Pan y repostería',1),(5,'Limpieza','Productos de limpieza del hogar',1),(6,'Cuidado Personal','Higiene y cuidado personal',1),(7,'Snacks','Botanas y frituras',1),(8,'Congelados','Alimentos congelados',1),(9,'Mascotas','Alimento y accesorios para mascotas',1),(10,'Papelería','Artículos de oficina y escolares',1);
/*!40000 ALTER TABLE `categoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `ID_Cliente` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Telefono` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Puntos_Fidelidad` int NOT NULL DEFAULT '0',
  `Fecha_Registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`ID_Cliente`),
  CONSTRAINT `CK_Cliente_Puntos` CHECK ((`Puntos_Fidelidad` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES (1,'Roberto Fernández','3311112222',150,'2025-01-10 00:00:00',1),(2,'Karla Jiménez','3322223333',320,'2025-02-14 00:00:00',1),(3,'Miguel Ángel Torres','3333334444',45,'2025-03-05 00:00:00',1),(4,'Daniela Ortiz','3344445555',0,'2025-04-20 00:00:00',1),(5,'Fernando Castillo','3355556666',890,'2024-11-11 00:00:00',1),(6,'Sofía Vargas','3366667777',200,'2025-05-01 00:00:00',1),(7,'Alejandro Núñez','3377778888',60,'2025-06-15 00:00:00',1),(8,'Paola Medina','3388889999',10,'2025-07-22 00:00:00',1),(9,'Ricardo Salas','3399990000',500,'2024-09-30 00:00:00',1),(10,'Gabriela Reyes','3300001111',25,'2025-08-02 00:00:00',0);
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compra`
--

DROP TABLE IF EXISTS `compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compra` (
  `ID_Compra` int NOT NULL AUTO_INCREMENT,
  `Fecha_Hora` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Total` decimal(10,2) NOT NULL DEFAULT '0.00',
  `Num_Factura` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ID_Proveedor` int NOT NULL,
  `ID_Empleado` int NOT NULL,
  PRIMARY KEY (`ID_Compra`),
  KEY `FK_Compra_Proveedor` (`ID_Proveedor`),
  KEY `FK_Compra_Empleado` (`ID_Empleado`),
  CONSTRAINT `FK_Compra_Empleado` FOREIGN KEY (`ID_Empleado`) REFERENCES `empleado` (`ID_Empleado`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_Compra_Proveedor` FOREIGN KEY (`ID_Proveedor`) REFERENCES `proveedor` (`ID_Proveedor`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `CK_Compra_Total` CHECK ((`Total` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compra`
--

LOCK TABLES `compra` WRITE;
/*!40000 ALTER TABLE `compra` DISABLE KEYS */;
INSERT INTO `compra` VALUES (1,'2026-08-25 08:30:00',1440.00,'CCF-000451',3,5),(2,'2026-08-25 10:15:00',1520.00,'LAL-002310',4,5),(3,'2026-08-26 09:00:00',1260.00,'BIM-118204',2,3),(4,'2026-08-26 11:30:00',2525.00,'DLC-004587',1,3),(5,'2026-08-27 08:45:00',1100.00,'SAB-770912',5,9),(6,'2026-08-27 12:00:00',950.00,'FUD-003345',6,9),(7,'2026-08-28 09:30:00',480.00,'PAJ-009871',7,5),(8,'2026-08-28 13:00:00',1400.00,'PUR-005620',8,3),(9,'2026-08-29 10:00:00',1350.00,'COL-002198',9,5),(10,'2026-08-29 15:20:00',840.00,'DLC-004612',1,3);
/*!40000 ALTER TABLE `compra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_compra`
--

DROP TABLE IF EXISTS `detalle_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_compra` (
  `ID_Compra` int NOT NULL,
  `ID_Producto` int NOT NULL,
  `Cantidad` int NOT NULL,
  `Costo_Unitario` decimal(10,2) NOT NULL,
  `Subtotal` decimal(10,2) NOT NULL,
  PRIMARY KEY (`ID_Compra`,`ID_Producto`),
  KEY `FK_DetCompra_Producto` (`ID_Producto`),
  CONSTRAINT `FK_DetCompra_Compra` FOREIGN KEY (`ID_Compra`) REFERENCES `compra` (`ID_Compra`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_DetCompra_Producto` FOREIGN KEY (`ID_Producto`) REFERENCES `producto` (`ID_Producto`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `CK_DetCompra_Cantidad` CHECK ((`Cantidad` > 0)),
  CONSTRAINT `CK_DetCompra_Costo` CHECK ((`Costo_Unitario` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_compra`
--

LOCK TABLES `detalle_compra` WRITE;
/*!40000 ALTER TABLE `detalle_compra` DISABLE KEYS */;
INSERT INTO `detalle_compra` VALUES (1,1,120,12.00,1440.00),(2,2,80,19.00,1520.00),(3,3,45,28.00,1260.00),(4,4,60,16.00,960.00),(4,5,50,18.00,900.00),(4,7,70,9.50,665.00),(5,6,100,11.00,1100.00),(6,9,25,38.00,950.00),(7,11,40,12.00,480.00),(8,10,20,70.00,1400.00),(9,8,30,45.00,1350.00),(10,4,30,16.00,480.00),(10,5,20,18.00,360.00);
/*!40000 ALTER TABLE `detalle_compra` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_DetalleCompra_AfterInsert` AFTER INSERT ON `detalle_compra` FOR EACH ROW BEGIN
    IF @DISABLE_TRIGGERS IS NULL OR @DISABLE_TRIGGERS = 0 THEN
        UPDATE COMPRA
           SET Total = Total + NEW.Subtotal
         WHERE ID_Compra = NEW.ID_Compra;

        UPDATE PRODUCTO
           SET Stock_Actual = Stock_Actual + NEW.Cantidad
         WHERE ID_Producto = NEW.ID_Producto;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_DetalleCompra_AfterUpdate` AFTER UPDATE ON `detalle_compra` FOR EACH ROW BEGIN
    IF @DISABLE_TRIGGERS IS NULL OR @DISABLE_TRIGGERS = 0 THEN
        UPDATE COMPRA
           SET Total = Total - OLD.Subtotal + NEW.Subtotal
         WHERE ID_Compra = NEW.ID_Compra;

        UPDATE PRODUCTO
           SET Stock_Actual = Stock_Actual - OLD.Cantidad + NEW.Cantidad
         WHERE ID_Producto = NEW.ID_Producto;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_DetalleCompra_AfterDelete` AFTER DELETE ON `detalle_compra` FOR EACH ROW BEGIN
    IF @DISABLE_TRIGGERS IS NULL OR @DISABLE_TRIGGERS = 0 THEN
        UPDATE COMPRA
           SET Total = Total - OLD.Subtotal
         WHERE ID_Compra = OLD.ID_Compra;

        UPDATE PRODUCTO
           SET Stock_Actual = Stock_Actual - OLD.Cantidad
         WHERE ID_Producto = OLD.ID_Producto;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `detalle_venta`
--

DROP TABLE IF EXISTS `detalle_venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_venta` (
  `ID_Venta` int NOT NULL,
  `ID_Producto` int NOT NULL,
  `Cantidad` int NOT NULL,
  `Precio_Unitario` decimal(10,2) NOT NULL,
  `Subtotal` decimal(10,2) NOT NULL,
  PRIMARY KEY (`ID_Venta`,`ID_Producto`),
  KEY `FK_DetVenta_Producto` (`ID_Producto`),
  CONSTRAINT `FK_DetVenta_Producto` FOREIGN KEY (`ID_Producto`) REFERENCES `producto` (`ID_Producto`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_DetVenta_Venta` FOREIGN KEY (`ID_Venta`) REFERENCES `venta` (`ID_Venta`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `CK_DetVenta_Cantidad` CHECK ((`Cantidad` > 0)),
  CONSTRAINT `CK_DetVenta_Precio` CHECK ((`Precio_Unitario` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_venta`
--

LOCK TABLES `detalle_venta` WRITE;
/*!40000 ALTER TABLE `detalle_venta` DISABLE KEYS */;
INSERT INTO `detalle_venta` VALUES (1,1,2,18.00,36.00),(1,6,3,17.00,51.00),(2,2,1,24.50,24.50),(3,4,2,22.00,44.00),(3,5,1,25.00,25.00),(4,8,1,65.00,65.00),(5,3,2,38.00,76.00),(5,7,1,15.00,15.00),(6,1,1,18.00,18.00),(7,6,2,17.00,34.00),(7,9,1,55.00,55.00),(8,10,1,95.00,95.00),(9,11,3,20.00,60.00),(10,2,2,24.50,49.00),(10,4,1,22.00,22.00);
/*!40000 ALTER TABLE `detalle_venta` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_DetalleVenta_AfterInsert` AFTER INSERT ON `detalle_venta` FOR EACH ROW BEGIN
    IF @DISABLE_TRIGGERS IS NULL OR @DISABLE_TRIGGERS = 0 THEN
        UPDATE VENTA
           SET Total = Total + NEW.Subtotal
         WHERE ID_Venta = NEW.ID_Venta;

        UPDATE PRODUCTO
           SET Stock_Actual = Stock_Actual - NEW.Cantidad
         WHERE ID_Producto = NEW.ID_Producto;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_DetalleVenta_AfterUpdate` AFTER UPDATE ON `detalle_venta` FOR EACH ROW BEGIN
    IF @DISABLE_TRIGGERS IS NULL OR @DISABLE_TRIGGERS = 0 THEN
        UPDATE VENTA
           SET Total = Total - OLD.Subtotal + NEW.Subtotal
         WHERE ID_Venta = NEW.ID_Venta;

        UPDATE PRODUCTO
           SET Stock_Actual = Stock_Actual + OLD.Cantidad - NEW.Cantidad
         WHERE ID_Producto = NEW.ID_Producto;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_DetalleVenta_AfterDelete` AFTER DELETE ON `detalle_venta` FOR EACH ROW BEGIN
    IF @DISABLE_TRIGGERS IS NULL OR @DISABLE_TRIGGERS = 0 THEN
        UPDATE VENTA
           SET Total = Total - OLD.Subtotal
         WHERE ID_Venta = OLD.ID_Venta;

        UPDATE PRODUCTO
           SET Stock_Actual = Stock_Actual + OLD.Cantidad
         WHERE ID_Producto = OLD.ID_Producto;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `empleado`
--

DROP TABLE IF EXISTS `empleado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleado` (
  `ID_Empleado` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Cargo` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Turno` enum('MATUTINO','VESPERTINO','NOCTURNO') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`ID_Empleado`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleado`
--

LOCK TABLES `empleado` WRITE;
/*!40000 ALTER TABLE `empleado` DISABLE KEYS */;
INSERT INTO `empleado` VALUES (1,'Juan Carlos Mendoza','Cajero','MATUTINO',1),(2,'Lucía Hernández','Cajera','VESPERTINO',1),(3,'Pedro Ramírez','Encargado','MATUTINO',1),(4,'Andrea Solís','Cajera','NOCTURNO',1),(5,'Óscar Delgado','Reponedor','MATUTINO',1),(6,'Marisol Peña','Cajera','VESPERTINO',1),(7,'Iván Cortés','Seguridad','NOCTURNO',1),(8,'Beatriz Luna','Cajera','MATUTINO',1),(9,'Raúl Aguilar','Reponedor','VESPERTINO',1),(10,'Cynthia Rojas','Cajera','NOCTURNO',0);
/*!40000 ALTER TABLE `empleado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto`
--

DROP TABLE IF EXISTS `producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `producto` (
  `ID_Producto` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Descripcion` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Precio_Venta` decimal(10,2) NOT NULL,
  `Precio_Costo` decimal(10,2) NOT NULL,
  `Stock_Actual` int NOT NULL DEFAULT '0',
  `Activo` tinyint(1) NOT NULL DEFAULT '1',
  `ID_Categoria` int NOT NULL,
  `ID_Proveedor` int DEFAULT NULL,
  PRIMARY KEY (`ID_Producto`),
  KEY `FK_Producto_Categoria` (`ID_Categoria`),
  KEY `FK_Producto_Proveedor` (`ID_Proveedor`),
  CONSTRAINT `FK_Producto_Categoria` FOREIGN KEY (`ID_Categoria`) REFERENCES `categoria` (`ID_Categoria`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `FK_Producto_Proveedor` FOREIGN KEY (`ID_Proveedor`) REFERENCES `proveedor` (`ID_Proveedor`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `CK_Producto_Precios` CHECK (((`Precio_Venta` >= 0) and (`Precio_Costo` >= 0))),
  CONSTRAINT `CK_Producto_Stock` CHECK ((`Stock_Actual` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto`
--

LOCK TABLES `producto` WRITE;
/*!40000 ALTER TABLE `producto` DISABLE KEYS */;
INSERT INTO `producto` VALUES (1,'Coca-Cola 600ml','Refresco de cola en botella PET de 600 ml',18.00,12.00,120,1,2,3),(2,'Leche Lala 1L','Leche entera pasteurizada en caja de 1 litro',24.50,19.00,80,1,3,4),(3,'Pan Blanco Bimbo','Pan de caja blanco, paquete grande',38.00,28.00,45,1,4,2),(4,'Arroz 1kg','Arroz blanco en bolsa de 1 kg',22.00,16.00,60,1,1,NULL),(5,'Frijol 1kg','Frijol en bolsa de 1 kg',25.00,18.00,50,1,1,NULL),(6,'Sabritas Original 45g','Papas fritas sabor original, bolsa de 45 g',17.00,11.00,100,1,7,5),(7,'Jabón Zote','Jabón de barra para lavar ropa',15.00,9.50,70,1,5,NULL),(8,'Shampoo Head&Shoulders','Shampoo anticaspa para cuidado del cabello',65.00,45.00,30,1,6,9),(9,'Nuggets Congelados Fud','Nuggets de pollo empanizados congelados',55.00,38.00,25,1,8,6),(10,'Croquetas Purina 1kg','Alimento seco para perro en bolsa de 1 kg',95.00,70.00,20,1,9,8),(11,'Cuaderno Profesional','Cuaderno profesional de rayas, 100 hojas',20.00,12.00,40,1,10,7),(12,'Sidral Mundet 600ml','Refresco de manzana en botella de 600 ml',16.00,10.50,0,0,2,3);
/*!40000 ALTER TABLE `producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedor`
--

DROP TABLE IF EXISTS `proveedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedor` (
  `ID_Proveedor` int NOT NULL AUTO_INCREMENT,
  `NIF_RFC` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Nombre_Empresa` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `Telefono` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Contacto` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `Activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`ID_Proveedor`),
  UNIQUE KEY `UK_Proveedor_RFC` (`NIF_RFC`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedor`
--

LOCK TABLES `proveedor` WRITE;
/*!40000 ALTER TABLE `proveedor` DISABLE KEYS */;
INSERT INTO `proveedor` VALUES (1,'DCE010203AB1','Distribuidora La Central','3312345678','Juan Pérez',1),(2,'GBI040506CD2','Grupo Bimbo Regional','3323456789','María López',1),(3,'CCF070809EF3','Coca-Cola FEMSA','3334567890','Carlos Ruiz',1),(4,'LLA101112GH4','Lala Alimentos','3345678901','Ana Torres',1),(5,'SAB131415IJ5','Sabritas Occidente','3356789012','Luis Gómez',1),(6,'PFU161718KL6','Productos Fud','3367890123','Rosa Díaz',1),(7,'PAJ192021MN7','Papelera Jalisco','3378901234','Jorge Sánchez',1),(8,'DPU222324OP8','Distribuidora Purina','3389012345','Elena Castro',1),(9,'CCO252627QR9','Comercializadora Colgate','3390123456','Pedro Ramírez',1),(10,'PIN282930ST0','Proveedor Independiente','3301234567',NULL,0);
/*!40000 ALTER TABLE `proveedor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `venta`
--

DROP TABLE IF EXISTS `venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `venta` (
  `ID_Venta` int NOT NULL AUTO_INCREMENT,
  `Fecha_Hora` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Total` decimal(10,2) NOT NULL DEFAULT '0.00',
  `Metodo_Pago` enum('EFECTIVO','TARJETA_DEBITO','TARJETA_CREDITO','TRANSFERENCIA') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ID_Cliente` int DEFAULT NULL,
  `ID_Empleado` int NOT NULL,
  PRIMARY KEY (`ID_Venta`),
  KEY `FK_Venta_Cliente` (`ID_Cliente`),
  KEY `FK_Venta_Empleado` (`ID_Empleado`),
  CONSTRAINT `FK_Venta_Cliente` FOREIGN KEY (`ID_Cliente`) REFERENCES `cliente` (`ID_Cliente`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `FK_Venta_Empleado` FOREIGN KEY (`ID_Empleado`) REFERENCES `empleado` (`ID_Empleado`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `CK_Venta_Total` CHECK ((`Total` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venta`
--

LOCK TABLES `venta` WRITE;
/*!40000 ALTER TABLE `venta` DISABLE KEYS */;
INSERT INTO `venta` VALUES (1,'2026-09-01 09:15:00',87.00,'EFECTIVO',1,1),(2,'2026-09-01 10:30:00',24.50,'TARJETA_DEBITO',2,3),(3,'2026-09-01 11:00:00',69.00,'EFECTIVO',NULL,1),(4,'2026-09-02 09:00:00',65.00,'TRANSFERENCIA',5,3),(5,'2026-09-02 13:20:00',91.00,'TARJETA_CREDITO',3,8),(6,'2026-09-02 18:45:00',18.00,'EFECTIVO',NULL,6),(7,'2026-09-03 08:50:00',89.00,'EFECTIVO',7,5),(8,'2026-09-03 12:10:00',95.00,'TARJETA_DEBITO',9,1),(9,'2026-09-03 19:30:00',60.00,'EFECTIVO',4,9),(10,'2026-09-04 23:45:00',71.00,'TRANSFERENCIA',NULL,4);
/*!40000 ALTER TABLE `venta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'abarrotes_placencia'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-21 21:30:34
