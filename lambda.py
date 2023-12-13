from typing import Dict, Any

def findCPUMemandNetKeys(input: dict):
    cpus_percent = []

    for key in input.keys():
        if "cpu_percent" in key:
            cpus_percent.append(input[key])

        if "net_io_counters_eth0-bytes_sent1" in key:
            bytes_sent = input[key]

        if "net_io_counters_eth0-bytes_recv1" in key:
            bytes_recv = input[key]

        if "virtual_memory-buffers" in key:
            mem_buff = input[key]

        if "virtual_memory-cached" in key:
            mem_cached = input[key]
        
        if "virtual_memory-total" in key:
            total_mem = input[key]

    return cpus_percent, bytes_sent, bytes_recv, mem_buff, mem_cached, total_mem


def handler(input: dict, context: object) -> Dict[str, Any]:

    cpus_percent, bytes_sent, bytes_recv, mem_buff, mem_cached, total_mem = findCPUMemandNetKeys(input)
    output = {}

    if getattr(context.env, "counter", None) is None:
        context.env["counter"] = 1

        for idx, cpu in enumerate(cpus_percent):
            label_min = "mvg_avg_cpu_" + str(idx) + "_last_minute"
            context.env[label_min] = cpu
            output[label_min] = cpu

        return output
    
    context.env["counter"] += 1
    counter = context.env["counter"]

    n_min = 60

    if counter < 60:
        n_min = counter


    for idx, cpu in enumerate(cpus_percent):
        label_min = "mvg_avg_cpu_" + str(idx) + "_last_minute"
        last_mvg_avg_min = context.env[label_min]
        new_mvg_avg_min = (last_mvg_avg_min * (n_min - 1) + cpu) / n_min
        context.env[label_min] = new_mvg_avg_min
        output[label_min] = new_mvg_avg_min

    total_bytes = bytes_sent + bytes_recv
    outgoing_percent = (bytes_sent / total_bytes) * 100 if total_bytes > 0 else 0
    output["outgoing_traffic"] = outgoing_percent

    cached_memory = mem_cached + mem_buff
    caching_percentage = (cached_memory / total_mem) * 100
    output["memory_caching"] = caching_percentage

    return output