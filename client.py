import socket
import threading
import os
import ssl

online = False


# receive part
def received():
    global online
    while online:
        try:
            msg = soc.recv(1024).decode("utf-8")
            if msg != "CLOSE":
                print(msg)
            elif msg == "CLOSE":
                print('Connection closed by the server')
                online = False
                soc.close()
                os._exit(1)
            else:
                continue
        except Exception as ex:
            print(ex)
            exit()


soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect((input("Enter the host ip address: "), int(input("Enter the port number of the hosting: "))))
try:
    ctx = ssl.create_default_context()
    # self-signed dev mode. For production remove the next two lines.
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    server_name = soc.getpeername()[0]  # use the connected host
    soc = ctx.wrap_socket(soc, server_hostname=server_name)  # TLS handshake now
    print("TLS enabled")
except Exception as e:
    print("TLS failed:", e)
if soc.recv(1024).decode("utf-8") == "DONE":
    print("connection established")
    online = True
    rec_thread = threading.Thread(target=received)
    rec_thread.start()

    # send part
    while online:
        try:
            signal = input()
            if signal != 'QUIT':
                soc.send(signal.encode("utf-8"))
            elif signal == 'QUIT':
                online = False
                soc.send("QUIT".encode("utf-8"))
                print("connection closed")
                os._exit(1)
            else:
                continue
        except Exception as e:
            print(e)
            exit()
