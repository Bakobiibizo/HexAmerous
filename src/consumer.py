import threading
from concurrent.futures import ThreadPoolExecutor
import pika
import os
from dotenv import load_dotenv
from run_executor.main import ExecuteRun

load_dotenv()

RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")


class RabbitMQConsumer:
    def __init__(
        self, max_workers=5
    ):  # max_workers can be adjusted based on demand # noqa
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=30,
            )
        )
        self.channel = self.connection.channel()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def process_message(self, body):
        run_id = body.decode("utf-8")
        print(f"Processing {run_id}")
        run = ExecuteRun(run_id)
        run.execute()
        # Insert your Run Executor pipeline logic here

    def callback(self, ch, method, properties, body):
        self.executor.submit(self.process_message, body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self, queue_name):
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=self.callback, auto_ack=False
        )
        print("Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()


consumer = RabbitMQConsumer()
consumer.start_consuming("runs_queue")
