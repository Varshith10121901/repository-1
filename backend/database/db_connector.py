import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="1234",  # Note: password as a string
  auth_plugin='mysql_native_password'  # Add this parameter
)

print(mydb)