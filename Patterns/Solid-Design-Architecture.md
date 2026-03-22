## Demonstrating some SOLID design principles

Suppose we want to design an Alerting System that does queries on telemetry and log data to find issues that need attention.  The telemetry and log data come from multiple different systems, each with a different owner.  We want various queries to search the different systems at configurable intervals, and produce Alerts to are dispatched to the system owners.  Since the system owners are the experts of their systems and know the telemetry/logging produced by their systems, we want them to own the development of the Alerts for their system.

The following outlines design goals for such a system which illustrate good design principles for any type of system.

### Design Goals
#### 1) Scalability: The system must scale with both the number of Signal-Generators and the volume of signals produced.
Centralized scheduler + queue-based decoupling
  * Support many independent Signal-Generators without adding orchestration complexity
  * Efficiently handle high signal throughput without overwhelming downstream systems
  * Allow horizontal scaling of consumers (e.g., dispatch workers)

#### 2) Separation of Concerns & Modularity
The system must enforce clear boundaries between components and allow independent evolution.
* Signal generation (producer), transport, and consumers are fully decoupled
* Queue implementation is swappable (SQS, Kafka, Delta, etc.)
* New Signal-generators automatically "register" with the system - plug-n-play
* Alerting-dispatch is just one consumer, not baked into Signal-generation
* Future consumers (analytics, automation) can be added without modifying producers

#### 3) Self-Service & Distributed Ownership
Domain teams (system owners) should be able to define and manage their own Signals with minimal platform involvement. Goal: "Own your signals without needing to understand the system internals"
* Provide a sandbox development layer (Databricks notebooks + templates)
* Allow users to:
    - Create Signal-Generators
    - Test against real data
    - Submit via PR for promotion to Production pipeline
* Abstract away platform complexity (clusters, repo structure, queue)

#### 4) Targeted & Actionable Dispatch
Signals should result in precise, actionable alerts delivered to the correct owners.
* Support fine-grained routing (team, service, severity)
* Integrate with multiple channels/targets (Slack, email, etc.)
* Ensure Alerts are: limited, relevant, contextual, actionable (enforcement can be done multiple ways, not outlined here)

#### 5) User-Controlled Flow Management
Minor/temporary flow control updates, or routing rules, must be configurable by users without code changes.
* Users control: thresholds, throttling, silencing, routing rules
* Configuration exposed via: Delta tables+ SQL dashboards (self-service UI)

#### 6) Observability & Operational Transparency
The system must provide clear visibility into its behavior and health.
* Track:
   - Signal-generator execution success/failure
   - Signal volume and trends
   - Queue lag / backlog
   - Dispatch success rates
* Provide:
   - Dashboards (signal store + metrics)
   - Alerting on system health issues using the system's own dispatch pipeline to directly escalate a health Alert
* Enable debugging: trace signal from generation → dispatch (MVP++)

### Potential Future Enhancements
We don't want to over-design with capabilities that are not needed now. However we should consider the following components that are highly likely to be needed at some point. Just considering the future addition of these will demonstrate if we have a solid design.  Our modular, distributed architecture does indeed lend itself well to including the following features though they are not necessarily needed now.

#### A) Durability & Analytics (for Signals and Alerts)
We may find that we want to persist Signals and Alerts to long-term storage, decoupling analytics from queue retention. It should be very easy to add a new code path such that the Signal generators publish to a queue as well as write a Signal record to persistent storage (e.g., Delta table) without effecting the design. Similarly, it should be very easy to update the Dispatch-Engine workers to write a "dispatch" record to persistent storage in addition to dispatching Alerts to targets.  Persisting the Alerts is probably the most important of these - most likely to be needed in the near future.

#### B) Handle Signals from "External" Signal Producers
We find it necessary eto xpose a REST API into which Events (a.k.a. "Signals" in the new design) could be ingested from producers other than the internal producers running queries on the telemetry/logging. One example was ingestion of a webhook payload that Neuraspace sends to alert on Conjunction Events. The modular design of our new system lends itself well to adding such an API at a later time, if such a things continues to be needed. The API becomes just a new "Producer" pushing signals to the Signal Queue.  A simple model to consider:  AWS API Gateway → Lambda (with serializer) → Signal-Generator-Queue

## SOLID principles
#### Single Responsibility
* Each module = one concern
* Separate layers, each can be swapped out without effecting others

#### Open/Closed

#### Liskov Substitution

#### Interface Segregation

#### Dependency Inversion
Inject Spark, configs, and storage layers
