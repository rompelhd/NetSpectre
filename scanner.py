import subprocess
import threading
import queue
import time
import os
import scapy.all as scapy
from database import upsert_host

PARALLEL = 100
TIMEOUT = "300"

def get_local_ip():
    out = subprocess.check_output(
        ["ip", "route", "get", "8.8.8.8"],
        text=True
    )
    return out.split()[6]

def generate_ips(a, b):
    for i in range(256):
        for j in range(256):
            yield f"{a}.{b}.{i}.{j}"

def ping(ip):
    result = subprocess.run(
        ["fping", "-c1", f"-t{TIMEOUT}", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

def get_mac(ip):
    try:
        return scapy.getmacbyip(ip)
    except:
        return None

def worker(q, progress):
    while True:
        try:
            ip = q.get_nowait()
        except queue.Empty:
            return

        if ping(ip):
            mac = get_mac(ip)
            upsert_host(ip, mac)

        progress[0] += 1
        q.task_done()

def scan():
    if os.geteuid() != 0:
        raise SystemExit("Ejecuta como root")

    local_ip = get_local_ip()
    a, b, _, _ = local_ip.split(".")

    q = queue.Queue()
    for ip in generate_ips(a, b):
        q.put(ip)

    total = q.qsize()
    progress = [0]

    threads = []
    for _ in range(PARALLEL):
        t = threading.Thread(target=worker, args=(q, progress))
        t.daemon = True
        t.start()
        threads.append(t)

    while progress[0] < total:
        print(f"\r[{progress[0]}/{total}]", end="")
        time.sleep(0.2)

    q.join()
    print("\n[+] Scan finalizado")
