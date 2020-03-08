import mysql.connector as mysql

db = mysql.connect(host="160.20.188.232", user="remote", passwd="M4ndr4g0r4!", database="network")
databases = db.cursor()
query = "SELECT * FROM network.devices WHERE grupo='full';"
databases.execute(query)
data = databases.fetchall()
db.close()

for row in data:
    print(row)