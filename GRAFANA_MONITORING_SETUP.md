# Grafana Setup Guide for StartupScout

This guide will help you set up Grafana dashboards to visualize your StartupScout Prometheus metrics.

## Prerequisites

- Docker and Docker Compose installed
- StartupScout API running on `localhost:8000`
- Basic understanding of Prometheus and Grafana

## Step-by-Step Setup

### 1. Create Required Directories

```bash
mkdir -p grafana/{dashboards,provisioning/{datasources,dashboards}}
mkdir -p monitoring
```

### 2. Start Grafana and Prometheus

```bash
# Start the monitoring stack
docker-compose -f docker-compose.grafana.yml up -d

# Check if services are running
docker-compose -f docker-compose.grafana.yml ps
```

### 3. Access Grafana

1. **Open Grafana**: http://localhost:3000
2. **Login**:
   - Username: `admin`
   - Password: `admin123`

### 4. Verify Data Source

1. Go to **Configuration** → **Data Sources**
2. You should see **Prometheus** data source already configured
3. Click on it and test the connection
4. Should show "Data source is working"

### 5. Import Dashboards

The dashboards are automatically imported from the `grafana/dashboards/` directory:

- **StartupScout Overview**: General metrics and performance
- **StartupScout Cost Analysis**: LLM cost tracking and efficiency

### 6. Generate Some Data

Make some API requests to generate metrics:

```bash
# Generate sample data
curl "http://localhost:8000/ask?question=What are key startup metrics?"
curl "http://localhost:8000/ask?question=How to calculate CAC?"
curl "http://localhost:8000/ask?question=What is product-market fit?"
```

## Available Dashboards

### StartupScout Overview Dashboard

**Panels:**

- **Request Rate**: Real-time request rate by endpoint
- **LLM Cost**: Total cost by model with thresholds
- **RAG Query Duration**: Performance percentiles
- **LLM Token Usage**: Token consumption by type
- **Error Rate**: Error tracking by component

### Cost Analysis Dashboard

**Panels:**

- **Total LLM Cost Over Time**: Hourly cost trends
- **Cost Per 1K Tokens**: Cost efficiency metrics
- **Token Usage by Type**: Pie chart of token distribution
- **Cost Efficiency Trend**: Rate of cost accumulation

## Configuration Options

### Grafana Configuration

Edit `docker-compose.grafana.yml` to customize:

```yaml
environment:
  - GF_SECURITY_ADMIN_PASSWORD=your_password
  - GF_USERS_ALLOW_SIGN_UP=true # Enable user registration
  - GF_INSTALL_PLUGINS=grafana-piechart-panel,grafana-worldmap-panel
```

### Prometheus Configuration

Edit `monitoring/prometheus.yml` to adjust:

```yaml
global:
  scrape_interval: 15s # How often to scrape metrics

scrape_configs:
  - job_name: "startupscout"
    scrape_interval: 5s # How often to scrape your app
```

## Key Metrics to Monitor

### Critical Alerts

Set up alerts for:

- **High Cost**: `startupscout_llm_cost_usd_total > 10`
- **High Error Rate**: `rate(startupscout_errors_total[5m]) > 1`
- **Slow Performance**: `startupscout_rag_query_duration_seconds > 10`

### Business Metrics

Track these KPIs:

- **Daily Cost**: `increase(startupscout_llm_cost_usd_total[1d])`
- **Request Volume**: `rate(startupscout_requests_total[1h])`
- **Success Rate**: `rate(startupscout_rag_queries_total{status="success"}[5m]) / rate(startupscout_rag_queries_total[5m])`

## Updating Dashboards

### Add New Panels

1. Go to **Dashboards** → **StartupScout Overview**
2. Click **Add Panel**
3. Use Prometheus queries like:

   ```promql
   # Average answer length
   avg(startupscout_answer_length_chars)

   # Context utilization rate
   avg(startupscout_context_utilization_ratio)

   # Vector search performance
   histogram_quantile(0.95, rate(startupscout_vector_search_duration_seconds[5m]))
   ```

### Custom Queries

Common Prometheus queries for StartupScout:

```promql
# Total requests in last hour
increase(startupscout_requests_total[1h])

# Cost per request
startupscout_llm_cost_usd_total / startupscout_requests_total

# Average tokens per request
startupscout_llm_tokens_total / startupscout_requests_total

# Error percentage
rate(startupscout_errors_total[5m]) / rate(startupscout_requests_total[5m]) * 100
```

## Troubleshooting

### Common Issues

1. **No Data in Grafana**

   ```bash
   # Check if Prometheus is scraping
   curl http://localhost:9090/targets

   # Check if metrics endpoint works
   curl http://localhost:8000/metrics
   ```

2. **Connection Issues**

   ```bash
   # Restart services
   docker-compose -f docker-compose.grafana.yml restart

   # Check logs
   docker-compose -f docker-compose.grafana.yml logs
   ```

3. **Missing Metrics**
   ```bash
   # Generate some requests first
   for i in {1..10}; do
     curl "http://localhost:8000/ask?question=Test question $i"
   done
   ```

### Useful Commands

```bash
# View Grafana logs
docker logs startupscout-grafana

# View Prometheus logs
docker logs startupscout-prometheus

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Restart everything
docker-compose -f docker-compose.grafana.yml down
docker-compose -f docker-compose.grafana.yml up -d
```

## Customization

### Adding New Dashboards

1. Create a new JSON file in `grafana/dashboards/`
2. Use the Grafana UI to create the dashboard
3. Export the JSON and save it to the directory
4. Restart Grafana to auto-import

### Alerting

Set up alerts by:

1. Go to **Alerting** → **Alert Rules**
2. Create new rules using your metrics
3. Configure notification channels (email, Slack, etc.)

## Next Steps

1. **Set up alerts** for critical metrics
2. **Create custom dashboards** for your specific needs
3. **Configure notification channels** (email, Slack, PagerDuty)
4. **Set up retention policies** for long-term data storage
5. **Add more data sources** (databases, logs, etc.)

## Useful Links

- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [StartupScout Metrics Reference](./README.md#monitoring)

---

**You're all set!** Your StartupScout metrics are now beautifully visualized in Grafana!
