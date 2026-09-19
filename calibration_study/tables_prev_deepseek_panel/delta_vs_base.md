# Arm-vs-base paired deltas (arm − A)

Paired on the intersection of items valid in both arms; 10k event-level bootstrap resamples shared across arms;
two-sided percentile-bootstrap p; Holm–Bonferroni across the intervention arms within each model × task × partition × metric family.
Never read a delta without its CI. `*` marks Holm-adjusted p < 0.05.


## LLaMA 3.3 70B

| task | part | metric | B1 | B2 | C | D | E |
|---|---|---|---|---|---|---|---|

## DeepSeek R1

| task | part | metric | B1 | B2 | C | D | E |
|---|---|---|---|---|---|---|---|
| binary_merged | all | accuracy | — | — | +0.044 [+0.009, +0.081] p=0.0176/0.0176* n=679 | — | — |
| binary_merged | all | bias_index | — | — | +0.187 [+0.099, +0.275] p=0.0002/0.0002* n=679 | — | — |
| binary_merged | all | brier | — | — | +0.008 [-0.009, +0.025] p=0.346/0.346 n=678 | — | — |
| binary_merged | all | logloss | — | — | +0.047 [+0.001, +0.092] p=0.045/0.045* n=678 | — | — |
| binary_merged | all | ece | — | — | +0.027 [-0.007, +0.061] p=0.122/0.122 n=678 | — | — |
| binary_merged | all | rel | — | — | +0.019 [+0.002, +0.036] p=0.0338/0.0338* n=678 | — | — |
| binary_merged | all | res | — | — | +0.011 [+0.003, +0.019] p=0.008/0.008* n=678 | — | — |
| binary_merged | all | auroc | — | — | +0.080 [+0.029, +0.133] p=0.0018/0.0018* n=678 | — | — |
| binary_merged | all | brier_c | — | — | +0.008 [-0.009, +0.025] p=0.346/0.346 n=678 | — | — |
| binary_merged | all | ece_c | — | — | +0.029 [-0.009, +0.064] p=0.138/0.138 n=678 | — | — |
| binary_merged | all | auroc_c | — | — | +0.054 [+0.011, +0.098] p=0.0178/0.0178* n=678 | — | — |
| binary_merged | pre | accuracy | — | — | +0.156 [+0.059, +0.253] p=0.0022/0.0022* n=141 | — | — |
| binary_merged | pre | bias_index | — | — | +0.553 [+0.354, +0.745] p=0.0002/0.0002* n=141 | — | — |
| binary_merged | pre | brier | — | — | -0.011 [-0.061, +0.037] p=0.652/0.652 n=141 | — | — |
| binary_merged | pre | logloss | — | — | +0.054 [-0.088, +0.193] p=0.447/0.447 n=141 | — | — |
| binary_merged | pre | ece | — | — | +0.012 [-0.059, +0.102] p=0.65/0.65 n=141 | — | — |
| binary_merged | pre | rel | — | — | +0.008 [-0.038, +0.054] p=0.724/0.724 n=141 | — | — |
| binary_merged | pre | res | — | — | +0.016 [-0.013, +0.049] p=0.264/0.264 n=141 | — | — |
| binary_merged | pre | auroc | — | — | +0.164 [+0.050, +0.281] p=0.0056/0.0056* n=141 | — | — |
| binary_merged | pre | brier_c | — | — | -0.011 [-0.061, +0.037] p=0.652/0.652 n=141 | — | — |
| binary_merged | pre | ece_c | — | — | -0.001 [-0.088, +0.087] p=0.954/0.954 n=141 | — | — |
| binary_merged | pre | auroc_c | — | — | +0.044 [-0.053, +0.142] p=0.368/0.368 n=141 | — | — |
| binary_merged | post | accuracy | — | — | +0.015 [-0.023, +0.053] p=0.464/0.464 n=538 | — | — |
| binary_merged | post | bias_index | — | — | +0.075 [-0.019, +0.171] p=0.117/0.117 n=538 | — | — |
| binary_merged | post | brier | — | — | +0.013 [-0.004, +0.031] p=0.131/0.131 n=537 | — | — |
| binary_merged | post | logloss | — | — | +0.045 [+0.001, +0.090] p=0.0472/0.0472* n=537 | — | — |
| binary_merged | post | ece | — | — | +0.029 [-0.008, +0.062] p=0.134/0.134 n=537 | — | — |
| binary_merged | post | rel | — | — | +0.017 [-0.002, +0.037] p=0.0822/0.0822 n=537 | — | — |
| binary_merged | post | res | — | — | +0.004 [-0.004, +0.013] p=0.356/0.356 n=537 | — | — |
| binary_merged | post | auroc | — | — | +0.038 [-0.018, +0.095] p=0.193/0.193 n=537 | — | — |
| binary_merged | post | brier_c | — | — | +0.013 [-0.004, +0.031] p=0.131/0.131 n=537 | — | — |
| binary_merged | post | ece_c | — | — | +0.031 [-0.009, +0.071] p=0.133/0.133 n=537 | — | — |
| binary_merged | post | auroc_c | — | — | +0.031 [-0.017, +0.078] p=0.206/0.206 n=537 | — | — |
| binary | all | accuracy | — | — | +0.151 [+0.090, +0.212] p=0.0002/0.0002* n=292 | — | — |
| binary | all | brier | — | — | -0.009 [-0.035, +0.016] p=0.455/0.455 n=292 | — | — |
| binary | all | logloss | — | — | -0.039 [-0.102, +0.023] p=0.215/0.215 n=292 | — | — |
| binary | all | ece | — | — | -0.052 [-0.082, -0.023] p=0.0008/0.0008* n=292 | — | — |
| binary | all | brier_c | — | — | -0.009 [-0.035, +0.016] p=0.455/0.455 n=292 | — | — |
| binary | all | ece_c | — | — | -0.074 [-0.124, -0.018] p=0.0084/0.0084* n=292 | — | — |
| binary | all | auroc_c | — | — | -0.023 [-0.074, +0.028] p=0.369/0.369 n=292 | — | — |
| binary | pre | accuracy | — | — | +0.419 [+0.287, +0.548] p=0.0002/0.0002* n=74 | — | — |
| binary | pre | brier | — | — | -0.085 [-0.138, -0.032] p=0.0022/0.0022* n=74 | — | — |
| binary | pre | logloss | — | — | -0.228 [-0.353, -0.097] p=0.0016/0.0016* n=74 | — | — |
| binary | pre | ece | — | — | -0.171 [-0.235, -0.104] p=0.0002/0.0002* n=74 | — | — |
| binary | pre | brier_c | — | — | -0.085 [-0.138, -0.032] p=0.0022/0.0022* n=74 | — | — |
| binary | pre | ece_c | — | — | -0.113 [-0.212, -0.040] p=0.0046/0.0046* n=74 | — | — |
| binary | pre | auroc_c | — | — | +0.016 [-0.069, +0.097] p=0.67/0.67 n=74 | — | — |
| binary | post | accuracy | — | — | +0.060 [-0.005, +0.123] p=0.082/0.082 n=218 | — | — |
| binary | post | brier | — | — | +0.016 [-0.011, +0.043] p=0.244/0.244 n=218 | — | — |
| binary | post | logloss | — | — | +0.025 [-0.044, +0.093] p=0.483/0.483 n=218 | — | — |
| binary | post | ece | — | — | -0.012 [-0.042, +0.018] p=0.434/0.434 n=218 | — | — |
| binary | post | brier_c | — | — | +0.016 [-0.011, +0.043] p=0.244/0.244 n=218 | — | — |
| binary | post | ece_c | — | — | -0.059 [-0.124, -0.011] p=0.0198/0.0198* n=218 | — | — |
| binary | post | auroc_c | — | — | -0.059 [-0.123, +0.005] p=0.0708/0.0708 n=218 | — | — |
| binary_perturbed | all | accuracy | — | — | -0.036 [-0.088, +0.016] p=0.201/0.201 n=387 | — | — |
| binary_perturbed | all | brier | — | — | +0.022 [-0.005, +0.048] p=0.109/0.109 n=386 | — | — |
| binary_perturbed | all | logloss | — | — | +0.112 [+0.038, +0.185] p=0.0024/0.0024* n=386 | — | — |
| binary_perturbed | all | ece | — | — | -0.000 [-0.025, +0.024] p=0.957/0.957 n=386 | — | — |
| binary_perturbed | all | brier_c | — | — | +0.022 [-0.005, +0.048] p=0.109/0.109 n=386 | — | — |
| binary_perturbed | all | ece_c | — | — | -0.026 [-0.079, +0.026] p=0.328/0.328 n=386 | — | — |
| binary_perturbed | all | auroc_c | — | — | +0.072 [+0.016, +0.131] p=0.0112/0.0112* n=386 | — | — |
| binary_perturbed | pre | accuracy | — | — | -0.134 [-0.273, +0.014] p=0.0874/0.0874 n=67 | — | — |
| binary_perturbed | pre | brier | — | — | +0.072 [-0.019, +0.159] p=0.116/0.116 n=67 | — | — |
| binary_perturbed | pre | logloss | — | — | +0.366 [+0.097, +0.633] p=0.0072/0.0072* n=67 | — | — |
| binary_perturbed | pre | ece | — | — | +0.013 [-0.070, +0.091] p=0.772/0.772 n=67 | — | — |
| binary_perturbed | pre | brier_c | — | — | +0.072 [-0.019, +0.159] p=0.116/0.116 n=67 | — | — |
| binary_perturbed | pre | ece_c | — | — | +0.001 [-0.132, +0.135] p=0.975/0.975 n=67 | — | — |
| binary_perturbed | pre | auroc_c | — | — | +0.054 [-0.094, +0.208] p=0.468/0.468 n=67 | — | — |
| binary_perturbed | post | accuracy | — | — | -0.016 [-0.073, +0.040] p=0.631/0.631 n=320 | — | — |
| binary_perturbed | post | brier | — | — | +0.011 [-0.014, +0.037] p=0.374/0.374 n=319 | — | — |
| binary_perturbed | post | logloss | — | — | +0.059 [-0.007, +0.125] p=0.0814/0.0814 n=319 | — | — |
| binary_perturbed | post | ece | — | — | -0.003 [-0.028, +0.021] p=0.796/0.796 n=319 | — | — |
| binary_perturbed | post | brier_c | — | — | +0.011 [-0.014, +0.037] p=0.374/0.374 n=319 | — | — |
| binary_perturbed | post | ece_c | — | — | -0.030 [-0.086, +0.027] p=0.299/0.299 n=319 | — | — |
| binary_perturbed | post | auroc_c | — | — | +0.055 [-0.004, +0.115] p=0.0698/0.0698 n=319 | — | — |
| mcq | all | accuracy | — | — | +0.080 [+0.028, +0.133] p=0.0016/0.0016* n=386 | — | — |
| mcq | all | brier_c | — | — | -0.063 [-0.107, -0.020] p=0.0048/0.0048* n=382 | — | — |
| mcq | all | ece_c | — | — | -0.065 [-0.117, -0.012] p=0.0156/0.0156* n=382 | — | — |
| mcq | all | auroc_c | — | — | +0.061 [-0.003, +0.124] p=0.0638/0.0638 n=382 | — | — |
| mcq | pre | accuracy | — | — | +0.133 [+0.022, +0.247] p=0.0278/0.0278* n=75 | — | — |
| mcq | pre | brier_c | — | — | -0.121 [-0.215, -0.030] p=0.0114/0.0114* n=75 | — | — |
| mcq | pre | ece_c | — | — | -0.123 [-0.235, -0.014] p=0.0274/0.0274* n=75 | — | — |
| mcq | pre | auroc_c | — | — | +0.207 [+0.031, +0.380] p=0.0216/0.0216* n=75 | — | — |
| mcq | post | accuracy | — | — | +0.068 [+0.010, +0.126] p=0.027/0.027* n=311 | — | — |
| mcq | post | brier_c | — | — | -0.049 [-0.097, +0.000] p=0.0504/0.0504 n=307 | — | — |
| mcq | post | ece_c | — | — | -0.051 [-0.109, +0.008] p=0.0962/0.0962 n=307 | — | — |
| mcq | post | auroc_c | — | — | +0.042 [-0.028, +0.112] p=0.25/0.25 n=307 | — | — |

## GPT-4o

| task | part | metric | B1 | B2 | C | D | E |
|---|---|---|---|---|---|---|---|
| binary_merged | all | accuracy | — | — | +0.029 [-0.007, +0.064] p=0.121/0.121 n=690 | — | — |
| binary_merged | all | bias_index | — | — | +0.452 [+0.366, +0.536] p=0.0002/0.0002* n=690 | — | — |
| binary_merged | all | brier | — | — | +0.001 [-0.016, +0.020] p=0.887/0.887 n=690 | — | — |
| binary_merged | all | logloss | — | — | +0.017 [-0.026, +0.061] p=0.454/0.454 n=690 | — | — |
| binary_merged | all | ece | — | — | +0.004 [-0.032, +0.041] p=0.831/0.831 n=690 | — | — |
| binary_merged | all | rel | — | — | +0.006 [-0.010, +0.024] p=0.468/0.468 n=690 | — | — |
| binary_merged | all | res | — | — | +0.004 [-0.002, +0.011] p=0.213/0.213 n=690 | — | — |
| binary_merged | all | auroc | — | — | +0.093 [+0.052, +0.132] p=0.0002/0.0002* n=690 | — | — |
| binary_merged | all | brier_c | — | — | +0.001 [-0.016, +0.020] p=0.887/0.887 n=690 | — | — |
| binary_merged | all | ece_c | — | — | +0.009 [-0.028, +0.044] p=0.68/0.68 n=690 | — | — |
| binary_merged | all | auroc_c | — | — | +0.010 [-0.032, +0.051] p=0.643/0.643 n=690 | — | — |
| binary_merged | post | accuracy | — | — | +0.029 [-0.007, +0.064] p=0.121/0.121 n=690 | — | — |
| binary_merged | post | bias_index | — | — | +0.452 [+0.366, +0.536] p=0.0002/0.0002* n=690 | — | — |
| binary_merged | post | brier | — | — | +0.001 [-0.016, +0.020] p=0.887/0.887 n=690 | — | — |
| binary_merged | post | logloss | — | — | +0.017 [-0.026, +0.061] p=0.454/0.454 n=690 | — | — |
| binary_merged | post | ece | — | — | +0.004 [-0.032, +0.041] p=0.831/0.831 n=690 | — | — |
| binary_merged | post | rel | — | — | +0.006 [-0.010, +0.024] p=0.468/0.468 n=690 | — | — |
| binary_merged | post | res | — | — | +0.004 [-0.002, +0.011] p=0.213/0.213 n=690 | — | — |
| binary_merged | post | auroc | — | — | +0.093 [+0.052, +0.132] p=0.0002/0.0002* n=690 | — | — |
| binary_merged | post | brier_c | — | — | +0.001 [-0.016, +0.020] p=0.887/0.887 n=690 | — | — |
| binary_merged | post | ece_c | — | — | +0.009 [-0.028, +0.044] p=0.68/0.68 n=690 | — | — |
| binary_merged | post | auroc_c | — | — | +0.010 [-0.032, +0.051] p=0.643/0.643 n=690 | — | — |
| binary | all | accuracy | — | — | +0.287 [+0.225, +0.347] p=0.0002/0.0002* n=296 | — | — |
| binary | all | brier | — | — | -0.138 [-0.168, -0.107] p=0.0002/0.0002* n=296 | — | — |
| binary | all | logloss | — | — | -0.311 [-0.379, -0.241] p=0.0002/0.0002* n=296 | — | — |
| binary | all | ece | — | — | -0.165 [-0.198, -0.131] p=0.0002/0.0002* n=296 | — | — |
| binary | all | brier_c | — | — | -0.138 [-0.168, -0.107] p=0.0002/0.0002* n=296 | — | — |
| binary | all | ece_c | — | — | -0.234 [-0.287, -0.176] p=0.0002/0.0002* n=296 | — | — |
| binary | all | auroc_c | — | — | +0.145 [+0.054, +0.233] p=0.0014/0.0014* n=296 | — | — |
| binary | post | accuracy | — | — | +0.287 [+0.225, +0.347] p=0.0002/0.0002* n=296 | — | — |
| binary | post | brier | — | — | -0.138 [-0.168, -0.107] p=0.0002/0.0002* n=296 | — | — |
| binary | post | logloss | — | — | -0.311 [-0.379, -0.241] p=0.0002/0.0002* n=296 | — | — |
| binary | post | ece | — | — | -0.165 [-0.198, -0.131] p=0.0002/0.0002* n=296 | — | — |
| binary | post | brier_c | — | — | -0.138 [-0.168, -0.107] p=0.0002/0.0002* n=296 | — | — |
| binary | post | ece_c | — | — | -0.234 [-0.287, -0.176] p=0.0002/0.0002* n=296 | — | — |
| binary | post | auroc_c | — | — | +0.145 [+0.054, +0.233] p=0.0014/0.0014* n=296 | — | — |
| binary_perturbed | all | accuracy | — | — | -0.165 [-0.213, -0.117] p=0.0002/0.0002* n=394 | — | — |
| binary_perturbed | all | brier | — | — | +0.106 [+0.080, +0.132] p=0.0002/0.0002* n=394 | — | — |
| binary_perturbed | all | logloss | — | — | +0.263 [+0.200, +0.326] p=0.0002/0.0002* n=394 | — | — |
| binary_perturbed | all | ece | — | — | +0.088 [+0.064, +0.111] p=0.0002/0.0002* n=394 | — | — |
| binary_perturbed | all | brier_c | — | — | +0.106 [+0.080, +0.132] p=0.0002/0.0002* n=394 | — | — |
| binary_perturbed | all | ece_c | — | — | +0.125 [+0.063, +0.183] p=0.0002/0.0002* n=394 | — | — |
| binary_perturbed | all | auroc_c | — | — | -0.167 [-0.240, -0.091] p=0.0002/0.0002* n=394 | — | — |
| binary_perturbed | post | accuracy | — | — | -0.165 [-0.213, -0.117] p=0.0002/0.0002* n=394 | — | — |
| binary_perturbed | post | brier | — | — | +0.106 [+0.080, +0.132] p=0.0002/0.0002* n=394 | — | — |
| binary_perturbed | post | logloss | — | — | +0.263 [+0.200, +0.326] p=0.0002/0.0002* n=394 | — | — |
| binary_perturbed | post | ece | — | — | +0.088 [+0.064, +0.111] p=0.0002/0.0002* n=394 | — | — |
| binary_perturbed | post | brier_c | — | — | +0.106 [+0.080, +0.132] p=0.0002/0.0002* n=394 | — | — |
| binary_perturbed | post | ece_c | — | — | +0.125 [+0.063, +0.183] p=0.0002/0.0002* n=394 | — | — |
| binary_perturbed | post | auroc_c | — | — | -0.167 [-0.240, -0.091] p=0.0002/0.0002* n=394 | — | — |
| mcq | all | accuracy | — | — | +0.046 [+0.000, +0.091] p=0.0582/0.0582 n=435 | — | — |
| mcq | all | brier_c | — | — | -0.022 [-0.056, +0.013] p=0.219/0.219 n=435 | — | — |
| mcq | all | ece_c | — | — | -0.020 [-0.064, +0.027] p=0.395/0.395 n=435 | — | — |
| mcq | all | auroc_c | — | — | +0.051 [-0.006, +0.111] p=0.0804/0.0804 n=435 | — | — |
| mcq | post | accuracy | — | — | +0.046 [+0.000, +0.091] p=0.0582/0.0582 n=435 | — | — |
| mcq | post | brier_c | — | — | -0.022 [-0.056, +0.013] p=0.219/0.219 n=435 | — | — |
| mcq | post | ece_c | — | — | -0.020 [-0.064, +0.027] p=0.395/0.395 n=435 | — | — |
| mcq | post | auroc_c | — | — | +0.051 [-0.006, +0.111] p=0.0804/0.0804 n=435 | — | — |

## GPT-OSS 20B

| task | part | metric | B1 | B2 | C | D | E |
|---|---|---|---|---|---|---|---|
