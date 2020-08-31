import socket
import pickle 

# host and port to sent data
HOST = '127.0.0.1'
PORT = 9999
# HOST = socket.gethostname() 
# PORT = 22

# Default Timeout
socket.setdefaulttimeout(60)

# Mount host & listen
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

# Initial print
print("Listening...")

# Stores each node and it's connection
nodes = {}

while True:

    # Connected nodes
    print(nodes)

    # Conection
    conn, addr = s.accept()
    print("\nConnection, Addr: " + str(addr) +"\n")

    # Received data
    try:
        data = conn.recv(4096)
        data = pickle.loads(data)
        data['action']  
    except:
        continue

    print("Message rec: " + str(data) + "\n")

    # Get action of message
    act = data["action"]

    # Recognition of connection
    if act == "recognition":
        nodes[str(data["id"])] = conn

    # Redirect flooding message
    elif act == "sent_msg_flood":
        # Arguments
        original_node = data["original_node"]
        from_nodes = data["from_nodes"]
        to_node = data["to_node"]
        destination = data["destination"]
        message = data["msg"]

        # Complete message
        msg = {"action":"sent_msg_flood", "original_node":original_node,\
            "from_nodes":from_nodes, "destination":destination, "msg":message}
        msg = pickle.dumps(msg)

        # Sent message to node
        conn_to_node = nodes[to_node]
        conn_to_node.sendall(msg)

    # Kill server
    elif act == "kill_server":
        exit()