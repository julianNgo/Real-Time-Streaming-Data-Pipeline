from json import dumps
import json
import websocket
import datetime
from kafka import KafkaProducer
import time
# {"e":"trade","E":1667285388702,"s":"ETHUSDT","t":1003541951,"p":"1596.30000000","q":"0.23310000","b":11480035203,"a":11480035455,"T":1667285388702,"m":true,"M":true}

TOPIC_NAME_CONS = "binance-live-data-streaming"
BOOTSTRAP_SERVERS_CONS = '172.16.30.89:9092'
Coin_Symbol =  "btcusdt"

def ws_trades(sym): 
    socket = f'wss://stream.binance.com:9443/ws/{sym}@kline_1m'

    def on_message(wsapp,message):  
        json_message = json.loads(message)
        data = handle_trades(json_message)
        

    def on_error(wsapp,error):
        print(error)

    wsapp = websocket.WebSocketApp(socket, on_message=on_message, on_error=on_error)
    wsapp.run_forever()

def send_to_kafka(message):
    TOPIC_NAME_CONS = "binance-live-data-streaming"
    BOOTSTRAP_SERVERS_CONS = '172.16.30.89:9092'
    kafka_producer_obj = None
    kafka_producer_obj = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS_CONS,
                             value_serializer=lambda x: dumps(x).encode('utf-8'))
    kafka_producer_obj.send(TOPIC_NAME_CONS, message)

def handle_trades(json_message):
    TOPIC_NAME_CONS = "binance-live-data-streaming"
    BOOTSTRAP_SERVERS_CONS = '172.16.30.89:9092'
    message ={}
    print(json_message)
    date_time = datetime.datetime.fromtimestamp(json_message['E']/1000).strftime('%Y-%m-%d %H:%M:%S')
    message["Timestamp"] = date_time
    message["symbol"] = json_message['s']
    message["price"] = json_message['p']
    message["qty"] = json_message['q']
    kafka_producer_obj = None
    kafka_producer_obj = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS_CONS,
                             value_serializer=lambda x: dumps(x).encode('utf-8'))
    kafka_producer_obj.send(TOPIC_NAME_CONS, message)
    print("sent to broker: ", message)
    print("-------------------------------------------------------------------------")



if __name__ == "__main__":
    ws_trades('btcusdt')