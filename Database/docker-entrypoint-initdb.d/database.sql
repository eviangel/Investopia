CREATE TABLE IF NOT EXISTS `Asset` (
  `id` INT(9) UNSIGNED NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(100) NOT NULL,
  `Amount` FLOAT(20,10) NOT NULL,
  `UserID` int(9) NOT NULL,
  `Average_Price` float(20,10) NOT NULL,
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

CREATE TABLE IF NOT EXISTS `Transaction` (
  `id` INT(9) UNSIGNED NOT NULL AUTO_INCREMENT,
  `AssetID` int(9) NOT NULL,
  `UserID` int(9) NOT NULL,
  `Time` VARCHAR(255) NOT NULL,
  `Quantity` VARCHAR(255) NOT NULL,
  `Price` DECIMAL(20,10) NOT NULL,
  `Action` VARCHAR(255) NOT NULL,
  `Commission` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;


CREATE TABLE IF NOT EXISTS  `Users`(
  `UserID` INT(9) UNSIGNED NOT NULL AUTO_INCREMENT,
  `Username` VARCHAR(100) NOT NULL,
  `Email` VARCHAR(100) NOT NULL,
  `Password_hash` VARCHAR(100) NOT NULL,
  `Created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

CREATE TABLE IF NOT EXISTS DailyPerformance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_balance DECIMAL(20, 10),
    daily_pnl DECIMAL(20, 10),
    best_performer VARCHAR(100),
    best_performer_gain DECIMAL(10, 2),
    worst_performer VARCHAR(100),
    worst_performer_loss DECIMAL(10, 2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS coin_mapping (
    symbol VARCHAR(20) PRIMARY KEY,
    coin_id VARCHAR(100) NOT NULL
);



Insert INTO `Users` (`UserID`, `API`, `Secret`, `Username`)
Values (999,'dummy_api_key','Dummy_secret_key','dummy_user');