import os
import shutil
import json
import platform
import subprocess

def get_cpu_info():
    try:
        return os.cpu_count() or 0
    except:
        return 0

def get_ram_info():
    try:
        if platform.system() == "Windows":
            # TotalVisibleMemorySize and FreePhysicalMemory are BOTH in 'OS'
            output = subprocess.check_output("wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Value", shell=True).decode()
            
            total = 0
            free = 0
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("FreePhysicalMemory="):
                    free = int(line.split("=")[1]) * 1024
                elif line.startswith("TotalVisibleMemorySize="):
                    total = int(line.split("=")[1]) * 1024
            return total, free
        else:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                total = int(lines[0].split()[1]) * 1024
                free = int(lines[1].split()[1]) * 1024
                return total, free
    except Exception as e:
        print(f"RAM check error: {e}")
        return 0, 0

def get_disk_info():
    try:
        usage = shutil.disk_usage(".")
        return usage.total, usage.free
    except:
        return 0, 0

def main():
    cpu = get_cpu_info()
    total_ram, free_ram = get_ram_info()
    total_disk, free_disk = get_disk_info()
    
    # Ready if at least 1.5GB free
    min_ram_needed = 1.5 * 1024 * 1024 * 1024 
    
    is_ready = free_ram > min_ram_needed
    
    data = {
        "cpu_cores": cpu,
        "ram": {
            "total_gb": round(total_ram / (1024**3), 2),
            "free_gb": round(free_ram / (1024**3), 2),
            "percent_free": round((free_ram / total_ram) * 100, 1) if total_ram > 0 else 0
        },
        "disk": {
            "total_gb": round(total_disk / (1024**3), 2),
            "free_gb": round(free_disk / (1024**3), 2)
        },
        "status": "READY" if is_ready else "LOW_RESOURCES",
        "timestamp": platform.node()
    }
    
    with open("resources.json", "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"Resource check completed. Status: {data['status']}")

if __name__ == "__main__":
    main()
