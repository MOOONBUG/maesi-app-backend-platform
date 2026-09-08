-- GPUOps additive schema: asset, snapshot, diagnostic audit.
CREATE TABLE IF NOT EXISTS gpu_host (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  hostname VARCHAR(128) NOT NULL,
  ip_address VARCHAR(45) NULL,
  environment VARCHAR(32) NOT NULL DEFAULT 'dev',
  driver_version VARCHAR(64) NULL,
  cuda_version VARCHAR(64) NULL,
  status ENUM('ONLINE','OFFLINE','UNKNOWN') NOT NULL DEFAULT 'UNKNOWN',
  last_seen_at DATETIME(3) NULL,
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id), UNIQUE KEY uk_gpu_host_hostname (hostname), KEY idx_gpu_host_status_seen (status,last_seen_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS gpu_snapshot (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, host_id BIGINT UNSIGNED NOT NULL, gpu_index INT NOT NULL,
  gpu_name VARCHAR(128) NULL, temperature_c DECIMAL(6,2) NULL, utilization_pct DECIMAL(6,2) NULL,
  memory_total_mb DECIMAL(12,2) NULL, memory_used_mb DECIMAL(12,2) NULL, power_draw_w DECIMAL(10,2) NULL,
  captured_at DATETIME(3) NOT NULL, PRIMARY KEY (id), KEY idx_gpu_snapshot_host_time (host_id,captured_at),
  CONSTRAINT fk_gpu_snapshot_host FOREIGN KEY (host_id) REFERENCES gpu_host(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS diagnostic_record (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, host_id BIGINT UNSIGNED NULL, question VARCHAR(2000) NOT NULL,
  severity ENUM('INFO','WARNING','CRITICAL') NOT NULL DEFAULT 'INFO', result_mode VARCHAR(32) NOT NULL,
  evidence_json JSON NULL, created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id), KEY idx_diagnostic_host_time (host_id,created_at), KEY idx_diagnostic_severity_time (severity,created_at),
  CONSTRAINT fk_diagnostic_host FOREIGN KEY (host_id) REFERENCES gpu_host(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
