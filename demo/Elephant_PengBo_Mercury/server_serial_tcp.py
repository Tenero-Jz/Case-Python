
import socket
import threading
from pymycobot import *
# from exoskeleton_api import Exoskeleton

# 外骨骼初始化
EXO_PORT = "COM3"
obj = Exoskeleton(port=EXO_PORT)

# TCP配置
TCP_IP = "0.0.0.0"
TCP_PORT = 7000


def handle_client(client_socket, arm):
    def read_from_arm():
        while True:
            try:
                data = arm.get_arm_data(1)   # 获取外骨骼数据
                if data:
                    # 转成字符串并发给客户端
                    msg = (str(data) + "\n").encode("utf-8")
                    client_socket.sendall(msg)
            except Exception as e:
                print("外骨骼读取错误:", e)
                break

    def read_from_socket():
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
            except Exception as e:
                print("Socket错误:", e)
                break

    threading.Thread(target=read_from_arm, daemon=True).start()
    threading.Thread(target=read_from_socket, daemon=True).start()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((TCP_IP, TCP_PORT))
    server.listen(1)
    print(f"外骨骼 {EXO_PORT} 已初始化，TCP服务器监听 {TCP_PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"客户端连接: {addr}")
        handle_client(client_socket, obj)


if __name__ == "__main__":
    main()

