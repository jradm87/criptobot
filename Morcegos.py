#!/usr/bin/python 
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas
from multiprocessing import Process
import requests
import os
from datetime import datetime

api_key = "123"
api_secret = "456"
client = Client(api_key, api_secret)
moedas = []
Pros = []

def entra(coin,price):
	check = "pendente/" + coin
	price = (str(price))
	if not os.path.exists(check):
		f = open(check,"a")
		f.write(price)
		f.close()

def verifica(coin,value):
    pendente = "pendente/" + coin
    fechado = "fechado/" + coin
    value = float(value)
    loss = 0.01
    gain = 0.02
    now = datetime.now()
    dt_v= now.strftime("%d/%m/%Y %H:%M:%S")
    if not os.path.exists(fechado):
        if os.path.exists(pendente):
            with open(pendente) as f:
                pcompra = f.readlines()
            for p in pcompra:
                precision = 5
                decrease = float(float(p) * loss)
                increase = float(float(p) * gain)
                l = float(p) - decrease
                g = float(p) + increase
                l = float("{:0.0{}f}".format(l, precision))
                g = float("{:0.0{}f}".format(g, precision))
                
                if value > g:
                    print("ganhou")
					
                    #os.remove(pendente)
                    f = open(fechado,"a")
                    f.write(str(dt_v)+" - Compra: - "+str(p)+"                 - Venda: "+str(g)+"                                   - ganho")
                    f.close()
#                    send_msg(str(dt_v)+" - Compra: - "+str(p)+"                 - Venda: "+str(g)+"                                   - ganho")
                    
                if value < l:
                    print("perdeu: ",l,value)
                    f = open(fechado,"a")
                    f.write(str(dt_v)+" - Compra: "+str(p)+"                   - Valor atual: "+str(value)+"                         - Stop: "+str(l)+" perda")
                    f.close()
#                    send_msg(str(dt_v)+" - Compra: "+str(p)+"                   - Valor atual: "+str(value)+"                         - Stop: "+str(l)+" perda")

                continue

def histCoin(value,coin,status):
		now = datetime.now()
		status = str(status)
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
		if coin not in 'BCHABUSD':
			check = "history/" + coin
			f = open(check, "a")
			f.write(coin+" - "+dt_string+" - "+str(value)+" - "+status+"\n")
			f.close()

			check = "history.csv"
			f = open(check, "a")
			f.write(dt_string+";"+coin+";"+str(value)+";"+status+"\n")
			f.close()

#histCoin('33,2','FORTBUSD','Entra')
def send_msg(text):
   token = "TOKENTELEGRAM"
   chat_id = "CHATTELEGRAM"
   url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text 
   results = requests.get(url_req)
   #print(results.json)

def getData(coin):
	try:
	 data = pandas.read_json('https://api.binance.com/api/v3/klines?symbol='+coin+'&interval=1m')
	 
	except:
	 	print("Erro na moeda: ",coin)
	 	data = ""
	
	try:
		date = data[0][499]
	except:
		print("ERRO - Possível nova moeda encontrada",coin,len(data),"posições")
		check = "moeda/" + coin
		if not os.path.exists(check):
			f = open(check, "a")
			f.write("Moeda nova")
			f.close()
			send_msg("Possível nova moeda: "+coin)

	try:
		constructData(data,coin)
	except Exception as e: print(e)

def constructData(data,coin):
	size = len(data[0]) - 1
	lastPosition = size - 1
	calcData2(data,coin,lastPosition,size)

def calcData2(data,coin,lastPosition,size):
	periodo = 30
	posicao = lastPosition - periodo
	open_time = data[0][lastPosition]
	price_open = data[1][lastPosition]
	price_max = data[2][lastPosition]
	price_min = data[3][lastPosition]
	price_closed = data[4][lastPosition]
	volume = data[5][lastPosition]
	closed_time = data[6][lastPosition]
	quote_asset_volume = data[7][lastPosition]
	number_of_traders = data[8][lastPosition]
	taker_buy_base_asset_volume = data[9][lastPosition]
	taker_buy_quote_asset_volume = data[10][lastPosition]
	verifica(coin,price_closed)

	mediaVolume = 0
	for i in range(size, posicao, -1):
		mediaVolume += data[5].iloc[i]
	mediaVolume = mediaVolume / periodo
	
	MediaTraders = 0
	for i in range(size, posicao, -1):
		MediaTraders += data[8].iloc[i]
	MediaTraders = MediaTraders / periodo

	MediaMovel = 0
	for i in range(size, posicao, -1):
		MediaMovel += data[4].iloc[i]
	MediaMovel = MediaMovel / periodo
	
	invest = 0
	if volume > mediaVolume:
		invest += 1
	if number_of_traders > MediaTraders:
		invest += 1
	if price_closed > MediaMovel:
		invest += 1

	check = "alert/" + coin
	if invest == 3:
		histCoin(price_closed,coin,'Entra')
		print("investe",coin)
		print("Ultimos preços \n1: "+str(price_closed),"\n2: "+str(data[4][lastPosition- 1])+"\n3: "+str(data[4][lastPosition- 2])+"\n4: "+str(data[4][lastPosition- 3])+"\n5: "+str(data[4][lastPosition -4]))
		if not os.path.exists(check):
			f = open(check, "a")
			f.write("invest")
			f.close()
			send_msg("Possivel investimento: "+coin+" \nPreço médio: "+str(MediaMovel))
		entra(coin,price_closed)
			
			
	else:
		if os.path.exists(check):
			histCoin(price_closed,coin,'Sai')
			os.remove(check)



def getAtivos():
	exchange_info = client.get_exchange_info()
	for s in exchange_info['symbols']:
		ativo = s['symbol']
		if ativo.endswith(('BUSD')):
			try:
				moedas.append(ativo)
			except:
				print("erro ativo")

def logo():
	print("""\
   ____      _       _        ____        _   
  / ___|_ __(_)_ __ | |_ ___ | __ )  ___ | |_ 
 | |   | '__| | '_ \| __/ _ \|  _ \ / _ \| __|
 | |___| |  | | |_) | || (_) | |_) | (_) | |_ 
  \____|_|  |_| .__/ \__\___/|____/ \___/ \__|
              |_|                              V1.0 Junão

""")

def main():
	clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
	clearConsole()
	logo()
	getAtivos()
	print("Verificando mercados de criptomoedas, aguarde...")
	m=0
	for moeda in moedas:
		m += 1
		#print(moeda)
		p = Process(target=getData, args=(moeda,))
		Pros.append(p)
		p.start()
	for t in Pros:
		t.join()

	print("Tarefa concluída: ",m,"moedas processadas, aguarde novo processamento...")
		
main()
