export LIBFABRIC_URL=git@github.com:cornelisnetworks/libfabric-internal.git
export LIBFABRIC_COMMITS=("04ddccff781ea389c0123017119ddb9b4407da5e")
export PSM2_LIBFABRIC_COMMIT="04ddccff781ea389c0123017119ddb9b4407da5e"
export SYSTEM=OPX-JKR-GEN-MYR-2
export BUILD_ROOT=/home/cmann/builds/${SYSTEM}
export LIBFABRIC_BUILD_DIR=${BUILD_ROOT}/libfabric-internal-development-builds
export LIBFABRIC_BUILD_SCRIPT=/home/cmann/code/libfabric-devel/build-scripts/build.sh
export INTEL_MPI_INSTALL=${BUILD_ROOT}/mpi/intel-mpi-2021.15.0.495
export RUN_RESULTS_ROOT=/tmp/test-results
export RESULTS_COMPLETED_ROOT=/home/cmann/test-results

export NUM_NODES=2
export PPN=12
export BENCHMARKS=Biband,Uniband
export ITER=1000
export MSG_LOG=0:22
export HOSTS=opx-gen-005,opx-gen-006
export RUN_ITERS=1

declare -a RUNS=("opx" "opx_2way" "opx_3way" "opx_4way")

declare -A LIBFABRIC_BUILDS=(
    ["opx"]="/home/cmann/builds/OPX-JKR-GEN-MYR-2/libfab-builds/${LIBFABRIC_COMMITS}.optimized"
    ["opx_2way"]="/home/cmann/builds/OPX-JKR-GEN-MYR-2/libfab-builds/${LIBFABRIC_COMMITS}.optimized"
    ["opx_3way"]="/home/cmann/builds/OPX-JKR-GEN-MYR-2/libfab-builds/${LIBFABRIC_COMMITS}.optimized"
    ["opx_4way"]="/home/cmann/builds/OPX-JKR-GEN-MYR-2/libfab-builds/${LIBFABRIC_COMMITS}.optimized"
    ["psm2"]=""
    ["psm2_2way"]=""
)

declare -A ENVS=(
    ["opx"]="FI_PROVIDER=opx FI_OPX_CONTEXT_SHARING=false FI_OPX_MAX_PKT_SIZE=10240"
    ["opx_2way"]="FI_PROVIDER=opx FI_OPX_CONTEXT_SHARING=true FI_OPX_ENDPOINTS_PER_HFI_CONTEXT=2 FI_OPX_MAX_PKT_SIZE=10240"
    ["opx_3way"]="FI_PROVIDER=opx FI_OPX_CONTEXT_SHARING=true FI_OPX_ENDPOINTS_PER_HFI_CONTEXT=3 FI_OPX_MAX_PKT_SIZE=10240"
    ["opx_4way"]="FI_PROVIDER=opx FI_OPX_CONTEXT_SHARING=true FI_OPX_ENDPOINTS_PER_HFI_CONTEXT=4 FI_OPX_MAX_PKT_SIZE=10240"
    ["psm2"]="FI_PROVIDER=psm2"
    ["psm2_2way"]="FI_PROVIDER=psm2 PSM2_SHAREDCONTEXTS=1 PSM2_RANKS_PER_CONTEXT=2 HFI_UNIT=0"
)
