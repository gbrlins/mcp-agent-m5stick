from m5stack import *
from m5ui import *
from uiflow import *
import unit
import time
import network
import socket
import json

# Configuração inicial da tela (Modo Paisagem/Landscape para melhor leitura de IPs)
lcd.setRotation(1) # Rotaciona para horizontal (160x80 pixels)
BG_COLOR = 0x1A1A1A   # Cinza escuro premium
ACCENT_COLOR = 0x00F5D4 # Verde-água/Teal moderno
TEXT_COLOR = 0xFFFFFF   # Branco para contraste
GREEN = 0x2ECC71        # Verde sucesso
AMBER = 0xF1C40F        # Amarelo/Laranja pronto
RED = 0xE74C3C          # Vermelho erro

# Garante o uso da fonte padrão compacta para evitar textos gigantes
lcd.font(lcd.FONT_Default)
lcd.clear(BG_COLOR)

# Inicializa o sensor ENV2 no Port A
env2_0 = unit.get(unit.ENV2, unit.PORTA)

# Inicializa Wi-Fi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect('Gabirol', '24082024')

# Tela de conexão inicial estilizada
lcd.print('CONECTANDO WIFI...', 5, 20, AMBER)
lcd.print('Aguarde...', 5, 40, TEXT_COLOR)

for i in range(20):
    if wifi.isconnected():
        break
    wait_ms(500)

if not wifi.isconnected():
    lcd.clear(BG_COLOR)
    lcd.print('WIFI ERROR!', 10, 25, RED)
    lcd.print('Reiniciando...', 10, 45, TEXT_COLOR)
    time.sleep(3)
    machine.reset()

# Conectado com sucesso! Coleta o IP obtido
ip = wifi.ifconfig()[0]
port = "5000"

# --- FUNÇÕES DE RENDERIZAÇÃO DA INTERFACE ---

def desenhar_layout_estatico():
    """Desenha a estrutura visual fixa (linhas de divisão e rótulos)"""
    lcd.clear(BG_COLOR)
    
    # Header (Barra Superior) - 16px de altura
    lcd.rect(0, 0, 160, 15, ACCENT_COLOR, ACCENT_COLOR)
    lcd.print("M5 STICK - ENV II", 4, 1, 0x000000)
    
    # Divisórias de quadrantes
    lcd.line(0, 15, 160, 15, 0x333333)       # Linha horizontal sob o Header
    lcd.line(82, 15, 82, 63, 0x333333)       # Linha vertical central separando Sensor e IP
    lcd.line(0, 63, 160, 63, 0x333333)       # Linha horizontal superior ao Rodapé
    
    # Rótulos de Rede (Lado Direito) - Espaçamento vertical exato de 14px
    lcd.print("WIFI IP:", 86, 19, ACCENT_COLOR)
    lcd.print(ip, 86, 33, GREEN)
    lcd.print("PORT:" + port, 86, 47, TEXT_COLOR)

def atualizar_leituras_tela(temp, hum, pres):
    """Atualiza as métricas lidas do sensor na metade esquerda da tela"""
    # Desenha um retângulo escuro sobre a área antiga do sensor para evitar sobreposição de letras
    lcd.rect(0, 16, 81, 46, BG_COLOR, BG_COLOR)
    
    # Exibe os dados formatados com espaçamento vertical simétrico de 14px
    lcd.print("T:" + str(round(temp, 1)) + " C", 4, 19, TEXT_COLOR)
    lcd.print("U:" + str(round(hum, 1)) + " %", 4, 33, TEXT_COLOR)
    lcd.print("P:" + str(round(pres, 0)), 4, 47, TEXT_COLOR)

def atualizar_status_requisicao(status_text, cor_status, total_requisicoes):
    """Atualiza a barra inferior de status e o totalizador de requisições atendidas"""
    # Limpa apenas a região do status e do contador no rodapé (y=64 a 80)
    lcd.rect(0, 64, 160, 16, BG_COLOR, BG_COLOR)
    
    # Status compacto para caber sem espremer ("ST:" em vez de "STATUS:")
    lcd.print("ST:", 4, 66, TEXT_COLOR)
    lcd.print(status_text, 28, 66, cor_status)
    
    # Imprime o contador de requisições alinhado à direita de forma segura
    lcd.print("REQ:" + str(total_requisicoes), 108, 66, ACCENT_COLOR)

# --- INICIALIZAÇÃO DO SERVIDOR COM TIMEOUT ---

desenhar_layout_estatico()

s = socket.socket()
# Define um timeout de 0.5 segundos para o socket.
# Assim, se ninguém chamar o IP do M5Stick em meio segundo, ele levanta uma exceção temporária,
# permitindo ao loop ler o sensor físico, atualizar a tela e voltar a escutar a rede.
s.settimeout(0.5)
s.bind(('0.0.0.0', int(port)))
s.listen(1)

req_count = 0

while True:
    # 1. Faz a leitura constante do sensor ENV2 para manter a tela viva
    temp = env2_0.temperature
    hum = env2_0.humidity
    pres = env2_0.pressure
    
    # Atualiza as métricas físicas no visor do M5Stick
    atualizar_leituras_tela(temp, hum, pres)
    
    try:
        # Tenta aceitar conexões entrantes (bloqueia por no máximo 500ms devido ao timeout)
        c, a = s.accept()
        
        # Conexão estabelecida! Atualiza o status temporariamente
        atualizar_status_requisicao("ENVIANDO", AMBER, req_count)
        r = c.recv(1024).decode()
        
        # Prepara o payload de resposta JSON
        data = {'temp': round(temp, 2), 'hum': round(hum, 2), 'pres': round(pres, 2)}
        body = json.dumps(data)
        
        resp = 'HTTP/1.1 200 OK\r\n'
        resp = resp + 'Content-Type: application/json\r\n'
        resp = resp + 'Content-Length: ' + str(len(body)) + '\r\n'
        resp = resp + '\r\n'
        resp = resp + body
        
        # Envia e encerra o canal socket
        c.sendall(resp.encode())
        c.close()
        
        # Sucesso! Incrementa contador e atualiza status na tela
        req_count += 1
        atualizar_status_requisicao("SUCESSO", GREEN, req_count)
        wait_ms(400) # Pequena pausa para o usuário ver o "SUCESSO" brilhando em verde
        
    except OSError:
        # Se entrar aqui, significa que ninguém conectou nos últimos 500ms.
        # Mantém o status como PRONTO para receber novas chamadas.
        atualizar_status_requisicao("PRONTO", AMBER, req_count)
