import socket
import threading
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", 5000))
server.listen()
print("MSOLIDCHAT SERVER STARTED...")
clients = []
usernames = []
def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode())
        except:
            pass

def remove_client(client):
    if client in clients:
        index = clients.index(client)
        username = usernames[index]
        clients.remove(client)
        usernames.remove(username)
        broadcast(f"{username} left the chat.")
        print(f"{username} disconnected.")
        client.close()

def handle_client(client):
    while True:
        try:
            message = client.recv(1024).decode()
            if not message:
                remove_client(client)
                break
            if message.lower() == "exit":
                remove_client(client)
                break
            index = clients.index(client)
            username = usernames[index]
            full_message = f"{username}: {message}"
            print(full_message)
            broadcast(full_message)
        except:
            remove_client(client)
            break

while True:
    client, address = server.accept()
    print(f"CONNECTED TO: {address}")
    client.send("USERNAME".encode())
    username = client.recv(1024).decode()
    usernames.append(username)
    clients.append(client)
    print(f"{username} joined the chat.")
    broadcast(f"{username} joined the chat.")
    client.send("Connected to MSOLIDCHAT".encode())
    thread = threading.Thread(target=handle_client, args=(client,))
    thread.start()