import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        port=3307,
        user="root",
        password="mysql@123",
        database="hostel_management"
    )

    print("MYSQL CONNECTION SUCCESSFUL!")

    connection.close()

except mysql.connector.Error as error:
    print("MYSQL CONNECTION FAILED!")
    print(error)