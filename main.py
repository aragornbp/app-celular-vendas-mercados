from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
import requests
from bannervenda import BannerVenda
import os
from functools import partial
from myfirebase import MyFirebase
from bannervendedor import BannerVendedor
from datetime import date

GUI = Builder.load_file('main.kv')
class MainApp(App):
    cliente = None
    produto = None
    unidade = None


    def build(self):
        self.firebase = MyFirebase()
        return GUI

    def on_start(self):
        #carregar fotos perfil
        arquivos = os.listdir('icones/fotos_perfil')
        pagina_fotoperfil = self.root.ids['fotoperfilpage']
        lista_fotos = pagina_fotoperfil.ids['lista_fotos_perfil']
        for foto in arquivos:
            imagem = ImageButton(source= f'icones/fotos_perfil/{foto}', on_release=partial(self.mudar_foto_perfil, foto))
            lista_fotos.add_widget(imagem)

        #carregar as fotos clientes
        arquivos = os.listdir('icones/fotos_clientes')
        pagina_addvendas = self.root.ids['adicionarvendaspage']
        lista_clientes = pagina_addvendas.ids['lista_clientes']
        for foto_cliente in arquivos:
            imagem = ImageButton(source= f'icones/fotos_clientes/{foto_cliente}', on_release= partial(self.selecionar_cliente, foto_cliente))
            label = LabelButton(text=foto_cliente.replace('.png', '').capitalize(),  on_release=partial(self.selecionar_cliente, foto_cliente))
            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label)

        #carregar fotos produtos
        arquivos = os.listdir('icones/fotos_produtos')
        pagina_addvendas = self.root.ids['adicionarvendaspage']
        lista_produtos = pagina_addvendas.ids['lista_produtos']
        for foto_produto in arquivos:
            imagem = ImageButton(source=f'icones/fotos_produtos/{foto_produto}', on_release= partial(self.selecionar_produto, foto_produto))
            label = LabelButton(text=foto_produto.replace('.png', '').capitalize(), on_release= partial(self.selecionar_produto, foto_produto))
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label)

        #carregar a data
        pagina_addvendas = self.root.ids['adicionarvendaspage']
        label_data = pagina_addvendas.ids['label_data']
        label_data.text = f'Data: {date.today().strftime("%d/%m/%Y")}'


        #carrega as infos do usuario
        self.carregar_infos_usuario()


    def carregar_infos_usuario(self):
        try:
            with open('refreshtoken.txt', "r") as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            # pegar info dos usuarios
            requisicao = requests.get(f'https://aplicativovendashash-2026e-default-rtdb.firebaseio.com/{self.local_id}.json')
            requisicao_dic = requisicao.json()
            print(requisicao_dic)

            # preencher foto perfil
            avatar = requisicao_dic['avatar']
            self.avatar = avatar
            foto_perfil = self.root.ids['foto_perfil']
            foto_perfil.source = f'icones/fotos_perfil/{avatar}'

            # preencher o id unico
            id_vendedor = requisicao_dic['id_vendedor']
            self.id_vendedor = id_vendedor
            pagina_ajustes = self.root.ids['ajustespage']
            pagina_ajustes.ids['label_vendedor'].text = f'Seu id Único: {id_vendedor}'

            # preencher o total de vendas
            total_vendas = requisicao_dic['total_vendas']
            self.total_vendas = total_vendas
            vendas = self.root.ids['homepage']
            vendas.ids['label_total_vendas'].text = f'Total de Vendas: [b]R${total_vendas}[/b]'


            #preencher equipe
            equipe = requisicao_dic['equipe']
            self.equipe = equipe
            print(equipe)


            # preencher lista de vendas
            try:
                vendas = requisicao_dic['vendas']
                pagina_homepage = self.root.ids['homepage']
                lista_vendas = pagina_homepage.ids['lista_vendas']
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                         produto=venda["produto"], foto_produto=venda['foto_produto'],
                                         data=venda['data'], preco=venda['preco'], unidade=venda['unidade'],
                                         quantidade=venda['quantidade'])
                    lista_vendas.add_widget(banner)

                #preencher equipe vendedores
                pagina_listavendedores = self.root.ids['listarvendedorespage']
                lista_vendedores = pagina_listavendedores.ids['lista_vendedores']
                lista_equipe = equipe.split(",")

                for id_vendedor_equipe in lista_equipe:
                    if id_vendedor_equipe != "":
                        banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                        lista_vendedores.add_widget(banner_vendedor)
            except:
                pass
            self.mudar_tela('homepage')
        except:
            pass


    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela

    def mudar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{foto}'
        info = f'{{"avatar":"{foto}"}}'
        requests.patch(f'https://aplicativovendashash-2026e-default-rtdb.firebaseio.com/{self.local_id}.json', data=info)
        self.mudar_tela('ajustespage')

    def adicionar_vendedor(self, id_vendedor_adicionado):
        link = f'https://aplicativovendashash-2026e-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor_adicionado}"'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()

        pagina_adicionarvendedor = self.root.ids["adicionarvendedorpage"]
        mensagem_texto = pagina_adicionarvendedor.ids["mensagem_outrovendedor"]

        if requisicao_dic == {}:
            mensagem_texto.text = "Usuário não encontrado"
        else:
            equipe = self.equipe.split(',')
            if id_vendedor_adicionado in equipe:
                mensagem_texto.text = "Vendedor já faz parte da equipe"
            else:
                self.equipe = self.equipe + f",{id_vendedor_adicionado}"
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f"https://aplicativovendashash-2026e-default-rtdb.firebaseio.com/{self.local_id}.json",
                               data=info)
                mensagem_texto.text = "Vendedor Adicionado com Sucesso"
                # adicionar um novo banner na lista de vendedores
                pagina_listavendedores = self.root.ids["listarvendedorespage"]
                lista_vendedores = pagina_listavendedores.ids["lista_vendedores"]
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_adicionado)
                lista_vendedores.add_widget(banner_vendedor)


    def selecionar_cliente(self, foto, *args):
        self.cliente = foto.replace('.png', '')
        pagina_addvendas = self.root.ids['adicionarvendaspage']
        lista_clientes = pagina_addvendas.ids['lista_clientes']
        for item in list(lista_clientes.children):
            item.color = (1, 1, 1, 1)
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 0, 1, 1)
            except:
                pass

    def selecionar_produto(self, foto, *args):
        self.produto = foto.replace('.png', '')
        pagina_addvendas = self.root.ids['adicionarvendaspage']
        lista_produtos = pagina_addvendas.ids['lista_produtos']
        for item in list(lista_produtos.children):
            item.color = (1, 1, 1, 1)
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 0, 1, 1)
            except:
                pass

    def selecionar_unidade(self, id_label, *args):
        paginaaddvendas = self.root.ids['adicionarvendaspage']
        self.unidade = id_label.replace('unidades_', '')
        paginaaddvendas.ids['unidades_kg'].color = (1, 1, 1, 1)
        paginaaddvendas.ids['unidades_unidades'].color = (1, 1, 1, 1)
        paginaaddvendas.ids['unidades_litros'].color = (1, 1, 1, 1)

        paginaaddvendas.ids[id_label].color = (0, 0, 1, 1)

    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade


        paginaaddvendas = self.root.ids['adicionarvendaspage']
        data = paginaaddvendas.ids['label_data'].text.replace('Data: ', '')
        preco = paginaaddvendas.ids['preco_total'].text
        quantidade = paginaaddvendas.ids['quantidade'].text

        if not cliente:
            paginaaddvendas.ids['label_selecione_cliente'].color = (1, 0, 0, 1)
        if not produto:
            paginaaddvendas.ids['label_selecione_produto'].color = (1, 0, 0, 1)
        if not unidade:
            paginaaddvendas.ids['unidades_kg'].color = (1, 0, 0, 1)
            paginaaddvendas.ids['unidades_unidades'].color = (1, 0, 0, 1)
            paginaaddvendas.ids['unidades_litros'].color = (1, 0, 0, 1)

        if not preco:
            paginaaddvendas.ids['input_preco'].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                paginaaddvendas.ids['input_preco'].color = (1, 0, 0, 1)

        if not quantidade:
            paginaaddvendas.ids['input_quantidade'].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(preco)
            except:
                paginaaddvendas.ids['input_quantidade'].color = (1, 0, 0, 1)

        if cliente and produto and unidade and (type(preco) == float) and (type(quantidade) == float):
            foto_cliente = cliente + '.png'
            foto_produto = produto + '.png'

            info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", "foto_produto": "{foto_produto}", "data": "{data}", "unidade": "{unidade}", "preco": "{preco}","quantidade": "{quantidade}"}}'
            link = f'https://aplicativovendashash-2026e-default-rtdb.firebaseio.com/{self.local_id}/vendas.json'
            requests.post(link, data=info)

            banner = BannerVenda(cliente= cliente, produto= produto, foto_cliente= foto_cliente,
                                 foto_produto= foto_produto, data= data, preco= preco, unidade= unidade, quantidade= quantidade)
            pagina_homepage = self.root.ids['homepage']
            lista_vendas = pagina_homepage.ids['lista_vendas']
            lista_vendas.add_widget(banner)

            requisicao = requests.get(f'https://aplicativovendashash-2026e-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json')
            total_vendas = float(requisicao.json())
            total_vendas += preco
            info1 = f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f'https://aplicativovendashash-2026e-default-rtdb.firebaseio.com/{self.local_id}.json', data= info1)

            homepage = self.root.ids['homepage']
            homepage.ids['label_total_vendas'].text = f'Total de Vendas: [b]R${total_vendas}[/b]'

            self.mudar_tela('homepage')

        self.cliente = None
        self.produto = None
        self.unidade = None

    def carregar_todas_vendas(self):
        pagina_vendas = self.root.ids['vendaspage']
        lista_vendas = pagina_vendas.ids['lista_vendas']

        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)

        # pegar info dos usuarios
        requisicao = requests.get(f'https://aplicativovendashash-2026e-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')
        requisicao_dic = requisicao.json()

        # preencher foto perfil
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/hash.png'

        total_vendas = 0
        for local_id_usuario in requisicao_dic:
            try:
                vendas = requisicao_dic[local_id_usuario]['vendas']
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    total_vendas += float(venda['preco'])
                    banner = BannerVenda(cliente=venda['cliente'], produto=venda['produto'], foto_cliente=venda['foto_cliente'],
                                         foto_produto=venda['foto_produto'], data=venda['data'], preco=venda['preco'], unidade=venda['unidade'],
                                         quantidade=venda['quantidade'])
                    lista_vendas.add_widget(banner)
            except Exception as excecao:
                print(excecao)

        # preencher o total de vendas
        vendas = self.root.ids['vendaspage']
        vendas.ids['label_total_vendas'].text = f'Total de Vendas: [b]R${total_vendas}[/b]'

        #redirecionar para pagina todas as vendas
        self.mudar_tela("vendaspage")

    def sair_vendas(self, id_tela):
        # preencher foto perfil
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{self.avatar}'

        self.mudar_tela('ajustespage')

    def carregar_vendas_vendedor(self, dic_info_vendedor, *args):
        try:
            vendas = dic_info_vendedor['vendas']
            vendasoutrovendedor = self.root.ids['vendasoutrovendedor']
            lista_vendas = vendasoutrovendedor.ids['listavendas']

            for item in list(lista_vendas.children):
                lista_vendas.remove_widget(item)

            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda['cliente'], produto=venda['produto'], foto_cliente=venda['foto_cliente'],
                                     foto_produto=venda['foto_produto'], data=venda['data'], preco=venda['preco'], unidade=venda['unidade'],
                                     quantidade=venda['quantidade'])
                lista_vendas.add_widget(banner)
        except Exception as excecao:
            print(excecao)
        #preencher total vendas
        total_vendas = dic_info_vendedor['total_vendas']
        vendasoutrovendedor.ids['label_total_vendas'].text = f'Total de Vendas: [b]R${total_vendas}[/b]'

        # preencher foto perfil
        foto_perfil = self.root.ids['foto_perfil']
        avatar = dic_info_vendedor['avatar']
        foto_perfil.source = f'icones/fotos_perfil/{avatar}'

        self.mudar_tela('vendasoutrovendedorpage')



MainApp().run()
