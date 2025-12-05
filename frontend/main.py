import sys 
import os

# Permite que o Python reconheça a pasta backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivymd.app import MDApp   # <<< ALTERADO AQUI
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.lang import Builder

# Backend
from backend.usuarios import (
    validar_login,
    cadastrar_usuario,
    recuperar_senha,
    verificar_codigo,
    definir_nova_senha
)

from backend.home import HomeScreen
from backend.catalogo import CatalogoScreen, ItensCategoriaScreen

# Eventos
from backend.eventos import EventosScreen, DetalhesEventoScreen


# -------------------------------
# 📌 TELAS DO SISTEMA
# -------------------------------

class LoginScreen(Screen):
    def fazer_login(self):
        nome = self.ids.nome_input.text.strip()
        senha = self.ids.senha_input.text.strip()

        usuario = validar_login(nome, senha)

        if usuario:
            app = MDApp.get_running_app()
            app.usuario_atual = usuario  # guarda dict inteiro
            self.manager.current = "home"
        else:
            self.ids.msg.text = "❌ Usuário ou senha inválidos."

    def abrir_cadastro(self):
        self.manager.current = "cadastro"

    def abrir_recuperacao(self):
        self.manager.current = "recuperar"


class CadastroScreen(Screen):
    def cadastrar(self):
        nome = self.ids.nome_input.text.strip()
        email = self.ids.email_input.text.strip()
        senha = self.ids.senha_input.text.strip()
        confirmar = self.ids.confirmar_input.text.strip()

        msg = cadastrar_usuario(nome, email, senha, confirmar)
        self.ids.msg.text = msg


class RecuperarScreen(Screen):
    def recuperar(self):
        email = self.ids.email_input.text.strip()
        msg = recuperar_senha(email)
        self.ids.msg.text = msg

        if "enviado" in msg.lower():
            tela_codigo = self.manager.get_screen("codigo")
            tela_codigo.email = email
            self.manager.current = "codigo"


class TelaCodigo(Screen):
    email = StringProperty("")

    def confirmar_codigo(self):
        codigo = self.ids.codigo_input.text.strip()
        resultado = verificar_codigo(self.email, codigo)

        if resultado == "OK":
            app = MDApp.get_running_app()
            tela_nova = app.root.get_screen("nova_senha")
            tela_nova.email = self.email
            app.root.current = "nova_senha"
        else:
            self.ids.codigo_input.text = ""
            self.ids.msg.text = resultado


class TelaNovaSenha(Screen):
    email = StringProperty("")

    def salvar_senha(self):
        s1 = self.ids.senha1.text.strip()
        s2 = self.ids.senha2.text.strip()

        if s1 != s2:
            self.ids.msg.text = "❌ As senhas não coincidem."
            return

        msg = definir_nova_senha(self.email, s1)
        self.ids.msg.text = msg

        if "alterada" in msg.lower():
            MDApp.get_running_app().root.current = "login"


# -------------------------------
# 📌 GERENCIADOR DE TELAS
# -------------------------------

class GerenciadorTelas(ScreenManager):
    pass


# -------------------------------
# 📌 CARREGAMENTO DOS ARQUIVOS KV
# -------------------------------
Builder.load_file(os.path.join("telas", "login.kv"))
Builder.load_file(os.path.join("telas", "home.kv"))
Builder.load_file(os.path.join("telas", "catalogo.kv"))
Builder.load_file(os.path.join("telas", "eventos.kv"))  # <<< EVENTOS



# -------------------------------
# 📌 APP PRINCIPAL
# -------------------------------

class SistemaAtelieApp(MDApp):   # <<< ALTERADO AQUI
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.usuario_atual = None   # aqui vamos guardar o user logado

    def build(self):
        self.title = "EventPlus"

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Red"

        sm = GerenciadorTelas()

        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(CadastroScreen(name="cadastro"))
        sm.add_widget(RecuperarScreen(name="recuperar"))
        sm.add_widget(TelaCodigo(name="codigo"))
        sm.add_widget(TelaNovaSenha(name="nova_senha"))

        sm.add_widget(HomeScreen(name="home"))

        sm.add_widget(CatalogoScreen(name="catalogo"))
        sm.add_widget(ItensCategoriaScreen(name="itens_categoria"))

        sm.add_widget(EventosScreen(name="eventos"))
        sm.add_widget(DetalhesEventoScreen(name="detalhes_evento"))

        return sm


# -------------------------------
# 📌 EXECUÇÃO
# -------------------------------
if __name__ == "__main__":
    SistemaAtelieApp().run()
