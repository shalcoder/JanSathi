# Failure Mode Analysis & Reliability (AWS Stack)

## System-Level Failure Modes

| Component | Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Mobile App (Flutter)** | No Internet Connectivity | User cannot send queries | **Offline-First Cache:** Top 50 FAQs stored locally (Hive/SQLite). Sync when back online. |
| **AWS Lambda** | Cold Start / Timeout | Latency spike causing bad UX | **Provisioned Concurrency:** Keep warm instances. Set timeout to 29s (API Gateway limit). |
| **Amazon Bedrock** | ThrottlingException | Response failure | **Exponential Backoff:** Retry with jitter. Fallback to lighter model (e.g., Haiku instead of Sonnet). |
| **Amazon Kendra** | Index Sync Latency | Stale data | **Scheduled Crawling:** Force sync updates on document upload via Lambda. |
| **AWS Transcribe** | Low Confidence / Accents | Incorrect text | **Confirmation UI:** If confidence < 60%, return text to user for 'Yes/No' confirmation before processing. |
| **Amazon Connect (IVR)** | User Hangup / Drop | Incomplete Session | **State Persistence:** Save session state to DynamoDB immediately. SMS follow-up with answer. |

## Recovery Point Objective (RPO) & Recovery Time Objective (RTO)

- **RPO:** < 1 minute (DynamoDB Streams & Point-in-Time Recovery).
- **RTO:** < 5 minutes (Infrastructure as Code - Terraform/CDK redeploy).

## Circuit Breaker Logic (Lambda Orchestrator)

```python
def safe_invoke_service(service_func, fallback_value):
    try:
        return service_func()
    except ClientError as e:
        if e.response['Error']['Code'] == 'ThrottlingException':
            log_error("Service Throttled")
            return fallback_value
        raise e
    except ReadTimeoutError:
        log_error("Service timeout")
        return fallback_value
```

## Offline Strategy
If **Internet** is down → App switches to "Offline Mode".
- **Voice Disabled**: "Please type or connect to internet."
- **Local FAQs**: "How to apply for PM-KISAN?" (Served from local JSON).
- **Queueing**: Non-urgent queries queued to sync later.
