import json
import BlockChain
from datetime import datetime
blockchain =BlockChain.Blockchain()
data = {}
data['chain'] = [blockchain.bloques]
data['longitud'] = len(blockchain.bloques)
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
data['date'] = dt_string
with open('data.json', 'w') as file:
    json.dump(data, file, indent=4)