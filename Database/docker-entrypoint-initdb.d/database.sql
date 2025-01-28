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
  `API` VARCHAR(100) NOT NULL,
  `Secret` VARCHAR(100) NOT NULL,
  `Username` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

Insert INTO `Users` (`UserID`, `API`, `Secret`, `Username`)
Values (999,'dummy_api_key','Dummy_secret_key','dummy_user');