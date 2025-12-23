# client_latency_test.py
import socket
import time

# 替换为你公司电脑的 IP
SERVER_IP = "X.X.X.X"  # 例如 192.168.1.100
SERVER_PORT = 7000


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))
    print("已连接到外骨骼数据服务器")

    while True:
        # 发送一个心跳请求（不一定要发，但便于计算延迟）
        t_send = time.time()
        sock.sendall(b"ping\n")

        # 等待外骨骼的数据返回
        data = sock.recv(1024)
        t_recv = time.time()

        latency_ms = (t_recv - t_send) * 1000
        print(f"[延迟] {latency_ms:.2f} ms | 数据: {data.decode(errors='ignore').strip()}")

        time.sleep(1)


if __name__ == "__main__":
    main()
