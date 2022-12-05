import BlockChain
from uuid import uuid4
from threading import Semaphore ,Thread
import time
import random
import socket
from flask import Flask, jsonify, request
from argparse import ArgumentParser
from datetime import datetime
import json
import platform

# semaforo para no pisarse con el escritor de la cadena al añadir un bloque
# y el escritor de la cadena en archivo json
backup = Semaphore(1) 

# Instancia del nodo
app =Flask(__name__)

# Instanciacion de la aplicacion
blockchain =BlockChain.Blockchain()

# Para saber mi ip
mi_ip =socket.gethostbyname(socket.gethostname())


@app.route('/transacciones/nueva', methods=['POST'])
def nueva_transaccion():
    values =request.get_json()
    # Comprobamos que todos los datos de la transaccion estan
    required =['origen', 'destino', 'cantidad']
    if not all(k in values for k in required):
        return 'Faltan valores', 400
    # Creamos una nueva transaccion aqui
    blockchain.nueva_transaccion(values['origen'], values['destino'], values['cantidad'])
    index = len(blockchain.bloques) + 1 # la transaccion se guardará en el bloque siguiente (+1)
    response ={'mensaje': f'La transaccion se incluira en el bloque con indice {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def blockchain_completa():
    response ={
    # Solamente permitimos la cadena de aquellos bloques finales que tienen hash
    'chain': [b.toDict() for b in blockchain.bloques if b.hash_bloque is not None],
    }
    response['longitud']= len(response['chain']) # esto no se si está bn, pide la longitud de los bloques con hash, es decir, lo de encima
    return jsonify(response), 200

@app.route('/minar', methods=['GET'])
def minar():
    global backup,mi_ip
    
    # No hay transacciones
    if len(blockchain.transacciones) == 0:
        response ={
        'mensaje': "No es posible crear un nuevo bloque. No hay transacciones"
        }
    else:
        # se añade la transaccion del minero
        blockchain.nueva_transaccion('0', mi_ip, 1)
        # se obtiene el hash previo
        hash_previo = blockchain.bloques[-1].hash_bloque
        # nuevo bloque 
        new = blockchain.nuevo_bloque(hash_previo)
        # nuevo hash 
        new_hash = blockchain.prueba_trabajo(new)
        # para insertar el bloque tenemos que no solaparnos con el json que escribe la cadena cada 60s
        backup.acquire()
        if blockchain.integra_bloque(new,new_hash):
            response ={
            'mensaje': "Nuevo bloque minado \n"+ str(new.toDict())
            }
        backup.release()
    return jsonify(response), 200


def copia_de_seguridad(): # copia de seguridad que se ejecuta cada 60s para obtener la lsita de los bloques, su longitud, y la hora de la copia, en un fichero json
    global backup
    while True:
        time.sleep(60)
        backup.acquire()
        data = {}
        data['chain'] = [blockchain.bloques]
        data['longitud'] = len(blockchain.bloques)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        data['date'] = dt_string
        with open('data.json', 'w') as file:
            json.dump(data, file, indent=4)
        backup.release()

@app.route('/system', methods=['GET'])
def detallesnodo():
    detalles = {'maquina':platform.machine(),'nombre_sistema':platform.system(),'version':platform.vesion()}
    return detalles

if __name__ =='__main__':
    parser =ArgumentParser()
    parser.add_argument('-p', '--puerto', default=5000, type=int, help='puerto   para escuchar')
    args =parser.parse_args()
    puerto =args.puerto
    th1 = Thread ( target = copia_de_seguridad )
    app.run(host='0.0.0.0', port=puerto)
    th1 . start ()
    th1 . join ()
    
    
