# **USE Method: Linux Performance Checklist**

## **Summary**

"For every resource, check utilization, saturation, and errors."

[The USE Method](http://www.brendangregg.com/usemethod.html)

[USE Method: Linux Performance Checklist](http://www.brendangregg.com/USEmethod/use-linux.html)

## **CPU**

### **Utilization**

#### system-wide

| command  | check for...                            |
| -------- | --------------------------------------- |
| vmstat 1 | "us" + "sy" + "st"                      |
| sar -u   | sum fields except "%idle" and "%iowait" |
| dstat -c | sum fields except "idl" and "wai"       |

#### per-cpu

| command         | check for...                            |
| --------------- | --------------------------------------- |
| mpstat -P ALL 1 | sum fields except "%idle" and "%iowait" |
| sar -P ALL      | sum fields except "%idle" and "%iowait" |

#### per-process

| command    | check for... |
| ---------- | ------------ |
| top        | "%CPU"       |
| htop       | "CPU%"       |
| ps -o pcpu |              |
| pidstat 1  | "%CPU"       |

#### per-kernel-thread

| command                  | check for...                |
| ------------------------ | --------------------------- |
| top/htop ("K" to toogle) | where VIRT == 0 (heuristic) |

- There can be some oddities with the %CPU from top/htop in virtualized environments;
- CPU utilization: a single hot CPU can be caused by a single hot thread, or mapped hardware interrupt.  Relief of the bottleneck usually involves tuning to use more CPUs in parallel.
- `uptime` "load average" (or /proc/loadavg) wasn't included for CPU metrics since Linux load averages include tasks in the uninterruptable state (usually I/O).

### **Saturation**

#### system-wide

| command  | check for...          |
| -------- | --------------------- |
| vmstat 1 | "r" > CPU count (*)   |
| sar -q`  | "runq-sz" > CPU count |
| dsat -p  | "run" > CPU count     |

(*) The man page for vmstat describes "r" as "The number of processes waiting for run time", which is either incorrect or misleading (on recent Linux distributions it's reporting those threads that are waiting, and threads that are running on-CPU; it's just the wait threads in other OSes).

#### per-process

| command                                                      | check for... |
| ------------------------------------------------------------ | ------------ |
| /proc/PID/schedstat 2nd field (sched_info.run_delay)         |              |
| `perf sched latency` (shows "Average" and "Maximum" delay per-schedule) |              |
| dynamic tracing, eg, SystemTap schedtimes.stp "queued(us)" (*) |              |

(*) There may be a way to measure per-process scheduling latency with perf's sched:sched_process_wait event, otherwise perf probe to dynamically trace the scheduler functions, although, the overhead under high load to gather and post-process many (100s of) thousands of events per second may make this prohibitive. SystemTap can aggregate per-thread latency in-kernel to reduce overhead, although, last I tried schedtimes.stp (on FC16) it produced thousands of "unknown transition:" warnings.

- LPE == Linux Performance Events, aka perf_events. This is a powerful observability toolkit that reads CPC and can also use static and dynamic tracing. Its interface is the perf command.
- CPC == CPU Performance Counters (aka "Performance Instrumentation Counters" (PICs) or "Performance Monitoring Counters" (PMCs), or "Performance Monitoring Unit" (PMU) Hardware Events), read via programmable registers on each CPU by perf (which it was originally designed to do). These have traditionally been hard to work with due to differences between CPUs. LPE perf makes life easier by providing aliases for commonly used counters. Be aware that there are usually many more made available by the processor, accessible by providing their hex values to perf stat -e. Expect to spend some quality time (days) with the processor vendor manuals when trying to use these. (My short video about CPC may be useful, despite not being on Linux).

[Perf Examples](http://www.brendangregg.com/perf.html)

### **Errors**

`perf` (LPE) if processor specific error events (CPC) are available; eg, AMD64's "04Ah Single-bit ECC Errors Recorded by Scrubber"

## **Memory**

### **Utilization**

#### system-wide

| command      | check for...                                   |
| ------------ | ---------------------------------------------- |
| free -m      | "Mem:" (main memory), "Swap:" (virtual memory) |
| vmstat 1     | "free" (main memory), "swap" (virtual memory)  |
| sar -r       | "%memused"                                     |
| dstat -m     | "free"                                         |
| slabtop -s c | for kmem slab usage                            |

#### per-process

| command  | check for...                                                 |
| -------- | ------------------------------------------------------------ |
| top/htop | "RES" (resident main memory), "VIRT" (virtual memory), "Mem" for system-wide summary |

### **Saturation**

#### system-wide

| command  | check for...                     |
| -------- | -------------------------------- |
| vmstat 1 | "si"/"so" (swapping)             |
| sar -B   | "pgscank" + "pgscand" (scanning) |
| sar -W   |                                  |

#### per-process

| command              | check for...                                                 |
| -------------------- | ------------------------------------------------------------ |
|                      | 10th field (min_flt) from /proc/PID/stat for minor-fault rate, or dynamic tracing (*) |
| dmesg \| grep killed | OOM killer                                                   |

(*) The goal is a measure of memory capacity saturation - the degree to which a process is driving the system beyond its ability (and causing paging/swapping). High fault latency works well, but there isn't a standard LPE probe or existing SystemTap example of this (roll your own using dynamic tracing). Another metric that may serve a similar goal is minor-fault rate by process, which could be watched from /proc/PID/stat. This should be available in htop as MINFLT.

### **Errors**

dmesg for physical failures; dynamic tracing, eg, SystemTap uprobes for failed malloc()s

## **Network**

### **Utilization**

| command       | check for...               |
| ------------- | -------------------------- |
| sar -n DEV 1  | "rxKB/s"/max "txKB/s"/max  |
| ip -s link    | RX/TX tput / max bandwidth |
| /proc/net/dev | "bytes" RX/TX tput/max     |
| nicstat       | "%Util" (*)                |

(*) Tim Cook ported nicstat to Linux; it can be found on sourceforge or his blog.

[nicstat sourceforge page](https://sourceforge.net/projects/nicstat/)
[Tim Cook blog - nicstat ](https://blogs.oracle.com/timc/nicstat-the-solaris-and-linux-network-monitoring-tool-you-did-not-know-you-needed)

### **Saturation**

| command       | check for...                                         |
| ------------- | ---------------------------------------------------- |
| ifconfig      | "overruns", "dropped"                                |
| netstat -s    | "segments retransmited"                              |
| sar -n EDEV   | *drop and *fifo metrics                              |
| /proc/net/dev | RX/TX "drop"                                         |
| nicstat       | "Sat" (*)                                            |
|               | dynamic tracing for other TCP/IP stack queueing (**) |

(*) See above for URL of this binary
(**) Dropped packets are included as both saturation and error indicators, since they can occur due to both types of events.

### **Errors**

| command       | check for...                                   |
| ------------- | ---------------------------------------------- |
| ifconfig      | "errors", "dropped"                            |
| netstat -i    | "RX-ERR"/"TX-ERR"                              |
| ip -s link    | "errors"                                       |
| sar -n EDEV   | "rxerr/s" "txerr/s"                            |
| /proc/net/dev | "errs", "drop"                                 |
|               | extra counters may be under /sys/class/net/... |

## **Disk**

### **Utilization**

#### system-wide

| command      | check for... |
| ------------ | ------------ |
| iostat -xz 1 | "%util"      |
| sar -d       | "%util"      |

#### per-process

| command         | check for...               |
| --------------- | -------------------------- |
| iotop           |                            |
| pidstat -d      |                            |
| /proc/PID/sched | "se.statistics.iowait_sum" |

### **Saturation**

| command       | check for...                                                 |
| ------------- | ------------------------------------------------------------ |
| iostat -xnz 1 | "avgqu-sz" > 1, or high "await"                              |
| sar -d        | same                                                         |
|               | LPE block probes for queue length/latency                    |
|               | dynamic/static tracing of I/O subsystem (incl. LPE block probes) |

### **Errors**

| command                    | check for... |
| -------------------------- | ------------ |
| /sys/devices/.../ioerr_cnt |              |
| smartctl                   |              |