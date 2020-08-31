import os
import pathlib

node_a = "\"A\" \"B,C\" \"7,20\""
node_b = "\"B\" \"A,C\" \"7,10\""
node_c = "\"C\" \"B,A\" \"10,20\""

nodes = [node_a, node_b, node_c]

net_node = pathlib.Path("network_node.py").absolute()
net_node = os.path.join(net_node)

print(net_node)

for i in nodes:
    os.system('start cmd.exe /k python \"' + str(net_node) + "\" " + i)