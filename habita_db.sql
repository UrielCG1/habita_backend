/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.5.29-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: habita_db
-- ------------------------------------------------------
-- Server version	10.5.29-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('fc01abbad52d');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `favorites`
--

DROP TABLE IF EXISTS `favorites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `favorites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `property_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_favorites_user_property` (`user_id`,`property_id`),
  KEY `ix_favorites_id` (`id`),
  KEY `ix_favorites_property_id` (`property_id`),
  KEY `ix_favorites_user_id` (`user_id`),
  CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`property_id`) REFERENCES `properties` (`id`) ON DELETE CASCADE,
  CONSTRAINT `favorites_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `favorites`
--

LOCK TABLES `favorites` WRITE;
/*!40000 ALTER TABLE `favorites` DISABLE KEYS */;
INSERT INTO `favorites` VALUES (2,2,2,'2026-03-15 12:21:42','2026-03-15 12:21:42'),(3,1,2,'2026-03-15 17:09:37','2026-03-15 17:09:37'),(5,3,3,'2026-03-15 21:34:18','2026-03-15 21:34:18'),(7,1,3,'2026-03-17 19:50:15','2026-03-17 19:50:15');
/*!40000 ALTER TABLE `favorites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `properties`
--

DROP TABLE IF EXISTS `properties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `properties` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `owner_id` int(11) NOT NULL,
  `title` varchar(180) NOT NULL,
  `description` text DEFAULT NULL,
  `price` decimal(12,2) NOT NULL,
  `property_type` varchar(50) NOT NULL,
  `status` varchar(30) NOT NULL,
  `address_line` varchar(255) NOT NULL,
  `neighborhood` varchar(120) DEFAULT NULL,
  `city` varchar(100) NOT NULL,
  `state` varchar(100) NOT NULL,
  `bedrooms` int(11) NOT NULL,
  `bathrooms` int(11) NOT NULL,
  `parking_spaces` int(11) DEFAULT NULL,
  `area_m2` decimal(10,2) DEFAULT NULL,
  `latitude` decimal(10,7) DEFAULT NULL,
  `longitude` decimal(10,7) DEFAULT NULL,
  `is_published` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
  `postal_code` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_properties_city` (`city`),
  KEY `ix_properties_id` (`id`),
  KEY `ix_properties_owner_id` (`owner_id`),
  KEY `ix_properties_state` (`state`),
  KEY `ix_properties_postal_code` (`postal_code`),
  CONSTRAINT `properties_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `properties`
--

LOCK TABLES `properties` WRITE;
/*!40000 ALTER TABLE `properties` DISABLE KEYS */;
INSERT INTO `properties` VALUES (2,1,'Departamento Normal en Querétaro','Departamento con excelente ubicación y servicios cercanos.',9200.00,'apartment','available','Av. Universidad 123','Centro','Querétaro','Querétaro',3,1,1,78.50,20.5888000,-100.3899000,1,'2026-03-11 21:26:23','2026-03-11 21:34:54',NULL),(3,4,'Bosques PB','casa de 1 piso con patio grande',10000.00,'house','available','Casas Platino 103','76114','Querétaro','Santiago de Querétaro',2,2,2,71.47,0.0000001,0.0000001,1,'2026-03-15 13:58:54','2026-03-15 13:59:55',NULL),(4,4,'Casa color verde en jardines de la hacienda','asdasdasd',10000.00,'house','available','Jazmin 223','','Querétaro','Querétaro',2,2,2,147.00,20.6357761,-100.4121478,1,'2026-03-15 19:11:35','2026-03-24 22:11:42',NULL),(5,2,'Departamento con terraza en el centro de querétaro','Departamento bonito',35000.00,'apartment','available','Francisco I madero #52','Centro','Querétaro','Santiago de Querétaro',2,1,0,150.00,-0.0000001,0.0000001,1,'2026-03-15 22:23:10','2026-03-15 22:23:10',NULL),(6,4,'Propiedad de Prueba','Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. \r\n\r\nExcepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.\r\n\r\nLorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',12000.00,'house','available','1 de mayo','La campana','Santiago de Querétaro','Querétaro',2,2,1,140.00,20.6781133,-100.4501202,1,'2026-03-17 19:54:37','2026-03-24 22:42:19','76100'),(7,5,'Casa de prueba','1500 todo incluido',1500.00,'house','available','O','S','A','A',2,2,2,1500.00,NULL,NULL,1,'2026-03-21 12:38:11','2026-03-21 12:44:29',NULL),(8,4,'Propidad de prueba 2','dfjvgkjsdbfksjdfbjkbjksdfbjksdfbjksfdjkb jkjksb jsfd bjksjbksfbkhjsdasdasd',12000.00,'house','available','Av. Peñuelas 120','Los Vitrales','Querétaro','Querétaro',1,1,1,80.00,NULL,NULL,1,'2026-03-23 20:56:35','2026-03-24 00:22:05','76150');
/*!40000 ALTER TABLE `properties` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `property_images`
--

DROP TABLE IF EXISTS `property_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `property_images` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `property_id` int(11) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `alt_text` varchar(255) DEFAULT NULL,
  `is_cover` tinyint(1) NOT NULL,
  `sort_order` int(11) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `ix_property_images_id` (`id`),
  KEY `ix_property_images_property_id` (`property_id`),
  CONSTRAINT `property_images_ibfk_1` FOREIGN KEY (`property_id`) REFERENCES `properties` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `property_images`
--

LOCK TABLES `property_images` WRITE;
/*!40000 ALTER TABLE `property_images` DISABLE KEYS */;
INSERT INTO `property_images` VALUES (1,2,'properties/9c800ec7357f4eccaed740c050eb4529.png','Captura de prueba propiedad 2',1,0,'2026-03-11 22:31:33','2026-03-11 22:31:33'),(2,2,'properties/ff1244f2455b486b906fca0ccdb76107.png','Captura de prueba propiedad 2_1',0,1,'2026-03-11 22:34:57','2026-03-11 22:34:57'),(3,3,'properties/21c9fb897cf34856a92a15a6564d8eea.jpg','Bosques PB',1,0,'2026-03-15 13:58:54','2026-03-15 13:58:54'),(4,3,'properties/48dcbb8d32bc4779a9346264918d9c12.jpg','Bosques PB',0,1,'2026-03-15 13:58:54','2026-03-15 13:58:54'),(5,3,'properties/7e737a3d039f400083f9365083956109.jpg','Bosques PB',0,2,'2026-03-15 13:58:54','2026-03-15 13:58:54'),(6,4,'properties/ba1fb7ae11e2485ab25e40b36d1119e2.jpg','Casa color verde en jardines de la hacienda',0,0,'2026-03-15 19:11:35','2026-03-24 21:04:11'),(7,4,'properties/3f7bc7a061de4764bc8f2b930a9f5dd9.jpg','Casa color verde en jardines de la hacienda',0,1,'2026-03-15 19:11:35','2026-03-24 21:04:11'),(8,4,'properties/10916a064baf4fd49b146f8b0289a8bb.jpg','Casa color verde en jardines de la hacienda',0,2,'2026-03-15 19:11:35','2026-03-24 21:04:11'),(9,5,'properties/26ea53c645ee4d1198bf894e1b6f1404.jpg','Departamento con terraza en el centro de querétaro',1,0,'2026-03-15 22:23:10','2026-03-15 22:23:10'),(10,5,'properties/d3e1b89a048246429036fc602171fca3.jpg','Departamento con terraza en el centro de querétaro',0,1,'2026-03-15 22:23:10','2026-03-15 22:23:10'),(11,5,'properties/4ac967fbd030485ca6eae5b6245605af.jpg','Departamento con terraza en el centro de querétaro',0,2,'2026-03-15 22:23:10','2026-03-15 22:23:10'),(12,5,'properties/aeaeb7241f6e424eb46dfee452c7387f.jpg','Departamento con terraza en el centro de querétaro',0,3,'2026-03-15 22:23:10','2026-03-15 22:23:10'),(13,5,'properties/f83fc18e46d1442bb69755ca60e7a250.jpg','Departamento con terraza en el centro de querétaro',0,4,'2026-03-15 22:23:10','2026-03-15 22:23:10'),(14,6,'properties/0e3fe7f0293b4ee5a84e0073c8a87e92.jpg','Propiedad de Prueba',0,2,'2026-03-17 19:54:37','2026-03-24 22:42:09'),(15,6,'properties/4ccea5bcf7f743e2afe3bf8831f4ed76.jpg','Propiedad de Prueba',0,1,'2026-03-17 19:54:37','2026-03-23 21:08:44'),(16,6,'properties/4fdb72ecac1746eb825a1b6770656867.jpg','Propiedad de Prueba',0,0,'2026-03-17 19:54:37','2026-03-24 22:42:09'),(17,6,'properties/6aba9cf1da874e348b1353e91491b906.jpg','Propiedad de Prueba',0,3,'2026-03-17 19:54:37','2026-03-23 21:08:44'),(18,6,'properties/4b00e3325f2e43eca35e90288153afab.jpg','Propiedad de Prueba',0,4,'2026-03-17 19:54:37','2026-03-23 21:08:44'),(19,8,'properties/0b6dddecba934b91b7317a7d39795527.png','Propidad de prueba 2',0,0,'2026-03-23 20:56:35','2026-03-23 20:56:58'),(20,8,'properties/18e828cf7be1463e9e36573b3b652372.jpg','Propidad de prueba 2',0,1,'2026-03-23 20:56:35','2026-03-23 20:56:58'),(21,8,'properties/5ffbb3872e4c481b8ed44818b8e6e4c4.png','Propidad de prueba 2',0,2,'2026-03-23 20:56:35','2026-03-23 20:56:58');
/*!40000 ALTER TABLE `property_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rental_requests`
--

DROP TABLE IF EXISTS `rental_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `rental_requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `property_id` int(11) NOT NULL,
  `status` varchar(30) NOT NULL,
  `message` text DEFAULT NULL,
  `move_in_date` date DEFAULT NULL,
  `monthly_budget` decimal(12,2) DEFAULT NULL,
  `owner_notes` text DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `ix_rental_requests_id` (`id`),
  KEY `ix_rental_requests_property_id` (`property_id`),
  KEY `ix_rental_requests_user_id` (`user_id`),
  CONSTRAINT `rental_requests_ibfk_1` FOREIGN KEY (`property_id`) REFERENCES `properties` (`id`) ON DELETE CASCADE,
  CONSTRAINT `rental_requests_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rental_requests`
--

LOCK TABLES `rental_requests` WRITE;
/*!40000 ALTER TABLE `rental_requests` DISABLE KEYS */;
INSERT INTO `rental_requests` VALUES (1,1,2,'pending','Me interesa rentar esta propiedad lo antes posible.','2026-04-01',9500.00,NULL,'2026-03-11 22:44:01','2026-03-11 22:44:01'),(2,1,3,'pending','asdasdasdasdasdasd','2027-01-12',9500.00,NULL,'2026-03-15 15:30:39','2026-03-15 15:30:39'),(3,3,3,'rejected','Quisiera rentar esta casa','2026-03-18',9500.00,'Muy baja la oferta','2026-03-15 19:13:09','2026-03-15 21:37:37'),(4,3,3,'pending','asdasd','2026-03-18',12000.00,NULL,'2026-03-15 23:07:03','2026-03-15 23:07:03'),(5,3,6,'accepted','Me interesa rentar esta propiedad \r\n\r\nLorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.','2026-03-19',8700.00,'asdasdasdasdasdasdasd','2026-03-17 19:57:44','2026-03-17 19:58:15'),(6,4,6,'pending',NULL,NULL,NULL,NULL,'2026-03-19 09:32:47','2026-03-19 09:32:47'),(7,3,8,'pending','asbn,hjdbasdbasj bhdjas dasb djhasdjasd hkasd ha shdashjd','2026-03-24',11500.00,NULL,'2026-03-23 21:10:03','2026-03-23 21:10:03');
/*!40000 ALTER TABLE `rental_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `property_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL,
  `comment` text DEFAULT NULL,
  `is_visible` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `ix_reviews_id` (`id`),
  KEY `ix_reviews_property_id` (`property_id`),
  KEY `ix_reviews_user_id` (`user_id`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`property_id`) REFERENCES `properties` (`id`) ON DELETE CASCADE,
  CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
INSERT INTO `reviews` VALUES (1,1,2,5,'Muy buena ubicación y excelente atención.',1,'2026-03-11 22:45:40','2026-03-11 22:45:40'),(2,2,2,5,'Está muy bien todo',1,'2026-03-15 12:47:51','2026-03-15 12:47:51'),(3,3,3,5,'muy mal xd',1,'2026-03-15 23:07:10','2026-03-15 23:07:10'),(4,1,3,4,'test',1,'2026-03-17 19:50:45','2026-03-17 19:50:45');
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `full_name` varchar(150) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `role` varchar(20) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Admin Habita','admin@habita.com','$argon2id$v=19$m=65536,t=3,p=4$Qy1t3NVwRZnNiLqDDAVCxw$kwoL7MApvBAMU28qJBeEoii9e/tcCwGWqrSK1Dl9lzE','4420000000','admin',1,'2026-03-11 21:20:15','2026-03-15 15:06:34'),(2,'Uriel Carbajal','uriel@example.com','$argon2id$v=19$m=65536,t=3,p=4$IxenG8VbdbrC44b6FmLOIA$lfZR7wBWfUz1zpmAYQ9W7FABjhkV64kUeLaVrgNsq8A','1234567890','owner',1,'2026-03-15 10:39:19','2026-03-15 10:40:49'),(3,'Regina Cortes Vargas','regina@test.com','$argon2id$v=19$m=65536,t=3,p=4$PBF6h6sFv9KO/s5DrhFxHw$Bvjl+kG2YpKuIRwY2UphnwNp7eIzwV2sbTdcAwH1bmY','1234567890','tenant',1,'2026-03-15 11:47:48','2026-03-15 11:47:48'),(4,'juan perez','juan@owner.com','$argon2id$v=19$m=65536,t=3,p=4$FCG3jHZzBwOg1baxp4jlrw$LTy32Pshi2UKJXtW/VeR0NpNqLIALmzYtfLRHeYDkX8','1234567890','owner',1,'2026-03-15 13:13:38','2026-03-15 13:13:38'),(5,'Miguel','miguelibarra641@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$sdCFQwwQzTmzPmsEJIxe+A$ckog9MytktXd+sPcxjFROlRwYfwFkQoNaI866rreysM','+524424650849','owner',1,'2026-03-21 12:36:07','2026-03-21 12:36:07');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-26 17:51:00
