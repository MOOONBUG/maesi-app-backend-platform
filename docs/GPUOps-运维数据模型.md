# GPUOps 运维数据模型

`gpu_host` 保存资产、驱动/CUDA版本和心跳状态。
`gpu_snapshot` 保存 GPU 温度、利用率、显存和功耗时间序列。
`diagnostic_record` 保存诊断问题、严重级别、回答模式和证据摘要。

生产环境建议：DCGM Exporter + Prometheus 负责指标，MySQL 只保留资产、诊断和审计事实；采集失败记录错误，不写入伪造的 0 值。
