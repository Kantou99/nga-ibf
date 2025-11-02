# Production Deployment & Operations Guide
## Nigeria Impact-Based Forecasting System v2.0

---

## Executive Summary

This document provides complete deployment and operational procedures for the world-class Nigeria IBF system. The system is production-ready with enterprise-grade features including automated quality control, real-time monitoring, and sophisticated multi-hazard modeling.

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                      │
├───────────────┬──────────────────┬─────────────────────────┤
│ GloFAS Floods │ ACLED Conflict   │ Population/Exposure     │
└───────┬───────┴────────┬─────────┴──────────┬──────────────┘
        │                │                     │
        ▼                ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   PROCESSING LAYER                           │
├─────────────────────────────────────────────────────────────┤
│ • Hazard Processing      • Quality Control                   │
│ • ML Vulnerability       • Multi-Hazard Interaction          │
│ • Uncertainty Analysis   • Impact Calculation                │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    DECISION LAYER                            │
├─────────────────────────────────────────────────────────────┤
│ • Alert Generation       • Performance Metrics               │
│ • Risk Assessment        • Forecast Validation               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   DISSEMINATION LAYER                        │
├───────────────┬──────────────────┬─────────────────────────┤
│ Email Alerts  │ SMS Notifications│ API/Dashboard           │
└───────────────┴──────────────────┴─────────────────────────┘
```

---

## System Requirements

### Hardware Requirements

**Minimum (Development)**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB SSD
- Network: 10 Mbps

**Recommended (Production)**
- CPU: 16+ cores (Intel Xeon or AMD EPYC)
- RAM: 64 GB
- Storage: 500 GB NVMe SSD
- Network: 100+ Mbps with low latency
- Backup: 1 TB network storage

**Optimal (High-Performance)**
- CPU: 32+ cores
- RAM: 128 GB
- Storage: 1 TB NVMe SSD RAID
- GPU: NVIDIA A100 or V100 (optional, for ML training)
- Network: 1 Gbps dedicated

### Software Requirements

```yaml
Operating System:
  - Ubuntu 22.04 LTS (recommended)
  - CentOS 8+ or RHEL 8+
  - Windows Server 2019+ (not recommended)

Python: 3.9 - 3.11

Core Dependencies:
  - climada>=4.0.0
  - numpy>=1.21.0
  - pandas>=1.3.0
  - geopandas>=0.10.0
  - xarray>=0.20.0
  - scikit-learn>=1.0.0
  - scipy>=1.7.0
  - matplotlib>=3.4.0
  - pyyaml>=6.0
  - joblib>=1.1.0

Optional (Production):
  - redis>=4.0 (caching)
  - postgresql>=13 (database)
  - nginx (web server)
  - supervisor (process management)
  - prometheus + grafana (monitoring)
```

---

## Installation Guide

### 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y \
    build-essential \
    python3.9 \
    python3.9-dev \
    python3-pip \
    git \
    libgeos-dev \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    postgresql-13 \
    redis-server \
    nginx

# Create application user
sudo useradd -r -m -s /bin/bash nigeria-ibf
sudo usermod -aG sudo nigeria-ibf
```

### 2. Application Setup

```bash
# Switch to application user
sudo su - nigeria-ibf

# Clone repository
git clone https://github.com/your-org/nigeria-ibf.git
cd nigeria-ibf

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Install system
pip install -e .
```

### 3. Configuration

```bash
# Create configuration directory
mkdir -p config logs data/centroids outputs

# Generate production configuration
python -m config --generate-config production

# Edit configuration file
nano config/config_prod.yaml
```

**Key Configuration Items:**

```yaml
# config/config_prod.yaml
environment: production

paths:
  data_dir: /data/nigeria-ibf
  output_dir: /data/outputs
  logs_dir: /var/log/nigeria-ibf
  
forecast:
  lead_times: [0.5, 1, 1.5, 2, 2.5, 3, 5, 7]
  update_frequency_hours: 12
  
uncertainty:
  n_samples: 5000
  
compute:
  n_cores: -1  # Use all available
  use_gpu: false
  
alert:
  enable_email: true
  enable_sms: true
  enable_api_webhook: true
  alert_recipients:
    emergency:
      - operations@nema.gov.ng
      - director@nema.gov.ng
      - emergency@nigeria.gov.ng
```

### 4. Database Setup

```bash
# Create database
sudo -u postgres psql
CREATE DATABASE nigeria_ibf;
CREATE USER ibf_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE nigeria_ibf TO ibf_user;
\q

# Initialize database schema
python scripts/init_database.py
```

### 5. Data Preparation

```bash
# Generate centroids
python -m nigeria_data_preparation --create-centroids

# Prepare historical events database
python -m nigeria_data_preparation --prepare-events \
    --dtm-files data/raw/dtm/*.xlsx \
    --acled-files data/raw/acled/*.csv

# Verify data
python scripts/verify_data.py
```

---

## Operational Procedures

### Daily Operations

#### 1. Automated Forecast Execution

**Cron Schedule** (runs at 00:00 and 12:00 UTC):

```bash
# Add to crontab: crontab -e
0 0,12 * * * /home/nigeria-ibf/run_forecast.sh

# /home/nigeria-ibf/run_forecast.sh
#!/bin/bash
set -e

cd /home/nigeria-ibf/nigeria-ibf
source venv/bin/activate

export NIGERIA_IBF_ENV=production

# Run forecast
python -m production_forecast_engine \
    --environment production \
    --forecast-date $(date +%Y-%m-%d) \
    --lead-time 2.0 \
    --hazards flood conflict \
    >> /var/log/nigeria-ibf/forecast_$(date +%Y%m%d_%H%M).log 2>&1

# Check exit code
if [ $? -eq 0 ]; then
    echo "Forecast completed successfully"
    # Send success notification
    python scripts/notify_success.py
else
    echo "Forecast failed"
    # Send failure alert
    python scripts/notify_failure.py
    exit 1
fi
```

#### 2. Manual Forecast Execution

```bash
# Activate environment
cd /home/nigeria-ibf/nigeria-ibf
source venv/bin/activate

# Run forecast
python -m production_forecast_engine \
    --environment production \
    --forecast-date 2025-01-20 \
    --lead-time 2.0 \
    --hazards flood conflict

# Check results
ls -lh outputs/*/
```

#### 3. Monitoring and Health Checks

```bash
# Check system status
python scripts/system_status.py

# View recent forecasts
python scripts/forecast_history.py --days 7

# Check quality metrics
python scripts/quality_report.py --date today

# Monitor resource usage
htop
df -h
```

### Weekly Procedures

#### 1. Model Retraining

```bash
# Update vulnerability models with new data
python scripts/retrain_models.py \
    --start-date 2024-01-01 \
    --end-date $(date +%Y-%m-%d)

# Validate new models
python scripts/validate_models.py

# Deploy if performance improved
python scripts/deploy_models.py
```

#### 2. Performance Review

```bash
# Generate weekly performance report
python scripts/weekly_report.py \
    --output reports/weekly_$(date +%Y%m%d).pdf

# Compare forecasts vs actuals
python scripts/validation_report.py --week last
```

#### 3. Data Backup

```bash
# Backup all data
./scripts/backup.sh

# Verify backups
./scripts/verify_backup.sh
```

### Monthly Procedures

#### 1. System Validation

```bash
# Run comprehensive validation
python test_suite.py --suite all

# Run historical replay tests
python scripts/historical_replay.py \
    --start-date 2024-01-01 \
    --end-date 2024-12-31

# Generate validation report
python scripts/validation_summary.py --month last
```

#### 2. Parameter Calibration

```bash
# Recalibrate vulnerability parameters
python scripts/calibrate_vulnerability.py \
    --historical-data data/2024_events.xlsx

# Update configuration
python scripts/update_config.py --calibrated-params params.json
```

#### 3. Documentation Update

```bash
# Update operational metrics
python scripts/update_metrics_dashboard.py

# Generate monthly report
python scripts/monthly_report.py
```

---

## Monitoring and Alerting

### System Metrics

**Key Performance Indicators (KPIs):**

1. **Forecast Quality**
   - Bias: Target ±10%
   - MAE: Target <25%
   - ROC-AUC: Target >0.75
   - Hit Rate: Target >75%

2. **System Performance**
   - Forecast completion time: <30 minutes
   - System uptime: >99.5%
   - Data freshness: <6 hours
   - Alert delivery time: <5 minutes

3. **Operational Metrics**
   - Forecasts per day: 2 (00:00 and 12:00 UTC)
   - False alarm rate: <20%
   - Alert response time: <1 hour
   - Data completeness: >95%

### Prometheus Metrics

```yaml
# /etc/prometheus/prometheus.yml
scrape_configs:
  - job_name: 'nigeria_ibf'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 30s
    
# Custom metrics exported
metrics:
  - nigeria_ibf_forecast_duration_seconds
  - nigeria_ibf_forecast_quality_score
  - nigeria_ibf_displacement_forecast_total
  - nigeria_ibf_alert_level
  - nigeria_ibf_processing_errors_total
  - nigeria_ibf_data_freshness_seconds
```

### Grafana Dashboards

**Dashboard Components:**

1. **Operational Overview**
   - Current forecast status
   - Recent alerts
   - System health
   - Data pipeline status

2. **Forecast Performance**
   - Forecast accuracy trends
   - Uncertainty quantification
   - Alert distribution
   - State-level breakdown

3. **System Performance**
   - Processing times
   - Resource utilization
   - Error rates
   - Queue depths

### Alert Rules

```yaml
# Prometheus alert rules
groups:
  - name: nigeria_ibf_alerts
    rules:
      - alert: ForecastFailed
        expr: nigeria_ibf_last_forecast_success == 0
        for: 1h
        labels:
          severity: critical
        annotations:
          summary: "Forecast execution failed"
          
      - alert: HighDisplacementForecast
        expr: nigeria_ibf_displacement_forecast_total > 50000
        labels:
          severity: warning
        annotations:
          summary: "High displacement forecast detected"
          
      - alert: DataStale
        expr: nigeria_ibf_data_freshness_seconds > 21600  # 6 hours
        labels:
          severity: warning
        annotations:
          summary: "Input data is stale"
          
      - alert: LowQualityScore
        expr: nigeria_ibf_forecast_quality_score < 0.5
        labels:
          severity: warning
        annotations:
          summary: "Forecast quality score below threshold"
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Forecast Execution Fails

**Symptoms:**
- Script exits with error
- No output files generated
- Log shows exceptions

**Diagnosis:**
```bash
# Check logs
tail -100 /var/log/nigeria-ibf/forecast_latest.log

# Check system resources
free -h
df -h

# Verify data availability
python scripts/check_data.py
```

**Solutions:**
- Insufficient memory: Reduce `n_samples` in config
- Missing data: Check data pipeline
- Permission issues: Fix file permissions
- Dependency issues: Reinstall packages

#### 2. Poor Forecast Quality

**Symptoms:**
- Quality score < 0.5
- High uncertainty ranges
- Frequent false alarms

**Diagnosis:**
```bash
# Run diagnostics
python scripts/diagnose_quality.py --forecast-id <ID>

# Check input data quality
python scripts/validate_inputs.py
```

**Solutions:**
- Retrain vulnerability models
- Recalibrate regional parameters
- Update hazard processing algorithms
- Review historical validation

#### 3. Alert Distribution Fails

**Symptoms:**
- Alerts not received by users
- Email bounces
- SMS failures

**Diagnosis:**
```bash
# Check alert logs
grep "Alert" /var/log/nigeria-ibf/forecast_latest.log

# Test email configuration
python scripts/test_email.py

# Test SMS gateway
python scripts/test_sms.py
```

**Solutions:**
- Verify email server configuration
- Check SMS gateway credentials
- Update recipient lists
- Test webhook endpoints

---

## Performance Optimization

### Computational Optimization

```python
# config optimization for faster processing

# Development (fast iteration)
uncertainty:
  n_samples: 500
forecast:
  lead_times: [1, 2, 3]
  
# Production (full analysis)
uncertainty:
  n_samples: 5000
forecast:
  lead_times: [0.5, 1, 1.5, 2, 2.5, 3, 5, 7]
  
compute:
  n_cores: -1  # Use all cores
  cache_intermediate_results: true
```

### Database Optimization

```sql
-- Create indices for faster queries
CREATE INDEX idx_forecasts_date ON forecasts(forecast_date);
CREATE INDEX idx_forecasts_state ON forecasts(state);
CREATE INDEX idx_alerts_level ON alerts(alert_level);

-- Partition large tables
CREATE TABLE forecasts_2025 PARTITION OF forecasts
  FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

### Caching Strategy

```python
# Enable Redis caching for frequently accessed data
cache_config:
  enable: true
  backend: redis
  redis_host: localhost
  redis_port: 6379
  cache_ttl: 3600  # 1 hour
  
  cache_items:
    - centroids
    - vulnerability_parameters
    - historical_statistics
```

---

## Security Best Practices

### Access Control

```bash
# File permissions
chmod 600 config/config_prod.yaml  # Config files
chmod 700 scripts/*.sh  # Shell scripts
chmod 755 venv/  # Virtual environment

# User permissions
sudo usermod -aG nigeria-ibf <username>
```

### API Security

```python
# API authentication configuration
api:
  authentication:
    method: token  # or oauth2
    token_expiry: 3600
    
  rate_limiting:
    enabled: true
    max_requests_per_hour: 100
    
  encryption:
    ssl_enabled: true
    certificate: /etc/ssl/nginx.crt
    key: /etc/ssl/nginx.key
```

### Data Protection

```bash
# Encrypt sensitive data at rest
sudo cryptsetup luksFormat /dev/sdb1
sudo cryptsetup open /dev/sdb1 encrypted_data

# Encrypt backups
tar -czf - data/ | gpg --encrypt --recipient admin@example.com > backup.tar.gz.gpg
```

---

## Disaster Recovery

### Backup Strategy

**Daily Backups:**
- Forecast outputs
- Configuration files
- Logs (last 7 days)

**Weekly Backups:**
- Complete database
- Model files
- Historical data

**Monthly Backups:**
- Full system image
- Documentation
- Source code

### Recovery Procedures

**Minor Issues (< 1 hour downtime):**
1. Restart services
2. Clear cache
3. Rerun failed forecasts

**Major Issues (> 1 hour downtime):**
1. Restore from backup
2. Verify data integrity
3. Resume operations
4. Notify stakeholders

**Complete System Failure:**
1. Deploy to backup server
2. Restore database
3. Reconfigure services
4. Full system verification
5. Incident report

### Recovery Time Objectives (RTO)

- **Critical Functions:** < 4 hours
- **Standard Operations:** < 24 hours
- **Historical Analysis:** < 72 hours

---

## Contact Information

### Support Tiers

**Tier 1: Operations Team**
- Email: operations@nema.gov.ng
- Phone: +234-XXX-XXX-XXXX
- Hours: 24/7
- Response Time: 1 hour

**Tier 2: Technical Team**
- Email: tech@nema.gov.ng
- Phone: +234-XXX-XXX-XXXX
- Hours: 08:00-18:00 WAT
- Response Time: 4 hours

**Tier 3: Development Team**
- Email: dev@nigeria-ibf.org
- Hours: On-call rotation
- Response Time: 24 hours

### Escalation Matrix

```
Level 1: System Warning → Operations Team
Level 2: System Error → Technical Team
Level 3: System Failure → Development Team + Management
Level 4: Critical Incident → All Teams + Executive Leadership
```

---

## Appendix

### A. File Structure

```
nigeria-ibf/
├── config/
│   ├── config_dev.yaml
│   ├── config_staging.yaml
│   └── config_prod.yaml
├── data/
│   ├── centroids/
│   ├── hazards/
│   ├── exposure/
│   └── historical/
├── outputs/
│   └── YYYYMMDD_HH/
│       ├── forecast_results.csv
│       ├── metrics.json
│       ├── alert.json
│       └── alert_message.txt
├── logs/
│   └── ibf_YYYYMMDD_HHMMSS.log
├── models/
│   ├── flood_vulnerability_rf_v1.pkl
│   └── conflict_vulnerability_rf_v1.pkl
├── scripts/
│   ├── run_forecast.sh
│   ├── backup.sh
│   └── monitor.sh
├── src/
│   ├── config.py
│   ├── advanced_multi_hazard.py
│   ├── production_forecast_engine.py
│   └── test_suite.py
└── docs/
    ├── DEPLOYMENT.md
    ├── API.md
    └── USER_GUIDE.md
```

### B. Environment Variables

```bash
# ~/.bashrc or /etc/environment
export NIGERIA_IBF_ENV=production
export NIGERIA_IBF_HOME=/home/nigeria-ibf/nigeria-ibf
export NIGERIA_IBF_CONFIG=/home/nigeria-ibf/config/config_prod.yaml
export NIGERIA_IBF_DATA=/data/nigeria-ibf
export NIGERIA_IBF_LOGS=/var/log/nigeria-ibf
```

### C. Service Management

```bash
# Create systemd service
sudo nano /etc/systemd/system/nigeria-ibf-forecast.service

[Unit]
Description=Nigeria IBF Forecast Service
After=network.target

[Service]
Type=simple
User=nigeria-ibf
WorkingDirectory=/home/nigeria-ibf/nigeria-ibf
ExecStart=/home/nigeria-ibf/nigeria-ibf/venv/bin/python -m production_forecast_engine
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable nigeria-ibf-forecast
sudo systemctl start nigeria-ibf-forecast
sudo systemctl status nigeria-ibf-forecast
```

---

**Document Version:** 2.0.0  
**Last Updated:** October 14, 2025  
**Next Review:** January 14, 2026
