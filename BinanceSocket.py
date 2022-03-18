#!/usr/bin/env python3
import asyncio
from binance import AsyncClient, BinanceSocketManager
from binance.enums import *
import datetime


#from setting import API_KEY, SECRET_KEY

API_KEY = "123"
SECRET_KEY = "321"

def calcMedia(list,time):
    m = 0
    for i in range(len(list)):
        m += float(list[i])
    m = m/time
    return m

async def main():
    coin="ETHBUSD"
    client = await AsyncClient.create(API_KEY, SECRET_KEY)
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket
    ts = bm.trade_socket(coin)
    ks = bm.kline_socket(coin, interval=KLINE_INTERVAL_1MINUTE)
    ats = bm.aggtrade_socket(coin)
    ds = bm.depth_socket(coin)

    # then start receiving messages
    listVol = []
    listPrice = []
    listBaseAssetVolume = []
    listTraders = []

    async with ks as tscm:
         while True:
             res = await tscm.recv()
             date = res['k']['t']
             date = datetime.datetime.fromtimestamp(date / 1000)
             volume = res['k']['q']
             moeda = res['k']['s']
             close_price = res['k']['c']
             listVol.append(volume)
             listPrice.append(close_price)
             v = calcMedia(listVol,len(listVol))
             p = calcMedia(listPrice,len(listVol))

             if len(listVol) == 21:
                del listVol[0]
                del listPrice[0]
                print(coin,"Volume:",volume,"Media Volume: ",v," Media Price: ",p,"Price: ",close_price)
                if float(volume) > float(v):
                    if float(close_price) > float(p):
                        print("9.1 arriba")
                    
             else:
                if float(volume) > float(v):
                    if float(close_price) > float(p):
                        print("9.1 arriba")
                print(coin,"Volume:",volume,"Media Volume: ",v," Media Price: ",p,"Price: ",close_price)
           

    await client.close_connection()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
