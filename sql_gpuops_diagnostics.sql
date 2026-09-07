-- AppCore Service Platform diagnostic migration
CREATE TABLE IF NOT EXISTS diagnostic_record (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  host_id INT NULL,
  question VARCHAR(2000) NOT NULL,
  severity ENUM('INFO','WARNING','CRITICAL') NOT NULL DEFAULT 'INFO',
  result_mode VARCHAR(32) NOT NULL DEFAULT 'pending',
  evidence_json JSON NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_diagnostic_created_at (created_at),
  INDEX idx_diagnostic_severity (severity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
