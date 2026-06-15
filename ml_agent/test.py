import pandas as pd
import numpy as np

df = pd.read_csv("2026-06-14T07-44_export.csv")


latency = df["Latency(s)"] * 1000

p95 = np.percentile(latency, 95)

print(f"P95 latency: {p95:.2f} ms")