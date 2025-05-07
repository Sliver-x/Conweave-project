# -*- coding: utf-8 -*-
import sys
import random
import math
import heapq
from optparse import OptionParser
from custom_rand import CustomRand

class Flow:
    def __init__(self, src, dst, size, t):
        self.src, self.dst, self.size, self.t = src, dst, size, t
        
    def __str__(self):
        return "%d %d 3 %d %.9f" % (self.src, self.dst, self.size, self.t)

def translate_bandwidth(b):
    if b is None or not isinstance(b, str):
        return None
    unit = b[-1]
    value = float(b[:-1])
    if unit == 'G':
        return value * 1e9
    elif unit == 'M':
        return value * 1e6
    elif unit == 'K':
        return value * 1e3
    else:
        return float(b)

def poisson(lam):
    return -math.log(1 - random.random()) * lam

def get_flow_size(customRand, fixed, size_factor=1.0):
    if fixed == 1:
        # 使用固定大小
        fixed_size = 50000  
        return max(1, int(fixed_size * size_factor))
    else:
        return max(1, int(customRand.rand() * size_factor))

def generate_all_to_all(nhost, customRand, base_t, time_ns, fixed=0):
    flows = []
    fixed_size_factor = 1.0 
    for src in range(nhost):
        for dst in range(nhost):
            if src != dst:
                # 添加微小时间抖动
                t = base_t + random.randint(0, 1000)
                if t > base_t + time_ns:
                    continue
                size = get_flow_size(customRand, fixed, fixed_size_factor)
                flows.append(Flow(src, dst, size, t * 1e-9))
    return flows


def generate_ring_all_reduce(nhost, customRand, base_t, time_ns, fixed=0):
    flows = []
    num_steps = 2 * (nhost - 1)
    step_duration = time_ns // num_steps
    fixed_size_factor = 100.0 / nhost  
    
    # 每个节点的数据分成nhost份
    chunk_size_ratio = 1.0 / nhost
    
    # 分散-归约阶段
    for step in range(nhost - 1):
        step_start = base_t + step * step_duration
        for src in range(nhost):
            dst = (src + 1) % nhost
            # 计算当前步骤传输的块索引
            chunk_idx = (src - step) % nhost
            size = get_flow_size(customRand, fixed, fixed_size_factor if fixed == 1 else chunk_size_ratio)
            t = step_start + random.randint(0, 100)  
    
    # 全收集阶段
    for step in range(nhost - 1):
        step_start = base_t + (step + nhost - 1) * step_duration
        for src in range(nhost):
            dst = (src + 1) % nhost
            chunk_idx = (src - nhost + 1 + step) % nhost
            ize = get_flow_size(customRand, fixed, fixed_size_factor if fixed == 1 else chunk_size_ratio)
            t = step_start + random.randint(0, 100) 
            flows.append(Flow(src, dst, size, t * 1e-9))
    
    return flows

def generate_butterfly_all_reduce(nhost, customRand, base_t, time_ns, fixed=0):
    flows = []
    # 校验节点数是否为2的幂
    if (nhost & (nhost - 1)) != 0:
        raise ValueError("Butterfly需要节点数为2的幂")

    fixed_size_factor = 100.0 / nhost  
    # 计算阶段数
    num_phases = int(math.log(nhost, 2))
    phase_duration = time_ns // num_phases
    
    for phase in range(num_phases):
		# 计算当前阶段的步长
        stride = 2 ** phase
        phase_start = base_t + phase * phase_duration
        
        for group in range(0, nhost, 2 * stride):
            for i in range(group, group + stride):
                j = i + stride
                size = get_flow_size(customRand, fixed, fixed_size_factor)
                
                # 创建双向通信流量
                t1 = phase_start + random.randint(0, 10)  
                t2 = phase_start + random.randint(0, 10)  
                
                flows.append(Flow(i, j, size, t1 * 1e-9))
                flows.append(Flow(j, i, size, t2 * 1e-9))
    
    return flows

def generate_normal_traffic(nhost, customRand, base_t, time_ns, avg_inter_arrival, fixed=0):
    flows = []
    host_heap = []
    fixed_size_factor = 1.0  
    
    for i in range(nhost):
        start_time = base_t + int(poisson(avg_inter_arrival))
        host_heap.append((start_time, i))
    
    heapq.heapify(host_heap)
    
    while host_heap:
        current_time, src = heapq.heappop(host_heap)
        
        if current_time > base_t + time_ns:
            continue
        
        dst = random.randint(0, nhost - 1)
        while dst == src:
            dst = random.randint(0, nhost - 1)
        
        size = get_flow_size(customRand, fixed, fixed_size_factor)
        flows.append(Flow(src, dst, size, current_time * 1e-9))
        
        next_time = current_time + int(poisson(avg_inter_arrival))
        if next_time <= base_t + time_ns:
            heapq.heappush(host_heap, (next_time, src))
    
    return flows

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-c", "--cdf", dest="cdf_file", help="CDF文件路径", default="Solar2022.txt")
    parser.add_option("-n", "--nhost", dest="nhost", help="主机数量")
    parser.add_option("-l", "--load", dest="load", help="网络负载比例", default="0.3")
    parser.add_option("-b", "--bandwidth", dest="bandwidth", help="带宽", default="10G")
    parser.add_option("-t", "--time", dest="time", help="运行时间（秒）", default="10")
    parser.add_option("-m", "--mode", dest="mode", help="流量模式(normal, all-to-all, r-all-reduce, b-all-reduce)", default="normal")
    parser.add_option("-o", "--output", dest="output", help="输出文件", default="traffic.txt")
    parser.add_option("-f", "--fixed", dest="fixed", help="是否使用固定大小(1=固定, 0=CDF分布)", default="0")
    
    options, args = parser.parse_args()
    
    if not options.nhost:
        print("请使用-n指定主机数量")
        sys.exit(1)
    
    nhost = int(options.nhost)
    load = float(options.load)
    bandwidth = translate_bandwidth(options.bandwidth)
    time_ns = float(options.time) * 1e9
    mode = options.mode
    output = options.output
    fixed = int(options.fixed)
    
    if bandwidth is None:
        print("带宽格式错误")
        sys.exit(1)
    
    # 加载CDF文件
    cdf = []
    with open(options.cdf_file, "r") as f:
        for line in f:
            x, y = map(float, line.strip().split())
            cdf.append([x, y])
    
    customRand = CustomRand()
    if not customRand.setCdf(cdf):
        print("无效的CDF文件")
        sys.exit(1)
    
    avg = customRand.getAvg()
    avg_inter_arrival = 1 / (bandwidth * load / 8 / avg) * 1e9  # 转换为纳秒
    
    # 生成流量
    flows = []
    if mode == "normal":
        flows = generate_normal_traffic(nhost, customRand, 2000000000, time_ns, avg_inter_arrival, fixed)
    elif mode == "all-to-all":
        flows = generate_all_to_all(nhost, customRand, 2000000000, time_ns, fixed)
    elif mode == "r-all-reduce":
        flows = generate_ring_all_reduce(nhost, customRand, 2000000000, time_ns, fixed)
    elif mode == "b-all-reduce":
        flows = generate_butterfly_all_reduce(nhost, customRand, 2000000000, time_ns, fixed)
    else:
        print("无效的模式")
        sys.exit(1)
    
    # 写入输出文件
    with open(output, "w") as f:
        f.write("%d\n" % len(flows))
        for flow in sorted(flows, key=lambda x: x.t):
            f.write("%s\n" % flow)
