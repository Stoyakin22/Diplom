import random
from datetime import datetime


def generate_netflow_data(num_flows=50):
    protocols = ["TCP", "UDP", "ICMP"]
    src_ips = [f"192.168.1.{i}" for i in range(10, 20)]
    dst_ips = [f"10.0.0.{i}" for i in range(10, 20)]

    netflow_data = []

    for _ in range(num_flows):
       netflow_data.append({
            "src_ip": random.choice(src_ips),
            "dst_ip": random.choice(dst_ips),
            "src_port": random.randint(1024, 65535),
            "dst_port": random.randint(1024, 65535),
            "protocol": random.choice(protocols),
            "bytes": random.randint(100, 10000),
            "timestamp": datetime.now().isoformat()
        })
    return netflow_data
