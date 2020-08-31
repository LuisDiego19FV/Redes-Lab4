import socket
import bitarray
import pickle

HOST = '127.0.0.1'
PORT = 9999

# HOST = 'redesgameserver.eastus.cloudapp.azure.com' 
# PORT = 22

msm = {"action":"kill_server"}
msm = pickle.dumps(msm)

# Sent message
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.connect((HOST, PORT))
s.sendall(msm)
