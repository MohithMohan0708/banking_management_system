-- CREATE TABLE Users (
--     id INTEGER PRIMARY KEY AUTO_INCREMENT,
--     username VARCHAR(255) UNIQUE,
--     password VARCHAR(255),
--     email VARCHAR(255)
-- );


-- CREATE TABLE Accounts ( 
--     id INT PRIMARY KEY AUTO_INCREMENT, 
--     user_id INT, 
--     balance DECIMAL(10, 2) DEFAULT 0, 
--     FOREIGN KEY(user_id) REFERENCES Users(id) 
-- );



-- CREATE TABLE Transactions ( 
--     id INT PRIMARY KEY AUTO_INCREMENT, 
--     account_id INT, type VARCHAR(255), 
--     amount DECIMAL(10, 2), 
--     date DATE, 
--     FOREIGN KEY(account_id) REFERENCES Accounts(id) 
-- );