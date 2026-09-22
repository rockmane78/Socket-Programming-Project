from socket import AF_INET, SOCK_STREAM, socket
import threading

serverName = '10.8.93.243' 
serverPort = 12000

def recevoir_messages(client_socket):
	flux = client_socket.makefile('r', encoding='utf-8')
	try:
		for message in flux:
			print(f"\n{message.rstrip()}\n> ", end='', flush=True)
	except OSError:
		pass
	finally:
		flux.close()

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

pseudo = input("Votre pseudo : ").strip()
clientSocket.sendall(f"{pseudo}\n".encode('utf-8'))

threading.Thread(target=recevoir_messages, args=(clientSocket,), daemon=True).start()
print("/join grp, /group grp mess, /priv pseudo mess, /q")

try:
	while True:
		commande = input("> ").strip()
		if not commande:
			continue
		if commande == '/q':
			break
		morceaux = commande.split(' ', 2)
		if commande.startswith('/join ') and len(morceaux) == 2:
			message = f"JOIN_GROUP:{morceaux[1]}"
		elif commande.startswith('/group ') and len(morceaux) == 3:
			message = f"GROUP:{morceaux[1]}:{morceaux[2]}"
		elif commande.startswith('/priv ') and len(morceaux) == 3:
			message = f"PRIV:{morceaux[1]}:{morceaux[2]}"
		else:
			print("Commande inconnue ou incomplete.")
			continue
		clientSocket.sendall(f"{message}\n".encode('utf-8'))
finally:
	clientSocket.close()
