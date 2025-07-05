import os
import time
import json
import shutil
import tempfile
import numpy as np
import multiprocessing
from timeit import timeit

# Check GPU availability with detailed info
GPU_AVAILABLE = False
GPU_STATUS = "Unknown"

try:
    from numba import cuda
    if cuda.is_available():
        GPU_AVAILABLE = True
        GPU_STATUS = "CUDA Available"
        try:
            devices = cuda.list_devices()
            if devices:
                GPU_STATUS = f"CUDA Available ({len(devices)} device(s))"
            else:
                GPU_AVAILABLE = False
                GPU_STATUS = "CUDA Available but no devices found"
        except:
            GPU_STATUS = "CUDA Available but device query failed"
    else:
        GPU_STATUS = "CUDA not available (no NVIDIA GPU or drivers)"
except ImportError:
    GPU_STATUS = "Numba not installed"
except Exception as e:
    GPU_STATUS = f"GPU check failed: {str(e)}"

print(f"GPU Status: {GPU_STATUS}")


# -------------------- CPU --------------------

def cpu_single_thread():
    def cpu_task():
        total = 0
        for i in range(1_000_000):
            total += i ** 0.5
        return total
    duration = timeit(cpu_task, number=5)
    return round(duration, 3)


# Worker function for multiprocessing (must be at module level)
def _cpu_worker(_):
    """Worker function for CPU multi-thread benchmark"""
    total = 0
    for i in range(500_000):
        total += i ** 0.5
    return total


def cpu_multi_thread():
    start = time.time()
    with multiprocessing.Pool() as pool:
        pool.map(_cpu_worker, range(multiprocessing.cpu_count()))
    end = time.time()
    return round(end - start, 3)


# -------------------- RAM --------------------

def ram_copy_speed():
    size = 500_000_000  # 500 MB
    a = np.random.rand(size).astype(np.float32)

    start = time.time()
    b = a.copy()
    end = time.time()

    mbps = (a.nbytes / (end - start)) / (1024 ** 2)
    return round(mbps, 2)


# -------------------- Disk --------------------

def disk_benchmark():
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, "testfile.tmp")
    size_mb = 100
    data = os.urandom(size_mb * 1024 * 1024)

    try:
        # Write
        start = time.time()
        with open(path, "wb") as f:
            f.write(data)
        end = time.time()
        write_speed = size_mb / (end - start)

        # Read
        start = time.time()
        with open(path, "rb") as f:
            f.read()
        end = time.time()
        read_speed = size_mb / (end - start)

    finally:
        if os.path.exists(path):
            os.remove(path)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    return round(write_speed, 2), round(read_speed, 2)


# -------------------- GPU --------------------

def gpu_benchmark():
    if not GPU_AVAILABLE:
        return GPU_STATUS

    try:
        from numba import cuda
        
        @cuda.jit
        def vector_add(x, y, out):
            idx = cuda.grid(1)
            if idx < x.size:
                out[idx] = x[idx] + y[idx]

        size = 10_000_000
        x = np.ones(size, dtype=np.float32)
        y = np.ones(size, dtype=np.float32)

        d_x = cuda.to_device(x)
        d_y = cuda.to_device(y)
        d_out = cuda.device_array_like(x)

        start = time.time()
        vector_add.forall(size)(d_x, d_y, d_out)
        cuda.synchronize()
        end = time.time()

        return round(end - start, 4)
    except Exception as e:
        return f"GPU test failed: {str(e)}"


# -------------------- Full Benchmark --------------------

def run_full_benchmark():
    try:
        cpu_single = cpu_single_thread()
        cpu_multi = cpu_multi_thread()
        ram_speed = ram_copy_speed()
        disk_write, disk_read = disk_benchmark()
        gpu = gpu_benchmark()

        return {
            "cpu_single_thread_sec": cpu_single,
            "cpu_multi_thread_sec": cpu_multi,
            "ram_copy_speed_MBps": ram_speed,
            "disk_write_MBps": disk_write,
            "disk_read_MBps": disk_read,
            "gpu_vector_add_sec": gpu,
            "gpu_status": GPU_STATUS
        }
    except Exception as e:
        print(f"Full benchmark failed: {e}")
        return {
            "error": str(e),
            "cpu_single_thread_sec": -1,
            "cpu_multi_thread_sec": -1,
            "ram_copy_speed_MBps": -1,
            "disk_write_MBps": -1,
            "disk_read_MBps": -1,
            "gpu_vector_add_sec": GPU_STATUS,
            "gpu_status": GPU_STATUS
        }


# -------------------- Main --------------------

if __name__ == "__main__":
    # Protect multiprocessing code
    multiprocessing.freeze_support()
    results = run_full_benchmark()
    print(json.dumps(results, indent=4))
