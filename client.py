from socket import *

# Remplace par l'IP exacte de la machine serveur !
serverName = '10.8.93.243' 
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

sentence = input("Entre une phrase en minuscules : ")
clientSocket.send(sentence.encode())

modifiedSentence = clientSocket.recv(1024).decode()
print("Réponse du serveur :", modifiedSentence)

clientSocket.close()