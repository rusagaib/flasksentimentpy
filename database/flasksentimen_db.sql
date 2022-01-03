/*
SQLyog Ultimate v12.4.3 (64 bit)
MySQL - 5.6.16 : Database - flasksentimen_db
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`flasksentimen_db` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `flasksentimen_db`;

/*Table structure for table `dataset_procesed` */

DROP TABLE IF EXISTS `dataset_procesed`;

CREATE TABLE `dataset_procesed` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `label` int(11) NOT NULL,
  `tweet_tokens_stemmed` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=521 DEFAULT CHARSET=utf8;

/*Data for the table `dataset_procesed` */

insert  into `dataset_procesed`(`id`,`label`,`tweet_tokens_stemmed`) values
(1,0,'(\'ulang\',\'minggu\',\'lambat\',\'sinyal\',\'telfon\',\'pulsa\',\'ganggu\')'),
(2,0,'(\'paket\',\'data\',\'lambat\')'),
(3,1,'(\'kuat\',\'sinyal\',\'telkomsel\',\'sehat\',\'mental\',\'himbauan\',\'pandemi\',\'covid\',\'karna\',\'sinyal\',\'lancar\',\'jaya\',\'kaya\',\'jalan\',\'tol\')'),
(4,1,'(\'jaring\',\'kepri\',\'aman\',\'pjj\',\'aman\',\'telkomsel\',\'hebat\',\'thanks\',\'telkomsel\')'),
(5,1,'(\'telkomsel\',\'anak\',\'pjj\')');

/*Table structure for table `dataset_raw` */

DROP TABLE IF EXISTS `dataset_raw`;

CREATE TABLE `dataset_raw` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `tweets` text NOT NULL,
  `label` varchar(7) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=521 DEFAULT CHARSET=utf8;

/*Data for the table `dataset_raw` */

insert  into `dataset_raw`(`id`,`username`,`tweets`,`label`) values
(1,'dummy1','@Telkomsel Sudah berulang kali dari beberapa minggu yg lalu udah lelet. Sinyal selalu 3G bahkan telfon lewat pulsa jadi terganggu. Ada apa ya?','negatif'),
(2,'dummy2','@Telkomsel paket datanya kok lemot ini bos, tolong di jawab','negatif'),
(3,'dummy3','Hanya dengan kekuatan sinyal Telkomsel, aku bisa tetap sehat mental di tengah himbauan #dirumahaja selama Pandemi COVID-19. Karna sinyal @Telkomsel lancar jaya kaya di jalan tol ??','positif'),
(4,'dummy4','Jaringan @Telkomsel di Kepri aman, PJJ jadinya aman juga, Telkomsel hebat, Thanks Telkomsel','positif'),
(5,'dummy5','@Telkomsel Justru Telkomsel care sama makmak yg anaknya pjj..','positif');

/*Table structure for table `dataset_tes` */

DROP TABLE IF EXISTS `dataset_tes`;

CREATE TABLE `dataset_tes` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `label` tinyint(1) NOT NULL,
  `tweet_tokens_stemmed` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=105 DEFAULT CHARSET=utf8;

/*Table structure for table `dataset_training` */

DROP TABLE IF EXISTS `dataset_training`;

CREATE TABLE `dataset_training` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `label` int(1) NOT NULL,
  `tweet_tokens_stemmed` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=417 DEFAULT CHARSET=utf8;


/*Table structure for table `kamus_data_all` */

DROP TABLE IF EXISTS `kamus_data_all`;

CREATE TABLE `kamus_data_all` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `term` varchar(50) NOT NULL,
  `df` int(11) NOT NULL,
  `idf` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1020 DEFAULT CHARSET=utf8;

/*Table structure for table `kamus_negatif` */

DROP TABLE IF EXISTS `kamus_negatif`;

CREATE TABLE `kamus_negatif` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `term` varchar(50) NOT NULL,
  `tf` int(11) NOT NULL,
  `idf` double NOT NULL,
  `tf_idf_dict` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=663 DEFAULT CHARSET=utf8;


/*Table structure for table `kamus_positif` */

DROP TABLE IF EXISTS `kamus_positif`;

CREATE TABLE `kamus_positif` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `term` varchar(50) NOT NULL,
  `tf` int(11) NOT NULL,
  `idf` double NOT NULL,
  `tf_idf_dict` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=508 DEFAULT CHARSET=utf8;

/*Table structure for table `log_riwayat_testing` */

DROP TABLE IF EXISTS `log_riwayat_testing`;

CREATE TABLE `log_riwayat_testing` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `datetime` datetime NOT NULL,
  `sentimen` text NOT NULL,
  `hasil_sentimen` varchar(7) NOT NULL,
  `validasi_sentimen` varchar(7) DEFAULT 'NULL',
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `log_riwayat_testing_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `pengguna` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

/*Data for the table `log_riwayat_testing` */

insert  into `log_riwayat_testing`(`id`,`datetime`,`sentimen`,`hasil_sentimen`,`validasi_sentimen`,`user_id`) values
(1,'2021-06-09 15:51:01','wah tumben nih  Telkomsel baik banget mau bagi kuota gratis makasih loh   ','Positif','NULL',1);

/*Table structure for table `pengguna` */

DROP TABLE IF EXISTS `pengguna`;

CREATE TABLE `pengguna` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

/*Data for the table `pengguna` */

insert  into `pengguna`(`id`,`username`,`password`) values
(1,'admin','$2b$12$hjZzr8I/Mk6ZLF2rB5rAe.OvvF1o/9yD4766vIhlm4HmAV.iZ9COe');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
