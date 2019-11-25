#!/usr/bin/env python
def uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])

    return int(uptime_seconds)