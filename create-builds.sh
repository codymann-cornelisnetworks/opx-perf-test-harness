#! /usr/bin/env bash
#SBATCH --job-name='create-builds'
#SBATCH --nodes=1
#SBATCH --output=/home/cmann/slurm-logs/%x-%j.out
#SBATCH --error=/home/cmann/slurm-logs/%x-%j.err

source ./setup-env.sh
source ../utilities.sh

# Clone the libfabric repository to tmp directory
rm -rf /tmp/libfabric-internal
git clone $LIBFABRIC_URL /tmp/libfabric-internal || die "Failed to clone libfabric directory."
cd /tmp/libfabric-internal || die "Failed to change to libfabric repository."

for commit in "${LIBFABRIC_COMMITS[@]}"
do
    # Create a clean build directory for optimized build
    export LIBFABRIC_OPTIMIZED_INSTALL=$LIBFABRIC_BUILD_DIR/${commit}.optimized
    mkdir -p $LIBFABRIC_OPTIMIZED_INSTALL
    rm -rf $LIBFABRIC_OPTIMIZED_INSTALL/*

    log "Building libfabric commit $commit installed to $LIBFABRIC_OPTIMIZED_INSTALL"
    git checkout $commit || die "Failed to checkout libfabric commit: $commit"
    $LIBFABRIC_BUILD_SCRIPT -c gnu -t optimized || die "Failed build of libfabric commit $commit"
    cp config.log $LIBFABRIC_OPTIMIZED_INSTALL/ || die "Failed to copy config.log to $LIBFABRIC_OPTIMIZED_INSTALL"

    # Create a clean build directory for debug counters
    export LIBFABRIC_OPTIMIZED_INSTALL=$LIBFABRIC_BUILD_DIR/${commit}.optimized_counters
    mkdir -p $LIBFABRIC_OPTIMIZED_INSTALL
    rm -rf $LIBFABRIC_OPTIMIZED_INSTALL/*

    log "Building libfabric commit $commit installed to $LIBFABRIC_OPTIMIZED_INSTALL"
    $LIBFABRIC_BUILD_SCRIPT -c gnu -t optimized -d OPX_DEBUG_COUNTERS || die "Failed build of libfabric commit $commit"
    cp config.log $LIBFABRIC_OPTIMIZED_INSTALL/ || die "Failed to copy config.log to $LIBFABRIC_OPTIMIZED_INSTALL"

    # Create a clean build directory for debug build
    export LIBFABRIC_DEBUG_INSTALL=$LIBFABRIC_BUILD_DIR/${commit}.debug
    mkdir -p $LIBFABRIC_DEBUG_INSTALL
    rm -rf $LIBFABRIC_DEBUG_INSTALL/*

    log "Building libfabric commit $commit installed to $LIBFABRIC_DEBUG_INSTALL"
    $LIBFABRIC_BUILD_SCRIPT -c gnu -t debug || die "Failed build of libfabric commit $commit"
    cp config.log $LIBFABRIC_DEBUG_INSTALL/ || die "Failed to copy config.log to $LIBFABRIC_DEBUG_INSTALL"

done

# Create a build of psm2
log "Creating a build of psm2"
git checkout $PSM2_LIBFABRIC_COMMIT || die "Failed to checkout libfabric commit $PSM2_LIBFABRIC_COMMIT of libfabric internal"

# Setup clean directory to place psm2 build in
PSM2_BUILD_DIR=$LIBFABRIC_BUILD_DIR/${PSM2_LIBFABRIC_COMMIT}_psm2.optimized
mkdir -p $PSM2_BUILD_DIR
rm -rf $PSM2_BUILD_DIR/*

log "Placing psm2 build in $PSM2_BUILD_DIR"

./configure --enable-psm2 --enable-only --prefix=$PSM2_BUILD_DIR CFLAGS="-g -O3 -fPIC" CXXFLAGS="-g -O3 -fPIC" || die "Failed to configure psm2 build"
make clean || die "Failed to make clean libfabric source directory in preparation for psm2 build"
make -j$(nproc) || die "Make failed for psm2 build"
make install || die "Make install failed for psm2 build"
cp config.log $PSM2_BUILD_DIR || die "Failed to copy config.log to psm2 build directory $PSM2_BUILD_DIR"

log "Done."