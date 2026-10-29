import mysql.connector
import os
import pickle

mycon= mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_PASSWORD",
    database="airbnb_db"
)

cursor = mycon.cursor()
name=input("Enter your name")



cursor.execute(
    "INSERT INTO users(name) VALUES(%s)",
    (name,)
)

mycon.commit()
cursor.execute("SELECT * FROM destinations")

for row in cursor.fetchall():
    print(row)