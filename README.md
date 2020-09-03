# Redes-Lab4
Lenguaje de programación:
- Python 3.6 < 

Librerias necesarias:
- socket
- operator
- pickle

Para correr el programa:
- Correr programa bridge.py en un servidor, por default escuchara el puerto 22. Si se desea cambiar el Host y Port abrá que modificar el código. Si se desea correr localmente se puede descomentar las lineas 12 y 13 de bridge.py y comentar las lineas 14 y 15.
- Correr el programa network_node.py (para correr en un servidor especifico o localmente se debera modificar el Host y Port en el código), el cual conecta al servidor un nodo dentro de la red, de la siguiente manera:
```
    python network_node.py [node_id] [neighbors_node_string] [neighbors_weights_string]
    
    Donde:
      node_id: es el nombre unico para dicho nodo
      neighbors_node_string: debe ser un string que indique los nodos vecinos cada uno separado por solo una coma
      neighbors_weights_string: indica los pesos para enviar mensajes a cada nodo con un string separado por solo
                                una coma. Estos deben de ir ordenados respectivamente a como se introdujo sus 
                                respectivos nodos en el parametro anterior.
    
    example:
    
    python network_node.py A "B,C,F" "1,2,7"
    
```
- Para ver que comandos se deberían de correr para crear la red propuesta en el Lab4.txt, cada uno en diferente terminal, chequear el archivo command_network.txt
- Si se tiene windows y se quiere correr todos los nodos para crear la red propuesta en el Lab4.txt dentro de la misma maquina, correr el programa network.py sin ningun.

