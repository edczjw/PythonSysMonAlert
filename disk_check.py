#!/usr/bin/python2
# -*- coding: utf-8 -*-
import psutil
import requests
import socket
import platform
from datetime import datetime

# 企业微信 Webhook URL
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/enterprise"

# 服务器标识 手动更改！！
SERVER_NAME = "服务器 标识命名"

def get_system_info():
    """获取系统的基本信息"""
    # 获取主机名
    hostname = socket.gethostname()

    # 获取操作系统信息
    os_info = platform.uname()

    # 获取内存使用情况
    memory = psutil.virtual_memory()
    memory_info = "总内存: %.2f GB, 已用内存: %.2f GB, 空闲内存: %.2f GB" % (memory.total / (1024 ** 3), memory.used / (1024 ** 3), memory.free / (1024 ** 3))

    # 获取磁盘使用情况
    disk = psutil.disk_usage('/')
    disk_info = "磁盘总空间: %.2f GB, 已用空间: %.2f GB, 空闲空间: %.2f GB" % (disk.total / (1024 ** 3), disk.used / (1024 ** 3), disk.free / (1024 ** 3))

    # 获取 CPU 信息
    cpu_info = "CPU 核心数: %d, 线程数: %d" % (psutil.cpu_count(logical=False), psutil.cpu_count(logical=True))

    return hostname, os_info, memory_info, disk_info, cpu_info

def get_disk_usage():
    """获取磁盘使用情况"""
    disk = psutil.disk_usage('/')
    usage_percentage = disk.percent
    return usage_percentage

def get_memory_usage():
    """获取内存使用情况"""
    memory = psutil.virtual_memory()
    memory_percentage = memory.percent
    return memory_percentage

def get_cpu_usage():
    """获取CPU使用情况"""
    cpu_percentage = psutil.cpu_percent(interval=1)
    return cpu_percentage

def get_system_load():
    """获取系统负载"""
    load = psutil.getloadavg()
    return load

def send_wechat_alert(message):
    """发送企业微信告警消息"""
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    try:
        response = requests.post(WEBHOOK_URL, json=data, headers=headers)
        if response.status_code == 200:
            print("告警消息发送成功")
        else:
            print("发送告警时发生错误: %s" % response.text)
    except Exception as e:
        print("发送告警时发生错误: %s" % str(e))

def check_system_health():
    """检查系统健康状态并发送告警"""
    disk_usage = get_disk_usage()
    memory_usage = get_memory_usage()
    cpu_usage = get_cpu_usage()
    system_load = get_system_load()

    # 获取系统的其他信息
    hostname, os_info, memory_info, disk_info, cpu_info = get_system_info()

    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 收集告警信息
    alert_message = "【%s 系统告警】\n" % SERVER_NAME
    alert_message += "------------------------------\n"
    alert_message += "告警时间: %s\n" % current_time
    alert_message += "主机名: %s\n" % hostname
    alert_message += "操作系统: %s %s (%s)\n" % (os_info[0], os_info[2], os_info[4])  # 使用索引访问元组
    alert_message += "系统信息: %s\n" % cpu_info
    alert_message += "内存信息: %s\n" % memory_info
    alert_message += "磁盘信息: %s\n" % disk_info
    alert_count = 0

    # 检查磁盘使用情况
    if disk_usage > 80:  # 设置阈值为 80%
        alert_message += "❗ 磁盘使用率: %d%% (超出阈值)\n" % disk_usage
        alert_count += 1

    # 检查内存使用情况
    if memory_usage > 80:  # 设置阈值为 80%
        alert_message += "❗ 内存使用率: %d%% (超出阈值)\n" % memory_usage
        alert_count += 1

    # 检查CPU使用情况
    if cpu_usage > 80:  # 设置阈值为 80%
        alert_message += "❗ CPU使用率: %d%% (超出阈值)\n" % cpu_usage
        alert_count += 1

    # 检查系统负载情况
    if system_load[0] > 8.0:  # load[0] 为 1 分钟的平均负载
        alert_message += "❗ 系统负载: %.2f (超出阈值)\n" % system_load[0]
        alert_count += 1

    # 如果有告警信息，发送给企业微信
    if alert_count > 0:
        alert_message += "\n⚠️ 请及时检查系统。"
        send_wechat_alert(alert_message)
    else:
        print("系统运行正常，无告警。")

if __name__ == "__main__":
    check_system_health()
