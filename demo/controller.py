#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import enum
import time
from itertools import permutations
from pymycobot import Mercury


class Finger(enum.Enum):
    thumb = (1, 4)  # 拇指
    index = (2, 5)  # 食指
    ring = (3, 6)   # 无名指


class DexterousHandController(object):  # 灵巧手

    def __init__(self, mercury: Mercury):
        self.mercury = mercury

    def move(self, finger: Finger = Finger.thumb, angles: tuple = (50, 50), is_all: bool = False):
        for index, join_id in enumerate(finger.value):
            self.mercury.set_hand_gripper_angle(gripper_id=14, joint_id=join_id, gripper_angle=angles[index])
            if not is_all:
                break

    def permutations_and_combinations(self):
        self.move(Finger.thumb, angles=(0, 0))
        self.move(Finger.index, angles=(0, 0))
        self.move(Finger.ring, angles=(0, 0))

        time.sleep(2)
        print(" * initialization completed")
        for index, (master, follower) in enumerate(permutations([Finger.thumb, Finger.index, Finger.ring], 2), start=1):
            print(f"{index}. master: {master.name}, follower: {follower.name}")
            for count in range(1):
                self.move(master, angles=(80, 0))
                self.move(follower, angles=(80, 0))
                time.sleep(2)
                self.move(master, angles=(0, 0))
                self.move(follower, angles=(0, 0))
                time.sleep(1)
            time.sleep(1)

    def nieHeFangSong(self):
        self.move(Finger.thumb, angles=(37, 70), is_all=True)
        self.move(Finger.index, angles=(43, 100), is_all=True)    # 25 / 27 / 30
        self.move(Finger.ring, angles=(100, 90), is_all=True)

    def nieHe(self):
        self.move(Finger.thumb, angles=(56, 70), is_all=True)
        self.move(Finger.index, angles=(56, 100), is_all=True)    # 25 / 27 / 30
        self.move(Finger.ring, angles=(100, 90), is_all=True)

    def relaxation(self):
        self.move(Finger.thumb, angles=(0, 85), is_all=True)
        self.move(Finger.index, angles=(0, 100), is_all=True)    # 25 / 27 / 30
        self.move(Finger.ring, angles=(0, 100), is_all=True)

    def clasping(self):     # 握紧
        self.move(Finger.ring, angles=(32, 100), is_all=True)    # 25 / 27 / 30
        self.move(Finger.index, angles=(32, 100), is_all=True)
        self.move(Finger.thumb, angles=(50, 85), is_all=True)

    def set_torques(self, torque: int):
        print(" * set torque", torque)
        for i in range(1, 7):
            self.mercury.set_hand_gripper_torque(gripper_id=14, joint_id=i, value=torque)
            time.sleep(0.2)

    def get_torques(self):
        print(" * get torques")
        torques = []
        for i in range(1, 7):
            tor = self.mercury.get_hand_gripper_torque(gripper_id=14, joint_id=i)
            time.sleep(0.2)
            torques.append(tor)
        return torques
