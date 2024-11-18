import socket
import binascii

def scan_for_kill_pattern(buffer):
    min_size = 9 + (64 * 5)  #prob need to change to actual size of the real packet I assumed header plus 64 bytes for each string 9 + 64*5

    if len(buffer) < min_size:
        return None, 0

    for i in range(len(buffer) - min_size + 1):
        window = buffer[i:i + min_size]
        header = window[:9]
        string_section = window[9:]

        valid_strings = True
        decoded_strings = []

        for j in range(0, len(string_section), 64):
            block = string_section[j:j+64]
            try:
                #this fixed the chinese text 
                ascii_bytes = bytes([block[k] for k in range(0, len(block), 2)])
                decoded = ascii_bytes.decode('ascii').rstrip('\x00')
                
                if not decoded or not any(c.isalpha() for c in decoded):
                    valid_strings = False
                    break
                    
                decoded_strings.append(decoded)
            except UnicodeDecodeError:
                valid_strings = False
                break

        if valid_strings and len(decoded_strings) == 5:
            print(f"Kill packet detected - Header: {binascii.hexlify(header).decode()}")
            print("Decoded Strings:")
            for idx, s in enumerate(decoded_strings):
                print(f"  String {idx + 1}: {s}")
            return window, i + min_size

    return None, 0

def connect_to_server(host='localhost', port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    buffer = bytearray()
    
    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
                
            buffer.extend(data)
            
            if len(buffer) > 8192:
                buffer = buffer[-8192:]
            
            detected_packet, end_pos = scan_for_kill_pattern(buffer)
            if detected_packet:
                buffer = buffer[end_pos:]
                
    except ConnectionResetError:
        print("Server closed the connection")
    finally:
        client_socket.close()

if __name__ == "__main__":
    connect_to_server()
