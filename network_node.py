import sys
import math
import socket 
import pickle
import threading as th
from time import sleep
from operator import itemgetter
from node_classes import Graph
from node_classes import Node

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


# def state_message for sending trough link state calulation
def state_message(msg, destination, original):
    # Get nodes from routing table
    tmp_nodes = []
    tmp_keys = []
    for i in network_table.keys():
        tmp_keys.append(i)
        tmp_nodes.append(Node(str(i)))

    # Create graph
    graph = Graph.create_from_nodes(tmp_nodes)

    # Connect each node according to the routing table specs
    for i in network_table.keys():
        node_pivot = tmp_nodes[tmp_keys.index(i)]
        connections = network_table[i]

        for j in connections:
            node_path = tmp_nodes[tmp_keys.index(j[0])]
            weight = j[1]

            graph.connect(node_pivot, node_path, weight)

    # This node
    node_pivot = tmp_nodes[0]

    # Node number and list for possible paths
    nodenum = graph.get_index_from_node(node_pivot)
    dist = [None] * len(graph.nodes)

    # Start every path with a infinity
    for i in range(len(dist)):
        dist[i] = [float("inf")]
        dist[i].append([graph.nodes[nodenum]])

    # Set queue
    dist[nodenum][0] = 0
    queue = [i for i in range(len(graph.nodes))]
    seen = set()

    # Search shortest possibles paths
    while len(queue) > 0:
        min_dist = float("inf")
        min_node = None

        # For node in queue
        for n in queue: 
            if dist[n][0] < min_dist and n not in seen:
                min_dist = dist[n][0]
                min_node = n
        
        queue.remove(min_node)
        seen.add(min_node)
        connections = graph.connections_from(min_node)

        # Get connections
        for (tmp_node, weight) in connections:
            tot_dist = weight + min_dist
            if tot_dist < dist[tmp_node.index][0]:
                dist[tmp_node.index][0] = tot_dist
                dist[tmp_node.index][1] = list(dist[min_node][1])
                dist[tmp_node.index][1].append(tmp_node)  
    
    dist = sorted(dist, key=itemgetter(0))     

    shortest_way = None
    for i in dist:
        exit_loop = False

        for j in i[1]:
            if j.data == destination:
                shortest_way = i
                exit_loop = True
                break

        if exit_loop:
            break

    # Exit condition
    if dist[0][0] == math.inf or shortest_way == None:
        print("No path found")
        return 0

    # Get node to sent message trough
    to_node = str(shortest_way[1][1].data)  

    # Prepare message to sent
    msg = {"action":"sent_msg_lstate", "original_node":original, \
            "destination":destination, "msg":msg, "to_node":to_node}

    msg = pickle.dumps(msg)

    # Connect to bridge
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((HOST, PORT))

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
    2. Create Routing tables (using vector method)
    3. Print Routing table
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
                meth = 0
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
                        print("Routing table needs syncronization")
                        print("Or network needs more than one node")
                    else:
                        original = node["id"]
                        message = str(input("Enter your message: ") )
                        destination = str(input("Enter message's destination: ") )

                        vector_message(message, destination, node["id"], original)

                # By distance vector algorithm
                if meth == 3:
                    if len(network_table) == 1:
                        print("Routing table needs syncronization")
                        print("Or network needs more than one node")
                    else:
                        original = node["id"]
                        message = str(input("Enter your message: ") )
                        destination = str(input("Enter message's destination: ") )

                        state_message(message, destination, node["id"])

            # Option 2, sync network table
            elif mi == 2:
                print("\nsyncronizing...")
                vector_table_creation()

                timer = 0
                stop_table_sync = False

                while stop_table_sync == False and timer < 15 * TIME_MULT:
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
                    print("\nGOT MAIL - Delivered by Flooding")
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
                    print("\nGOT MAIL - Delivered by Distance Vectoring")
                    print("From: Node_" + original)
                    print("Message: " + message + "\n")

                    print(menu)

                else:
                    vector_message(message, destination, node["id"], original)

            # A message by link state method received
            elif act == "sent_msg_lstate":
                # destination, message and from
                destination = data["destination"]
                message = data["msg"]
                original = data["original_node"]

                # Data received by destination node
                if destination == node["id"]:
                    print("\nGOT MAIL - Delivered by Link State")
                    print("From: Node_" + original)
                    print("Message: " + message + "\n")

                    print(menu)

                else:
                    state_message(message, destination, original)

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




