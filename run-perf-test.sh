#! /usr/bin/env bash
#SBATCH --job-name='perf-test'
#SBATCH --nodes=2
#SBATCH --output=/home/cmann/slurm-logs/%x-%j.out
#SBATCH --error=/home/cmann/slurm-logs/%x-%j.err

source ./config.sh
source ./utilities.sh

date_string=$(date +%F-%H-%M-%S-%N)
RESULTS_DIR=$RUN_RESULTS_ROOT/${date_string}

# Setup a clean results directory
mkdir -p $RESULTS_DIR
rm -rf $RESULTS_DIR/*

# Add Intel MPI to path
source $INTEL_MPI_INSTALL/mpi/latest/env/vars.sh -i_mpi_ofi_internal=0

if [[ $PPN == "full" ]]
then
    PPN=$(nproc)
fi

# Set the number of processes = ppn X (number of nodes)
NP=$(($PPN*$NUM_NODES))

# Calculate the IMPI logical core pin list
MAX_PIN=$(($PPN-1))
PIN_LIST=$(seq -s, 0 $MAX_PIN)

for run in "${RUNS[@]}"
do
    for ((i=0; i<${RUN_ITERS}; i++))
    do

        LOGFILE=$RESULTS_DIR/IMB-MPI1.${run}_${i}.out
        LIBFAB_BUILD_PATH=${LIBFABRIC_BUILDS["$run"]}
        RUN_ENV=${ENVS["$run"]}
        STDERR_LOG_DIR=$RESULTS_DIR/${run}_${i}

        # Create a clean directory for stderr logging
        mkdir -p $STDERR_LOG_DIR
        rm -rf $STDERR_LOG_DIR/*

        COMMAND="LD_LIBRARY_PATH=$LIBFAB_BUILD_PATH/lib:$LD_LIBRARY_PATH I_MPI_FABRICS=ofi I_MPI_OFI_LIBRARY_INTERNAL=off I_MPI_PIN_PROCESSOR_LIST=$PIN_LIST ${RUN_ENV}"
        COMMAND=$COMMAND" mpirun -errfile-pattern=$STDERR_LOG_DIR/output.err-%r-%h -np $NP -ppn $PPN -host $HOSTS -genvall IMB-MPI1 $BENCHMARKS -iter $ITER -msglog $MSG_LOG -npmin $NP"

        echo "${run}_${i}: $COMMAND" >> $LOGFILE
        eval $COMMAND | tee -a $LOGFILE
    done
done

# Parse the results
python3 ./parse.py $RESULTS_DIR

mv $RESULTS_DIR $RESULTS_COMPLETED_ROOT/ || die "Failed to move $RESULTS_DIR to $RESULTS_COMPLETED_ROOT"