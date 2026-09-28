#!/bin/bash
# Serve openai/gpt-oss-20b locally with vLLM (same route the extension-half base run used:
# scripts/run_ext_gptoss_local.sh -> http://127.0.0.1:8077/v1). Azure's deployment is gone (404).
# Usage: bash scripts/serve_gptoss.sh   (foreground; Ctrl-C or kill by PID to stop)
set -u
cd /home/seanwu/FutureScience
exec /home/seanwu/vllm-env/bin/vllm serve openai/gpt-oss-20b --served-model-name gpt-oss-20b \
     --port 8077 --host 127.0.0.1 --max-model-len 8192 --gpu-memory-utilization 0.85 \
     --tensor-parallel-size 1 >> results/A8_base_rate/logs/vllm_gptoss.log 2>&1
