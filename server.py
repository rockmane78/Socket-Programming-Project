import socket
import threading

# Dictionnaires pour stocker les connexions
# clients = { "pseudo": socket_client }
clients = {}
# groupes = { "nom_groupe": [socket1, socket2] }
groupes = {}
verrou = threading.Lock()

HOST = '0.0.0.0'  # Écoute sur toutes les interfaces réseau
PORT = 12000

def gerer_client(client_socket, client_address):
    pseudo = None
    flux = client_socket.makefile('r', encoding='utf-8')
    try:
        # Le protocole utilise une ligne TCP par message.
        pseudo = flux.readline().strip()
        if not pseudo:
            return

        with verrou:
            if pseudo in clients:
                client_socket.sendall('[Erreur] Ce pseudo est deja utilise.\n'.encode('utf-8'))
                return
            clients[pseudo] = client_socket
        print(f"[+] {pseudo} s'est connecté depuis {client_address}")
        client_socket.sendall(f"[Info] Bienvenue {pseudo}. Utilisez /join <groupe>.\n".encode('utf-8'))

        # 2. Boucle de réception des messages du client
        while True:
            data = flux.readline().strip()
            if not data:
                break
            
            # Exemple de décodage selon le protocole
            # Format attendu : "PRIV:destinataire:message" ou "GROUP:nom_groupe:message"
            parties = data.split(':', 2)
            type_msg = parties[0]

            if type_msg == "PRIV" and len(parties) == 3:
                destinataire, msg = parties[1], parties[2]
                with verrou:
                    destinataire_socket = clients.get(destinataire)
                if destinataire_socket:
                    destinataire_socket.sendall(f"[Privé de {pseudo}] {msg}\n".encode('utf-8'))
                else:
                    client_socket.sendall('[Erreur] Destinataire introuvable.\n'.encode('utf-8'))

            elif type_msg == "JOIN_GROUP" and len(parties) >= 2:
                nom_groupe = parties[1]
                if nom_groupe not in groupes:
                    groupes[nom_groupe] = []
                if client_socket not in groupes[nom_groupe]:
                    groupes[nom_groupe].append(client_socket)
                client_socket.sendall(f"[Info] Vous avez rejoint le groupe {nom_groupe}\n".encode('utf-8'))

            elif type_msg == "GROUP" and len(parties) == 3:
                nom_groupe, msg = parties[1], parties[2]
                if nom_groupe in groupes:
                    for s in groupes[nom_groupe]:
                        if s != client_socket:  # Ne pas se renvoyer le message à soi-même
                            s.sendall(f"[{nom_groupe}] {pseudo}: {msg}\n".encode('utf-8'))

    except Exception as e:
        print(f"Erreur avec {pseudo}: {e}")
    finally:
        # Nettoyage lors de la déconnexion
        with verrou:
            if pseudo and clients.get(pseudo) is client_socket:
                del clients[pseudo]
            for membres in groupes.values():
                if client_socket in membres:
                    membres.remove(client_socket)
            print(f"[-] {pseudo} s'est déconnecté.")
        flux.close()
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