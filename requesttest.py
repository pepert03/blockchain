import requests
import json
# Cabecera JSON (comun a todas
nodo1="http://172.20.10.6:5000"
nodo2="http://172.20.10.6:5001"
cabecera ={'Content-type': 'application/json', 'Accept': 'text/plain'}
# datos transaccion
transaccion_nueva ={'origen': 'nodoA', 'destino': 'nodoB', 'cantidad': 10}

r =requests.post(nodo1+'/transacciones/nueva', data =json.dumps(
transaccion_nueva), headers=cabecera)
print(r.json())
r =requests.get(nodo1+'/minar')
print(r.json())
r =requests.get(nodo1+'/chain')
print(r.json())

r =requests.post(nodo1+'/nodos/registrar', data =json.dumps({'direccion_nodos': [nodo2]}), headers=cabecera)
print(r.json())