import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
import paho.mqtt.client as mqtt
from kivy.uix.gridlayout import GridLayout
import random
import requests

class CountdownScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")
        self.label = Label(text="App Life Box", font_size=30)
        self.countdown_label = Label(text="5", font_size=24)
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.countdown_label)
        self.add_widget(self.layout)
        self.countdown = 5

    def on_pre_enter(self):
        self.schedule_countdown(self.countdown)

    def schedule_countdown(self, countdown):
        if countdown > 0:
            self.countdown_label.text = str(countdown)
            countdown -= 1
            Clock.schedule_once(lambda dt, c=countdown: self.schedule_countdown(c), 1)
        else:
            self.manager.current = "login"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('usuarios.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios
                              (nome TEXT, senha TEXT, tipo TEXT)''')
        self.conn.commit()

    def add_user(self, nome, senha, tipo):
        self.cursor.execute("INSERT INTO usuarios (nome, senha, tipo) VALUES (?, ?, ?)", (nome, senha, tipo))
        self.conn.commit()

    def check_user(self, nome, senha):
        self.cursor.execute("SELECT * FROM usuarios WHERE nome = ? AND senha = ?", (nome, senha))
        return self.cursor.fetchone() is not None

    def get_user_type(self, nome):
        self.cursor.execute("SELECT tipo FROM usuarios WHERE nome = ?", (nome,))
        result = self.cursor.fetchone()
        return result[0] if result else None

class CadastroScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.layout = BoxLayout(orientation="vertical")
        self.label = Label(text="Cadastro", font_size=30)
        self.nome = TextInput(hint_text="Nome", multiline=False)
        self.senha = TextInput(hint_text="Senha", multiline=False, password=True)
        self.senha_autorizacao = TextInput(hint_text="Senha de Autorização", multiline=False, password=True)
        self.botao_verificar_autorizacao = Button(text="Verificar Autorização")
        self.botao_verificar_autorizacao.bind(on_press=self.verificar_autorizacao)

        self.tipo_dropdown = DropDown()
        tipos = ["Operador"]
        for tipo in tipos:
            btn = Button(text=tipo, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn, tipo=tipo: self.tipo_dropdown.select(tipo))
            self.tipo_dropdown.add_widget(btn)

        self.tipo_button = Button(text="Escolher Tipo", size_hint=(None, None))
        self.tipo_button.bind(on_release=self.tipo_dropdown.open)
        self.tipo_dropdown.bind(on_select=lambda instance, x: setattr(self.tipo_button, 'text', x))

        self.botao = Button(text="Cadastrar")
        self.botao.bind(on_press=self.cadastrar)

        self.layout.add_widget(self.label)
        self.layout.add_widget(self.nome)
        self.layout.add_widget(self.senha)
        self.layout.add_widget(self.tipo_button)
        self.layout.add_widget(self.botao)
        self.add_widget(self.layout)
        self.layout.add_widget(self.senha_autorizacao)
        self.layout.add_widget(self.botao_verificar_autorizacao)

    def cadastrar(self, instance):
        nome = self.nome.text
        senha = self.senha.text
        tipo = self.tipo_button.text
    
        # Verifique se o nome de usuário tem até no máximo 10 caracteres
        if len(nome) > 10:
            self.label.text = "O nome de usuário deve ter até no máximo 10 caracteres"
            return
    
        # Verifique se a senha tem exatamente 4 dígitos numéricos
        if not senha.isdigit() or len(senha) != 4:
            self.label.text = "A senha deve ter exatamente 4 dígitos numéricos"
            return
    
        if nome and senha and tipo:
            self.db.add_user(nome, senha, tipo)
            self.nome.text = ""
            self.senha.text = ""
            self.tipo_button.text = "Escolher Tipo"
            self.manager.current = "login"

    def verificar_autorizacao(self, instance):
        senha_autorizacao = self.senha_autorizacao.text

        senha_correta = "medico123"  # Senha de autorização fixa para médicos

        if senha_autorizacao == senha_correta:
            self.cadastrar_medico()
        else:
            self.label.text = "Senha de autorização incorreta"

    def cadastrar_medico(self):
        nome = self.nome.text
        senha = self.senha.text
        tipo = "Médico"
        
        # Verifique se o nome de usuário tem até no máximo 10 caracteres
        if len(nome) > 10:
            self.label.text = "O nome de usuário deve ter até no máximo 10 caracteres"
            return
    
        # Verifique se a senha tem exatamente 4 dígitos numéricos
        if not senha.isdigit() or len(senha) != 4:
            self.label.text = "A senha deve ter exatamente 4 dígitos numéricos"
            return

        if nome and senha and tipo:
            self.db.add_user(nome, senha, tipo)
            self.nome.text = ""
            self.senha.text = ""
            self.tipo_button.text = "Escolher Tipo"
            self.manager.current = "login"

class LoginScreen(Screen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.layout = BoxLayout(orientation="vertical")
        self.label = Label(text="Login", font_size=30)
        self.nome = TextInput(hint_text="Nome", multiline=False)
        self.senha = TextInput(hint_text="Senha", multiline=False, password=True)
        self.botao = Button(text="Entrar")
        self.botao.bind(on_press=self.logar)
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.nome)
        self.layout.add_widget(self.senha)
        self.layout.add_widget(self.botao)
        self.add_widget(self.layout)
        self.cadastro_button = Button(text="Cadastrar")
        self.cadastro_button.bind(on_press=self.ir_para_cadastro)
        self.layout.add_widget(self.cadastro_button)

    def ir_para_cadastro(self, instance):
        self.manager.current = "cadastro"

    def logar(self, instance):
        nome = self.nome.text
        senha = self.senha.text
        if nome and senha:
            if self.db.check_user(nome, senha):
                self.nome.text = ""
                self.senha.text = ""
                tipo = self.db.get_user_type(nome)
                if tipo == "Operador":
                    self.manager.current = "operador"
                elif tipo == "Médico":
                    self.manager.current = "medico"
            else:
                self.label.text = "Usuário ou senha inválidos"

class OperadorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.temperatura_medida = 0  # Inicialize a temperatura medida como 0
        
        # Crie um GridLayout para organizar os elementos
        self.layout = GridLayout(cols=2, spacing=10, padding=10)
        
        # Elementos da interface
        self.temperature_label = Label(text="Temperature: °C")
        self.potentiometer_label = Label(text="Potentiometer: ")
        self.led_label = Label(text="LED Status: ")

        # Adicione os elementos ao GridLayout
        self.layout.add_widget(self.temperature_label)
        self.layout.add_widget(self.potentiometer_label)
        self.layout.add_widget(self.led_label)

        # Inicialize os clientes MQTT para cada tópico
        self.init_mqtt_led("led")
        self.init_mqtt_pot("pot")
        self.init_mqtt_temp("temper")

        # Adicione o GridLayout à tela
        self.add_widget(self.layout)
        
        self.logout_button = Button(text="Logout", on_press=self.logout)
        self.layout.add_widget(self.logout_button)
        
        # Use a função buscar_opcoes_caixas para obter as opções do banco de dados
        opcoes_caixas = self.buscar_opcoes_caixas()
        
        # Adicione um Spinner para selecionar a caixa
        self.caixa_spinner = Spinner(text="Selecione a Caixa", values=opcoes_caixas, size_hint=(None, None))
        self.caixa_spinner.bind(text=self.on_caixa_spinner_select)
        self.layout.add_widget(self.caixa_spinner)
        
        # Exiba o erro de temperatura
        self.erro_temperatura_label = Label(text="Erro de Temperatura: N/A")
        self.layout.add_widget(self.erro_temperatura_label)
        
    def buscar_opcoes_caixas(self):
        conn = sqlite3.connect('database.db')  # Substitua 'database.db' pelo nome do seu banco de dados
        cursor = conn.cursor()

        # Consulte o banco de dados para obter as opções de caixas
        cursor.execute("SELECT id FROM caixas")
        resultados = cursor.fetchall()
        
        conn.close()

        if resultados:
            # Extrai as opções do banco de dados (IDs das caixas)
            opcoes_caixas = [str(resultado[0]) for resultado in resultados]
            return opcoes_caixas
        else:
            return []

    def on_caixa_spinner_select(self, instance, text):
        self.atualizar_erro_temperatura(text)
        
    def atualizar_erro_temperatura(self, caixa_selecionada):
        if not caixa_selecionada:
            self.erro_temperatura_label.text = "Erro de Temperatura: N/A (Selecione uma caixa)"
            return
    
        # Use a função buscar_informacoes_caixa para obter a temperatura da caixa selecionada
        temperatura_caixa = self.buscar_informacoes_caixa(caixa_selecionada)
    
        # Use o valor da temperatura medida no Node-RED
        temperatura_medida = self.temperatura_medida
    
        if temperatura_caixa is not None:
            # Calcule o erro de temperatura
            erro_temperatura = float(temperatura_caixa) - float(temperatura_medida)
    
            # Exiba o erro de temperatura
            self.erro_temperatura_label.text = f"Erro de Temperatura: {erro_temperatura} °C"
        else:
            self.erro_temperatura_label.text = f"Erro de Temperatura: N/A (Caixa '{caixa_selecionada}' não encontrada no banco de dados)"

    def buscar_informacoes_caixa(self, id_caixa):
        conn = sqlite3.connect('database.db')  # Substitua 'database.db' pelo nome do seu banco de dados
        cursor = conn.cursor()
        
        # Consulte o banco de dados para obter as informações da caixa com base no ID
        cursor.execute("SELECT temperatura FROM caixas WHERE id=?", (id_caixa,))
        resultado = cursor.fetchone()
        
        conn.close()

        if resultado:
            return resultado[0]  # Retorna a temperatura da caixa
        else:
            return None  # Retorna None se o ID da caixa não for encontrado



    def init_mqtt_led(self, mqtt_topic):
        self.led_client = mqtt.Client()
        self.led_client.on_connect = self.on_connect_led
        self.led_client.on_message = self.on_message_led
        self.connect_mqtt(self.led_client, mqtt_topic)

    def init_mqtt_pot(self, mqtt_topic):
        self.pot_client = mqtt.Client()
        self.pot_client.on_connect = self.on_connect_pot
        self.pot_client.on_message = self.on_message_pot
        self.connect_mqtt(self.pot_client, mqtt_topic)

    def init_mqtt_temp(self, mqtt_topic):
        self.temp_client = mqtt.Client()
        self.temp_client.on_connect = self.on_connect_temp
        self.temp_client.on_message = self.on_message_temp
        self.connect_mqtt(self.temp_client, mqtt_topic)

    def connect_mqtt(self, client, mqtt_topic):
        mqtt_broker_host = "127.0.0.1"
        mqtt_broker_port = 1883

        client.connect(mqtt_broker_host, mqtt_broker_port, 60)
        client.loop_start()
        client.subscribe(mqtt_topic)

    def on_connect_led(self, client, userdata, flags, rc):
        print(f"Conectado ao tópico LED com código de resultado: {rc}")

    def on_message_led(self, client, userdata, msg):
        mensagem_mqtt = msg.payload.decode()
        print(f"Recebido mensagem no tópico LED: {mensagem_mqtt}")
        self.led_label.text = f"LED Status: {mensagem_mqtt}"

    def on_connect_pot(self, client, userdata, flags, rc):
        print(f"Conectado ao tópico Potenciômetro com código de resultado: {rc}")

    def on_message_pot(self, client, userdata, msg):
        mensagem_mqtt = msg.payload.decode()
        print(f"Recebido mensagem no tópico Potenciômetro: {mensagem_mqtt}")
        self.potentiometer_label.text = f"Potentiometer: {mensagem_mqtt}"

    def on_connect_temp(self, client, userdata, flags, rc):
        print(f"Conectado ao tópico Temperatura com código de resultado: {rc}")

    # Atualize a temperatura medida quando uma nova leitura é recebida no MQTT
    def on_message_temp(self, client, userdata, msg):
        mensagem_mqtt = msg.payload.decode()
        self.temperatura_medida = float(mensagem_mqtt)  # Atribui o valor de mensagem_mqtt a temperatura_medida
        self.temperature_label.text = f"Temperature: {mensagem_mqtt} °C"  # Atualiza o rótulo com o valor recebido
        
    def logout(self, instance):
        self.manager.current = "login"



class MedicoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.display_data_button = Button(text="Mostrar Dados", on_press=self.display_data)
        self.layout.add_widget(self.display_data_button)
        self.data_display = Label(text="")
        self.layout.add_widget(self.data_display)
        self.edit_data_label = Label(text="Editar Dados:")
        self.layout.add_widget(self.edit_data_label)
        self.edit_id = TextInput(hint_text="ID (opcional)")
        self.layout.add_widget(self.edit_id)
        self.edit_objeto = TextInput(hint_text="Objeto")
        self.layout.add_widget(self.edit_objeto)
        self.edit_temperatura = TextInput(hint_text="Temperatura Segura")
        self.layout.add_widget(self.edit_temperatura)
        self.edit_button = Button(text="Editar", on_press=self.edit_data)
        self.layout.add_widget(self.edit_button)
        self.logout_button = Button(text="Logout", on_press=self.logout)
        self.layout.add_widget(self.logout_button)
        self.add_widget(self.layout)
        
        # Adicione um botão para mudar para a tela "Operador"
        self.operador_button = Button(text="Ir para Operador")
        self.operador_button.bind(on_press=self.ir_para_operador)
        self.layout.add_widget(self.operador_button)

    def ir_para_operador(self, instance):
        self.manager.current = "operador"

    def display_data(self, instance):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM caixas")
        data = cursor.fetchall()
        if data:
            display_text = "Dados no Banco de Dados:\n"
            for row in data:
                display_text += f"ID: {row[0]}, Objeto: {row[1]}, Temperatura: {row[2]}\n"
            self.data_display.text = display_text
        else:
            self.data_display.text = "Nenhum dado encontrado no banco de dados."

    def edit_data(self, instance):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        id_to_edit = self.edit_id.text.strip()
        objeto = self.edit_objeto.text
        temperatura = self.edit_temperatura.text

        if not id_to_edit:
            cursor.execute("INSERT INTO caixas (objeto, temperatura) VALUES (?, ?)", (objeto, temperatura))
        else:
            cursor.execute("UPDATE caixas SET objeto=?, temperatura=? WHERE id=?", (objeto, temperatura, id_to_edit))
        conn.commit()
        self.edit_id.text = ""
        self.edit_objeto.text = ""
        self.edit_temperatura.text = ""

    def logout(self, instance):
        self.manager.current = "login"


class MyApp(App):
    def build(self):
        db = Database()
        sm = ScreenManager()
        countdown_screen = CountdownScreen(name="countdown")
        ls = LoginScreen(db, name="login")
        cs = CadastroScreen(db, name="cadastro")
        os = OperadorScreen(name="operador")
        ms = MedicoScreen(name="medico")
        sm.add_widget(countdown_screen)
        sm.add_widget(ls)
        sm.add_widget(cs)
        sm.add_widget(os)
        sm.add_widget(ms)
        sm.current = "countdown"
        return sm


if __name__ == '__main__':
    MyApp().run()
   
