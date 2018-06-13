-- 主机: localhost
-- 生成日期: 2018-03-23 16:21:36
-- 服务器版本: 5.5.57-0ubuntu0.14.04.1
-- PHP 版本: 5.5.9-1ubuntu4.22

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- 数据库: `db_bupt`
--

-- --------------------------------------------------------

--
-- 表的结构 `t_message`
--
DROP DATABASE IF EXISTS `db_bupt`;

CREATE DATABASE db_bupt;

use db_bupt;

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `t_message`
-- ----------------------------
DROP TABLE IF EXISTS `t_message`;
CREATE TABLE `t_message` (
  `msg_index` bigint(20) NOT NULL AUTO_INCREMENT,
  `meter_id` varchar(32) NOT NULL,
  `msg_content` text NOT NULL,
  `update_time` bigint(20) NOT NULL,
  `ipfs_address` varchar(46) NOT NULL,
  PRIMARY KEY (`msg_index`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

-- ----------------------------
--  Table structure for `t_meter`
-- ----------------------------
DROP TABLE IF EXISTS `t_meter`;
CREATE TABLE `t_meter` (
  `meter_index` bigint(20) NOT NULL AUTO_INCREMENT,
  `meter_id` varchar(32) NOT NULL,
  `meter_prikey` text NOT NULL,
  `meter_pubkey` text NOT NULL,
  PRIMARY KEY (`meter_index`),
  UNIQUE KEY `meter_id` (`meter_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;


-- --------------------------------------------------------

-- -----------------------------------
--  Table structure for `t_meterdata`
-- -----------------------------------
DROP TABLE IF EXISTS `t_meterdata`;
CREATE TABLE `t_meterdata` (
  `meterdata_index` bigint(20) NOT NULL AUTO_INCREMENT,
  `meter_id` varchar(32) NOT NULL,
  `powerconsum` double NOT NULL,
  `eleremain` double NOT NULL,
  `timestamp` bigint(20) NOT NULL,
  PRIMARY KEY (`meterdata_index`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;


SET FOREIGN_KEY_CHECKS = 1;