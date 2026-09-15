import re


def parse_memory_kib_to_mib(value) -> float:
    value = str(value)
    match = re.fullmatch(r"([\d.]+)(KiB|MiB|GiB)?", value)
    if not match:
        raise ValueError(f"Invalid memory value: {value!r}")

    number = float(match.group(1))
    unit = match.group(2) or "KiB"
    multipliers = {"KiB": 1 / 1024, "MiB": 1, "GiB": 1024}
    return number * multipliers[unit]

def parse_cpu_percent(cpu_str):
    """Convert docker stats CPU string to float percent. E.g.: '101.5%' -> 101.5"""
    return float(cpu_str.replace("%", ""))
