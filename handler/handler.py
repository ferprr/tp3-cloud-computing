from typing import Dict, Any

def find_cpu_mem_and_net_keys(input_data: dict) -> Any:
    cpus_percent = [input_data[key] for key in input_data if "cpu_percent" in key]
    bytes_sent = input_data.get("net_io_counters_eth0-bytes_sent1", 0)
    bytes_recv = input_data.get("net_io_counters_eth0-bytes_recv1", 0)
    mem_buff = input_data.get("virtual_memory-buffers", 0)
    mem_cached = input_data.get("virtual_memory-cached", 0)
    total_mem = input_data.get("virtual_memory-total", 0)

    return cpus_percent, bytes_sent, bytes_recv, mem_buff, mem_cached, total_mem

def update_cpu_average(cpus_percent: Any, context: object) -> Dict[str, Any]:
    output = {}
    
    if context.env.get("counter") is None:
        context.env["counter"] = 1

        for idx, cpu in enumerate(cpus_percent):
            label_min = f"mvg_avg_cpu_{idx}_last_minute"
            context.env[label_min] = cpu
            output[label_min] = cpu

        return output
    
    context.env["counter"] += 1
    counter = context.env["counter"]

    n_min = min(60, counter)

    for idx, cpu in enumerate(cpus_percent):
        label_min = f"mvg_avg_cpu_{idx}_last_minute"
        last_mvg_avg_min = context.env[label_min]
        new_mvg_avg_min = (last_mvg_avg_min * (n_min - 1) + cpu) / n_min
        context.env[label_min] = new_mvg_avg_min
        output[label_min] = new_mvg_avg_min

    return output

def calculate_and_update_metrics(input_data: dict, context: object) -> Dict[str, Any]:
    cpus_percent, bytes_sent, bytes_recv, mem_buff, mem_cached, total_mem = find_cpu_mem_and_net_keys(input_data)
    output = update_cpu_average(cpus_percent, context)

    total_bytes = bytes_sent + bytes_recv
    outgoing_traffic = (bytes_sent / total_bytes) * 100 if total_bytes > 0 else 0
    output["outgoing_traffic"] = outgoing_traffic

    cached_memory = mem_cached + mem_buff
    memory_caching = (cached_memory / total_mem) * 100
    output["memory_caching"] = memory_caching

    return output

def handler(input_data: dict, context: object) -> Dict[str, Any]:
    return calculate_and_update_metrics(input_data, context)
