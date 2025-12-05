# backend/eventos.py
import os
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty, NumericProperty, ObjectProperty
from kivy.graphics.texture import Texture
from kivy.uix.image import Image

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDFloatingActionButton, MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel

from kivy.utils import get_color_from_hex

from backend.db_eventos import (
    criar_evento,
    listar_eventos,
    buscar_evento,
    ativar_evento_manual,
    adicionar_item_evento,
    listar_itens_evento,
    registrar_devolucao,
    gerar_pdf_evento,
    cancelar_evento,
    listar_itens_catalogo,
    atualizar_item_evento
)


from kivy.utils import get_color_from_hex


def rgba(x):
    return get_color_from_hex(x)


# ----------------------------------------
# Auxiliar: BLOB → textura
# ----------------------------------------
def blob_to_texture(blob):
    try:
        import PIL.Image as pil
        import io

        stream = io.BytesIO(blob)
        pil_image = pil.open(stream).convert("RGBA")

        tex = Texture.create(size=pil_image.size)
        tex.blit_buffer(pil_image.tobytes(), colorfmt="rgba", bufferfmt="ubyte")
        tex.flip_vertical()
        return tex

    except:
        return None


# ========================================
# TELA PRINCIPAL: LISTA DE EVENTOS
# ========================================
class EventosScreen(Screen):
    eventos = ListProperty([])

    def on_pre_enter(self):
        self.carregar_eventos()

    def carregar_eventos(self):
        app = MDApp.get_running_app()
        user_id = app.usuario_atual["id_usuario"]

        self.eventos = listar_eventos(user_id)
        lista = self.ids.lista_eventos
        lista.clear_widgets()

        # para cada evento → criar um card KivyMD
        for ev in self.eventos:
            card = MDCard(
                style="outlined",
                md_bg_color=rgba("#fcf6d2"),
                padding=15,
                size_hint_y=None,
                height=110
            )

            box = MDBoxLayout(orientation="vertical", spacing=3)

            box.add_widget(MDLabel(
                text=ev["nome_evento"],
                font_style="H6",
                theme_text_color="Custom",
                text_color=rgba("#281f20")
            ))

            box.add_widget(MDLabel(
                text=f"Data: {ev['data_evento']}",
                theme_text_color="Custom",
                text_color=rgba("#281f20")
            ))

            box.add_widget(MDLabel(
                text=f"Status: {ev['status']}",
                theme_text_color="Custom",
                text_color=rgba("#281f20")
            ))

            card.add_widget(box)

            card.bind(on_release=lambda inst, e=ev: self.abrir_evento(e["id_evento"]))

            lista.add_widget(card)

    def abrir_evento(self, id_evento):
        tela = self.manager.get_screen("detalhes_evento")
        tela.id_evento = id_evento
        self.manager.current = "detalhes_evento"

    def popup_novo_evento(self):
        NovoEventoDialog(self).open()


# ========================================
# POPUP CRIAR NOVO EVENTO
# ========================================
from kivy.uix.modalview import ModalView

class NovoEventoDialog(ModalView):
    def __init__(self, tela_eventos, **kwargs):
        super().__init__(size_hint=(0.9, 0.75), auto_dismiss=False, **kwargs)
        self.tela_eventos = tela_eventos

        root = MDBoxLayout(orientation="vertical", spacing=15, padding=20, md_bg_color=rgba("#fcf6d2"))

        root.add_widget(MDLabel(
            text="Novo Evento",
            font_style="H6",
            halign="center",
            theme_text_color="Custom",
            text_color=rgba("#281f20"),
            size_hint_y=None,
            height=40
        ))

        self.nome = MDTextField(hint_text="Nome do evento", mode="rectangle")
        self.data = MDTextField(hint_text="Data (AAAA-MM-DD)", mode="rectangle")
        self.cliente = MDTextField(hint_text="Cliente", mode="rectangle")
        self.endereco = MDTextField(hint_text="Endereço", mode="rectangle")
        self.obs = MDTextField(hint_text="Observações", multiline=True, mode="rectangle")

        root.add_widget(self.nome)
        root.add_widget(self.data)
        root.add_widget(self.cliente)
        root.add_widget(self.endereco)
        root.add_widget(self.obs)

        botoes = MDBoxLayout(size_hint_y=None, height=50, spacing=10)
        botoes.add_widget(MDFlatButton(
            text="Cancelar",
            theme_text_color="Custom",
            text_color=rgba("#281f20"),
            on_release=lambda *_: self.dismiss()
        ))
        botoes.add_widget(MDRaisedButton(
            text="Salvar",
            md_bg_color=rgba("#281f20"),
            text_color=(1,1,1,1),
            on_release=self.salvar
        ))
        root.add_widget(botoes)

        self.add_widget(root)

    def salvar(self, *args):
        nome = self.nome.text.strip()
        data = self.data.text.strip()
        cliente = self.cliente.text.strip()
        endereco = self.endereco.text.strip()
        obs = self.obs.text.strip()

        if not nome:
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text="O nome do evento é obrigatório.").open()
            return

        try:
            datetime.strptime(data, "%Y-%m-%d")
        except:
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text="Data inválida. Use formato AAAA-MM-DD.").open()
            return

        app = MDApp.get_running_app()
        user_id = app.usuario_atual["id_usuario"]

        criar_evento(nome, data, cliente, endereco, obs, user_id)

        self.dismiss()
        self.tela_eventos.carregar_eventos()


# ========================================
# TELA DETALHES DO EVENTO
# ========================================
class DetalhesEventoScreen(Screen):
    id_evento = NumericProperty(0)
    dados_evento = ObjectProperty(None)

    def on_pre_enter(self):
        self.carregar_evento()

    def carregar_evento(self):
        ev = buscar_evento(self.id_evento)
        self.dados_evento = ev

        # Bloco reorganizado conforme solicitado
        self.ids.lbl_titulo.text = ev["nome_evento"]
        self.ids.lbl_data.text = f"Data: {ev['data_evento']}"
        self.ids.lbl_cliente.text = f"Cliente: {ev['nome_cliente']}"
        self.ids.lbl_endereco.text = f"Endereço: {ev['endereco_evento']}"
        self.ids.lbl_obs.text = ev["observacoes"] or "Nenhuma observação."
        self.ids.lbl_status.text = f"Status: {ev['status']}"

        self.carregar_itens()

    def adicionar_item(self):
        AdicionarItemDialog(self).open()

    def carregar_itens(self):
        lista = listar_itens_evento(self.id_evento)
        box = self.ids.lista_itens_evento
        box.clear_widgets()

        for it in lista:
            card = MDCard(
                style="outlined",
                md_bg_color=rgba("#fcf6d2"),
                padding=10,
                size_hint_y=None,
                height=150
            )

            interno = MDBoxLayout(orientation="horizontal", spacing=10)

            if it["imagem"]:
                tex = blob_to_texture(it["imagem"])
                interno.add_widget(Image(texture=tex, size_hint=(None, None), size=(90, 90)))
            else:
                interno.add_widget(MDLabel(text="Sem imagem", size_hint=(None, None), size=(90, 90)))

            col = MDBoxLayout(orientation="vertical")
            col.add_widget(MDLabel(text=it["nome_item"], font_style="H6"))
            col.add_widget(MDLabel(text=f"Locado: {it['quantidade_locada']}"))
            col.add_widget(MDLabel(text=f"Devolvido: {it.get('quantidade_devolvida', 0)}"))

            card.add_widget(interno)
            interno.add_widget(col)

            interno.add_widget(
                MDRaisedButton(
                    text="Editar",
                    md_bg_color=rgba("#c6c39a"),
                    text_color=rgba("#281f20"),
                    on_release=lambda inst, item=it: EditarItemDialog(self, item).open()
                )
            )

            box.add_widget(card)

    # -------- Botões inferiores --------
    def ativar_evento(self):
        ok = ativar_evento_manual(self.id_evento)
        if ok:
            self.carregar_evento()
        else:
            MDDialog(title="Erro", text="Falta estoque!", md_bg_color=rgba("#fcf6d2")).open()

    def concluir_evento(self):
        if self.dados_evento["status"] != "ativo":
            MDDialog(
                title="Atenção",
                text="Ative o evento antes de concluir.",
                md_bg_color=rgba("#fcf6d2")
            ).open()
            return

        ConcluirEventoDialog(self).open()

    def gerar_pdf(self):
        caminho = os.path.join(os.getcwd(), f"evento_{self.id_evento}.pdf")
        gerar_pdf_evento(self.id_evento, caminho)
        MDDialog(
            title="PDF gerado!",
            text=f"Arquivo salvo em:\n{caminho}",
            md_bg_color=rgba("#fcf6d2")
        ).open()

    def cancelar_evento(self):
        cancelar_evento(self.id_evento)
        self.manager.current = "eventos"


# ========================================
# POPUP ADICIONAR ITEM A EVENTO
# ========================================
class AdicionarItemDialog(ModalView):
    def __init__(self, tela_evento, **kwargs):
        super().__init__(size_hint=(0.9, 0.6), auto_dismiss=False, **kwargs)
        self.tela_evento = tela_evento

        itens = listar_itens_catalogo()
        self.itens_db = itens
        self.item_selecionado = {"id_item": None}

        root = MDBoxLayout(orientation="vertical", spacing=15, padding=20, md_bg_color=rgba("#fcf6d2"))

        root.add_widget(MDLabel(
            text="Adicionar Item ao Evento",
            font_style="H6",
            halign="center",
            theme_text_color="Custom",
            text_color=rgba("#281f20"),
            size_hint_y=None,
            height=40
        ))

        self.campo_item = MDTextField(
            hint_text="Item do catálogo",
            mode="rectangle",
            readonly=True
        )

        # Botão para abrir menu do catálogo
        btn_catalogo = MDRaisedButton(
            text="Selecionar do catálogo",
            md_bg_color=rgba("#c6c39a"),
            text_color=(0,0,0,1)
        )

        self.campo_qtd = MDTextField(
            hint_text="Quantidade",
            text="1",
            mode="rectangle"
        )

        root.add_widget(self.campo_item)
        root.add_widget(btn_catalogo)
        root.add_widget(self.campo_qtd)

        botoes = MDBoxLayout(size_hint_y=None, height=50, spacing=10)
        botoes.add_widget(MDFlatButton(
            text="Cancelar",
            theme_text_color="Custom",
            text_color=rgba("#281f20"),
            on_release=lambda *_: self.dismiss()
        ))
        botoes.add_widget(MDRaisedButton(
            text="Adicionar",
            md_bg_color=rgba("#281f20"),
            text_color=(1,1,1,1),
            on_release=self.salvar
        ))
        root.add_widget(botoes)

        self.add_widget(root)

        # Criar menu de itens do catálogo
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"{i['nome_item']} (ID: {i['id_item']})",
                "on_release": lambda x=i: self._selecionar_item_catalogo(x)
            }
            for i in self.itens_db
        ]

        self._menu = MDDropdownMenu(
            caller=btn_catalogo,
            items=menu_items,
            width_mult=4
        )

        btn_catalogo.bind(on_release=lambda *_: self._menu.open())

    def _selecionar_item_catalogo(self, item):
        self.item_selecionado["id_item"] = item["id_item"]
        self.campo_item.text = item["nome_item"]
        self._menu.dismiss()

    def salvar(self, *args):
        nome = self.campo_item.text.strip()
        try:
            qtd = int(self.campo_qtd.text or "0")
        except ValueError:
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text="Quantidade inválida. Digite um número.").open()
            return

        if qtd <= 0:
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text="Quantidade deve ser maior que zero.").open()
            return

        # Se usuário selecionou do catálogo, usa diretamente
        item = None
        if self.item_selecionado["id_item"] is not None:
            for i in self.itens_db:
                if i["id_item"] == self.item_selecionado["id_item"]:
                    item = i
                    break
        else:
            # fallback: tentar achar pelo nome
            for i in self.itens_db:
                if i["nome_item"].lower() == nome.lower():
                    item = i
                    break

        if not item:
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text="Item não encontrado no catálogo.").open()
            return

        try:
            adicionar_item_evento(self.tela_evento.id_evento, item["id_item"], qtd)
        except Exception as e:
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text=f"Erro: {str(e)}").open()
            return

        self.dismiss()
        self.tela_evento.carregar_evento()


# ========================================
# POPUP EDITAR ITEM
# ========================================
class EditarItemDialog(ModalView):
    def __init__(self, tela_evento, item, **kwargs):
        super().__init__(size_hint=(0.9, 0.6), auto_dismiss=False, **kwargs)
        self.item = item
        self.tela_evento = tela_evento

        root = MDBoxLayout(orientation="vertical", spacing=15, padding=20, md_bg_color=rgba("#fcf6d2"))

        root.add_widget(MDLabel(
            text=f"Editar: {item['nome_item']}",
            font_style="H6",
            halign="center",
            theme_text_color="Custom",
            text_color=rgba("#281f20"),
            size_hint_y=None,
            height=40
        ))

        self.campo_qtd = MDTextField(
            text=str(item["quantidade_locada"]),
            hint_text="Quantidade",
            mode="rectangle"
        )

        self.campo_obs = MDTextField(
            text=item.get("observacoes", "") or "",
            hint_text="Observações",
            mode="rectangle",
            multiline=True
        )

        root.add_widget(self.campo_qtd)
        root.add_widget(self.campo_obs)

        botoes = MDBoxLayout(size_hint_y=None, height=50, spacing=10)
        botoes.add_widget(MDFlatButton(
            text="Cancelar",
            theme_text_color="Custom",
            text_color=rgba("#281f20"),
            on_release=lambda *_: self.dismiss()
        ))
        botoes.add_widget(MDRaisedButton(
            text="Salvar",
            md_bg_color=rgba("#281f20"),
            text_color=(1,1,1,1),
            on_release=self.salvar
        ))
        root.add_widget(botoes)

        self.add_widget(root)

    def salvar(self, *args):
        try:
            qtd  = int(self.campo_qtd.text or "0")
        except ValueError:
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text="Quantidade inválida. Digite um número.").open()
            return

        obs = self.campo_obs.text.strip()

        if qtd <= 0:
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text="Quantidade deve ser maior que zero.").open()
            return

        try:
            atualizar_item_evento(self.tela_evento.id_evento, self.item["id_item"], qtd, obs)
        except Exception as e:
            from kivymd.uix.snackbar import Snackbar
            Snackbar(text=f"Erro: {str(e)}").open()
            return

        self.dismiss()
        self.tela_evento.carregar_evento()


# ========================================
# POPUP CONCLUSÃO DE EVENTO
# ========================================
class ConcluirEventoDialog(ModalView):
    def __init__(self, tela_evento, **kwargs):
        super().__init__(size_hint=(0.9, 0.8), auto_dismiss=False, **kwargs)
        self.tela_evento = tela_evento
        self.lista_itens = listar_itens_evento(tela_evento.id_evento)

        self.inputs = {}

        root = MDBoxLayout(orientation="vertical", spacing=15, padding=20, md_bg_color=rgba("#fcf6d2"))

        root.add_widget(MDLabel(
            text="Concluir Evento",
            font_style="H6",
            halign="center",
            theme_text_color="Custom",
            text_color=rgba("#281f20"),
            size_hint_y=None,
            height=40
        ))

        scroll = MDBoxLayout(orientation="vertical", spacing=10, adaptive_height=True)

        for it in self.lista_itens:
            bloco = MDBoxLayout(orientation="vertical", spacing=5, size_hint_y=None, height=100)

            bloco.add_widget(MDLabel(
                text=it["nome_item"],
                font_style="Subtitle1",
                theme_text_color="Custom",
                text_color=rgba("#281f20")
            ))

            campo = MDTextField(
                hint_text=f"Devolvido (locado: {it['quantidade_locada']})",
                text=str(it['quantidade_locada']),
                mode="rectangle"
            )

            self.inputs[it["id_item"]] = campo
            bloco.add_widget(campo)
            scroll.add_widget(bloco)

        root.add_widget(scroll)

        botoes = MDBoxLayout(size_hint_y=None, height=50, spacing=10)
        botoes.add_widget(MDFlatButton(
            text="Cancelar",
            theme_text_color="Custom",
            text_color=rgba("#281f20"),
            on_release=lambda *_: self.dismiss()
        ))
        botoes.add_widget(MDRaisedButton(
            text="Concluir",
            md_bg_color=rgba("#281f20"),
            text_color=(1,1,1,1),
            on_release=self.finalizar
        ))
        root.add_widget(botoes)

        self.add_widget(root)

    def finalizar(self, *args):
        devolucoes = []

        for id_item, campo in self.inputs.items():
            qtd = int(campo.text or "0")
            locado = 0
            for it in self.lista_itens:
                if it["id_item"] == id_item:
                    locado = it["quantidade_locada"]
                    break

            devolucoes.append({
                "id_item": id_item,
                "locado": locado,
                "devolvido": qtd,
                "quebrado": qtd < locado,
                "obs": ""
            })

        registrar_devolucao(self.tela_evento.id_evento, devolucoes)
        self.dismiss()
        self.tela_evento.carregar_evento()

