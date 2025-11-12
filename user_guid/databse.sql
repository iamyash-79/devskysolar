-- Create Database (optional)
CREATE DATABASE IF NOT EXISTS solarcrm_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE solarcrm_app;

-- ----------------------------
-- Table structure for `admins`
-- ----------------------------
CREATE TABLE IF NOT EXISTS admins (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  mobile VARCHAR(15) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password VARCHAR(100) NOT NULL,
  role VARCHAR(50) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for `faq`
-- ----------------------------
CREATE TABLE IF NOT EXISTS faq (
  id INT NOT NULL AUTO_INCREMENT,
  category VARCHAR(100) DEFAULT NULL,
  question TEXT DEFAULT NULL,
  answer TEXT DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for `leads`
-- ----------------------------
CREATE TABLE IF NOT EXISTS leads (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  company VARCHAR(50) NOT NULL,
  phone VARCHAR(15) NOT NULL,
  address TEXT NOT NULL,
  kw_required VARCHAR(50) DEFAULT NULL,
  installation_time VARCHAR(50) DEFAULT NULL,
  comments TEXT DEFAULT NULL,
  added_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  Remarks TEXT DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for `visits`
-- ----------------------------
CREATE TABLE IF NOT EXISTS visits (
  id INT NOT NULL AUTO_INCREMENT,
  ip TEXT NOT NULL,
  user_agent TEXT NOT NULL,
  pages TEXT NOT NULL,
  timestamp DATETIME NOT NULL,
  name TEXT DEFAULT NULL,
  contact TEXT DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
