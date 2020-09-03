import socket
import pickle 

# host and port to sent data
# HOST = '127.0.0.1'
# PORT = 9999
HOST = socket.gethostname() 
PORT = 22

# Default Timeout
socket.setdefaulttimeout(240)

# Mount host & listen
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

# Initial print
print("Listening...")

# Stores each node and it's connection
nodes = {}

# Store messages in stack
messages_to_sent = []

while True:

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
        nodes[str(data["id"])+"_status"] = True

        un_sent_messages = []
        for msg in messages_to_sent:
            print(msg)
            to_node = msg["to_node"]

            if nodes[to_node + "_status"]:
                msg = pickle.dumps(msg)
                conn_to_node = nodes[to_node]
                conn_to_node.sendall(msg)

                nodes[to_node + "_status"] = False

                print("renegate sent")
            else:
                un_sent_messages.append(msg)

        messages_to_sent = un_sent_messages

    # Redirect flooding message
    elif act == "sent_msg_flood":
        # Arguments
        original_node = data["original_node"]
        from_nodes = data["from_nodes"]
        destination = data["destination"]
        message = data["msg"]
        to_node = data["to_node"]

        # Complete message
        msg = {"action":"sent_msg_flood", "original_node":original_node,\
            "from_nodes":from_nodes, "destination":destination, "msg":message, "to_node":to_node}

        # Sent message to node if connection is active
        if  nodes[to_node + "_status"]:
            msg = pickle.dumps(msg)
            conn_to_node = nodes[to_node]
            conn_to_node.sendall(msg)

            nodes[to_node + "_status"] = False
        else:
            messages_to_sent.append(msg)

    # Redirect dvector message
    elif act == "sent_msg_dvector":
        # Arguments
        original_node = data["original_node"]
        to_node = data["to_node"]
        destination = data["destination"]
        message = data["msg"]

        # Complete message
        msg = {"action":"sent_msg_dvector", "original_node":original_node,\
            "destination":destination, "msg":message, "to_node":to_node}

        # Sent message to node if connection is active
        if  nodes[to_node + "_status"]:
            msg = pickle.dumps(msg)
            conn_to_node = nodes[to_node]
            conn_to_node.sendall(msg)

            nodes[to_node + "_status"] = False
        else:
            messages_to_sent.append(msg)

    # Redirect lstate message
    elif act == "sent_msg_lstate":
        # Arguments
        original_node = data["original_node"]
        to_node = data["to_node"]
        destination = data["destination"]
        message = data["msg"]

        # Complete message
        msg = {"action":"sent_msg_lstate", "original_node":original_node,\
            "destination":destination, "msg":message, "to_node":to_node}
        msg = pickle.dumps(msg)

        # Sent message to node if connection is active
        if  nodes[to_node + "_status"]:
            msg = pickle.dumps(data)
            conn_to_node = nodes[to_node]
            conn_to_node.sendall(msg)

            nodes[to_node + "_status"] = False
        else:
            messages_to_sent.append(data)

    # Redirect table to node
    elif act == "dist_table":
        # Node to sent to
        to_node = data["to_node"]

        # Sent message to node if connection is active
        if  nodes[to_node + "_status"]:
            msg = pickle.dumps(data)
            conn_to_node = nodes[to_node]
            conn_to_node.sendall(msg)

            nodes[to_node + "_status"] = False
        else:
            messages_to_sent.append(data)

    # Kill server
    elif act == "kill_server":
        exit()