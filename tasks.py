import time

from celery_app import app


@app.task(name="kbj.process_request")
def process_request(app_id, req_type, message, routing_key=""):
    req_type = req_type.upper()
    if req_type == "LONG":
        time.sleep(2)
        result = f"Hasil kompleks: {message} diselesaikan"
    elif req_type == "SHORT":
        result = f"Echo: {message}"
    else:
        raise ValueError(f"Tipe request tidak dikenal: {req_type}")

    print(
        f"[WORKER] app_id={app_id} type={req_type} "
        f"routing_key={routing_key or '-'} result={result}",
        flush=True,
    )
    return {
        "app_id": app_id,
        "req_type": req_type,
        "routing_key": routing_key,
        "result": result,
    }
