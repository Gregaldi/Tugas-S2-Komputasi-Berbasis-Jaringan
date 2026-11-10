import argparse
import uuid

from celery_app import FANOUT_EXCHANGE, TOPIC_EXCHANGE
from tasks import process_request

ROUTES = {
    "topic": ["job.short.created", "job.long.created"],
    "wildcard": [
        "job.short.created",
        "job.long.created",
        "job.short.completed",
        "job.created",
    ],
}


def publish(mode, count):
    for index in range(count):
        app_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
        req_type = "LONG" if index % 2 else "SHORT"
        message = f"Pesan contoh nomor {index + 1}"

        if mode == "fanout":
            routing_key = ""
            exchange = FANOUT_EXCHANGE
        else:
            routing_key = ROUTES[mode][index % len(ROUTES[mode])]
            exchange = TOPIC_EXCHANGE

        result = process_request.apply_async(
            args=[app_id, req_type, message, routing_key],
            exchange=exchange,
            routing_key=routing_key,
        )
        print(
            f"[PRODUCER] mode={mode} app_id={app_id} "
            f"routing_key={routing_key or '-'} task_id={result.id}"
        )


def main():
    parser = argparse.ArgumentParser(description="Generator pesan demo Celery KBJ")
    parser.add_argument(
        "--mode",
        choices=("fanout", "topic", "wildcard", "all"),
        default="all",
    )
    parser.add_argument("--count", type=int, default=4)
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count minimal 1")

    modes = ("fanout", "topic", "wildcard") if args.mode == "all" else (args.mode,)
    for mode in modes:
        publish(mode, args.count)


if __name__ == "__main__":
    main()
