from pymycobot import ElephantRobot
import time
if __name__=='__main__':
    "将ip更改成P600树莓派的实时ip"
    elephant_client = ElephantRobot("192.168.137.182", 5001)

    "启动机器人必要指令"
    elephant_client.start_client()  
    time.sleep(1) 

    "夹爪设置透传模式"
    elephant_client.set_gripper_mode(0)
    time.sleep(1) 

    "夹爪完全张开"
    elephant_client.set_gripper_state(1,100)
    time.sleep(1)

    for i in range (1):
        "机器人关节运动到安全点,需更改为自己设定的关节角度"
        elephant_client.write_angles([94.828,-143.513,135.283,-82.969,-87.257,-44.033],1000)
        "等待机器人运动到目标位置再执行后续指令"
        elephant_client.command_wait_done()

        "机器人笛卡尔运动到码垛抓取过渡点,需更改为自己设定的位姿"
        elephant_client.write_coords([-130.824,256.262,321.533,176.891,-0.774,-128.700], 3000)
        elephant_client.command_wait_done()

        "机器人以当前坐标位置往Z轴负方向整体运动100mm,到达木块抓取位置"
        elephant_client.jog_relative("Z",-100,1500,1)
        elephant_client.command_wait_done()

        "控制夹爪闭合到30mm"
        elephant_client.set_gripper_value(30,100)
        "控制机器人等待1秒后再动作"
        elephant_client.wait(1)

        "机器人以当前坐标位置往Z轴正方向整体运动100mm,到达木块抓取过渡点"
        elephant_client.jog_relative("Z",100,1500,0)
        elephant_client.command_wait_done()

        "机器人以当前坐标位置往Y轴正方向整体运动300mm,到达木块放置过渡点"
        elephant_client.jog_relative("Y",300,1500,0)
        elephant_client.command_wait_done()

        "机器人以当前坐标位置往Z轴负方向整体运动100mm,到达木块放置位置"
        elephant_client.jog_relative("Z",-100,1500,0)
        elephant_client.command_wait_done()

        "控制夹爪完全张开"
        elephant_client.set_gripper_value(100,100)
        "控制机器人等待1秒后再动作"
        elephant_client.wait(1)

        "机器人以当前坐标位置往Z轴正方向整体运动100mm,到达木块放置过渡点"
        elephant_client.jog_relative("Z",100,1500,1)
        elephant_client.command_wait_done()

        "机器人关节运动到安全点"
        elephant_client.write_angles([94.828,-143.513,135.283,-82.969,-87.257,-44.033],1000)
        elephant_client.command_wait_done()