--------------------------------------------------------------------------------

CREATE TABLE Users (
  UserId INT PRIMARY KEY IDENTITY,
  FirstName NVARCHAR(50) NOT NULL,
  LastName NVARCHAR(50) NOT NULL,
  Email NVARCHAR(100) NOT NULL UNIQUE,
  Password NVARCHAR(255) NOT NULL
);

CREATE TABLE Accounts (
  AccountId INT PRIMARY KEY IDENTITY,
  UserId INT NOT NULL,
  AccountType NVARCHAR(50) NOT NULL, --Active or Banned
  AccountNumber NVARCHAR(20) NOT NULL UNIQUE,
  Balance DECIMAL(18,2) NOT NULL,
  StartDate DATETIME not null,
  FOREIGN KEY (UserId) REFERENCES Users(UserId)
);

CREATE TABLE Transactions (
  TransactionId INT PRIMARY KEY IDENTITY(1,1), --?????????????????????????
  AccountNumber NVARCHAR(20) NOT NULL,
  TransactionDate DATETIME NOT NULL,
  TransactionType NVARCHAR(50) NOT NULL,
  TransactionAmount DECIMAL(18,2) NOT NULL,
  BalanceAfterTransacion DECIMAL(18,2) NOT NULL,
  FOREIGN KEY (AccountNumber) REFERENCES Accounts(AccountNumber)
);


CREATE TABLE Loans (
  LoanId INT PRIMARY KEY IDENTITY,
  AccountNumber NVARCHAR(20) NOT NULL UNIQUE,
  LoanAmount DECIMAL(18,2) NOT NULL,
  ApprovedAmount DECIMAL(18,2),
  ApprovedDate DATETIME,
  LoanStatus NVARCHAR(255) NOT NULL --Active or Dismissed
  FOREIGN KEY (AccountNumber) REFERENCES Accounts(AccountNumber)
);


CREATE TABLE Bills (
  BillId INT PRIMARY KEY IDENTITY,
  LoanId INT NOT NULL,
  DueDate DATE NOT NULL,
  Amount DECIMAL(18,2) NOT NULL,
  Paid INT NOT NULL,
  PaidDate DATETIME
);

CREATE TABLE BannedInfo (
  AccountNumber NVARCHAR(20) NOT NULL,
  Descript NVARCHAR(1000) NOT NULL,
  FOREIGN KEY (AccountNumber) REFERENCES Accounts(AccountNumber),
);
GO
--------------------------------------------------------------------------------DONE
ALTER PROCEDURE Login(@username NVARCHAR(100), @password NVARCHAR(255))
AS
BEGIN
    DECLARE @userId INT;
    SELECT @userId = UserId FROM Users
    WHERE Email = @username;

    IF @userId IS NULL
    BEGIN
		select 0;
		return;
	END

    DECLARE @hashedPassword NVARCHAR(255);

    SELECT @hashedPassword = Password FROM Users WHERE UserId = @userId;
    IF @hashedPassword IS NULL
	BEGIN
		select 0;
		return;
	END
    IF @hashedPassword != @password
    BEGIN
		select 0;
		return;
	END

	select 1;
	return;
END;

Go;
--------------------------------------------------------------------------------DONE
CREATE PROCEDURE ChangePassword(@userId INT, @oldPassword NVARCHAR(255), @newPassword NVARCHAR(255))
AS
BEGIN
    DECLARE @hashedOldPassword NVARCHAR(255), @hashedNewPassword NVARCHAR(255);

    SELECT @hashedOldPassword = Password FROM Users WHERE UserId = @userId;

    IF @hashedOldPassword IS NULL
        RETURN 0;

    IF @hashedOldPassword != @oldPassword
        RETURN 0;

    UPDATE Users
    SET Password = @newPassword
    WHERE UserId = @userId;

    RETURN 1;
END;

GO
--------------------------------------------------------------------------------DONE

ALTER PROCEDURE GetAllAccountsByUserId(@email NVARCHAR(100))
AS
BEGIN
	With Accounts_email(AccountNumber, AccountType, Balance, StartTime, Email) as
	(SELECT AccountNumber, AccountType, Balance, StartTime, Email FROM Users inner join Accounts on Users.UserId = Accounts.UserId)
    (SELECT * FROM Accounts_email WHERE Email = @email);

END;

GO
--------------------------------------------------------------------------------DONE!
ALTER PROCEDURE GetRecentAccountTransactions(@accountNumber NVARCHAR(20), @numTransactions INT)
AS
BEGIN -- If it's banned then still previous transactions are visible! and future transactions banned in the 
	  -- create transactions procedure
    SELECT TOP(@numTransactions) *
    FROM Transactions
    WHERE AccountNumber = @accountNumber
    ORDER BY TransactionDate DESC;
END;

GO
--------------------------------------------------------------------------------DONE!
CREATE PROCEDURE GetAccountTransactionsByDate(@startDate DATETIME, @endDate DATETIME, @accountnumber NVARCHAR(20))
AS
BEGIN
    SELECT *
    FROM Transactions
    WHERE (TransactionDate >= @startDate) AND (TransactionDate <= @endDate) and ( AccountNumber = @accountnumber)
	ORDER BY TransactionDate DESC;
END;

GO

--*****************************************************************************
--CREATE PROCEDURE CalculateAccountBalance(@userId INT, @accountNumber NVARCHAR(20))
--AS
--BEGIN
--    DECLARE @balance DECIMAL(18,2);
--	DECLARE @deposits DECIMAL(18,2);
--	DECLARE @withdrawals DECIMAL(18,2);
--    SELECT
--        (SELECT SUM(TransactionAmount) FROM Transactions WHERE AccountId = @accountNumber AND TransactionType = 'Deposit') AS Deposits,
--        (SELECT SUM(TransactionAmount) FROM Transactions WHERE AccountId = @accountNumber AND TransactionType = 'Withdrawal') AS Withdrawals
--    FROM Accounts
--    WHERE UserId = @userId;

--    SELECT @balance = @deposits - @withdrawals;

--    SELECT @balance;
--END;
--*****************************************************************************

GO
--------------------------------------------------------------------------------DONE
CREATE PROCEDURE GetAccountInformation(@accountNumber NVARCHAR(20))
AS
BEGIN
    SELECT
		Users.FirstName,
		Users.LastName,
		Users.Email,
		Accounts.StartTime
        AccountId,
        Users.UserId,
        AccountType,
        Balance
    FROM Accounts inner join Users on  Users.UserId = Accounts.UserId
    WHERE AccountNumber = @accountNumber;
END;

GO
-------------------------------------------------------------------------------- DONE

CREATE PROCEDURE GetOwnerName(@accountNumber NVARCHAR(20))
AS
BEGIN
    SELECT
        FirstName,
        LastName
    FROM Users inner join Accounts on Users.UserId = Accounts.UserId
    WHERE AccountNumber = @accountNumber;
END;

GO
--------------------------------------------------------------------------------DONE

ALTER PROCEDURE BanAccount(@accountNumber NVARCHAR(20) , @descryption NVARCHAR(250))
AS
BEGIN
    UPDATE Accounts
	SET AccountType = 'Banned'
	WHERE AccountNumber = @accountNumber;

	INSERT INTO BannedInfo(AccountNumber, Descript)
		VALUES (@accountNumber, @descryption);

	RETURN 1;
END;
GO
-------------------------------------------------------------------------------DONE

CREATE PROCEDURE UnBanAccount(@accountNumber NVARCHAR(20))
AS
BEGIN
    UPDATE Accounts
	SET AccountType = 'Active'
	WHERE AccountNumber = @accountNumber;

	RETURN 1;
END;

GO
--------------------------------------------------------------------------------DONE

ALTER PROCEDURE TransferMoney(@sourceAccountNumber NVARCHAR(20), @destinationAccountNumber NVARCHAR(20), @amount DECIMAL(18,2))
AS
BEGIN
	DECLARE @sourceUserId INT, @destinationUserId INT;
	DECLARE @sourceBalance DECIMAL(18,2), @destinationBalance DECIMAL(18,2);

	-- Get the user IDs for the source and destination account numbers and check not banned
	SELECT @sourceUserId = UserId FROM Accounts
	WHERE AccountNumber = @sourceAccountNumber and AccountType <> 'Banned';
	IF @sourceUserId IS NULL
	BEGIN
		SELECT 0;
		RETURN 0;
	END

	SELECT @destinationUserId = UserId FROM Accounts
	WHERE AccountNumber = @destinationAccountNumber and AccountType <> 'Banned';
	IF @destinationUserId IS NULL
	BEGIN
		SELECT 0;
		RETURN 0;
	END

	-- Check if the source account has enough balance for the transfer
	SELECT @sourceBalance = Balance FROM Accounts
	WHERE AccountNumber = @sourceAccountNumber;
	IF @sourceBalance < @amount
	BEGIN
		SELECT 0;
		RETURN 0;
	END

	SELECT @destinationBalance = Balance FROM Accounts
	WHERE AccountNumber = @destinationAccountNumber;

	BEGIN TRAN;
		-- Deduct the transfer amount from the source account
		UPDATE Accounts
		SET Balance = Balance - @amount
		WHERE AccountNumber = @sourceAccountNumber;

		-- Add the transfer amount to the destination account
		UPDATE Accounts
		SET Balance = Balance + @amount
		WHERE AccountNumber = @destinationAccountNumber;

		INSERT INTO Transactions (AccountNumber, TransactionDate, TransactionType, TransactionAmount, BalanceAfterTransacion)
		VALUES (@sourceAccountNumber, GETDATE(), 'Withdraw', -@amount, @sourceBalance - @amount);
		INSERT INTO Transactions (AccountNumber, TransactionDate, TransactionType, TransactionAmount , BalanceAfterTransacion)
		VALUES (@destinationAccountNumber, GETDATE(), 'Deposit', @amount, @destinationBalance + @amount);
	
	COMMIT TRAN;
	BEGIN
		SELECT 1;
		RETURN 1;
	END
END;

GO
--------------------------------------------------------------------------------DONE

ALTER PROCEDURE CalculateLoanEligibility(@accountNumber NVARCHAR(20))
AS
BEGIN
	
    DECLARE @userId INT, @accountBalance DECIMAL(18,2), @maximumLoanAmount DECIMAL(18,2);
	DECLARE @isLoanActive INT;
	DECLARE @hasGoodPaymentHistory INT;


    -- Get the user ID for the account number see if exists and not banned
    SELECT @userId = UserId FROM Accounts
    WHERE AccountNumber = @accountNumber and AccountType <> 'Banned';
    IF @userId IS NULL
	BEGIN
		select 0;
        RETURN 0;
	END

	
	--check for active loans on this account
	SELECT @isLoanActive = COUNT(*)
	FROM Loans
	WHERE AccountNumber = @accountNumber and LoanStatus = 'Active'

	
    IF @isLoanActive > 0
    BEGIN
		select 0;
        RETURN 0;
	END
	
    ---- Check if the account balance is sufficient
    --SELECT @accountBalance = Balance FROM Accounts
    --WHERE AccountNumber = @accountNumber;
    --IF @accountBalance < 10000
    --    RETURN 0;

	DECLARE @transactions TABLE (
        TransactionId INT ,
		AccountNumber NVARCHAR(20),
		TransactionDate DATETIME,
		TransactionType NVARCHAR(50) ,
		TransactionAmount DECIMAL(18,2) ,
		BalanceAfterTransacion DECIMAL(18,2)

    );

	

	DECLARE @TwoMonthsAgo DATETIME;
    SET @TwoMonthsAgo = DATEADD(MONTH, -2, GETDATE());

	DECLARE @Now DATETIME;
    SET @Now = GETDATE();

	
	BEGIN TRAN;
	INSERT INTO @transactions 
	EXEC GetAccountTransactionsByDate @TwoMonthsAgo, @Now, @accountNumber;
	COMMIT TRAN;

	DECLARE @MinValue DECIMAL(18,2);

	SELECT @MinValue = Min(BalanceAfterTransacion)
	FROM @transactions

	IF @MinValue IS NULL
	BEGIN
		SELECT 0;
        RETURN 0;
	END

	SELECT @MinValue as the_max;
    RETURN @MinValue;
END;

GO
-------------------------------------------------------------------------DONE

ALTER PROCEDURE ApplyForLoan(@accountNumber NVARCHAR(20), @loanAmount DECIMAL(18,2), @numberOfMonths INT)
AS
BEGIN
    DECLARE @maxLoanAmount DECIMAL(18,2), @approvedAmount DECIMAL(18,2);
	DECLARE @currentDate DATETIME, @startDate DATETIME, @endDate DATETIME;
    DECLARE @billId INT, @dueDate DATE, @amount DECIMAL(18,2);

    -- Check if the loan amount is within the allowable range
	
    EXEC @maxLoanAmount = CalculateLoanEligibility @accountNumber;
	select @maxLoanAmount;
	return;
    IF @maxLoanAmount < @loanAmount
	BEGIN
		print('ASSSSSSSSSSSSSSSSSSSS')
		select 0;
        RETURN 0;
	END
	
	--add loan to loans list
    SET @approvedAmount = @loanAmount * 1.2;

    INSERT INTO Loans (AccountNumber, LoanAmount, ApprovedAmount, ApprovedDate, LoanStatus)
    VALUES (@accountNumber, @loanAmount, @approvedAmount, GETDATE(), 'Active');

	DECLARE @loanId INT;
	SELECT @loanId = LoanId 
	FROM Loans
	where AccountNumber = @accountNumber;

    -- Update the user's account balance with the approved loan amount
    UPDATE Accounts
    SET Balance = Balance + @loanAmount
    WHERE AccountNumber = @accountNumber;

	--/////////////////////////////////////////////////calculate bills:
	DECLARE @remainingMonths INT;
    SET @remainingMonths = @numberOfMonths;

	 SET @currentDate = GETDATE();

    -- Calculate the end date
    IF @remainingMonths > 0
    BEGIN
        SET @endDate = DATEADD(MONTH, @remainingMonths, @currentDate);
    END
    ELSE
    BEGIN
        SET @endDate = NULL;
    END

    -- Generate and add bills to the Bills table
    DECLARE @billNumber INT = 1;
	DECLARE @counter INT;
	SET @counter = @numberOfMonths
    WHILE (@counter > 0)
    BEGIN
        -- Calculate the due date
        SET @dueDate = DATEADD(MONTH, 1, @currentDate);

        -- Calculate the bill amount for the current month
        SET @amount = @approvedAmount / @numberOfMonths;

        -- Add a new bill record to the Bills table
        INSERT INTO Bills (LoanId, DueDate, Amount, Paid, PaidDate)
        VALUES (@loanId, @dueDate, @amount, 0, NULL);

        --SET @billNumber += 1;
        SET @currentDate = @dueDate;
		SET @counter -= 1;
    END

    BEGIN
		select 1;
        RETURN 1;
	END
END;

GO
-------------------------------------------------------------------------DONE

CREATE PROCEDURE GetUserLoans(@userId INT)
AS
BEGIN
    SELECT Accounts.AccountNumber ,
		   LoanAmount,
		   ApprovedAmount ,
		   ApprovedDate,
		   LoanStatus
    FROM Loans inner join Accounts on Loans.AccountNumber = Accounts.AccountNumber
    WHERE UserId = @userId;
END;

-------------------------------------------------------------------------DONE
GO


CREATE PROCEDURE GetBills(@loanId INT)
AS
BEGIN
    SELECT *
    FROM Bills
    WHERE LoanId = @loanId;
END;

Go

-------------------------------------------------------------------------DONE

CREATE PROCEDURE PayBill(@loanId INT)
AS
BEGIN
    DECLARE @loanstatus NVARCHAR(255);
	DECLARE @accountNumber NVARCHAR(20);
    DECLARE @currentDate DATETIME, @nextDueDate DATETIME;
    DECLARE @billId INT, @amount DECIMAL(18,2);

	SELECT @accountNumber = AccountNumber
	FROM Loans
	WHERE LoanId = @loanId;

    -- Retrieve the loan status
    SELECT @loanstatus = LoanStatus
    FROM Loans
    WHERE LoanId = @loanId;

    -- Check if the loan is active
    IF @loanstatus = 'Active'
    BEGIN
        ---- Check if there are any unpaid bills for the loan
        SELECT @billId = BillId, @amount = Amount
        FROM Bills
        WHERE LoanId = @loanId AND Paid = 0 AND DueDate = (SELECT MIN(DueDate)
															FROM Bills
															WHERE LoanId = @loanId AND Paid = 0);
		
		--check enough money in account to pay the bills
		DECLARE @accountbalance DECIMAL(18,2);
		SELECT @accountbalance = Balance
		FROM Accounts
		WHERE AccountNumber = @accountNumber

		IF @accountbalance - @amount < 0
		RETURN 0;

		--///////////////////////////////////////check complete now some transaction
		BEGIN TRAN;

			UPDATE Bills
			SET Paid = 1, PaidDate = GETDATE()
			WHERE BillId = @billId;


			-- Decrease the unpaid amount by the paid bill amount
			UPDATE Accounts
			SET Balance = Balance - @amount
			WHERE AccountNumber = @accountNumber

			-- Update the loan status if all bills are paid
			IF (NOT EXISTS (SELECT * 
							FROM Bills
							WHERE LoanId = @loanId AND Paid = 0))
			BEGIN
				UPDATE Loans
				SET LoanStatus = 'Dismissed'
				WHERE LoanId = @loanId;
			END

		COMMIT TRAN;

    END

    RETURN 1;
END;

GO;


------------------------------------------------------------------------------------------------------------
CREATE PROCEDURE AddUser(@firstName NVARCHAR(50),@LastName NVARCHAR(50) ,@Email NVARCHAR(100) ,@Password NVARCHAR(255)) As
BEGIN
	INSERT INTO Users (FirstName,LastName,Email,Password) values (@firstName, @LastName, @Email, @Password);
END

GO

ALTER PROCEDURE AddAccount(@UserID INT,@AccountNumber NVARCHAR(20) ,@Balance DECIMAL(18,2)) As
BEGIN
	if (exists (select * from Users where UserId = @UserID)) 
		INSERT INTO Accounts(UserId,AccountNumber,Balance,StartTime,AccountType) values (@UserID,@AccountNumber,@Balance , GETDATE(),'Active');
END