# Architecture

## System Overview

```mermaid
graph TD
    subgraph Clients
        A["Discord Bot<br/>(TodoMaster AI)"]
        C["Next.js Frontend<br/>(2 replicas)"]
    end

    subgraph K8s Cluster - todo-app namespace
        subgraph Backend Pod
            B["FastAPI<br/>:8000"]
            DS["Dapr Sidecar<br/>:3500 / :9090"]
            CF["Constitutional AI<br/>Middleware"]
        end

        subgraph Data Layer
            D["PostgreSQL 15<br/>StatefulSet + PVC (5Gi)"]
            H["Redis 7<br/>State Store"]
        end

        subgraph Event Pipeline
            E["Apache Kafka<br/>Strimzi KRaft v4.0.0"]
            F["Notification<br/>Service"]
        end

        G["Prometheus<br/>:9090"]
    end

    A -->|REST API| B
    C -->|REST API| B
    CF -->|Block / Flag / Allow| B
    B -->|SQL| D
    DS -->|State Store| H
    DS -->|Pub/Sub| E
    E -->|Consume Events| F
    G -->|Scrape /metrics| B
    G -->|Scrape /metrics| DS
    G -->|Scrape /metrics| F

    style A fill:#5865F2,color:#fff
    style CF fill:#ff6b6b,color:#fff
    style E fill:#231f20,color:#fff
    style G fill:#e6522c,color:#fff
    style DS fill:#0d6efd,color:#fff
```

---

## Kubernetes Deployment Map

```mermaid
graph LR
    subgraph kafka namespace
        KO["Strimzi Operator"]
        KB["Kafka Broker<br/>1 replica, 5Gi PVC"]
        KT["3 Topics<br/>todo-events<br/>user-events<br/>system-events"]
        KO --> KB --> KT
    end

    subgraph todo-app namespace
        CM["ConfigMap"]
        SEC["Secrets<br/>(kubectl create)"]

        subgraph Deployments
            BE["Backend<br/>2 replicas<br/>100m-500m CPU<br/>256-512Mi RAM"]
            FE["Frontend<br/>2 replicas"]
            NS["Notification<br/>1 replica"]
            DB_BOT["Discord Bot<br/>1 replica<br/>100m-250m CPU<br/>128-256Mi RAM"]
        end

        subgraph StatefulSets
            PG["PostgreSQL<br/>1 replica<br/>5Gi PVC"]
        end

        subgraph Dapr Components
            DSS["Dapr State Store<br/>(Redis)"]
            DPS["Dapr Pub/Sub<br/>(Kafka)"]
        end

        RD["Redis"]
        PR["Prometheus<br/>+ RBAC"]

        CM --> BE
        CM --> FE
        SEC --> BE
        SEC --> DB_BOT
        BE --> PG
        BE --> DSS
        BE --> DPS
        DPS --> KT
        RD --> DSS
        PR --> BE
        PR --> NS
        DB_BOT --> BE
    end

    style BE fill:#2d6a4f,color:#fff
    style FE fill:#264653,color:#fff
    style PG fill:#336699,color:#fff
    style KB fill:#231f20,color:#fff
    style PR fill:#e6522c,color:#fff
    style DB_BOT fill:#5865F2,color:#fff
```

---

## Request Flow

### Normal Chat Request (ALLOW)

```mermaid
sequenceDiagram
    participant U as User (Web/Discord)
    participant B as FastAPI Backend
    participant CF as Constitutional Filter
    participant AI as OpenAI API
    participant D as Dapr Sidecar
    participant K as Kafka
    participant N as Notification Service
    participant V as Vault (Logs)

    U->>B: POST /api/chat {message, student_id}
    B->>CF: check(message)
    CF-->>B: decision: ALLOW
    B->>AI: generate response
    AI-->>B: AI response
    B->>V: log conversation (JSONL)
    B->>D: publish_event("chat-events")
    D->>K: produce {type: "chat_completed", ...}
    K->>N: consume event
    N-->>N: process notification
    B-->>U: {response, decision: "allow"}
```

### Blocked Chat Request (Constitutional Violation)

```mermaid
sequenceDiagram
    participant U as User
    participant B as FastAPI Backend
    participant CF as Constitutional Filter
    participant D as Dapr Sidecar
    participant K as Kafka

    U->>B: POST /api/chat {"solve my homework"}
    B->>CF: check(message)
    CF-->>B: decision: BLOCK, reason: "academic dishonesty"
    Note over B: Generate Socratic response instead
    B->>D: publish_event("chat-events")
    D->>K: produce {type: "chat_blocked", reason: ...}
    B-->>U: {socratic_response, decision: "block"}
```

### Flagged Chat Request (Human Review)

```mermaid
sequenceDiagram
    participant U as User
    participant B as FastAPI Backend
    participant CF as Constitutional Filter
    participant V as Vault
    participant D as Dapr Sidecar
    participant K as Kafka
    participant H as Human Reviewer

    U->>B: POST /api/chat {"exam tomorrow, need answers fast"}
    B->>CF: check(message)
    CF-->>B: decision: FLAG, reason: "time pressure detected"
    B->>V: create Pending_Approval/ file
    B->>D: publish_event("chat-events")
    D->>K: produce {type: "chat_flagged", ...}
    B-->>U: {hold_response, decision: "flag"}
    H->>V: review and approve/reject
```

---

## Constitutional AI Pipeline

```mermaid
graph TD
    Q[Incoming Query] --> P1{Pattern Match:<br/>Block List}
    P1 -->|"'solve my homework'<br/>'write code for me'<br/>'give me the answer'<br/>'do my assignment'"| BLOCK["BLOCK<br/>Return Socratic Response"]
    P1 -->|No match| P2{Pattern Match:<br/>Flag List}
    P2 -->|"'exam tomorrow'<br/>'due in 1 hour'<br/>'urgent need'<br/>'no time'"| FLAG["FLAG<br/>Route to Human Review"]
    P2 -->|No match| ALLOW["ALLOW<br/>Process with AI"]

    BLOCK --> E1[Publish chat_blocked event]
    FLAG --> E2[Publish chat_flagged event]
    FLAG --> VA[Create Vault Approval File]
    ALLOW --> AI[Call OpenAI API]
    AI --> E3[Publish chat_completed event]

    E1 --> K[Kafka]
    E2 --> K
    E3 --> K

    style BLOCK fill:#e63946,color:#fff
    style FLAG fill:#f4a261,color:#000
    style ALLOW fill:#2a9d8f,color:#fff
    style K fill:#231f20,color:#fff
```

---

## Event-Driven Architecture

```mermaid
graph LR
    subgraph Producers
        BE["Backend<br/>(via Dapr)"]
    end

    subgraph Kafka Topics
        T1["todo-events"]
        T2["user-events"]
        T3["system-events"]
    end

    subgraph Events Published
        E1["chat_completed"]
        E2["chat_blocked"]
        E3["chat_flagged"]
        E4["todo_created"]
        E5["todo_completed"]
    end

    subgraph Consumers
        NS["Notification Service"]
    end

    BE --> E1 & E2 & E3 & E4 & E5
    E1 & E4 & E5 --> T1
    E2 & E3 --> T3
    T1 --> NS
    T3 --> NS

    style BE fill:#2d6a4f,color:#fff
    style NS fill:#264653,color:#fff
    style T1 fill:#231f20,color:#fff
    style T2 fill:#231f20,color:#fff
    style T3 fill:#231f20,color:#fff
```

---

## Dapr Abstraction Layer

Shows how Dapr enabled a zero-code infrastructure swap from Redis to Kafka:

```mermaid
graph TD
    subgraph Application Code - unchanged
        APP["Backend Service<br/>dapr_service.publish_event()"]
    end

    subgraph Dapr Sidecar
        D["Dapr Runtime<br/>:3500"]
    end

    subgraph Before - Redis Pub/Sub
        R["Redis<br/>08-dapr-pubsub.yaml"]
    end

    subgraph After - Kafka Pub/Sub
        K["Apache Kafka<br/>11-dapr-pubsub-kafka.yaml"]
    end

    APP -->|Same API call| D
    D -.->|"Config A (old)"| R
    D -->|"Config B (current)"| K

    style APP fill:#2d6a4f,color:#fff
    style D fill:#0d6efd,color:#fff
    style R fill:#999,color:#fff
    style K fill:#231f20,color:#fff
```

**What changed:** 1 YAML file. **What didn't change:** Application code.

---

## Discord Bot Architecture

```mermaid
graph TD
    subgraph Discord
        U["Discord User"]
        DC["Discord API"]
    end

    subgraph K8s - todo-app namespace
        subgraph Discord Bot Pod
            BOT["TodoMaster AI<br/>discord.py"]
            API["API Client<br/>(aiohttp)"]
        end

        subgraph Backend Pod
            BE["FastAPI<br/>:8000"]
            CF["Constitutional<br/>Filter"]
        end
    end

    U -->|"/todo-create title:Buy groceries"| DC
    DC -->|Slash Command| BOT
    BOT -->|Format request| API
    API -->|"POST /todos"| BE
    BE -->|Check rules| CF
    CF -->|Allow| BE
    BE -->|Response| API
    API -->|Format embed| BOT
    BOT -->|Rich embed| DC
    DC -->|Display| U

    style U fill:#5865F2,color:#fff
    style DC fill:#5865F2,color:#fff
    style BOT fill:#5865F2,color:#fff
    style CF fill:#ff6b6b,color:#fff
    style BE fill:#2d6a4f,color:#fff
```

---

## Resource Allocation (6GB Minikube Cluster)

| Service | CPU Request | CPU Limit | RAM Request | RAM Limit | Replicas |
|---------|------------|-----------|-------------|-----------|----------|
| Backend | 100m | 500m | 256Mi | 512Mi | 2 |
| Frontend | -- | -- | -- | -- | 2 |
| PostgreSQL | -- | -- | -- | -- | 1 |
| Redis | -- | -- | -- | -- | 1 |
| Kafka | 250m | 500m | 512Mi | 1Gi | 1 |
| Notification | -- | -- | -- | -- | 1 |
| Prometheus | -- | -- | -- | -- | 1 |
| Discord Bot | 100m | 250m | 128Mi | 256Mi | 1 |

**Total cluster utilization: ~44% of 6GB**

---

## CI/CD Pipeline

```mermaid
graph LR
    subgraph Trigger
        P["Push to main"]
    end

    subgraph Test
        T1["pytest<br/>backend/tests/"]
        T2["ruff lint<br/>(E, F, W rules)"]
    end

    subgraph Build
        B1["Backend Image"]
        B2["Frontend Image"]
        B3["Notification Image"]
    end

    subgraph Validate
        V["kubectl --dry-run<br/>14 manifests"]
    end

    subgraph Security
        S["Trivy Scan<br/>CRITICAL + HIGH"]
    end

    P --> T1 & T2
    T1 & T2 --> B1 & B2 & B3
    T1 & T2 --> V
    B1 & B2 & B3 --> S

    style P fill:#2d6a4f,color:#fff
    style S fill:#e6522c,color:#fff
```
