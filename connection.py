import socket
import threading

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            break
        print("Received data: " + data)

        # Add your code here to process the received data

    client_socket.close()

def start_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(5)
    print(f"Server is listening on {ip}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address[0]}:{client_address[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

def start_client(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    while True:
        message = input("Enter a message to send: ")
        client_socket.send(message.encode('utf-8'))

if __name__ == "__main__":
    # Change these values for each Raspberry Pi
    pi1_ip = 'PI1_IP'
    pi2_ip = 'PI2_IP'

    pi1_port = 12345
    pi2_port = 12346

    # Start server and client threads on each Pi
    pi1_server_thread = threading.Thread(target=start_server, args=(pi1_ip, pi1_port))
    pi1_client_thread = threading.Thread(target=start_client, args=(pi2_ip, pi2_port))

    pi2_server_thread = threading.Thread(target=start_server, args=(pi2_ip, pi2_port))
    pi2_client_thread = threading.Thread(target=start_client, args=(pi1_ip, pi1_port))

    pi1_server_thread.start()
    pi1_client_thread.start()

    pi2_server_thread.start()
    pi2_client_thread.start()
