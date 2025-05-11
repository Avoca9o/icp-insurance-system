from prometheus_client import Counter

SUCCESS_COUNTER = Counter('policy_holder_bot_requests_success', 'Число успешных запросов')
FAILURE_COUNTER = Counter('policy_holder_bot_requests_failure', 'Число неудачных запросов')
