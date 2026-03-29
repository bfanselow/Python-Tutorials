## Event Processing Architectures

### Event-Driven vs Streaming-First: Conceptual Difference

#### Event-Driven
Focus: Individual events as they occur
How it works: A producer emits an event → a consumer reacts → optional state management
Examples:
 * Traditional message queues (Celery, SQS, RabbitMQ)
 * Webhooks
Characteristics:
* Often stateless consumers
* Events may be transient (once consumed, often gone)
* Good for fire-and-forget notifications or tasks

Analogy: Someone rings a doorbell (event), and you react immediately—then it’s done.

#### Streaming-First
Focus: Continuous, durable flow of data
How it works:
 * Data is written to a persistent, append-only log or table
 * Consumers process it continuously, often with stateful operations
 * Late-arriving or repeated data can be replayed or reprocessed
Examples:
 * Apache Spark Structured Streaming
 * Delta Live Tables on Databricks
 * Apache Kafka + stream processing
Characteristics:
 * Built for real-time analytics, aggregation, and stateful operations
 * Durable storage of events/signals
 * Supports complex time-windowed computations (thresholds, deduplication, suppression)

Analogy: A conveyor belt continuously carries packages (signals), and workers can inspect, aggregate, and react—but the belt never loses history, so you can pause, rewind, or reprocess packages.
