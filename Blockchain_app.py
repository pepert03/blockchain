import BlockChain
from threading import Semaphore ,Thread
import time
from flask import Flask, jsonify, request
from argparse import ArgumentParser
from datetime import datetime
import json
import platform
import requests

# semaforo para no pisarse con el escritor de la cadena al añadir un bloque
# y el escritor de la cadena en archivo json
backup = Semaphore(1) 

# Instancia del nodo
app =Flask(__name__)

# Instanciacion de la aplicacion
blockchain =BlockChain.Blockchain()
nodos_red = set() 

# Para saber mi ip
mi_ip = '172.20.10.6'


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
    'chain': [b.toDict() for b in blockchain.bloques]
    }
    response['longitud']= len(response['chain']) 
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
        conflicto= resuelve_conflictos()
        if conflicto:
            response ={
            'mensaje': "Se ha encontrado un conflicto. La cadena ha sido actualizada"
            }
            return jsonify(response), 201    
        if blockchain.integra_bloque(new,new_hash):
            response ={
            'mensaje': "Nuevo bloque minado",
            "bloque":new.toDict()
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


@app.route('/nodos/registrar', methods=['POST'])
def registrar_nodos_completo():
    values =request.get_json()
    global blockchain
    global nodos_red
    global puerto
    nodos_nuevos =values.get('direccion_nodos')
    if nodos_nuevos is None:
        return "Error: No se ha proporcionado una lista de nodos", 400
    all_correct =True
    for nodo in nodos_nuevos:
        # almacenar los nodos recibidos en nodos_red y enviará a dichos nodos la blockchain del nodo al que se han unido
        nodos_red.add(nodo)
        lista_nodos = list((nodos_red-{nodo}) | {f'http://{mi_ip}:{puerto}'})
        blockchain_2 = blockchain.toDict()
        data = {'chain': blockchain_2, 'nodos_direcciones': lista_nodos}
        response = requests.post(f'{nodo}/nodos/registro_simple', json=data)


    if all_correct:
        response ={
        'mensaje': 'Se han incluido nuevos nodos en la red',
        'nodos_totales': list(nodos_red)+[f'http://{mi_ip}:{puerto}']
        }
    else:
        response ={
            'mensaje': 'Error notificando el nodo estipulado',
            }
    return jsonify(response), 201



@app.route('/nodos/registro_simple', methods=['POST'])
def registrar_nodo_actualiza_blockchain():
    global blockchain
    read_json =request.get_json()
    nodes_addreses =read_json.get("nodos_direcciones")

    if nodes_addreses is None:
        response={
        'mensaje': 'Error: No se ha proporcionado una lista de nodos'
        }
        return jsonify(response), 400
    
    for node in nodes_addreses:
        nodos_red.add(node)

    blockchain_2 = read_json.get("chain")
    if blockchain_2 is None:
        response={
        'mensaje': 'Error: No se ha proporcionado una blockchain'
        }
        return jsonify(response), 400
    
    blockchain = blockchain.fromDict(blockchain_2)


    response={
    'mensaje': 'Se ha actualizado la blockchain',
    'nodos_totales': list(nodos_red)
    }
    return jsonify(response), 200


def resuelve_conflictos():
    global blockchain
    longitud_actual = len(blockchain.bloques)
    for nodo in nodos_red:
        print("COMPROBANDO NODO",nodo)
        response =requests.get(str(nodo) +'/chain')
        print(response.status_code)
        if response.status_code == 200:

            longitud = response.json()['longitud']
            chain_json = response.json()['chain']
            assert longitud == len(chain_json)
            chain=[ BlockChain.Bloque(0,[],0,0).fromDict(block) for block in chain_json]
            if longitud>longitud_actual:
                print("FUCK YOU ALL")
            if longitud > longitud_actual and blockchain.es_valida(chain):
                longitud_actual = longitud
    print(longitud_actual, len(blockchain.bloques))
    if longitud_actual > len(blockchain.bloques):
        blockchain.bloques = [ BlockChain.Bloque().fromDict(block) for block in chain]
        return True
    return False


if __name__ =='__main__':
    parser =ArgumentParser()
    parser.add_argument('-p', '--puerto', default=5000, type=int, help='puerto   para escuchar')
    args =parser.parse_args()
    puerto =args.puerto
    th1 = Thread ( target = copia_de_seguridad )
    app.run(host=mi_ip, port=puerto)
    th1 . start ()
    th1 . join ()
    
    
