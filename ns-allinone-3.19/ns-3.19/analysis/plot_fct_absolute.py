#!/usr/bin/python3

import numpy as np
import subprocess
import os
import sys
import argparse
import matplotlib as mpl
mpl.use('Agg')  # 必须在导入 pyplot 之前
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import math
from cycler import cycler


# 配置参数
FILE_DIR = "/home/jiaxue/conweave-project/ns-allinone-3.19/ns-3.19/mix/output"  # 文件所在目录
IDS = [955978430, 683878671]   
ALGORITHM_NAMES = {        
    475862836: "REPS",
    # 821433064: "letflow"
}
OUTPUT_IMAGE = "fct_absolute_comparison.pdf"  


plt.style.use('seaborn-v0_8')
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  
line_styles = ['-', '--', '-.', ':']  

def read_cdf_file(file_path):
    fct_values = []
    cdf_percent = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue  
                parts = line.strip().split()
                if len(parts) >= 4:
                    fct_values.append(float(parts[0]))  # 第一列：FCT值
                    cdf_percent.append(float(parts[3]))  # 第四列：CDF百分比
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
    return np.array(fct_values), np.array(cdf_percent)


plt.figure(figsize=(10, 6))
ax = plt.gca()


for idx, exp_id in enumerate(IDS):
  
    filename = f"{exp_id}_out_fct_all_absolute_cdf.txt"
    file_path = os.path.join(FILE_DIR, str(exp_id), filename)
    
    fct, cdf = read_cdf_file(file_path)
    
    if len(fct) == 0:
        print(f"Warning: No data found for ID {exp_id}")
        continue
    
    label = ALGORITHM_NAMES.get(exp_id, f"Algorithm {exp_id}")
    
    # 绘制曲线
    plt.semilogx(fct, cdf*100,  # 对x轴取对数
                 label=label,
                 color=colors[idx % len(colors)],
                 linestyle=line_styles[idx % len(line_styles)],
                 linewidth=2)

# 添加图例和标签
plt.legend(loc='lower right', fontsize=12)
plt.xlabel("Flow Completion Time (FCT)", fontsize=14)
plt.ylabel("CDF (%)", fontsize=14)
plt.title("FCT Distribution Comparison", fontsize=16)
plt.grid(True, which='both', linestyle='--', alpha=0.6)

# 设置坐标轴范围
plt.xlim(left=100)  
plt.ylim(0, 100)

# 保存和显示
plt.tight_layout()
plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches='tight')
print(f"Saved plot to {OUTPUT_IMAGE}")
plt.show()