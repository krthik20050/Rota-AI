---
title: System Requirements
---

Rota AI is optimized to run with low memory and CPU footprints. However, your requirements depend heavily on whether you choose a **Cloud Backend** or a **Local Offline Backend**.

### Minimum Specifications (Cloud-Only Backend)
If you use Groq or Gemini API keys, all transcription and cleaning calculations are offloaded to high-performance cloud hardware.

| Component | Minimum Requirement | Recommended |
|-----------|---------------------|-------------|
| **OS** | Windows 10/11, macOS 13+, Ubuntu 20.04+ | Windows 11, macOS 14+, Ubuntu 22.04+ |
| **CPU** | Any Dual-core x86_64 or ARM64 processor | Quad-core Intel Core i5/AMD Ryzen 5 / Apple M-series |
| **RAM** | 2 GB | 4 GB or more |
| **Storage** | 150 MB free disk space | 300 MB free disk space |
| **Internet** | Broad band internet connection (sub-50ms ping to API hosts) | Fiber or stable Wi-Fi (for low-latency voice data upload) |

### Minimum Specifications (Local Offline Backend)
If you configure Rota AI to use Ollama for offline transcription, the heavy neural network models run directly on your hardware.

| Component | Minimum (Whisper Small/Base) | Recommended (Whisper Large v3) |
|-----------|------------------------------|--------------------------------|
| **CPU** | Quad-core Intel/AMD x86_64 or Apple Silicon M1 | Octa-core CPU with AVX2 instruction support |
| **GPU** | Optional | NVIDIA GPU with CUDA support and 6GB+ VRAM |
| **RAM** | 8 GB System RAM | 16 GB System RAM (or unified memory on Apple Silicon) |
| **Storage** | 1.5 GB (model weights + binaries) | 5 GB (large model weights + audio buffers) |
| **Internet** | Required only for the first download of the Ollama model | None (completely air-gapped operations) |
