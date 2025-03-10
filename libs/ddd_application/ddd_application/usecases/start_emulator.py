import logging
import threading
import time
from typing import Any

from confluent_kafka.admin import AdminClient, NewTopic
from domain.value_objects.emulation_id import EmulationID
from fastapi import BackgroundTasks

from ddd_application.dtos.emulation_dto import EmulationScheduledDTO, StartEmulatorDTO
from ddd_application.fake_factory.transaction_factory import TransactionFakeFactory

logger = logging.getLogger(__name__)


class StartEmulatorUseCase:
    def __init__(
        self,
        producer_mapping: dict[str, Any],
        kafka_brokers: str,
        topics_mapping: dict[str, str] = None,
    ):
        self.producer_mapping = producer_mapping
        self.kafka_brokers = kafka_brokers
        self.topics_mapping = topics_mapping or {
            "transaction": "transactions",
            "default": "default_topic",
        }
        self.fake_factories: dict[str, Any] = {
            "transaction": TransactionFakeFactory,
        }

    def create_topic(
        self, topic_name: str, num_partitions: int = 5, replication_factor: int = 2
    ):
        admin_client = AdminClient({"bootstrap.servers": self.kafka_brokers})
        metadata = admin_client.list_topics(timeout=10)
        if topic_name not in metadata.topics:
            topic = NewTopic(
                topic=topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
            )
            fs = admin_client.create_topics([topic])
            for topic, future in fs.items():
                try:
                    future.result()
                    logger.info(f"Topic {topic} created successfully")
                except Exception as e:
                    logger.error(f"Failed to create topic {topic}: {e}")
        else:
            logger.info(f"Topic {topic_name} already exists")

    def execute(
        self, dto: StartEmulatorDTO, background_tasks: BackgroundTasks, num_threads: int
    ) -> EmulationScheduledDTO:
        emulation_id = EmulationID.generate()
        sync_type = dto.emulator_sync.lower()

        producer = self.producer_mapping.get(sync_type)
        if producer is None:
            raise ValueError(f"Producer not found for sync type: {sync_type}")

        topic = self.topics_mapping.get(dto.emulation_domain.lower(), "default_topic")
        self.create_topic(topic)

        fake_factory_class = self.fake_factories.get(dto.emulation_domain.lower())
        if fake_factory_class is None:
            raise ValueError(f"Domain not supported: {dto.emulation_domain}")

        fake_factory = fake_factory_class()

        background_tasks.add_task(
            self._run_emulation_task,
            emulation_id,
            producer,
            topic,
            fake_factory,
            dto.timeout,
            num_threads,
        )

        return EmulationScheduledDTO(
            id=emulation_id,
            emulator_sync=dto.emulator_sync,
            emulation_domain=dto.emulation_domain,
            timeout=dto.timeout,
        )

    def produce_data(
        self, emulation_id, thread_id, producer, topic, stop_event, factory
    ):
        while not stop_event.is_set():
            fake_data = factory.generate()
            message_payload = {
                "emulation_id": str(emulation_id),
                "timestamp": time.time(),
                "data": fake_data,
            }
            try:
                producer.produce(
                    topic=topic,
                    key=fake_data["transaction_id"],
                    value=message_payload,
                )
                logger.info(
                    f" Thread {thread_id} - Produced message: {message_payload}"
                )
            except Exception as e:
                logger.error(f"Failed to produce message: {e}")

    def produce_data_in_parallel(
        self, emulation_id, producer, topic, factory, stop_event, num_threads
    ):
        threads = []
        try:
            for i in range(num_threads):
                thread = threading.Thread(
                    target=self.produce_data,
                    args=(
                        emulation_id,
                        i,
                        producer,
                        topic,
                        stop_event,
                        factory,
                    ),
                )
                thread.daemon = True
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
        except Exception as e:
            logger.error(f"Failed to start threads: {e}")

    def _run_emulation_task(
        self, emulation_id, producer, topic, factory, timeout, num_threads
    ):
        stop_event = threading.Event()
        timer = threading.Timer(timeout, stop_event.set)
        timer.start()

        self.produce_data_in_parallel(
            emulation_id, producer, topic, factory, stop_event, num_threads
        )
        timer.cancel()
        producer.flush()
        logger.info("Emulation finished")
