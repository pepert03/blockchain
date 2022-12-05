from ast import Dict, List
import hashlib
import json
import time
 
class Bloque:
    def __init__(self,indice,transacciones,timestamp,hash_previo,prueba=0):
        self.indice = indice
        self.transacciones = transacciones
        self.timestamp = timestamp
        self.hash_previo = hash_previo
        self.hash_bloque = None
        self.prueba = prueba
        if not self.hash_bloque:
            self.hash_bloque = self.calcular_hash()
   
    def calcular_hash(self): # calcula el hash de un bloque
        block_string =json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest() 

    def toDict(self):
        bloque= {
        'hash_bloque': self.hash_bloque,
        'hash_previo': self.hash_previo,
        'indice': self.indice,
        'timestamp': self.timestamp,
        'prueba': self.prueba,
        'transacciones': self.transacciones }
        return bloque  
   
class Blockchain(object):
    def __init__(self):
        self.dificultad = 4
        self.transacciones=[]
        self.bloques = [self.primer_bloque()]
 
    def primer_bloque(self):
        primer_bloque = Bloque(1,transacciones =[], timestamp = 0, hash_previo= 1)
        return primer_bloque
 
    def nuevo_bloque(self, hash_previo):
        bloque = Bloque(len(self.bloques)+1,self.transacciones,time.time(),hash_previo)
        return bloque

    def nueva_transaccion(self, origen, destino, cantidad):
        transaccion= {"origen": origen,"destino": destino, "cantidad": cantidad,"timestamp": time.time()}
        self.transacciones.append(transaccion)
        return len(self.bloques)+1
   
    def prueba_trabajo(self, bloque):
        new_hash = bloque.calcular_hash()
        while str(new_hash)[:self.dificultad] != '0'*self.dificultad:
            bloque.prueba += 1
            new_hash =bloque.calcular_hash()
        return str(new_hash)
 
    def prueba_valida(self, bloque, hash_bloque):
        if hash_bloque[:self.dificultad] == '0'*self.dificultad:
            if bloque.calcular_hash() == hash_bloque:
                return True
        return False
   
    def integra_bloque(self, bloque_nuevo, hash_prueba):
        if self.prueba_valida(bloque_nuevo,hash_prueba):
            if bloque_nuevo.hash_previo == self.bloques[-1].hash_bloque:
                self.bloques.append(bloque_nuevo)
                bloque_nuevo.hash_bloque = hash_prueba
                bloque_nuevo.transacciones = self.transacciones
                self.transacciones = []
                return True
        return False
    


if __name__ == '__main__':
    print()
