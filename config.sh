export BUILD_ROOT=/home/cmann/builds/
export LIBFABRIC_BUILD_DIR=${BUILD_ROOT}/libfabric-internal-development-builds
export LIBFABRIC_BUILD_SCRIPT=/home/cmann/code/libfabric-devel/build-scripts/build.sh
export INTEL_MPI_INSTALL=/opx-dev/libfabric-internal-ci/clx/mpi/intel-mpi-2021.14.1.7
export RUN_RESULTS_ROOT=/tmp/perf-test-results
export RESULTS_COMPLETED_ROOT=/home/cmann/perf-test-results

export NUM_NODES=2
export PPN=full
export BENCHMARKS=Biband,Uniband
export ITER=1000
export MSG_LOG=0:22
export HOSTS=hds2fnc4041,hds2fnc4042
export RUN_ITERS=1

declare -a RUNS=("opx" "opx-sharing-default")

declare -A LIBFABRIC_BUILDS=(
    ["opx"]="/opx-dev/libfabric-internal-ci/clx/libfabric-internal-development-builds/66faf921b91af493f2ed65ff6336885761a46a3e/buildout/buildout"
    ["opx-sharing-default"]="/opx-dev/libfabric-internal-ci/clx/libfabric-internal-development-builds/11ebf7d434d4beab8f7569ea1305065a8a9be527/buildout/buildout"
)

declare -A ENVS=(
    ["opx"]="FI_PROVIDER=opx FI_OPX_CONTEXT_SHARING=false"
    [""opx-sharing-default""]="FI_PROVIDER=opx"
)
