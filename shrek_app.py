import tkinter as tk
import pyodbc
import hashlib
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime
from tkinter import messagebox,simpledialog

server = '.'
database = 'bank'
conn_str = 'Driver={SQL Server};Server=' + server+ ';Database=' + database + ';Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)




#-------------------------------------------------------------------------------------------------functions
def show_popup(input_string):
    popup = tk.Toplevel()
    popup.title(input_string)
    popup.geometry("200x100")
    popup.configure(bg="green")

    message_label = tk.Label(popup, text=input_string, font=("Arial", 14), fg="white", bg="green")
    message_label.pack(pady=20)

    ok_button = tk.Button(popup, text="OK", command=popup.destroy, bg="white", fg="green", font=("Arial", 12))
    ok_button.pack()

def login(email, password):
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()  # Hash the input password

    cursor = conn.cursor()
    try:
        cursor.execute("EXEC Login @username = ?, @password = ?", (email, hashed_password))
        result = cursor.fetchone()[0]
        return True if result else False  # If result is not None, login is successful
    except pyodbc.Error as ex:
        print("Error:", ex)
        return False
    finally:
        cursor.close()

def add_user(first_name, last_name, email, password):
    cursor = conn.cursor()
    try:
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()  # Hash the password
        cursor.execute("EXEC AddUser @firstName = ?, @LastName = ?, @Email = ?, @Password = ?",
                       (first_name, last_name, email, hashed_password))
        conn.commit()  # Commit the changes
        show_popup("User added successfully!")
    except pyodbc.Error as ex:
        show_popup("Error adding user:" + ex)
    finally:
        cursor.close()

def add_account(user_id, account_number, balance):
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC AddAccount @UserID = ?, @AccountNumber = ?, @Balance = ?",
                       (user_id, account_number, balance))
        conn.commit()  # Commit the changes
        print("Account added successfully!")
    except pyodbc.Error as ex:
        print("Error adding account")
    finally:
        cursor.close()

def transfer_money(source_account, dest_account, balance):
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC TransferMoney @sourceAccountNumber = ?, @destinationAccountNumber = ?, @amount = ?",
                       (source_account, dest_account, balance))
        result = cursor.fetchone()[0]
        if result:
            print('SUCCESSFUL!')
        else :
            print('UNSUCCESSFUL!')
    except pyodbc.Error as ex:
        print("some exception")
    finally:
        cursor.close()

def list_users():
    cursor = conn.cursor()
    try:
        cursor.execute("select * from Users")  # Assuming a stored procedure named GetUsers
        users = cursor.fetchall()  # Fetch all user records

        formatted_output = "\n".join([
            f"{user[0]:<10} {user[1]:<20} {user[2]:<30} {user[3]:<30} "  # Assuming fields are FirstName, LastName, Email
            for user in users
        ])
        return formatted_output
    except pyodbc.Error as ex:
        print("Error fetching users:", ex)
        return []  # Return an empty list in case of error
    finally:
        cursor.close()

def list_accounts():
    cursor = conn.cursor()
    try:
        cursor.execute("select * from Accounts")  # Assuming a stored procedure named GetUsers
        users = cursor.fetchall()  # Fetch all user records

        formatted_output = "\n".join([
            f"{user[0]:<10} {user[1]:<20} {user[2]:<30} {user[3]:<40} {user[4]:<40} {user[5]:<40}"  # Assuming fields are FirstName, LastName, Email
            for user in users
        ])

        return formatted_output
    except pyodbc.Error as ex:
        print("Error fetching users:", ex)
        return []  # Return an empty list in case of error
    finally:
        cursor.close()

def list_accounts_user(email):
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC GetAllAccountsByUserId @email = ?",(email))  # Replace with actual procedure name
        users = cursor.fetchall()  # Fetch all user records

        formatted_output = "\n".join([
            f"{user[0]:<10} {user[1]:<20} {user[2]:<30} {user[3]:<40} {user[4]:<40} "  # Assuming fields are FirstName, LastName, Email
            for user in users
        ])

        return formatted_output

    except pyodbc.Error as ex:
        print("Error fetching accounts:", ex)
        return ""
    finally:
        cursor.close()

def show_n_recent_transactions(account_number, n):
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC GetRecentAccountTransactions @accountNumber=?, @numTransactions=?",
                       (account_number, int(n)))
        users = cursor.fetchall()  # Fetch all user records

        formatted_output = "\n".join([
            f"{user[0]:<10} {user[1]:<20} {user[2]:<30} {user[3]:<40} {user[4]:<40} {user[5]:<40}"  # Assuming fields are FirstName, LastName, Email
            for user in users
        ])
        return formatted_output
    except pyodbc.Error as ex:
        print("Error fetching transactions:", ex)
    finally:
        cursor.close()

def show_transactions_by_date(account_number, start_date, end_date):
    cursor = conn.cursor()

# Convert string to datetime object
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    try:
        cursor.execute("EXEC GetAccountTransactionsByDate @startDate=?,  @endDate=? ,@accountnumber=? ",
                       (start_date, end_date , account_number ))
        
        users = cursor.fetchall()  # Fetch all user records

        formatted_output = "\n".join([
            f"{user[0]:<10} {user[1]:<20} {user[2]:<30} {user[3]:<40} {user[4]:<40} {user[5]:<40}"  # Assuming fields are FirstName, LastName, Email
            for user in users
        ])
        return formatted_output
    except pyodbc.Error as ex:
        print("Error fetching transactions:", ex)
    finally:
        cursor.close()

def ban_account(account_number, description):
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC BanAccount @accountNumber=?, @descryption=?",
                       (account_number, description))
        print("Account banned successfully!")
    except pyodbc.Error as ex:
        print("Error banning account:", ex)
        conn.rollback()  # Rollback if there's an error
    finally:
        cursor.close()

def emial_to_userid(email):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT UserId FROM Users Where Email = ?",(email))
        result = cursor.fetchone()[0]
        return int(result)
    except pyodbc.Error as ex:
        print("Error", ex)
        conn.rollback()  # Rollback if there's an error
    finally:
        cursor.close()

def list_of_loans(userid):
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC GetUserLoans @UserId=?", userid)
        loans = cursor.fetchall()

        # Format and return the list of loans (example)
        return [{"AccountNumber": loan[0], "LoanAmount": loan[1], "ApprovedAmount": loan[2],
                 "ApprovedDate": loan[3], "LoanStatus": loan[4]} for loan in loans]

    except pyodbc.Error as ex:
        print("Error fetching loans:", ex)
        return []
    finally:
        cursor.close()

def eligibility(accountNUmber):
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC CalculateLoanEligibility @accountNumber = ?;", (accountNUmber,))
        result = cursor.fetchval()
        print(result)

    except pyodbc.Error as ex:
        print("Error checking eligibility:", ex)
        return 0
    finally:
        cursor.close()

def apply_for_loan(account_number, loan_amount, number_of_months):
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC ApplyForLoan @accountNumber=?,@loanAmount=?, @numberOfMonths=?",
                                account_number, loan_amount, number_of_months)
        result =  cursor.fetchone()[0]  # Return 1 for success, 0 for failure
        return result
    except pyodbc.Error as ex:
        print("Error applying for loan:", ex)
        conn.rollback()
        return 0
    finally:
        cursor.close()

def list_of_bills(loan_id):
    cursor = conn.cursor()
    try:
        cursor.execute("EXEC GetBills @LoanId=?", loan_id)
        bills = cursor.fetchall()

        # Format and return the list of bills (example)
        return [{"BillId": bill[0], "DueDate": bill[1], "Amount": bill[2], "Paid": bill[3], "PaidDate": bill[4]}
                for bill in bills]

    except pyodbc.Error as ex:
        print("Error fetching bills:", ex)
        return []
    finally:
        cursor.close()

def pay_last_bill(loan_id):
    cursor = conn.cursor()
    try:
        result = cursor.execute("EXEC PayBill @LoanId=?", loan_id)
        conn.commit()
        return result.fetchval()  # Return 1 for success, 0 for failure

    except pyodbc.Error as ex:
        print("Error paying bill:", ex)
        conn.rollback()
        return 0
    finally:
        cursor.close()



the_path = "C:\\lessons\\7\\DB\\project files\\" + "2.PNG"
#****************************************************************************************************************

class LoadingScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Loading Screen")
        self.root.geometry("700x700")

        # Construct the image path for loading screen background
        loading_background_image_path = "C:\\lessons\\7\\DB\\project files\\" + "1.PNG"
        loading_background_image = Image.open(loading_background_image_path)
        loading_background_image = loading_background_image.resize((700, 700), Image.ANTIALIAS)
        self.background_image = ImageTk.PhotoImage(loading_background_image)

        # Create canvas for loading screen background image
        self.canvas = tk.Canvas(self.root, width=700, height=700)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

        # Create loading bar
        self.loading_bar = ttk.Progressbar(self.root, mode="indeterminate", length=600)
        self.loading_bar.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        # Schedule fake loading after 100 milliseconds
        self.root.after(100, self.fake_loading)

    def fake_loading(self):
        self.loading_bar.start(30)  # Start the progress bar animation
        self.root.update_idletasks()
        self.root.after(3000, self.destroy_loading_screen)

    def destroy_loading_screen(self):
        self.loading_bar.stop()  # Stop the progress bar animation
        self.root.destroy()  # Destroy the loading screen
        MainMenu()

class MainMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login Menu")
        self.root.geometry("700x700")

        # Construct the image path for the main menu background
        main_menu_background_image_path = the_path
        try:
            main_menu_background_image = Image.open(main_menu_background_image_path)
        except Exception as e:
            print(f"Error opening image: {e}")
            return

        main_menu_background_image = main_menu_background_image.resize((700, 700), Image.ANTIALIAS)
        self.background_image = ImageTk.PhotoImage(main_menu_background_image)

        # Create canvas for the main menu background image
        self.canvas = tk.Canvas(self.root, width=700, height=700)
        self.canvas.place(x=0, y=0)

        # Create Email (Username) Label and Entry
        email_label = tk.Label(self.root, text="Email (Username)", font=("Arial", 16))
        email_label.place(x=20, y=50)
        email_entry = tk.Entry(self.root, width=20, font=("Arial", 16))
        email_entry.place(x=20, y=100)

        # Create Password Label and Entry
        password_label = tk.Label(self.root, text="Password", font=("Arial", 16))
        password_label.place(x=20, y=200)
        password_entry = tk.Entry(self.root, width=20, show="*", font=("Arial", 16))
        password_entry.place(x=20, y=250)

        # Create OK Button
        ok_button = tk.Button(self.root, text="OK", command=lambda: self.check_credentials(email_entry.get(), password_entry.get()), bg="green", fg="white", font=("Arial", 16), width=15, height=2)
        ok_button.place(x=20, y=350)

        # Display the background image on the canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

        self.root.mainloop()

    def check_credentials(self, email, password):
        if (login(email,password)):
            if email == 'Admin':
                self.admin_menu = AdminMenu(self.root)  # Pass the root window to AdminMenu
                self.admin_menu.create_admin_menu()
                self.root.withdraw()
            else:
                self.user_menu = UserMenu(self.root,email=email)  # Pass the root window to AdminMenu
                self.user_menu.create_user_menu()
                self.root.withdraw()
        else:
            show_popup("unsuccessful login")

class AdminMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Menu")
        self.root.geometry("700x700")
        self.background_image = None  # Initialize as None

    def create_admin_menu(self):
        # Create canvas for the admin menu background image
        admin_menu_background_image_path = "C:\\lessons\\7\\DB\\project files\\" + "3.PNG"  # Replace with the actual path
        try:
            admin_menu_background_image = Image.open(admin_menu_background_image_path)
        except Exception as e:
            print(f"Error opening image: {e}")
            return

        admin_menu_background_image = admin_menu_background_image.resize((700, 700), Image.ANTIALIAS)
        self.background_image = ImageTk.PhotoImage(admin_menu_background_image)

        canvas = tk.Canvas(self.root, width=700, height=700)
        canvas.place(x=0, y=0)

        # Create 'Add User' Button
        add_user_button = tk.Button(self.root, text="Add User", command=self.add_user_popup, bg="green", fg="white", font=("Arial", 16), width=15, height=2)
        add_user_button.place(x=20, y=50)

        # Create 'Add Account' Button
        add_account_button = tk.Button(self.root, text="Add Account", command=self.add_account_popup, bg="green", fg="white", font=("Arial", 16), width=15, height=2)
        add_account_button.place(x=20, y=150)

        # Create 'List Accounts and Users' Button
        list_accounts_users_button = tk.Button(self.root, text="List Accounts and Users", command=self.list_accounts_users_popup, bg="green", fg="white", font=("Arial", 16), width=15, height=2)
        list_accounts_users_button.place(x=20, y=250)

        # Create 'Back to Login' Button
        back_to_login_button = tk.Button(self.root, text="Back to Login", command=self.back_to_login, bg="green", fg="white", font=("Arial", 16), width=15, height=2)
        back_to_login_button.place(x=500, y=600)

        # Display the background image on the canvas
        canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

        self.root.mainloop()

    def add_user_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add User")
        popup.geometry("400x600")

        # Create Firstname Label and Entry
        firstname_label = tk.Label(popup, text="Firstname", font=("Arial", 16))
        firstname_label.pack(pady=10)
        firstname_entry = tk.Entry(popup, font=("Arial", 16))
        firstname_entry.pack(pady=10)

        # Create Lastname Label and Entry
        lastname_label = tk.Label(popup, text="Lastname", font=("Arial", 16))
        lastname_label.pack(pady=10)
        lastname_entry = tk.Entry(popup, font=("Arial", 16))
        lastname_entry.pack(pady=10)

        # Create Email Label and Entry
        email_label = tk.Label(popup, text="Email", font=("Arial", 16))
        email_label.pack(pady=10)
        email_entry = tk.Entry(popup, font=("Arial", 16))
        email_entry.pack(pady=10)

        # Create Password Label and Entry
        password_label = tk.Label(popup, text="Password", font=("Arial", 16))
        password_label.pack(pady=10)
        password_entry = tk.Entry(popup, show="*", font=("Arial", 16))
        password_entry.pack(pady=10)

        # Create OK Button
        ok_button = tk.Button(popup, text="OK", command=lambda: add_user(firstname_entry.get(), lastname_entry.get(), email_entry.get(), password_entry.get()), bg="green", fg="white", font=("Arial", 16), width=10)
        ok_button.pack(pady=20)

    def add_account_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add Account")
        popup.geometry("400x600")

        # Create UserID Label and Entry
        user_id_label = tk.Label(popup, text="UserID", font=("Arial", 16))
        user_id_label.pack(pady=10)
        user_id_entry = tk.Entry(popup, font=("Arial", 16))
        user_id_entry.pack(pady=10)

        # Create Account Number Label and Entry
        account_number_label = tk.Label(popup, text="Account Number", font=("Arial", 16))
        account_number_label.pack(pady=10)
        account_number_entry = tk.Entry(popup, font=("Arial", 16))
        account_number_entry.pack(pady=10)

        # Create Balance Label and Entry
        balance_label = tk.Label(popup, text="Balance", font=("Arial", 16))
        balance_label.pack(pady=10)
        balance_entry = tk.Entry(popup, font=("Arial", 16))
        balance_entry.pack(pady=10)

        # Create OK Button
        ok_button = tk.Button(popup, text="OK", command=lambda: add_account(user_id_entry.get(), account_number_entry.get(), balance_entry.get()), bg="green", fg="white", font=("Arial", 16), width=10)
        ok_button.pack(pady=20)

    def list_accounts_users_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("List Accounts and Users")
        popup.geometry("900x800")

        # Retrieve and display the list of accounts and users
        accounts_text = list_accounts()
        text_widget = tk.Text(popup, wrap=tk.WORD, font=("Arial", 12))
        text_widget.insert(tk.END, accounts_text)
        text_widget.pack(pady=20)

        accounts_text = list_users()
        text_widget = tk.Text(popup, wrap=tk.WORD, font=("Arial", 12))
        text_widget.insert(tk.END, accounts_text)
        text_widget.pack(pady=20)

    def back_to_login(self):
        self.root.destroy()  # Destroy the current admin menu
        login_menu = MainMenu()  # Create a new login menu

class UserMenu:
    def __init__(self, root, email):
        self.root = root
        self.root.title("User Menu")
        self.root.geometry("700x700")
        self.background_image = None  # Initialize as None
        self.email = email
        

    def create_user_menu(self):
        # Create canvas for the user menu background image
        user_menu_background_image_path = "C:\\lessons\\7\\DB\\project files\\" + "4.PNG" # Replace with the actual path
        try:
            user_menu_background_image = Image.open(user_menu_background_image_path)
        except Exception as e:
            print(f"Error opening image: {e}")
            return

        user_menu_background_image = user_menu_background_image.resize((700, 700), Image.ANTIALIAS)
        self.background_image = ImageTk.PhotoImage(user_menu_background_image)

        canvas = tk.Canvas(self.root, width=700, height=700)
        canvas.place(x=0, y=0)

        # Create 'List of Accounts' Button
        list_accounts_button = tk.Button(self.root, text="List of Accounts", command=self.list_accounts_popup, bg="green", fg="white", font=("Arial", 16), width=15, height=2)
        list_accounts_button.place(x=500, y=50)

        # Create 'Transfer Money' Button
        transfer_money_button = tk.Button(self.root, text="Transfer Money", command=self.transfer_money_popup, bg="green", fg="white", font=("Arial", 16), width=15, height=2)
        transfer_money_button.place(x=500, y=150)

        # Create 'Show N Recent Transactions' Button
        recent_transactions_button = tk.Button(self.root, text="Show N Recent Transactions", command=self.recent_transactions_popup, bg="green", fg="white", font=("Arial", 12), width=22, height=2)
        recent_transactions_button.place(x=500, y=250)

        # Create 'Show Transactions by Date' Button
        transactions_by_date_button = tk.Button(self.root, text="Show Transactions by Date", command=self.transactions_by_date_popup, bg="green", fg="white", font=("Arial", 12), width=22, height=2)
        transactions_by_date_button.place(x=500, y=350)

        # Create 'Ban Account' Button
        ban_account_button = tk.Button(self.root, text="Ban Account", command=self.ban_account_popup, bg="green", fg="white", font=("Arial", 16), width=15, height=2)
        ban_account_button.place(x=500, y=450)

        loans_button = tk.Button(self.root, text="Loans", command=self.loans_popup, bg="green", fg="white", font=("Arial", 16), width=15, height=2)
        loans_button.place(x=500, y=550)

        # Display the background image on the canvas
        canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

        self.root.mainloop()

    def list_accounts_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("List of Accounts")
        popup.geometry("800x600")

        # Retrieve and display the list of accounts
        accounts_text = list_accounts_user(self.email)
        text_widget = tk.Text(popup, wrap=tk.WORD, font=("Arial", 14))
        text_widget.insert(tk.END, accounts_text)
        text_widget.pack(pady=20)

    def transfer_money_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Transfer Money")
        popup.geometry("400x600")

        # Create Source Account Label and Entry
        source_account_label = tk.Label(popup, text="Source Account", font=("Arial", 16))
        source_account_label.pack(pady=10)
        source_account_entry = tk.Entry(popup, font=("Arial", 16))
        source_account_entry.pack(pady=10)

        # Create Destination Account Label and Entry
        destination_account_label = tk.Label(popup, text="Destination Account", font=("Arial", 16))
        destination_account_label.pack(pady=10)
        destination_account_entry = tk.Entry(popup, font=("Arial", 16))
        destination_account_entry.pack(pady=10)

        # Create Amount Label and Entry
        amount_label = tk.Label(popup, text="Amount", font=("Arial", 16))
        amount_label.pack(pady=10)
        amount_entry = tk.Entry(popup, font=("Arial", 16))
        amount_entry.pack(pady=10)

        # Create OK Button
        ok_button = tk.Button(popup, text="OK", command=lambda: transfer_money(source_account_entry.get(), destination_account_entry.get(), amount_entry.get()), bg="green", fg="white", font=("Arial", 16), width=10)
        ok_button.pack(pady=20)

    def recent_transactions_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Show N Recent Transactions")
        popup.geometry("400x600")

        # Create Account Number Label and Entry
        account_number_label = tk.Label(popup, text="Account Number", font=("Arial", 16))
        account_number_label.pack(pady=10)
        account_number_entry = tk.Entry(popup, font=("Arial", 16))
        account_number_entry.pack(pady=10)

        # Create N Label and Entry
        n_label = tk.Label(popup, text="Number of recent transactions", font=("Arial", 16))
        n_label.pack(pady=10)
        n_entry = tk.Entry(popup, font=("Arial", 16))
        n_entry.pack(pady=10)

        # Create OK Button
        ok_button = tk.Button(popup, text="OK", command=lambda: self.pre_show_n_recent_transactions(account_number_entry.get(), n_entry.get(),popup), bg="green", fg="white", font=("Arial", 16), width=10)
        ok_button.pack(pady=20)
    
    def pre_show_n_recent_transactions(self, account_number, n, popup):
        # Replace this with the actual logic to get and show N recent transactions
        print(f"Showing N recent transactions for account {account_number}, N={n}")

        # Close the current popup
        popup.destroy()

        # Open another popup with the result
        result_popup = tk.Toplevel(self.root)
        result_popup.title("Recent Transactions Result")
        result_popup.geometry("700x800")

        # Display the result in a text widget
        result_text = show_n_recent_transactions(account_number,n)
        text_widget = tk.Text(result_popup, wrap=tk.WORD, font=("Arial", 14))
        text_widget.insert(tk.END, result_text)
        text_widget.pack(pady=20)
    
    def transactions_by_date_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Show Transactions by Date")
        popup.geometry("500x400")

        # Create Account Number Label and Entry
        account_number_label = tk.Label(popup, text="Account Number", font=("Arial", 16))
        account_number_label.pack(pady=10)
        account_number_entry = tk.Entry(popup, font=("Arial", 16))
        account_number_entry.pack(pady=10)

        # Create Start Date Label and Entry
        start_date_label = tk.Label(popup, text="Start Date (YYYY-MM-DD)", font=("Arial", 16))
        start_date_label.pack(pady=10)
        start_date_entry = tk.Entry(popup, font=("Arial", 16))
        start_date_entry.pack(pady=10)

        # Create End Date Label and Entry
        end_date_label = tk.Label(popup, text="End Date (YYYY-MM-DD)", font=("Arial", 16))
        end_date_label.pack(pady=10)
        end_date_entry = tk.Entry(popup, font=("Arial", 16))
        end_date_entry.pack(pady=10)

        # Create OK Button
        ok_button = tk.Button(popup, text="OK", command=lambda: show_transactions_by_date(account_number_entry.get(), start_date_entry.get(), end_date_entry.get()), bg="green", fg="white", font=("Arial", 16), width=10)
        ok_button.pack(pady=20)

    def ban_account_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Ban Account")
        popup.geometry("400x300")

        # Create Account Number Label and Entry
        account_number_label = tk.Label(popup, text="Account Number", font=("Arial", 16))
        account_number_label.pack(pady=10)
        account_number_entry = tk.Entry(popup, font=("Arial", 16))
        account_number_entry.pack(pady=10)

        # Create Description Label and Entry
        description_label = tk.Label(popup, text="Description", font=("Arial", 16))
        description_label.pack(pady=10)
        description_entry = tk.Entry(popup, font=("Arial", 16))
        description_entry.pack(pady=10)

        # Create OK Button
        ok_button = tk.Button(popup, text="OK", command=lambda: ban_account(account_number_entry.get(), description_entry.get()), bg="green", fg="white", font=("Arial", 16), width=10)
        ok_button.pack(pady=20)

    def loans_popup(self):
        self.loans_menu = LoansMenu(self.root,self.email)
        self.loans_menu.create_loans_menu()

class LoansMenu:
    def __init__(self, root, email):
        self.root = root
        self.email = email
        self.userid = emial_to_userid(email)

    def create_loans_menu(self):
    
        # Create canvas for the loans menu background image
        loans_menu_background_image_path = "C:\\lessons\\7\\DB\\project files\\" + "6.PNG" # Replace with the actual path
        try:
            loans_menu_background_image = Image.open(loans_menu_background_image_path)
        except Exception as e:
            print(f"Error opening image: {e}")
            return

        loans_menu_background_image = loans_menu_background_image.resize((700, 700), Image.ANTIALIAS)
        background_image = ImageTk.PhotoImage(loans_menu_background_image)

        canvas = tk.Canvas(self.root, width=700, height=700)
        canvas.place(x=0, y=0)

        # Display the background image on the canvas
        canvas.create_image(0, 0, anchor=tk.NW, image=background_image)

        # Create 'List of Loans' Button
        list_of_loans_button = tk.Button(self.root, text="List of Loans", command=lambda: self.list_of_loans_popup(userid=self.userid), bg="green", fg="white", font=("Arial", 16), width=15, height=2)
        list_of_loans_button.place(x=50, y=50)

        # Create 'Loan Eligibility' Button
        eligibility_button = tk.Button(self.root, text="Loan Eligibility", command= self.eligibility_popup, bg="green", fg="white", font=("Arial", 16), width=15, height=2)
        eligibility_button.place(x=50, y=150)

        # Create 'Apply for Loan' Button
        apply_for_loan_button = tk.Button(self.root, text="Apply for Loan", command=lambda: self.apply_for_loan_popup(self.userid), bg="green", fg="white", font=("Arial", 16), width=15, height=2)
        apply_for_loan_button.place(x=50, y=250)

        # Create 'List of Bills' Button
        list_of_bills_button = tk.Button(self.root, text="List of Bills", command=lambda: self.list_of_bills_popup, bg="green", fg="white", font=("Arial", 16), width=15, height=2)
        list_of_bills_button.place(x=50, y=350)

        # Create 'Pay Last Bill' Button
        pay_last_bill_button = tk.Button(self.root, text="Pay Last Bill", command=lambda: self.pay_last_bill_popup, bg="green", fg="white", font=("Arial", 16), width=15, height=2)
        pay_last_bill_button.place(x=50, y=450)

        self.root.mainloop()

    def list_of_loans_popup(self,userid):
        result = list_of_loans(userid)
        self.show_result_popup("List of Loans", result)

    def eligibility_popup(self):
        account_number = self.get_account_number_input()
        result = eligibility(accountNUmber=account_number)
        self.show_result_popup("Loan Eligibility", result)

    def apply_for_loan_popup(self,userid):
        account_number = self.get_account_number_input()
        number_of_months = simpledialog.askinteger("Number of Months", "Enter Number of Months:")
        loan_amount = simpledialog.askfloat("Loan Amount", "Enter Loan Amount:")

        if apply_for_loan(account_number,loan_amount,number_of_months):
            messagebox.showinfo("Loan Application", "Loan application submitted successfully!")
        else:
            messagebox.showinfo("Loan Application", "Loan application not successful!")

    def list_of_bills_popup(self):
        result = self.list_of_bills()
        self.show_result_popup("List of Bills", result)

    def pay_last_bill_popup(self):
        self.pay_last_bill()
        messagebox.showinfo("Payment", "Last bill paid successfully!")

    def show_result_popup(self, title, result):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("700x800")

        # Display the result in a text widget
        text_widget = tk.Text(popup, wrap=tk.WORD, font=("Arial", 14))
        text_widget.insert(tk.END, result)
        text_widget.pack(pady=20)

    def get_account_number_input(self):
        account_number = simpledialog.askstring("Account Number", "Enter Account Number:")
        return account_number
           
if __name__ == "__main__":
    root = tk.Tk()
    LoadingScreen__ = LoadingScreen(root)
    root.mainloop()
    #---------------------------------------------
    # root = tk.Tk()
    # loans_menu = LoansMenu(root,'MJ@gmail.com')
    # loans_menu.create_loans_menu()
    # root.mainloop()
    #---------------------------------------------


#****************************************************************************************************************
conn.close()