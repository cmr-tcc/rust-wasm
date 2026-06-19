import re


def parse_memory_mib(memory_str):
    """Convert docker stats memory string to MiB. E.g.: '121.8MiB' -> 121.8, '1.5GiB' -> 1536.0"""
    match = re.match(r"([\d.]+)([KMG]iB)", memory_str)
    if not match:
        return 0.0
    value = float(match.group(1))
    unit = match.group(2)
    unit_to_mib = {"KiB": 1 / 1024, "MiB": 1.0, "GiB": 1024.0}
    return value * unit_to_mib[unit]


def parse_cpu_percent(cpu_str):
    """Convert docker stats CPU string to float percent. E.g.: '101.5%' -> 101.5"""
    return float(cpu_str.replace("%", ""))
