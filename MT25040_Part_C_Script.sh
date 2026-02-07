#!/bin/bash



# Configuration
SIZES=(1024 16384 65536 262144) 
THREADS=(1 2 4 8)

ITERATIONS=1000                
OUTPUT_FILE="final_results.csv"

# Network Config
NS_SERVER="ns_server"
NS_CLIENT="ns_client"
VETH_SERVER="veth_server"
VETH_CLIENT="veth_client"
IP_SERVER="10.0.0.1"
IP_CLIENT="10.0.0.2"
PORT=8080

# 1. Compilation
echo "--- [Setup] Cleaning & Compiling ---"
mkdir -p results
make clean > /dev/null
make > /dev/null

# CSV Header (Added Latency_us)
echo "Implementation,MessageSize,Threads,Throughput_Gbps,Latency_us,Cycles,ContextSwitches,LLCMisses,L1Misses" > $OUTPUT_FILE

# Helper: Cleanup
cleanup() {
    killall -9 server_a1 server_a2 server_a3 client_a1 2>/dev/null
    ip netns del $NS_SERVER 2>/dev/null
    ip netns del $NS_CLIENT 2>/dev/null
    rm -f perf_current.txt
}

# Helper: Setup Namespaces
setup_namespaces() {
    cleanup
    ip netns add $NS_SERVER
    ip netns add $NS_CLIENT
    ip link add $VETH_SERVER type veth peer name $VETH_CLIENT
    ip link set $VETH_SERVER netns $NS_SERVER
    ip link set $VETH_CLIENT netns $NS_CLIENT

    ip netns exec $NS_SERVER ip addr add $IP_SERVER/24 dev $VETH_SERVER
    ip netns exec $NS_SERVER ip link set $VETH_SERVER up
    ip netns exec $NS_SERVER ip link set lo up
    ip netns exec $NS_CLIENT ip addr add $IP_CLIENT/24 dev $VETH_CLIENT
    ip netns exec $NS_CLIENT ip link set $VETH_CLIENT up
    ip netns exec $NS_CLIENT ip link set lo up
}

run_experiment() {
    TYPE=$1
    SERVER_BIN="./server_$TYPE"
    CLIENT_BIN="./client_a1"
    SIZE=$2
    THREAD=$3

    echo "[Test] Type: $TYPE | Size: $SIZE | Threads: $THREAD"

    # Start Server
    ip netns exec $NS_SERVER $SERVER_BIN $SIZE &
    
    # Wait for Server
    MAX_RETRIES=50
    COUNT=0
    SERVER_READY=0
    while [ $COUNT -lt $MAX_RETRIES ]; do
        if ip netns exec $NS_SERVER ss -lnt | grep -q ":$PORT"; then
            SERVER_READY=1
            break
        fi
        sleep 0.1
        ((COUNT++))
    done

    if [ $SERVER_READY -eq 0 ]; then
        echo "   [Error] Server failed to bind port. Skipping."
        return
    fi

    SERVER_PID=$(pidof server_$TYPE | awk '{print $1}')

    # Run Client Wrapped in Perf
    START_TIME=$(date +%s.%N)
    
    perf stat -p $SERVER_PID -e cycles,context-switches,cache-misses,L1-dcache-load-misses \
        -o perf_current.txt -- \
        ip netns exec $NS_CLIENT $CLIENT_BIN $IP_SERVER $PORT $THREAD $SIZE > client_output.txt

    # 2. Extract Total Bytes
    BYTES=$(grep "TOTAL_BYTES" client_output.txt | awk -F':' '{print $2}')
    
    # Handle empty result (in case of error)
    if [ -z "$BYTES" ]; then BYTES=0; fi

    # 3. Calculate Throughput/Latency with Python (Dynamic)
    METRICS=$(python3 -c "
try:
    total_bytes = float($BYTES)
    duration = 6.0  # We enforced 6 seconds in server
    
    # Throughput (Gbps) = (Bytes * 8) / Duration / 1e9
    gbps = (total_bytes * 8) / duration / 1e9
    
    # Latency (us) = Duration / Total_Messages * 1e6
    # Total_Messages = Total_Bytes / Message_Size
    msg_size = float($SIZE)
    if total_bytes > 0:
        total_msgs = total_bytes / msg_size
        latency = (duration * 1e6) / total_msgs
    else:
        latency = 0
        
    print(f'{gbps:.6f},{latency:.6f}')
except:
    print('0,0')
")

    # Parse Perf Data
    CYCLES=$(grep "cycles" perf_current.txt | awk '{print $1}' | tr -d ',')
    CS=$(grep "context-switches" perf_current.txt | awk '{print $1}' | tr -d ',')
    LLC=$(grep "cache-misses" perf_current.txt | awk '{print $1}' | tr -d ',')
    L1=$(grep "L1-dcache-load-misses" perf_current.txt | awk '{print $1}' | tr -d ',')

    # Defaults
    CYCLES=${CYCLES:-0}
    CS=${CS:-0}
    LLC=${LLC:-0}
    L1=${L1:-0}

    # Save to CSV (Added METRICS which contains 'TP,LAT')
    echo "$TYPE,$SIZE,$THREAD,$METRICS,$CYCLES,$CS,$LLC,$L1" >> $OUTPUT_FILE
}

echo "--- Starting Loops ---"

for TYPE in "a1" "a2" "a3"; do
    for SIZE in "${SIZES[@]}"; do
        for THREAD in "${THREADS[@]}"; do
            setup_namespaces
            run_experiment $TYPE $SIZE $THREAD
        done
    done
done

cleanup
echo "--- All Done! Results: $OUTPUT_FILE ---"