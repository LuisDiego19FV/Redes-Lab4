import sys
import math
import socket 
import pickle
import threading as th
from time import sleep
from operator import itemgetter

# Host and port of bridge
HOST = '127.0.0.1'
PORT = 9999
# HOST = 'redesgameserver.eastus.cloudapp.azure.com' 
# PORT = 22

# Time wait multiplier
TIME_MULT = 1

# Arguments: id, neighbors and weight of the node
args = sys.argv

# Error in number of args
if len(args) != 4:
    print("Error in number of args")
    exit()

# Error in structure of args
try:
    n_id = str(args[1])
    n_neighbors = args[2].split(",")
    n_w = [int(i) for i in args[3].split(",")]

    network_table = {}
    network_table[n_id] = [(n_neighbors[i], n_w[i]) for i in range(len(n_w))]

    print("Node: " + n_id)
except:
    print("Error in structure of args")
    exit()

# Init node
node = {"id":n_id, "neighbors":n_neighbors, "weights":n_w}

# Global stop for threads & table sync
stop_threads = False
stop_table_sync = False


class Node:
  
    def __init__(self, data, indexloc = None):
        self.data = data
        self.index = indexloc
        
class Graph:
    @classmethod
    def create_from_nodes(self, nodes):
        return Graph(len(nodes), len(nodes), nodes)

    def __init__(self, row, col, nodes = None):
        self.adj_mat = [[0] * col for _ in range(row)]
        self.nodes = nodes
        for i in range(len(self.nodes)):
            self.nodes[i].index = i

    def connect_dir(self, node1, node2, weight):
        node1, node2 = self.get_index_from_node(node1), self.get_index_from_node(node2)
        self.adj_mat[node1][node2] = weight
  
    def connect(self, node1, node2, weight):
        self.connect_dir(node1, node2, weight)
        self.connect_dir(node2, node1, weight)

    def connections_from(self, node):
        node = self.get_index_from_node(node)
        return [(self.nodes[col_num], self.adj_mat[node][col_num]) for col_num in range(len(self.adj_mat[node])) if self.adj_mat[node][col_num] != 0]
   
    def get_index_from_node(self, node):
        if not isinstance(node, Node) and not isinstance(node, int):
            raise ValueError("node must be an integer or a Node object")
        if isinstance(node, int):
            return node
        else:
            return node.index

# def state_message(mensaje, destino, original):

# Distance vector table creation
def vector_table_creation():
    # Prepare neighbors
    neighbors = node["neighbors"]

    # Sent to each neighbor the flooding message
    for index, i in enumerate(neighbors):

        tmp_msg = network_table.copy()
        tmp_msg["action"] = "dist_table"
        tmp_msg["to_node"] = i
        tmp_msg = pickle.dumps(tmp_msg)

        # Connect to bridge
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect((HOST, PORT))

        # sent message and add delay
        s.sendall(tmp_msg)
        sleep(TIME_MULT * 0.01 * int(node["weights"][index]))

# def distance vector calculation
def distance_vector(route, destination, actual, avoid, weight = 0):

    neighbors = network_table[actual]

    shortest_way = []
    no_way = True

    for neighbor, w in neighbors:

        if neighbor in avoid:
            continue

        no_way = False
        
        if neighbor == destination:
            tmp_route = route + neighbor
            tmp_weight = weight + w
            shortest_way.append([tmp_route, tmp_weight])
            continue
        
        # Next section of route variables
        tmp_route = route + neighbor
        tmp_avoid = avoid.copy()
        tmp_avoid.append(neighbor)
        tmp_weight = weight + w

        # Get shortest way recursively
        recursive_way = distance_vector(tmp_route, destination, neighbor, tmp_avoid, tmp_weight)

        # Append possible way
        shortest_way.append(recursive_way)

    # No optimal route found for this branch
    if no_way or len(shortest_way) == 0:
        return ["", math.inf]

    # Calcullate tmp shortest way
    shortest_way = sorted(shortest_way, key=itemgetter(1))

    return shortest_way[0]

# Link state message function
def state_message(node):
    # Cuando mando a llamar a state_message en la linea 363  tira error que a no esta definida (el a de la linea 154) 

    graph = Graph.create_from_nodes([a,b,c,d,e,f,g,h])
    graph.connect(a,b,7)
    graph.connect(a,i,2)
    graph.connect(a,c,7)
    graph.connect(b,f,2)
    graph.connect(c,d,5)
    graph.connect(d,f,2)
    graph.connect(d,i,6)
    graph.connect(d,e,3)
    graph.connect(e,g,4)
    graph.connect(f,h,4)
    graph.connect(f,g,3)

    nodenum = graph.get_index_from_node(node)
    dist = [None] * len(graph.nodes)
    for i in range(len(dist)):
        dist[i] = [float("inf")]
        dist[i].append([graph.nodes[nodenum]])

    dist[nodenum][0] = 0
    queue = [i for i in range(len(graph.nodes))]
    seen = set()
    while len(queue) > 0:
        min_dist = float("inf")
        min_node = None
        for n in queue: 
            if dist[n][0] < min_dist and n not in seen:
                min_dist = dist[n][0]
                min_node = n
        
        queue.remove(min_node)
        seen.add(min_node)
        connections = graph.connections_from(min_node)
        for (node, weight) in connections:
            tot_dist = weight + min_dist
            if tot_dist < dist[node.index][0]:
                dist[node.index][0] = tot_dist
                dist[node.index][1] = list(dist[min_node][1])
                dist[node.index][1].append(node)
                if node.index == 1:
                    print("Sending message through path: " + "A" + ", total weight: " + str(weight))
                if node.index == 2:
                    print("Sending message through path: " + "B" + ", total weight: " + str(weight)) 
                if node.index == 3:
                    print("Sending message through path: " + "C" + ", total weight: " + str(weight)) 
                if node.index == 4:
                    print("Sending message through path: " + "D" + ", total weight: " + str(weight)) 
                if node.index == 5:
                    print("Sending message through path: " + "E" + ", total weight: " + str(weight)) 
                if node.index == 6:
                    print("Sending message through path: " + "F" + ", total weight: " + str(weight)) 
                if node.index == 7:
                    print("Sending message through path: " + "G" + ", total weight: " + str(weight)) 
                if node.index == 8:
                    print("Sending message through path: " + "H" + ", total weight: " + str(weight))          

        return dist

    # Connect to bridge
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((HOST, PORT))

    msg = pickle.dumps(msg)

    # sent message and add delay
    s.sendall(msg)
    sleep(TIME_MULT * 0.01)


# Distance vector message function
def vector_message(message, destination, actual, original):

    shortest_way = distance_vector(actual, destination, actual, avoid = [actual])

    if shortest_way[0] == "" or shortest_way[1] == math.inf:
        print("No path found")
        return 0

    print_way = ""
    for i in shortest_way[0]:
        print_way += i + " - "

    print("Sending message through path: " + print_way + ", total weight: " + str(shortest_way[1]))

    # Prepare message to sent
    msg = {"action":"sent_msg_dvector", "original_node":original,\
            "destination":destination, "msg":message}

    # Sent to
    next_node = shortest_way[0][1]
    msg["to_node"] = next_node

    # Connect to bridge
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((HOST, PORT))

    msg = pickle.dumps(msg)

    # sent message and add delay
    s.sendall(msg)
    sleep(TIME_MULT * 0.01)

# Flooding message function
def flooding_message(message, destination, original, from_nodes):
    # Prepare message to sent
    msg = {"action":"sent_msg_flood", "original_node":original,\
            "from_nodes":from_nodes, "destination":destination, "msg":message}
    
    # Prepare neighbors
    neighbors = node["neighbors"]

    # Sent to each neighbor the flooding message
    for index, i in enumerate(neighbors):
        
        # Avoid looping between nodes
        if i in from_nodes:
            continue

        tmp_msg = msg.copy()
        tmp_msg["to_node"] = i

        # Connect to bridge
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect((HOST, PORT))

        tmp_msg = pickle.dumps(tmp_msg)

        # sent message and add delay
        s.sendall(tmp_msg)
        sleep(TIME_MULT * 0.01 * int(node["weights"][index]))

# Thread function
def thread_function(index):

    # Global variable for stoping threads & table sync
    global stop_threads 
    global stop_table_sync

    # Menu to print later
    menu = '''
Node menu
    1. Sent message
    2. (Vector routing) Create route tables
    3. (Vector routing) Print route table
    4. Turn off node 
    99. Stop server
'''

    # Interface thread
    if index == 0:
        while stop_threads == False:
            # Menu input (mi)
            mi = input(menu)  

            # Check for int
            try:
                mi = int(mi)
            except:
                print("Enter option in menu")
                continue
            
            # Option 1, sent message
            if mi == 1:
                print("Choose a method for sending the message:")
                try:
                    meth = int(input("1. Flooding \n2. Distance Vector \n3. Link state \n") )
                except:
                    print("Enter option in menu")

                # By flooding algorithm
                if meth == 1:
                    original = node["id"]
                    message = str(input("Enter your message: ") )
                    destination = str(input("Enter message's destination: ") )

                    flooding_message(message, destination, original, [node["id"]])

                # By distance vector algorithm
                if meth == 2:
                    if len(network_table) == 1:
                        print("Router table needs syncronization")
                        print("Or network needs more than one node")
                    else:
                        original = node["id"]
                        message = str(input("Enter your message: ") )
                        destination = str(input("Enter message's destination: ") )

                        vector_message(message, destination, node["id"], original)

                # By distance vector algorithm
                if meth == 3:
                    if len(network_table) == 1:
                        print("Router table needs syncronization")
                        print("Or network needs more than one node")
                    else:
                        original = node["id"]
                        message = str(input("Enter your message: ") )
                        destination = str(input("Enter message's destination: ") )

                        a = Node("A")
                        b = Node("B")
                        c = Node("C")
                        d = Node("D")
                        e = Node("E")
                        f = Node("F")
                        g = Node("G")
                        h = Node("H")
                        i = Node("I")

                        state_message(a)

            # Option 2, sync network table
            elif mi == 2:
                print("\nsyncronizing...")
                vector_table_creation()

                timer = 0
                stop_table_sync = False

                while stop_table_sync == False and timer < 10 * TIME_MULT:
                    timer += 0.5
                    sleep(0.5)
                
                print("Routing Table syncronized")

            # Option 3, print routing table
            elif mi == 3:
                print("\nROUTING TABLE")
                for i in network_table.keys():
                    print(i + ": " + str(network_table[i]))

            # Option 4, kill threads
            elif mi == 4:
                stop_threads = True
                break

            elif mi == 99:
                msm = {"action":"kill_server"}
                msm = pickle.dumps(msm)

                # Sent message
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                s.connect((HOST, PORT))
                s.sendall(msm)
            
            else:
                print("Enter option in menu")

    # Communication with server thread
    else:
        while stop_threads == False:
            # Connect to server
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                s.connect((HOST, PORT))
            except:
                print("Error in server connection")
                stop_threads = False
                break
            
            # Sent connection and node to the bridge
            msg = {"action":"recognition", "id":node["id"]}
            msg = pickle.dumps(msg)
            s.sendall(msg)

            # Wait for server data
            try:
                data = s.recv(4096)
                data = pickle.loads(data)
            except:
                print("Disconnected from server")

            # Get message action
            try:
                act = data['action']
            except:
                continue
            
            # A message by flooding method received
            if act == "sent_msg_flood":
                
                # destination, message and from
                destination = data["destination"]
                message = data["msg"]
                from_nodes = data["from_nodes"]
                original = data["original_node"]

                # Data received by destination node
                if destination == node["id"]:
                    print("\nGOT MAIL")
                    print("From: Node_" + original)
                    print("Message: " + message)

                    way = ""
                    for i in from_nodes:
                        way += i + "->"

                    print(way + node["id"] + "\n")

                # Sent data to next nodes 
                else:
                    from_nodes.append(node["id"])
                    flooding_message(message, destination, original, from_nodes)

            # A message by dvector method received
            elif act == "sent_msg_dvector":
                # destination, message and from
                destination = data["destination"]
                message = data["msg"]
                original = data["original_node"]

                # Data received by destination node
                if destination == node["id"]:
                    print("\nGOT MAIL")
                    print("From: Node_" + original)
                    print("Message: " + message + "\n")

                    print(menu)

                else:
                    vector_message(message, destination, node["id"], original)

            # A message to sync routing table received 
            elif act == "dist_table":
                
                sent_to_all = False
                table_keys = network_table.keys()

                for i in data.keys():

                    if i == "action" or i == "to_node":
                        continue

                    if i not in table_keys:
                        network_table[i] = data[i]
                        sent_to_all = True
                    
                if sent_to_all:
                    sleep(TIME_MULT * 0.5)
                    vector_table_creation()
                else:
                    stop_table_sync = True

# Thread list
thread_list = []

# Start threads
for index in range(2):
    thread = th.Thread(target=thread_function, args=(index,))
    thread_list.append(thread)
    thread.start()

# Gather threads
for index, thread in enumerate(thread_list):
    thread.join()
    print("Thread " + str(index) + " joined" )




