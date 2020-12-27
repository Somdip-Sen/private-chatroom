import socket
import threading
import sys
import ssl

# connection  192.168.0.102
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind((input("Enter the host ip address: "), int(input("Enter the port number of the hosting: "))))
client_list = []  # store all the active clients
client_name = []  # store corresponding nicknames
FORMAT = 'utf-8'
soc.listen()
print("server online .... \n")


def broadcast(client, msg):
    if msg == "LEFT":
        for clients in client_list:
            if clients != client:
                clients.send(
                    f"[{str(client_name[client_list.index(client)])}] has left the chatroom...".encode(FORMAT))
    else:
        for clients in client_list:
            if clients != client:
                clients.send((f"[{str(client_name[client_list.index(client)])}]: " + msg).encode(FORMAT))


def look_for_client():
    while True:
        client, address = soc.accept()  # new client
        new_client = threading.Thread(target=accept_client, args=(client, address))
        new_client.start()


def accept_client(client, address):
    # client accepting
    print(f"client address {address} has been connected. Total client : {threading.active_count() - 2}")
    client.send("DONE".encode(FORMAT))  # confirmation
    client.send("Enter the nickname:".encode(FORMAT))
    name = client.recv(1024).decode(FORMAT)
    client_list.append(client)
    client_name.append(name)
    connected = True
    client.send("Nickname Registered....".encode(FORMAT))

    # wait for client's message
    while connected:
        try:
            msg = client.recv(1024).decode(FORMAT)
            if not msg:
                index = client_list.index(client)
                print(f"""[{client_name[index]}] {address} disconnected... 
Connected client : {threading.active_count() - 3}""")  # client left
                broadcast(client, "LEFT")
                client_name.pop(index)
                client_list.pop(index)
                break
            else:
                if msg != "QUIT":
                    broadcast(client, msg)

                elif msg == "QUIT":  # client wants to disconnect
                    index = client_list.index(client)
                    print(f"""[{client_name[index]}] {address} has left... 
Connected client : {threading.active_count() - 3}""")
                    broadcast(client, "LEFT")  # giving client's left notification
                    client_list.pop(index)  # remove client from client list

                    client_name.pop(index)  # remove client's name from name list
                    client.shutdown(socket.SHUT_WR)

                    client.close()
                    connected = False
                    sys.exit()  # Thread close

        except Exception as e:
            print(e)
            try:
                print(f"Remaining client : {threading.active_count() - 3}")
                connected = False
                sys.exit()  # Thread close
            except Exception as e:
                print(e)

try:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    _orig_accept_client = accept_client

    def _accept_client_tls(client, address):
        try:
            client = ctx.wrap_socket(client, server_side=True)
        except ssl.SSLError:
            try:
                client.close()
            finally:
                return
        return _orig_accept_client(client, address)

    accept_client = _accept_client_tls  # all future accepts are TLS-wrapped
    print("TLS enabled")
except Exception as e:
    print("TLS disabled:", e)
look_thread = threading.Thread(target=look_for_client)
look_thread.start()
look_thread.join()
