from flask import session
import psycopg2

con=psycopg2.connect("postgresql://postgres.ltwkdwxckpewhmtpjpvj:oCD4aNWbC7dd7MYG@aws-1-eu-west-1.pooler.supabase.com:6543/postgres")

class User:
    def __init__(self,email, password, firstname, address, zip, city, country, phone, lastname):
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.zip = zip
        self.city = city
        self.country = country
        self.phone = phone
        

    def register(self, firstname, lastname, address, zip, city, country, phone, email, password):
        cur=con.cursor()
        cur.execute("SELECT * FROM bruger WHERE email = %s AND password = %s", (email, password))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO bruger (firstname, lastname , address, zip, city, country, phone, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (firstname, lastname, address, zip, city, country, phone, email, password))
            con.commit()
            cur.close()
            return True
        cur.close()
        return False
    
    def login(self, email, password):
        cur=con.cursor()
        cur.execute("SELECT * FROM bruger WHERE email = %s AND password = %s", (email, password)) # 'WHERE' looper gennem databasen
        user = cur.fetchone() # 'fetchone()' henter den første række, der matcher kriterierne. Hvis ingen rækker matcher, returneres 'None'.
        cur.close()
        if user: # hvis 'user' ikke er 'None', betyder det, at en matchende bruger blev fundet i databasen
            session['user_id'] = user[0] # gemmer brugerens ID i sessionen for at holde dem logget ind
            return True
        return False
    
    def get_user_info(self):
        cur = con.cursor()
        cur.execute("SELECT * FROM bruger WHERE id = %s", (session['user_id'],)) # Henter nuværende oplysninger for den loggede bruger baseret på deres ID, som er gemt i sessionen
        user_info = cur.fetchone() # 'fetchone()' henter den første række, der matcher kriterierne. Hvis ingen rækker matcher, returneres 'None'.
        cur.close()
        return user_info
    
    def update(self, firstname, lastname, address, zip, city, country, phone, email, password):
        cur = con.cursor()
        cur.execute("UPDATE bruger SET firstname = %s, lastname = %s, address = %s, zip = %s, city = %s, country = %s, phone = %s, email = %s, password = %s WHERE id = %s", (firstname, lastname, address, zip, city, country, phone, email, password, session['user_id'])) # Opdaterer brugerens oplysninger i databasen baseret på deres ID
        con.commit()
        cur.close()
    