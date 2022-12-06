import requests
import json
# Cabecera JSON (comun a todas
nodo1="http://172.20.10.6:5006"
nodo2="http://172.20.10.6:5007"
cabecera ={'Content-type': 'application/json', 'Accept': 'text/plain'}
# datos transaccion
transaccion_nueva ={'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 10}

r =requests.post(nodo1+'/transacciones/nueva', data =json.dumps(
transaccion_nueva), headers=cabecera)
print("RESPUESTA TRANSACCCION NODO 1: ")
print(r.json())
r =requests.get(nodo1+'/minar')
print("RESPUESTA MINAR NODO 1: ")
print(r.json())
r =requests.get(nodo1+'/chain')
print("RESPUESTA CHAIN NODO 1: ")
print(r.json())

r =requests.post(nodo1+'/nodos/registrar', data =json.dumps({'direccion_nodos': [nodo2]}), headers=cabecera)
print("RESPUESTA REGISTRAR NODO 1: ")
print(r.json())

r = requests.get(nodo2+'/chain')
print("RESPUESTA CHAIN NODO 2: ")
print(r.json())

transaccion_nueva ={'origen': 'nodoD', 'destino': 'nodoR', 'cantidad': 4}

r =requests.post(nodo1+'/transacciones/nueva', data =json.dumps(
transaccion_nueva), headers=cabecera)
print("RESPUESTA TRANSACCCION NODO 1: ")
print(r.json())
r =requests.get(nodo1+'/minar')
print("RESPUESTA MINAR NODO 1: ")
print(r.json())

r =requests.post(nodo2+'/transacciones/nueva', data =json.dumps(
transaccion_nueva), headers=cabecera)
print("RESPUESTA TRANSACCCION NODO 2: ")
print(r.json())

r =requests.get(nodo2+'/minar')
print("RESPUESTA MINAR NODO 2: ")
print(r.json())

r =requests.get(nodo2+'/chain')
print("RESPUESTA CHAIN NODO 2: ")
print(r.json())