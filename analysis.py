from collections import defaultdict
import datetime
import pandas as pd


def aggregate_netflow_data(netflow_data):
    aggregated_traffic = defaultdict(int)
    for flow in netflow_data:
            aggregated_traffic[flow.src_ip] += flow.bytes
    return aggregated_traffic


def calculate_traffic_rate(netflow_data):
    if not netflow_data:
        return None
    
    sorted_flows = sorted(netflow_data, key=lambda flow: datetime.datetime.fromisoformat(flow.timestamp))

    first_timestamp = datetime.datetime.fromisoformat(sorted_flows[0].timestamp)
    last_timestamp = datetime.datetime.fromisoformat(sorted_flows[-1].timestamp)

    duration_seconds = (last_timestamp - first_timestamp).total_seconds()
    if duration_seconds <= 0:
        return 0

    total_bytes = sum(flow.bytes for flow in netflow_data)
    bytes_per_second = total_bytes / duration_seconds
    return bytes_per_second


def top_talkers(netflow_data, top_n=5):
    if not netflow_data:
       return None

    traffic_by_source = defaultdict(int)
    for flow in netflow_data:
            traffic_by_source[flow.src_ip] += flow.bytes


    top_talkers_data = sorted(traffic_by_source.items(), key=lambda item: item[1], reverse=True)[:top_n]
    
    return [{"src_ip": src_ip, "bytes": total_bytes} for src_ip, total_bytes in top_talkers_data]
