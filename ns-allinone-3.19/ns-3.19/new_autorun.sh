#!/bin/bash

cecho(){  # source: https://stackoverflow.com/a/53463162/2886168
    RED="\033[0;31m"
    GREEN="\033[0;32m"
    YELLOW="\033[0;33m"
    # ... ADD MORE COLORS
    NC="\033[0m" # No Color

    printf "${!1}${2} ${NC}\n"
}

# cecho "GREEN" "Running RDMA Network Load Balancing Simulations (leaf-spine topology)"

TOPOLOGY="fat_k4_100G_OS2" # or, fat_k8_100G_OS2/leaf_spine_128_100G_OS2/fat_k4_100G_OS2
NETLOAD="50" # network load 50%
RUNTIME="0.1" # 0.1 second (traffic generation)

cecho "YELLOW" "\n----------------------------------"
cecho "YELLOW" "TOPOLOGY: ${TOPOLOGY}" 
cecho "YELLOW" "NETWORK LOAD: ${NETLOAD}" 
cecho "YELLOW" "TIME: ${RUNTIME}" 
cecho "YELLOW" "----------------------------------\n"

# Lossless RDMA
cecho "GREEN" "Run Lossless RDMA experiments..."
python3 newrun.py --lb fecmp --pfc 1 --irn 0 --cdf all_to_all_cdf --tmode all-to-all --reps 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
sleep 5
python3 newrun.py --lb fecmp --pfc 1 --irn 0 --cdf all_to_all_cdf --tmode all-to-all --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
sleep 5
# python3 newrun.py --lb letflow --pfc 1 --irn 0 --cdf all_to_all_cdf --tmode all-to-all --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb conga --pfc 1 --irn 0 --cdf all_to_all_cdf --tmode all-to-all --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb conweave --pfc 1 --irn 0 --cdf all_to_all_cdf --tmode all-to-all --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb fecmp --pfc 1 --irn 0 --tmode normal --reps 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
# sleep 5
# python3 newrun.py --lb fecmp --pfc 1 --irn 0 --tmode normal --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
# sleep 5
# python3 newrun.py --lb letflow --pfc 1 --irn 0 --tmode normal --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb conga --pfc 1 --irn 0 --tmode normal --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb conweave --pfc 1 --irn 0 --tmode normal --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb fecmp --pfc 1 --irn 0 --cdf all_reduce_cdf --tmode r-all-reduce --reps 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
# sleep 0.1
# python3 newrun.py --lb fecmp --pfc 1 --irn 0 --cdf all_reduce_cdf --tmode r-all-reduce --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
# sleep 0.1
# python3 newrun.py --lb letflow --pfc 1 --irn 0 --cdf all_reduce_cdf --tmode r-all-reduce --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb conga --pfc 1 --irn 0 --cdf all_reduce_cdf --tmode r-all-reduce --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb conweave --pfc 1 --irn 0 --cdf all_reduce_cdf --tmode r-all-reduce --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb fecmp --pfc 1 --irn 0 --cdf all_reduce_cdf --tmode b-all-reduce --reps 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
# sleep 5
# python3 newrun.py --lb fecmp --pfc 1 --irn 0 --cdf all_reduce_cdf --tmode b-all-reduce --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
# sleep 5
# python3 newrun.py --lb fecmp --pfc 1 --irn 0 --fixed 1 --tmode all-to-all --reps 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
# sleep 5
# python3 newrun.py --lb fecmp --pfc 1 --irn 0 --fixed 1 --tmode all-to-all --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
# sleep 5

# IRN RDMA
cecho "GREEN" "Run IRN RDMA experiments..."
# python3 newrun.py --lb fecmp --pfc 0 --irn 1 --tmode normal --reps 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
# sleep 5
# python3 newrun.py --lb fecmp --pfc 0 --irn 1 --tmode normal --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
# sleep 5
# python3 newrun.py --lb letflow --pfc 0 --irn 1 --tmode normal --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb conga --pfc 0 --irn 1 --tmode normal --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb conweave --pfc 0 --irn 1 --tmode normal --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb fecmp --pfc 0 --irn 1 --cdf all_to_all_cdf --tmode all-to-all --reps 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
# sleep 5
# python3 newrun.py --lb fecmp --pfc 0 --irn 1 --cdf all_to_all_cdf --tmode all-to-all --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
# sleep 5
# python3 newrun.py --lb fecmp --pfc 0 --irn 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 5
# python3 newrun.py --lb letflow --pfc 0 --irn 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb conga --pfc 0 --irn 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb conweave --pfc 0 --irn 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null &
# sleep 0.1
# python3 newrun.py --lb fecmp --pfc 0 --irn 1 --cdf all_reduce_cdf --tmode r-all-reduce --reps 1 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
# sleep 0.1
# python3 newrun.py --lb fecmp --pfc 0 --irn 1 --cdf all_reduce_cdf --tmode r-all-reduce --reps 0 --simul_time ${RUNTIME} --netload ${NETLOAD} --topo ${TOPOLOGY} 2>&1 > /dev/null & 
# sleep 0.1

cecho "GREEN" "Runing all in parallel. Check the processors running on background!"