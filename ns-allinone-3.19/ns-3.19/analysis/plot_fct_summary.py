import os
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import PercentFormatter

# ============= CONFIGURATION (MODIFY THESE VALUES) =============
# Base path for input files
BASE_PATH = "/home/jiaxue/conweave-project/ns-allinone-3.19/ns-3.19/mix/output"

# ID to algorithm name mapping
# Format: "numeric_id": "algorithm_display_name"
ID_TO_ALGORITHM = {
    "683878671": "ecmp",
    "955978430": "REPS",
    "322457326": "REPS",
    "547325709": "ecmp",
    "85011631": "ecmp",
    "475862836": "REPS",
    "196084976":"REPS",
    "537465470":"ecmp",
    # Add more mappings as needed
}

# List of experiment IDs to compare (use the numeric IDs from your directory structure)
IDS = ["196084976", "537465470"]  # Replace with your actual numeric IDs

# Metrics to plot (options: 'slowdown', 'absolute')
METRICS = ["slowdown","absolute"]
# "slowdown",

# Percentiles to plot (options: 'avg', '50%', '95%', '99%', '99.9%')
PERCENTILES = ["avg", "50%", "95%", "99%", "99.9%"]

# Categories to plot (options: '<1BDP', '>1BDP')
CATEGORIES = ["<1BDP", ">1BDP"]

# Output directory for plots
OUTPUT_DIR = "/home/jiaxue/conweave-project/ns-allinone-3.19/ns-3.19/analysis/figures-normal"
# ============= END CONFIGURATION =============

def get_algorithm_name(id_name):
    """Get algorithm name from ID mapping or return the ID if not found"""
    return ID_TO_ALGORITHM.get(id_name, id_name)

def parse_fct_summary(file_path):
    """Parse the FCT summary file and extract the data"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    data = {}
    
    # Parse SLOWDOWN section
    slowdown_match = re.search(r'\*\*SLOWDOWN#1BDP=(\d+)Bytes(.*?)ABSOLUTE', content, re.DOTALL)
    if slowdown_match:
        bdp_size = int(slowdown_match.group(1))
        slowdown_content = slowdown_match.group(2)
        
        # Extract category data
        category_match = re.search(r'#Category,Avg\s*,50%\s*,95%\s*,99%\s*,99.9%\s*\n(.*?)\n(.*?)\n', 
                                  slowdown_content, re.DOTALL)
        if category_match:
            less_than_1bdp = [float(x) for x in re.findall(r'[\d.]+', category_match.group(1))[1:]]
            more_than_1bdp = [float(x) for x in re.findall(r'[\d.]+', category_match.group(2))[1:]]
            
            data['slowdown_categories'] = {
                '<1BDP': less_than_1bdp,
                '>1BDP': more_than_1bdp
            }
        
        # Extract CDF data
        cdf_match = re.search(r'#CDF\s+Size\s+Avg\s+50%\s+95%\s+99%\s+99.9%\s+(.*?)\n#\n', 
                             slowdown_content, re.DOTALL)
        if cdf_match:
            cdf_rows = cdf_match.group(1).strip().split('\n')
            cdf_data = []
            
            for row in cdf_rows:
                if row.startswith('#'):
                    values = re.findall(r'[\d.]+', row)
                    if len(values) >= 7:
                        cdf_data.append({
                            'cdf': float(values[0]),
                            'size': int(values[1]),
                            'avg': float(values[2]),
                            '50%': float(values[3]),
                            '95%': float(values[4]),
                            '99%': float(values[5]),
                            '99.9%': float(values[6])
                        })
            
            data['slowdown_cdf'] = pd.DataFrame(cdf_data)
    
    # Parse ABSOLUTE section
    absolute_match = re.search(r'ABSOLUTE#1BDP=(\d+)Bytes(.*?)#EOF', content, re.DOTALL)
    if absolute_match:
        absolute_content = absolute_match.group(2)
        
        # Extract category data
        category_match = re.search(r'#Category,Avg\s*,50%\s*,95%\s*,99%\s*,99.9%\s*\n(.*?)\n(.*?)\n', 
                                  absolute_content, re.DOTALL)
        if category_match:
            less_than_1bdp = [float(x) for x in re.findall(r'[\d.]+', category_match.group(1))[1:]]
            more_than_1bdp = [float(x) for x in re.findall(r'[\d.]+', category_match.group(2))[1:]]
            
            data['absolute_categories'] = {
                '<1BDP': less_than_1bdp,
                '>1BDP': more_than_1bdp
            }
        
        # Extract CDF data
        cdf_match = re.search(r'#CDF\s*,Size\s*,Avg\s*,50%\s*,95%\s*,99%\s*,99.9%\s*>>.*?\n(.*?)\n#\n', 
                             absolute_content, re.DOTALL)
        if cdf_match:
            cdf_rows = cdf_match.group(1).strip().split('\n')
            cdf_data = []
            
            for row in cdf_rows:
                if row.startswith('#'):
                    values = re.findall(r'[\d.]+', row)
                    if len(values) >= 7:
                        cdf_data.append({
                            'cdf': float(values[0]),
                            'size': int(values[1]),
                            'avg': float(values[2]),
                            '50%': float(values[3]),
                            '95%': float(values[4]),
                            '99%': float(values[5]),
                            '99.9%': float(values[6])
                        })
            
            data['absolute_cdf'] = pd.DataFrame(cdf_data)
    
    return data

def plot_category_comparison(data_dict, metric_type, category, percentile, output_dir, ids):
    """Plot category comparison across different IDs with algorithm names"""
    plt.figure(figsize=(10, 6))
    
    # Use algorithm names instead of IDs for x-axis labels
    x_labels = [get_algorithm_name(id_name) for id_name in ids]
    values = []
    
    for id_name in ids:
        if id_name in data_dict and f"{metric_type}_categories" in data_dict[id_name]:
            cat_data = data_dict[id_name][f"{metric_type}_categories"]
            if category in cat_data:
                # Map percentile index: avg=0, 50%=1, 95%=2, 99%=3, 99.9%=4
                percentile_map = {"avg": 0, "50%": 1, "95%": 2, "99%": 3, "99.9%": 4}
                idx = percentile_map.get(percentile.lower(), 0)
                if idx < len(cat_data[category]):
                    values.append(cat_data[category][idx])
                else:
                    values.append(0)
            else:
                values.append(0)
        else:
            values.append(0)
    
    plt.bar(x_labels, values)
    plt.title(f"{metric_type.capitalize()} {category} {percentile}")
    plt.ylabel(f"{metric_type.capitalize()} Value")
    plt.xlabel("Load Balancing Algorithm")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add values on top of bars
    for i, v in enumerate(values):
        plt.text(i, v + max(values) * 0.02, f"{v:.2f}", ha='center')
    
    # Create filename based on IDs
    id_str = '_'.join(ids)
    output_file = os.path.join(output_dir, f"{metric_type}_{category.replace('<', 'less_').replace('>', 'more_')}_{percentile.replace('%', 'p')}_{id_str}.png")
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Saved: {output_file}")
    plt.close()

def plot_cdf_comparison(data_dict, metric_type, percentile, output_dir, ids):
    """Plot CDF comparison across different IDs with algorithm names"""
    plt.figure(figsize=(12, 7))
    
    for id_name in ids:
        if id_name in data_dict and f"{metric_type}_cdf" in data_dict[id_name]:
            df = data_dict[id_name][f"{metric_type}_cdf"]
            if percentile in df.columns:
                # Use algorithm name in the legend
                plt.plot(df['cdf'], df[percentile], marker='o', markersize=4, linestyle='-', 
                         label=get_algorithm_name(id_name))
    
    plt.title(f"{metric_type.capitalize()} CDF vs {percentile}")
    plt.xlabel("CDF")
    plt.ylabel(f"{metric_type.capitalize()} Value")
    plt.xscale('linear')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.gca().xaxis.set_major_formatter(PercentFormatter(1.0))
    
    # Create filename based on IDs
    id_str = '_'.join(ids)
    output_file = os.path.join(output_dir, f"{metric_type}_cdf_{percentile.replace('%', 'p')}_{id_str}.png")
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Saved: {output_file}")
    plt.close()

def plot_size_vs_metric(data_dict, metric_type, percentile, output_dir, ids):
    """Plot Size vs Metric comparison across different IDs with algorithm names"""
    plt.figure(figsize=(12, 7))
    
    for id_name in ids:
        if id_name in data_dict and f"{metric_type}_cdf" in data_dict[id_name]:
            df = data_dict[id_name][f"{metric_type}_cdf"]
            if percentile in df.columns and 'size' in df.columns:
                # Use algorithm name in the legend
                plt.plot(df['size'], df[percentile], marker='o', markersize=4, linestyle='-', 
                         label=get_algorithm_name(id_name))
    
    plt.title(f"{metric_type.capitalize()} Size vs {percentile}")
    plt.xlabel("Size (Bytes)")
    plt.ylabel(f"{metric_type.capitalize()} Value")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Create filename based on IDs
    id_str = '_'.join(ids)
    output_file = os.path.join(output_dir, f"{metric_type}_size_vs_{percentile.replace('%', 'p')}_{id_str}.png")
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Saved: {output_file}")
    plt.close()

def main():
    """Main function to process data and generate plots"""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Store data for all IDs
    all_data = {}
    
    # Read data for each ID
    for id_name in IDS:
        file_path = os.path.join(BASE_PATH, id_name, f"{id_name}_out_fct_summary.txt")
        
        if os.path.exists(file_path):
            print(f"Processing {id_name} ({get_algorithm_name(id_name)})...")
            all_data[id_name] = parse_fct_summary(file_path)
        else:
            print(f"Warning: File not found for ID {id_name} at {file_path}")
    
    # Generate plots for category comparisons
    for metric in METRICS:
        for category in CATEGORIES:
            for percentile in PERCENTILES:
                plot_category_comparison(all_data, metric, category, percentile, OUTPUT_DIR, IDS)
    
    # Generate CDF plots
    for metric in METRICS:
        for percentile in PERCENTILES:
            plot_cdf_comparison(all_data, metric, percentile, OUTPUT_DIR, IDS)
            plot_size_vs_metric(all_data, metric, percentile, OUTPUT_DIR, IDS)
    
    print(f"\nAll plots have been saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()