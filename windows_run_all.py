# Para la prueba en clase
import os
import pathlib

node_a = "\"A\" \"B,I,C\" \"5,3,1\""
node_b = "\"B\" \"F,A\" \"8,5\""
node_c = "\"C\" \"A,D\" \"1,4\""
node_d = "\"D\" \"F,I,C,E\" \"3,7,4,9\""
node_e = "\"E\" \"D,G\" \"9,5\""
node_f = "\"F\" \"B,H,G,D\" \"8,3,4,3\""
node_g = "\"G\" \"F,E\" \"4,5\""
node_h = "\"H\" \"F\" \"3\""
node_i = "\"I\" \"A,D\" \"3,7\""

nodes = [node_a, node_b, node_c,\
        node_d, node_e, node_f, \
        node_g, node_h, node_i]

net_node = pathlib.Path("network_node.py").absolute()
net_node = os.path.join(net_node)

print(net_node)

for i in nodes:
    os.system('start cmd.exe /k python \"' + str(net_node) + "\" " + i)