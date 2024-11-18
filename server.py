import socket
import random
import signal
import sys
import time

def signal_handler(sig, frame):
    print("\nShutting down server...")
    sys.exit(0)

def get_random_name():
    first_parts = ["Lolzy", "FTP", "Ainol", "Woosah", "Hakimaya", "Exceltior", "MIST", "Satzu", "Marv", "Raiga"]
    second_parts = ["Potcovaru", "Toby", "Waycoure", "Accessory", "Zior", "JONAS", "Felix", "Ocho", "RABBI", "Syngod"]
    return random.choice(first_parts) + random.choice(second_parts)

def get_random_guild():
    prefixes = ["Legion", "Empire", "Knights", "Warriors", "Dragons", "Ravens", "Wolves", "Eagles", "Lions", "Phoenix"]
    suffixes = ["ofDoom", "ofLight", "ofShadow", "Elite", "Prime", "Alpha", "Omega", "Supreme", "Divine", "Immortal"]
    return random.choice(prefixes) + random.choice(suffixes)

def create_noise_packet():
    #generating random len noise packets to mimic the other packets
    length = random.randint(50, 200)
    return bytes([random.randint(0, 255) for _ in range(length)])

def create_kill_packet():
    #We generate the random header
    field1 = b'\x00\x00\x00\x00'  #0ing the first 4 bytes but could remove it ?//random.randint(0, 255) 
    field2 = bytes([random.randint(0, 255), random.randint(0, 255)])  #2byte
    field3 = bytes([random.randint(0, 255), random.randint(0, 255)])  #2
    field4 = bytes([random.randint(0, 255)]) #1 

    header = field1 + field2 + field3 + field4
    print(f"Generated kill packet with header: {header.hex()}")

    #encode our strings in utf16 which is what bdo uses
    def encode_string(s, total_length):
        encoded = s.encode('utf-16le')
        padding_length = total_length - len(encoded)
        padded = encoded + b'\x00' * padding_length
        return padded

    guild_name_player_killed = get_random_guild()
    char_name_player_killed = get_random_name()
    family_name_player_killed = get_random_name()
    char_name_killer = get_random_name()
    family_name_killer = get_random_name()

    fixed_length = 64

    guild_name_killed_bytes = encode_string(guild_name_player_killed, fixed_length)
    char_name_killed_bytes = encode_string(char_name_player_killed, fixed_length)
    family_name_killed_bytes = encode_string(family_name_player_killed, fixed_length)
    char_name_killer_bytes = encode_string(char_name_killer, fixed_length)
    family_name_killer_bytes = encode_string(family_name_killer, fixed_length)

    packet = (
        header +
        guild_name_killed_bytes +
        char_name_killed_bytes +
        char_name_killer_bytes +
        family_name_killed_bytes +
        family_name_killer_bytes
    )

    return packet


def start_server(host='0.0.0.0', port=12345):
    signal.signal(signal.SIGINT, signal_handler)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"Server listening on {host}:{port}")
    print("Press Ctrl+C to shutdown the server")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        
        try:
            for _ in range(10):
                if random.random() < 0.3:
                    packet = create_kill_packet()
                    print("Sending kill packet")
                else:
                    packet = create_noise_packet()
                    print("Sending noise packet")
                    
                client_socket.sendall(packet)
                time.sleep(random.uniform(0.1, 0.5))
                
        except (ConnectionAbortedError, ConnectionResetError):
            print(f"Client {addr} disconnected")
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_server()
