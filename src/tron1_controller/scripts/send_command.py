#!/usr/bin/env python3
"""
TRON1机器人命令发送脚本
用法: python3 send_command.py [机器人IP] [ACCID] [命令]
命令: stand, walk, sitdown, stop
"""

import websocket
import json
import time
import sys
import argparse

def send_command(robot_ip, accid, command):
    """发送命令到TRON1机器人"""
    
    # 命令映射表
    commands = {
        "stand": "request_stand_mode",
        "walk": "request_walk_mode", 
        "sitdown": "request_sitdown",
        "stop": "request_emgy_stop",
        "height_up": "request_base_height",    # 升高
        "height_down": "request_base_height",  # 降低（需要data）
        "imu_on": "request_enable_imu",        # 开启IMU
        "imu_off": "request_enable_imu"        # 关闭IMU
    }
    
    # 需要额外data的命令
    extra_data = {
        "height_up": {"direction": 1},
        "height_down": {"direction": -1},
        "imu_on": {"enable": True},
        "imu_off": {"enable": False}
    }
    
    if command not in commands:
        print(f"❌ 未知命令: {command}")
        print(f"✅ 可用命令: {list(commands.keys())}")
        return False
    
    # 连接WebSocket
    ws_url = f"ws://{robot_ip}:5000"
    print(f"🔌 连接机器人: {ws_url}")
    
    try:
        ws = websocket.create_connection(ws_url, timeout=5)
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("请检查:")
        print("  1. 机器人是否已开机")
        print("  2. 是否已连接机器人Wi-Fi或网线")
        print(f"  3. 能否ping通 {robot_ip}")
        return False
    
    # 构造消息
    msg = {
        "accid": accid,
        "title": commands[command],
        "timestamp": int(time.time() * 1000),
        "guid": str(time.time_ns()),
        "data": extra_data.get(command, {})
    }
    
    # 发送
    print(f"📤 发送命令: {command}")
    ws.send(json.dumps(msg))
    
    # 接收响应（有些命令没有响应，等待1秒）
    try:
        ws.settimeout(2)
        response = ws.recv()
        print(f"📥 响应: {response}")
        
        # 解析响应结果
        try:
            resp_json = json.loads(response)
            if "data" in resp_json and "result" in resp_json["data"]:
                result = resp_json["data"]["result"]
                if result == "success":
                    print(f"✅ 命令执行成功")
                else:
                    print(f"⚠️ 命令执行结果: {result}")
        except:
            pass
            
    except websocket.WebSocketTimeoutException:
        print("⏱️ 无响应（部分命令正常）")
    except Exception as e:
        print(f"⚠️ 接收响应异常: {e}")
    
    ws.close()
    return True

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='TRON1机器人控制命令')
    parser.add_argument('robot_ip', nargs='?', default='10.192.1.2', 
                        help='机器人IP地址 (默认: 10.192.1.2)')
    parser.add_argument('accid', nargs='?', default='PF_TRON1A_075',
                        help='机器人序列号 (默认: PF_TRON1A_075)')
    parser.add_argument('command', nargs='?', default='sitdown',
                        help='命令: stand, walk, sitdown, stop, height_up, height_down')
    
    args = parser.parse_args()
    
    print(f"🤖 TRON1机器人控制")
    print(f"📍 机器人IP: {args.robot_ip}")
    print(f"🏷️  序列号: {args.accid}")
    print(f"🎮 命令: {args.command}")
    print("-" * 40)
    
    send_command(args.robot_ip, args.accid, args.command)

if __name__ == "__main__":
    main()