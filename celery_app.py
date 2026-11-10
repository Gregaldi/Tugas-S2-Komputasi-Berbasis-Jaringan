import os

from celery import Celery
from kombu import Exchange, Queue

BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
FANOUT_EXCHANGE = "kbj.fanout"
TOPIC_EXCHANGE = "kbj.topic"

default_exchange = Exchange("kbj.direct", type="direct", durable=True)
fanout_exchange = Exchange(FANOUT_EXCHANGE, type="fanout", durable=True)
topic_exchange = Exchange(TOPIC_EXCHANGE, type="topic", durable=True)

app = Celery("kbj", broker=BROKER_URL)
app.conf.update(
    task_queues=(
        Queue("default", default_exchange, routing_key="default"),
        Queue("fanout.audit", fanout_exchange, routing_key=""),
        Queue("fanout.analytics", fanout_exchange, routing_key=""),
        Queue("topic.short", topic_exchange, routing_key="job.short.*"),
        Queue("topic.long", topic_exchange, routing_key="job.long.*"),
        Queue("wildcard.one", topic_exchange, routing_key="job.*.created"),
        Queue("wildcard.many", topic_exchange, routing_key="job.#"),
    ),
    task_default_queue="default",
    task_default_exchange=default_exchange.name,
    task_default_exchange_type="direct",
    task_default_routing_key="default",
    task_create_missing_queues=False,
    imports=("tasks",),
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    timezone="Asia/Jakarta",
    enable_utc=True,
)

