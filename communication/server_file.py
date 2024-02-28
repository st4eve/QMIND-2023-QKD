import socket
import pickle

def start_server(host='127.0.0.1', port=12345, output_file=r"C:\Users\Owner\Desktop\Received Pickled File"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server started, listening on {host}:{port}")
        while True:  # Uncomment this line if you want to accept multiple connections
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                data = b''
                try:
                    while True:
                        packet = conn.recv(4096)
                        if not packet: break
                        data += packet
                    content = pickle.loads(data)
                    with open(output_file, 'wb') as f:
                        f.write(content)
                    print(f"File {output_file} has been received and saved.")
                except Exception as e:
                    print(f"An error occurred: {e}")
                # Uncomment the next line to keep the server running
                # continue  # Use continue if inside a loop to handle the next connection
                break  # Comment or remove this line if you want to accept multiple connections

if __name__ == "__main__":
    start_server()