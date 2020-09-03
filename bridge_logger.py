def write_to_file(file, message, to_node, destination):
    try:
        with open("logs/" + file, 'a') as outfile:
            outfile.write("Server redirecting message with " + str(file)+ " method:\n")
            outfile.write(" Msg: " + str(message) + "\n")
            outfile.write(" Destination: " + str(destination) + "\n")
            outfile.write(" Redirected to:" + str(to_node) + "\n")
    except:
        print("Error loggin")


def reset_all_files():
    file_list = ["log_flooding.txt", "log_dvector.txt", "log_lstate.txt"]
    try:
        for i in file_list:
            file = open("logs/" + i,"r+")
            file. truncate(0)
            file. close()
    except:
        print("Error loggin")