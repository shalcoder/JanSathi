# Failure Mode Analysis & Reliability

## System-Level Failure Modes

| Component | Failure Mode | Impact | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Mobile App** | No Internet Connectivity | User cannot send queries | **Offline-First Cache:** Top 50 FAQs stored locally (SQLite/Hive). Seamless retry when back online. |
| **API Gateway** | DDoS / Traffic Spike | System latency / downtime | **Throttling & WAF:** AWS WAF to block malicious IPs. Usage plans to rate-limit non-essential traffic. |
| **Amazon Transcribe** | Low Confidence / Accents | Incorrect text interpretation | **Fallback & Confirmation:** If confidence < 60%, app asks user to confirm via Yes/No buttons or retry. |
| **Amazon Bedrock** | LLM Hallucination | Misinformation (Dangerous) | **Strict RAG:** Temperature set to 0. System prompt explicitly forbids answering outside retrieved context. |
| **Amazon Kendra** | Data Staleness | Outdated market prices | **Scheduled Syllabus:** Lambda cron jobs update Kendra index every 6 hours from government APIs. |
| **DynamoDB** | Hot Partition Key | Database throttling | **Sharding Strategy:** Use randomized partition keys (e.g., `UserId + Date` bucketing) to distribute load. |

## Recovery Point Objective (RPO) & Recovery Time Objective (RTO)

- **RPO:** < 1 minute (Conversation state is crucial, but re-asking is acceptable).
- **RTO:** < 5 minutes (Serverless architecture automatically spins up; dependency failures handled by circuit breakers).

## Circuit Breaker Logic (Lambda Orchestrator)

```python
def safe_invoke_service(service_func, fallback_value):
    try:
        return service_func()
    except TimeOutError:
        log_error("Service timeout")
        return fallback_value
    except ServiceUnavailable:
        return fallback_value
```

If **Google/Mandi API** is down → Return "Service currently unavailable, showing last known prices from yesterday."
