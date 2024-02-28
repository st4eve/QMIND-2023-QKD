import socket
import pickle

def send_file(host='127.0.0.1', port=12345, input_file=r"C:\Users\Owner\Desktop\FilePickleTest.docx"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        with open(input_file, 'rb') as f:
            content = f.read()
        data = pickle.dumps(content)
        s.sendall(data)
        print(f"File {input_file} has been sent.")

if __name__ == "__main__":
    send_file()