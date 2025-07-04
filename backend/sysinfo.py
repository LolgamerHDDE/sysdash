import sys
import os
import platform
import psutil
import cpuinfo
import subprocess

def get_sys_info():
    return {
        "python_version": sys.version,
        "executable": sys.executable
    }

def get_platform_info():
    return {
        "processor": platform.processor(),
        "machine": platform.machine(),
        "platform": platform.platform(),
        "os_name": os.name,
        "architecture": platform.architecture()
    }

def get_cpu_stats():
    freq = psutil.cpu_freq()
    return {
        "logical_cpus": psutil.cpu_count(logical=True),
        "physical_cores": psutil.cpu_count(logical=False),
        "cpu_percent_per_core": psutil.cpu_percent(percpu=True, interval=1),
        "cpu_freq": freq._asdict() if freq else None
    }

def get_cpu_details():
    try:
        info = cpuinfo.get_cpu_info()
        return {k: str(v) for k, v in info.items()}
    except Exception as e:
        return {"error": str(e)}

def get_lscpu_info():
    """For Linux systems only"""
    if os.name != "posix":
        return {"error": "lscpu only available on Linux"}
    try:
        output = subprocess.check_output("lscpu", shell=True, text=True)
        return dict(line.split(":", 1) for line in output.strip().split("\n") if ":" in line)
    except Exception as e:
        return {"error": str(e)}

def get_wmic_info():
    """For Windows systems only - Updated for newer Windows versions"""
    if os.name != "nt":
        return {"error": "wmic only available on Windows"}
    try:
        # Try the newer PowerShell command first
        try:
            output = subprocess.check_output(
                'powershell "Get-WmiObject -Class Win32_Processor | Select-Object Name, Manufacturer, MaxClockSpeed, NumberOfCores, NumberOfLogicalProcessors | Format-List"',
                shell=True, text=True, stderr=subprocess.DEVNULL
            )
            result = {}
            for line in output.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    result[key.strip()] = value.strip()
            return result
        except:
            # Fallback to wmic if available
            output = subprocess.check_output("wmic cpu get Name,Manufacturer,MaxClockSpeed,NumberOfCores,NumberOfLogicalProcessors /format:list", shell=True, text=True)
            return dict(line.split("=", 1) for line in output.strip().split("\n") if "=" in line and line.strip())
    except Exception as e:
        return {"error": f"Windows CPU info not available: {str(e)}"}

def get_sysctl_info():
    """For macOS systems only"""
    if sys.platform != "darwin":
        return {"error": "sysctl only available on macOS"}
    try:
        output = subprocess.check_output("sysctl -a | grep machdep.cpu", shell=True, text=True)
        return dict(line.split(": ", 1) for line in output.strip().split("\n") if ": " in line)
    except Exception as e:
        return {"error": str(e)}

def get_all_cpu_info():
    result = {
        "sys_info": get_sys_info(),
        "platform_info": get_platform_info(),
        "cpu_stats": get_cpu_stats(),
        "cpu_details": get_cpu_details(),
    }
    
    if os.name == "posix" and sys.platform != "darwin":
        result["lscpu_info"] = get_lscpu_info()
    elif os.name == "nt":
        result["wmic_info"] = get_wmic_info()
    elif sys.platform == "darwin":
        result["sysctl_info"] = get_sysctl_info()
    
    return result

# ----- RAM Info -----
def get_ram_info():
    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()
    return {
        "total_ram": vm.total,
        "available_ram": vm.available,
        "used_ram": vm.used,
        "free_ram": vm.free,
        "ram_percent_used": vm.percent,
        "total_swap": sm.total,
        "used_swap": sm.used,
        "free_swap": sm.free,
        "swap_percent_used": sm.percent
    }

# ----- Disk Info -----
def get_disk_partitions():
    partitions = psutil.disk_partitions(all=False)
    result = []
    for p in partitions:
        try:
            usage = psutil.disk_usage(p.mountpoint)
            result.append({
                "device": p.device,
                "mountpoint": p.mountpoint,
                "fstype": p.fstype,
                "opts": p.opts,
                "total_size": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent_used": usage.percent,
            })
        except PermissionError:
            # some partitions may not be accessible
            result.append({
                "device": p.device,
                "mountpoint": p.mountpoint,
                "fstype": p.fstype,
                "opts": p.opts,
                "error": "Permission Denied"
            })
    return result

def get_disk_io():
    io_counters = psutil.disk_io_counters()
    if io_counters:
        return {
            "read_count": io_counters.read_count,
            "write_count": io_counters.write_count,
            "read_bytes": io_counters.read_bytes,
            "write_bytes": io_counters.write_bytes,
            "read_time_ms": io_counters.read_time,
            "write_time_ms": io_counters.write_time
        }
    else:
        return {}

# ----- Network Info -----
def get_network_info():
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    result = {}
    for iface_name, iface_addrs in addrs.items():
        result[iface_name] = {
            "addresses": [{"family": str(addr.family), "address": addr.address, "netmask": addr.netmask, "broadcast": addr.broadcast} for addr in iface_addrs],
            "is_up": stats[iface_name].isup if iface_name in stats else None,
            "speed_mbps": stats[iface_name].speed if iface_name in stats else None,
            "mtu": stats[iface_name].mtu if iface_name in stats else None,
        }
    return result

def get_full_system_info():
    return {
        "cpu_info": get_all_cpu_info(),
        "ram_info": get_ram_info(),
        "disk_partitions": get_disk_partitions(),
        "disk_io": get_disk_io(),
        "network_info": get_network_info()
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_full_system_info(), indent=4))
