import os
import time
import json
import shutil
import tempfile
import numpy as np
import multiprocessing
from timeit import timeit
from .test_logger import TestResultLogger

# Initialize logger
logger = TestResultLogger()

# Optional GPU support
try:
    from numba import cuda
    GPU_AVAILABLE = cuda.is_available()
except:
    GPU_AVAILABLE = False

def cpu_single_thread():
    """CPU single-thread benchmark with logging"""
    def cpu_task():
        total = 0
        for i in range(1_000_000):
            total += i ** 0.5
        return total
    
    start_time = time.time()
    duration = timeit(cpu_task, number=5)
    end_time = time.time()
    
    results = {
        'duration_seconds': round(duration, 3),
        'test_iterations': 5,
        'operations_per_test': 1_000_000,
        'total_duration': round(end_time - start_time, 3),
        'score': round(1000 / duration, 2)  # Higher is better
    }
    
    # Log the result
    logger.log_benchmark_result('cpu_single', results)
    
    return duration

def cpu_multi_thread():
    """CPU multi-thread benchmark with logging"""
    def worker(_):
        total = 0
        for i in range(500_000):
            total += i ** 0.5
        return total

    cpu_count = multiprocessing.cpu_count()
    start = time.time()
    with multiprocessing.Pool() as pool:
        pool.map(worker, range(cpu_count))
    end = time.time()
    
    duration = round(end - start, 3)
    
    results = {
        'duration_seconds': duration,
        'cpu_cores_used': cpu_count,
        'operations_per_core': 500_000,
        'total_operations': 500_000 * cpu_count,
        'score': round(1000 / duration, 2)  # Higher is better
    }
    
    # Log the result
    logger.log_benchmark_result('cpu_multi', results)
    
    return duration

def ram_copy_speed():
    """RAM benchmark with logging"""
    size = 500_000_000  # 500 MB
    a = np.random.rand(size).astype(np.float32)

    start = time.time()
    b = a.copy()
    end = time.time()

    duration = end - start
    mbps = (a.nbytes / duration) / (1024 ** 2)
    
    results = {
        'speed_mbps': round(mbps, 2),
        'test_size_mb': round(a.nbytes / (1024 ** 2), 2),
        'duration_seconds': round(duration, 3),
        'data_type': 'float32'
    }
    
    # Log the result
    logger.log_benchmark_result('ram', results)
    
    return mbps

def disk_benchmark():
    """Disk benchmark with logging"""
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, "testfile.tmp")
    size_mb = 100
    data = os.urandom(size_mb * 1024 * 1024)

    try:
        # Write test
        start = time.time()
        with open(path, "wb") as f:
            f.write(data)
        write_end = time.time()
        write_speed = size_mb / (write_end - start)

        # Read test
        read_start = time.time()
        with open(path, "rb") as f:
            read_data = f.read()
        read_end = time.time()
        read_speed = size_mb / (read_end - read_start)

        results = {
            'write_speed_mbps': round(write_speed, 2),
            'read_speed_mbps': round(read_speed, 2),
            'test_size_mb': size_mb,
            'write_duration': round(write_end - start, 3),
            'read_duration': round(read_end - read_start, 3),
            'temp_dir': temp_dir
        }
        
                # Log the result
        logger.log_benchmark_result('disk', results)

    finally:
        if os.path.exists(path):
            os.remove(path)
        shutil.rmtree(temp_dir)

    return write_speed, read_speed

def gpu_benchmark():
    """GPU benchmark with logging"""
    if not GPU_AVAILABLE:
        results = {
            'status': 'unavailable',
            'reason': 'CUDA not available or no NVIDIA GPU detected',
            'duration_seconds': 0
        }
        logger.log_benchmark_result('gpu', results)
        return None

    try:
        @cuda.jit
        def vector_add(x, y, out):
            idx = cuda.grid(1)
            if idx < x.size:
                out[idx] = x[idx] + y[idx]

        size = 10_000_000
        x = np.ones(size, dtype=np.float32)
        y = np.ones(size, dtype=np.float32)

        # Transfer to GPU
        transfer_start = time.time()
        d_x = cuda.to_device(x)
        d_y = cuda.to_device(y)
        d_out = cuda.device_array_like(x)
        transfer_end = time.time()

        # GPU computation
        compute_start = time.time()
        vector_add.forall(size)(d_x, d_y, d_out)
        cuda.synchronize()
        compute_end = time.time()

        # Transfer back
        result_start = time.time()
        result = d_out.copy_to_host()
        result_end = time.time()

        total_duration = round(compute_end - compute_start, 4)
        
        results = {
            'compute_duration_seconds': total_duration,
            'transfer_to_gpu_seconds': round(transfer_end - transfer_start, 4),
            'transfer_from_gpu_seconds': round(result_end - result_start, 4),
            'vector_size': size,
            'data_type': 'float32',
            'operations_per_second': round(size / total_duration, 0),
            'gpu_info': {
                'device_count': cuda.gpus.count,
                'current_device': cuda.get_current_device().id
            }
        }
        
        # Log the result
        logger.log_benchmark_result('gpu', results)
        
        return total_duration

    except Exception as e:
        results = {
            'status': 'error',
            'error': str(e),
            'duration_seconds': 0
        }
        logger.log_benchmark_result('gpu', results)
        return None

def run_full_benchmark():
    """Run complete benchmark suite with comprehensive logging"""
    benchmark_start = time.time()
    
    print("Starting comprehensive benchmark suite...")
    
    # Run all benchmarks
    cpu_single = cpu_single_thread()
    cpu_multi = cpu_multi_thread()
    ram_speed = ram_copy_speed()
    disk_write, disk_read = disk_benchmark()
    gpu = gpu_benchmark()
    
    benchmark_end = time.time()
    total_duration = round(benchmark_end - benchmark_start, 2)
    
    # Compile results
    full_results = {
        'cpu_single_thread_sec': cpu_single,
        'cpu_multi_thread_sec': cpu_multi,
        'ram_copy_speed_MBps': ram_speed,
        'disk_write_MBps': disk_write,
        'disk_read_MBps': disk_read,
        'gpu_vector_add_sec': gpu if gpu is not None else "GPU not available",
        'total_benchmark_duration': total_duration,
        'timestamp': time.time()
    }
    
    # Log the complete benchmark session
    logger.log_benchmark_result('full_suite', full_results)
    
    print(f"Benchmark suite completed in {total_duration} seconds")
    
    return full_results

# Add function to get benchmark history
def get_benchmark_history(benchmark_type: str = None, limit: int = 10):
    """Get benchmark history from encrypted logs"""
    return logger.get_benchmark_history(benchmark_type, limit)

def get_benchmark_statistics():
    """Get benchmark statistics"""
    return logger.get_test_statistics()
