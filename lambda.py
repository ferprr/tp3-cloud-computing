from typing import Dict, Any

N_MIN = 12

def findCPUandMemKeys(input: dict):
    cpus_percent = []
    memory_percent = 0
    for key in input.keys():
        if "cpu_percent" in key:
            cpus_percent.append(input[key])
        
        if "virtual_memory-percent" in key:
            memory_percent = input[key]

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

    return cpus_percent, memory_percent


def handler(input: dict, context: object) -> Dict[str, Any]:

    cpus_percent, memory_percent, bytes_sent, bytes_recv, mem_buff, mem_cached, total_mem = findCPUandMemKeys(input)
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

    n_min = N_MIN

    if counter < N_MIN:
        n_min = counter


    for idx, cpu in enumerate(cpus_percent):
        label_min = "mvg_avg_cpu_" + str(idx) + "_last_minute"
        last_mvg_avg_min = context.env[label_min]
        new_mvg_avg_min = (last_mvg_avg_min * (n_min - 1) + cpu) / n_min
        context.env[label_min] = new_mvg_avg_min
        output[label_min] = new_mvg_avg_min

    return output