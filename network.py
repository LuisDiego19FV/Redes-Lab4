import os
import pathlib

node_a = "\"A\" \"B,I,C\" \"7,2,7\""
node_b = "\"B\" \"F,A\" \"2,7\""
node_c = "\"C\" \"A,D\" \"7,5\""
node_d = "\"D\" \"F,I,C,E\" \"2,6,5,3\""
node_e = "\"E\" \"D,G\" \"3,4\""
node_f = "\"F\" \"B,H,G,D\" \"2,4,3,2\""
node_g = "\"G\" \"F,E\" \"3,4\""
node_h = "\"H\" \"F\" \"4\""
node_i = "\"I\" \"A,D\" \"2,6\""

nodes = [node_a, node_b, node_c,\
        node_d, node_e, node_f, \
        node_g, node_h, node_i]

net_node = pathlib.Path("network_node.py").absolute()
net_node = os.path.join(net_node)

print(net_node)

for i in nodes:
    os.system('start cmd.exe /k python \"' + str(net_node) + "\" " + i)