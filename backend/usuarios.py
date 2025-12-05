import re
import smtplib
from email.mime.text import MIMEText
from backend.conexao_mysql import conectar
import random
from datetime import datetime, timedelta
from backend.api_client import api


# -----------------------------------------
# 1️⃣ CADASTRAR USUÁRIO
# -----------------------------------------
def cadastrar_usuario(nome, email, senha, confirmar):
    if not all([nome, email, senha, confirmar]):
        return "⚠️ Preencha todos os campos."

    if senha != confirmar:
        return "❌ As senhas não coincidem."

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "❌ Email inválido."

    con = conectar()
    cur = con.cursor()

    try:
        cur.execute("SELECT * FROM usuarios WHERE email = %s OR nome = %s", (email, nome))
        if cur.fetchone():
            return "⚠️ Email ou nome de usuário já cadastrado."

        cur.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)",
            (nome, email, senha)
        )
        con.commit()
        return "✅ Usuário cadastrado com sucesso!"

    except Exception as e:
        return f"Erro ao cadastrar: {e}"

    finally:
        cur.close()
        con.close()


# -----------------------------------------
# 2️⃣ LOGIN
# -----------------------------------------
def validar_login(nome, senha):
    if not nome or not senha:
        return False

    con = conectar()
    cur = con.cursor()

    cur.execute("SELECT * FROM usuarios WHERE nome = %s AND senha = %s", (nome, senha))
    usuario = cur.fetchone()

    cur.close()
    con.close()

    return bool(usuario)


# -----------------------------------------
# 3️⃣ RECUPERAR SENHA (SEM LIMITES)
# -----------------------------------------
def recuperar_senha(email):
    resultado = api.post("/auth/recuperar", data={"email": email})
    if "error" in resultado:
        return f"❌ {resultado['error']}"
    return "Código enviado!"


# -----------------------------------------
# 4️⃣ VERIFICAR CÓDIGO
# -----------------------------------------
def verificar_codigo(email, codigo_digitado):
    resultado = api.post("/auth/verificar", data={
        "email": email,
        "codigo_digitado": codigo_digitado
    })

    if "error" in resultado:
        return resultado["error"]

    return "OK"


# -----------------------------------------
# 5️⃣ SALVAR NOVA SENHA
# -----------------------------------------
def definir_nova_senha(email, nova_senha):
    resultado = api.post("/auth/nova-senha", data={
        "email": email,
        "nova_senha": nova_senha
    })

    if "error" in resultado:
        return resultado["error"]

    return "Senha atualizada com sucesso!"