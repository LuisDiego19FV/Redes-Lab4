import sys
import socket 
import pickle
import threading as th
from time import sleep

# Host and port of bridge
HOST = '127.0.0.1'
PORT = 9999
# HOST = 'redesgameserver.eastus.cloudapp.azure.com' 
# PORT = 22

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
    print("Node: " + n_id)
except:
    print("Error in structure of args")

# Init node
node = {"id":n_id, "neighbors":n_neighbors, "weights":n_w}

# Global stop for threads
stop_threads = False

# Flooding function
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
        sleep(0.01 * int(node["weights"][index]))

# Thread function
def thread_function(index):

    # Global variable for stoping threads
    global stop_threads 

    # Menu to print later
    menu = '''\n  Node menu \n  1. Sent message \n  2. Turn off node \n  '''

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
                meth = int(input("1. Flooding\n") )

                # By flooding algorithm
                if meth == 1:
                    original = node["id"]
                    message = str(input("Enter your message: ") )
                    destination = str(input("Enter message's destination: ") )

                    flooding_message(message, destination, original, [node["id"]])

            # Option 2, kill threads
            elif mi == 2:
                stop_threads = True
                break
            
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
            data = s.recv(4096)
            data = pickle.loads(data)

            # Get message action
            try:
                act = data['action']
            except:
                continue
            
            # A message was sent by flooding method
            if act == "sent_msg_flood":
                
                # destination, message and from
                destination = data["destination"]
                message = data["msg"]
                from_nodes = data["from_nodes"]

                # Data received by destination node
                if destination == node["id"]:
                    print("\nGOT MAIL")
                    print(message)

                    way = ""
                    for i in from_nodes:
                        way += i + "->"

                    print(way + node["id"] + "\n")

                # Sent data to next nodes 
                else:
                    original = data["original_node"]
                    from_nodes.append(node["id"])
                    flooding_message(message, destination, original, from_nodes)


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




