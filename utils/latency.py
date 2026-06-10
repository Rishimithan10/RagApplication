import time

# Global store for all latency measurements
_latency_log = {}

def measure(label):
    """Context manager to measure latency of any block."""
    class Timer:
        def __enter__(self):
            self.start = time.perf_counter()
            return self

        def __exit__(self, *args):
            elapsed = time.perf_counter() - self.start
            _latency_log[label] = round(elapsed, 4)

    return Timer()

def get_all():
    return dict(_latency_log)

def reset():
    _latency_log.clear()