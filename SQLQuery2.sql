
INSERT INTO Users (FirstName, LastName, Email, Password)
VALUES ('John', 'Doe', 'johndoe@gmail.com', HASHBYTES('SHA2_512', 'Bb12345678')),
		('Mary', 'Jane', 'MJ@gmail.com' , HASHBYTES('SHA2_512', 'Bb12345678'));

DELETE FROM Transactions
DELETE FROM Accounts
INSERT INTO Accounts(UserId, AccountType,AccountNumber,Balance)
VALUES (1, 'Active', '12345678', 100000),
	   (1, 'Active', '24681012', 100000),
	   (2, 'Active', '36912151', 1000000);

------------------------------------------------------------LOGIN TEST
	   SELECT * FROM Accounts
	   DECLARE @password NVARCHAR(255);
	   SELECT @password = HASHBYTES('SHA2_512', 'Bb12345678');

	   DECLARE @newpassword NVARCHAR(255);
	   SELECT @newpassword = HASHBYTES('SHA2_512', '987654321');

	   DECLARE @BOOOl INT;
	   EXEC @BOOOl = Login 'johndoe@gmail.com' , @password;

	   IF @BOOOl = 1
	   BEGIN 
	   SELECT 'CORRECT'
	   END
	   ELSE
	   SELECT 'FALSE'
-------------------------------------------------------------------------------CHANGE PASSWORD
		EXEC ChangePassword 1, @password, @newpassword;
		SELECT * FROM Users	

	   EXEC @BOOOl = Login 'johndoe@gmail.com' , @newpassword;
	   IF @BOOOl = 1
	   BEGIN 
	   SELECT 'CORRECT'
	   END
	   ELSE
	   SELECT 'FALSE'
--------------------------------------------------------------------account information
	 EXEC GetAccountInformation '36912151';
---------------------------------------------------------------------account owner
	EXEC GetOwnerName '36912151';
----------------------------------------------------------------------Ban account
	EXEC BanAccount '36912151';
	SELECT * FROM Accounts;
----------------------------------------------------------------------UnBan account
	EXEC UnBanAccount '36912151';
	SELECT * FROM Accounts;
------------------------------------------------------------------------transaction
EXEC TransferMoney '6362111111111111','1111111111111111', 50000;
select * from Transactions
select * from Accounts
----------------------------------------------------------------recent transactions
EXEC GetRecentAccountTransactions '36912151', 3
-------------------------------------------------------------LOAN ELIG

DECLARE @MinValue DECIMAL(18,2);
EXEC @MinValue = CalculateLoanEligibility '36912151';
SELECT @MinValue;

---------------------------------------------------------------APPLY
EXEC ApplyForLoan '36912151',850000,12; 
EXEC ApplyForLoan '24681012',1000,3; 
select * from Loans
select * from Bills
EXEC PayBill 6;
EXEC GetBills 6;
select * from Loans;

DELETE FROM Transactions
DELETE FROm Bills
DELETE FROm Loans
DELETE FROm Accounts
DELETE FROm Users

INSERT INTO Users (FirstName,LastName,Email,Password) values ('Admin','Admin','Admin','bb421fa35db885ce507b0ef5c3f23cb09c62eb378fae3641c165bdf4c0272949')
SELECT * FROM Users
SELECT * FROM Accounts

EXEC Login @username = 'Admin', @password = '999999999';

select * from Transactions

SELECT UserId FROM Users Where Email = 'MJ@gmail.com';


EXEC CalculateLoanEligibility '1111111111111111'

select * from Loans

--DECLARE @TwoMonthsAgo DATETIME;
--SET @TwoMonthsAgo = DATEADD(MONTH, -2, GETDATE());

--DECLARE @Now DATETIME;
--SET @Now = GETDATE();

--EXEC GetAccountTransactionsByDate @TwoMonthsAgo, @Now, '1111111111111111';

EXEC CalculateLoanEligibility '888'
EXEC ApplyForLoan '1111111111111111',6000,12; 

select * from Loans
select * from Accounts
select * from Transactions
EXEC GetRecentAccountTransactions '11111111', 5