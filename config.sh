#! /usr/bin/env bash
export INTEL_MPI_INSTALL=/opx-dev/libfabric-internal-ci/bdx2699/mpi/intel-mpi-2021.14.1.7
export RUN_RESULTS_ROOT=/tmp/perf-test-results
export RESULTS_COMPLETED_ROOT=/home/cmann/perf-test-results
export NUM_NODES=2
export PPN=full
export BENCHMARKS=Biband
export ITER=1000
export MSG_LOG=0:22
export HOSTS=stl-dev-09,stl-dev-10
export RUN_ITERS=1

declare -a RUNS=("opx-main" "opx-1-way")

declare -A LIBFABRIC_BUILDS=(
    ["opx-main"]="/home/cmann/builds/bdx2699/libfabric-builds/66faf921b91af493f2ed65ff6336885761a46a3e.optimized"
    ["opx-1-way"]="/home/cmann/builds/bdx2699/libfabric-builds/427e505638f9542d7a1188e38e0c1773007287eb.optimized"
)

declare -A ENVS=(
    ["opx-main"]="FI_PROVIDER=opx FI_OPX_CONTEXT_SHARING=false"
    ["opx-1-way"]="FI_PROVIDER=opx"
)