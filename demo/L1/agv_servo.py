import socket
from pymycobot import MyAGVPro

# 初始化 AGV 控制
agv = MyAGVPro("/dev/ttyACM0", baudrate=1000000, debug=False)


# 控制指令处理
def handle_command(cmd):
    if cmd == "forward":
        agv.move_forward(0.2)
    elif cmd == "backward":
        agv.move_backward(0.2)
    elif cmd == "left":
        agv.move_left_lateral(0.2)
    elif cmd == "right":
        agv.move_right_lateral(0.2)
    elif cmd == "turn_left":
        agv.turn_left(0.35)
    elif cmd == "turn_right":
        agv.turn_right(0.35)
    elif cmd == "stop":
        agv.stop()
    else:
        print(f"收到未知指令：{cmd}")


# 启动服务器
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(1)
    print("AGV 服务器已启动，等待连接...")
    conn, addr = server.accept()
    print(f"连接来自：{addr}")

    while True:
        data = conn.recv(1024)
        if not data:
            break
        cmd = data.decode().strip()
        print(f"收到指令：{cmd}")
        handle_command(cmd)

    conn.close()


if __name__ == "__main__":
    start_server()
