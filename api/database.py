import mysql.connector

def conectar():
    try:
        con = mysql.connector.connect(
            host="srv795.hstgr.io",
            user="u800497449_Henrique",
            password="Souimperadordomundo10",
            database="u800497449_atelie_eventos",
            port=3306
        )
        return con
    except mysql.connector.Error as erro:
        print("Erro ao conectar:", erro)
        return None
