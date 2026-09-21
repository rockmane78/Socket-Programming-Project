import socket
import threading

# Dictionnaires pour stocker les connexions
# clients = { "pseudo": socket_client }
clients = {}
# groupes = { "nom_groupe": [socket1, socket2] }
groupes = {}

HOST = '0.0.0.0'  # Écoute sur toutes les interfaces réseau
PORT = 12000

def gerer_client(client_socket, client_address):
    pseudo = None
    try:
        # 1. Demander/recevoir le pseudo à la connexion
        pseudo = client_socket.recv(1024).decode('utf-8').strip()
        clients[pseudo] = client_socket
        print(f"[+] {pseudo} s'est connecté depuis {client_address}")

        # 2. Boucle de réception des messages du client
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            
            # Exemple de décodage selon le protocole
            # Format attendu : "PRIV:destinataire:message" ou "GROUP:nom_groupe:message"
            parties = data.split(':', 2)
            type_msg = parties[0]

            if type_msg == "PRIV" and len(parties) == 3:
                destinataire, msg = parties[1], parties[2]
                if destinataire in clients:
                    clients[destinataire].send(f"[Privé de {pseudo}] {msg}".encode('utf-8'))

            elif type_msg == "JOIN_GROUP" and len(parties) >= 2:
                nom_groupe = parties[1]
                if nom_groupe not in groupes:
                    groupes[nom_groupe] = []
                if client_socket not in groupes[nom_groupe]:
                    groupes[nom_groupe].append(client_socket)
                client_socket.send(f"[Info] Vous avez rejoint le groupe {nom_groupe}".encode('utf-8'))

            elif type_msg == "GROUP" and len(parties) == 3:
                nom_groupe, msg = parties[1], parties[2]
                if nom_groupe in groupes:
                    for s in groupes[nom_groupe]:
                        if s != client_socket:  # Ne pas se renvoyer le message à soi-même
                            s.send(f"[{nom_groupe}] {pseudo}: {msg}".encode('utf-8'))

    except Exception as e:
        print(f"Erreur avec {pseudo}: {e}")
    finally:
        # Nettoyage lors de la déconnexion
        if pseudo and pseudo in clients:
            del clients[pseudo]
            print(f"[-] {pseudo} s'est déconnecté.")
        client_socket.close()

def demarrer_serveur():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Serveur en écoute sur le port {PORT}...")

    while True:
        client_socket, client_address = server_socket.accept()
        # Création d'un thread dédié pour chaque nouveau client
        thread = threading.Thread(target=gerer_client, args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    demarrer_serveur()