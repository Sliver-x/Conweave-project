# -*- coding: utf-8 -*-
import math

# All-to-All
def generate_all_to_all_cdf(min_size=4096, max_size=262144, n_points=20):
    """对数正态 CDF"""
    cdf = []
    mu = math.log(min_size) + 0.5 * (math.log(max_size) - math.log(min_size))
    sigma = 0.5

    cdf.append([0, 0.0])

    for i in range(1, n_points):
        x = math.exp(math.log(min_size) + i * (math.log(max_size) - math.log(min_size)) / (n_points - 1))
        x_rounded = round(x)
        x_rounded = max(min(x_rounded, max_size), min_size)
        y = 0.5 + 0.5 * math.erf((math.log(x) - mu) / (sigma * math.sqrt(2)))
        cdf.append([x_rounded, y])

    cdf[-1][1] = 1.0
    return cdf


# All-Reduce
def generate_all_reduce_cdf(base_size=65536, variation=0.2, n_points=50):
    """截断正态 CDF"""
    cdf = []
    mu = base_size
    sigma = base_size * variation
    min_size = max(1, int(base_size * (1 - 2 * variation)))
    max_size = int(base_size * (1 + 2 * variation))

    cdf.append([0, 0.0])

    for i in range(1, n_points):
        x = min_size + i * (max_size - min_size) / (n_points - 1)
        x_rounded = round(x)
        x_rounded = max(min(x_rounded, max_size), min_size)
        norm_cdf = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
        y = (norm_cdf((x - mu) / sigma) - norm_cdf((min_size - mu) / sigma)) / (
                    norm_cdf((max_size - mu) / sigma) - norm_cdf((min_size - mu) / sigma))
        cdf.append([x_rounded, y])

    cdf[-1][1] = 1.0
    return cdf

def save_cdf_to_txt(cdf_data, filename):
    with open(filename, "w") as file:
        for item in cdf_data:
            file.write(f"{item[0]}\t{item[1] * 100:.2f}\n")

all_to_all_cdf = generate_all_to_all_cdf()
save_cdf_to_txt(all_to_all_cdf, "all_to_all_cdf.txt")

all_reduce_cdf = generate_all_reduce_cdf()
save_cdf_to_txt(all_reduce_cdf, "all_reduce_cdf.txt")