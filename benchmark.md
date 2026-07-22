# Benchmark Results

Evaluated end-to-end (input → search → response), on **Flickr30K** (31K+ images), CPU inference.
> Note: CPU inference; GPU deployment would reduce latency significantly.

## Text → Image (200 queries)

| Metric | Value |
|---|---|
| p50 latency | 169.45 ms |
| p95 latency | 385.77 ms |
| p99 latency | 1122.85 ms |
| mean latency | 221.56 ms |
| MRR | 0.9562 |
| recall@1 | 0.92 |
| recall@5 | 1.0 |
| recall@10 | 1.0 |

## Image → Image (200 queries)

| Test | p50 (ms) | p95 (ms) | p99 (ms) | mean (ms) | MRR | recall@1 | recall@5 | recall@10 |
|---|---|---|---|---|---|---|---|---|
| Exact duplicate | 2662.95 | 3714.71 | 4994.90 | 2777.73 | 1.000 | 1.000 | 1.000 | 1.000 |
| Light distortion | 2573.12 | 3058.15 | 4718.74 | 2669.36 | 0.990 | 0.985 | 0.995 | 0.995 |
| Heavy distortion | 2700.35 | 3809.88 | 4615.40 | 2830.71 | 0.848 | 0.815 | 0.895 | 0.920 |

*Light/heavy distortion = rotation, crop, brightness/contrast (+flip/blur for heavy) applied to held-out query images; ground truth is the original source image.*

## Summary

- **Text search** is fast (sub-400ms p95) and highly accurate (recall@5/10 = 1.0).
- **Image search** is robust to light transformations (recall@1 = 0.985) but degrades under heavy distortion (recall@1 = 0.815), showing a known limitation under strong visual perturbation.
- **Image search latency (~2.7–3.8s p95)** is the main bottleneck, driven by CPU-bound CLIP inference; expected to drop substantially on GPU.