import tkinter as tk
import pyodbc
import hashlib
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime

server = '.'
database = 'bank'
conn_str = 'Driver={SQL Server};Server=' + server+ ';Database=' + database + ';Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)

def emial_to_userid(email):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT UserId FROM Users Where Email = {email}", email = email)
        conn.commit()  # Commit the change
        result = cursor.fetchall
        return result
    except pyodbc.Error as ex:
        print("Error", ex)
        conn.rollback()  # Rollback if there's an error
    finally:
        cursor.close()

print(emial_to_userid('MJ@gmail.com'))