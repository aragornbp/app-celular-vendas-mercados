from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from botoes import *
import requests
from kivy.app import App
from functools import partial

class BannerVendedor(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__()
        id_vendedor = kwargs['id_vendedor']
        link = f'https://aplicativovendashash-2026e-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor}"'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()
        valor = list(requisicao_dic.values())[0]
        avatar = valor['avatar']
        total_vendas = valor['total_vendas']

        meu_app = App.get_running_app()

        imagem = ImageButton(source=f'icones/fotos_perfil/{avatar}',
                             pos_hint={"right":0.3 ,"top":0.9 }, size_hint=(0.3, 0.8),
                             on_release=partial(meu_app.carregar_vendas_vendedor, valor))
        label_id = LabelButton(text=f'Id Vendedor: {id_vendedor}',
                               pos_hint={"right":0.9 ,"top":0.9 }, size_hint=(0.3, 0.5),
                               on_release=partial(meu_app.carregar_vendas_vendedor, valor))
        label_total = LabelButton(text=f'Total de Vendas: {total_vendas}',
                                  pos_hint={"right":0.6 ,"top": 0.9}, size_hint=(0.3, 0.5),
                                  on_release=partial(meu_app.carregar_vendas_vendedor, valor))

        self.add_widget(imagem)
        self.add_widget(label_id)
        self.add_widget(label_total)