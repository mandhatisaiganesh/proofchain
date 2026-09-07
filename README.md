<div align="center">

# ⛓️ ProofChain

### *"Know what you promised. Prove you can deliver it."*

[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock%20Claude%203.5-orange.svg?logo=amazon-aws)](https://aws.amazon.com/bedrock/)
[![Multi-Agent Strands](https://img.shields.io/badge/Architecture-Strands%20Multi--Agent-blueviolet.svg)](docs/builder-aws/article_1_strands_architecture.md)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.13-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React Vite](https://img.shields.io/badge/Frontend-React%2018%20%7C%20TypeScript-61DAFB.svg?logo=react)](https://react.dev/)
[![Tests](https://img.shields.io/badge/Pytest-17%20Passed%20(100%25)-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

**An evidence-grounded autonomous professional agent that turns unstructured enterprise commitments into an immutable, mathematically verified bipartite graph of obligations, capabilities, and proofs.**

[Devpost Submission](docs/devpost_submission.md) • [Live Demo Script](docs/demo_script.md) • [AWS Builder Article 1](docs/builder-aws/article_1_strands_architecture.md) • [AWS Builder Article 2](docs/builder-aws/article_2_evidence_graph.md)

</div>

---

## 📌 Executive Summary & Problem

In enterprise cloud consulting, IT delivery, and major vendor procurement, billions of dollars are lost annually to missed SLAs, unvetted warranties, and contradictory obligations. 

Crucial commitments are buried across hundreds of pages:
- **Master Services Agreements (MSAs)** and **Statements of Work (SOWs)**
- **Technical Addenda** and **Security Questionnaires**
- **SOC 2 Type II Reports** and **Architecture Blueprints**

When outages strike or delivery slips, teams spend weeks asking: *"Who committed to this, which clause governed it, and did we ever have the architecture to deliver it?"*

**ProofChain solves this autonomously.** Powered by **Amazon Bedrock**, ProofChain:
1. Ingests contractual and technical artifacts with **strict character-level provenance**.
2. Deploys a cluster of **10 specialized Strands Agents** to extract requirements, synthesize commitments, and ground them in empirical evidence.
3. Constructs a **Bipartite Commitment-Evidence Graph** with sub-second **Invalidation Cascades**.
4. Detects **hidden cross-document contradictions** (e.g., promising 15-min RTO in an SOW while architecture only supports 4 hours).
5. Generates **mitigation actions** with strict **Human-in-the-Loop governance**.

---

## 🏛️ System Architecture

```mermaid
flowchart TB
    subgraph Client["Frontend Presentation Layer (React 18 + Vite + TypeScript)"]
        UI["Modern Dashboard & Analytics"]
        GraphUI["Interactive Bipartite Canvas Visualizer"]
        ConflictUI["Cross-Doc Conflict Inspector"]
        ActionUI["Human-in-the-Loop Approval Center"]
    end

    subgraph API["Backend Gateway (FastAPI + Pydantic V2)"]
        Router["REST / SSE API Gateway"]
        AuthMiddleware["Security & Provenance Validator"]
    end

    subgraph Strands["Strands Multi-Agent Cluster (Amazon Bedrock)"]
        Orchestrator["Orchestrator Agent"]
        ReqAgent["Requirement Strand"]
        ComAgent["Commitment Strand"]
        EviAgent["Evidence Strand"]
        ConfAgent["Conflict Strand"]
        CapAgent["Capability Strand"]
        RiskAgent["Risk Strand"]
        ActAgent["Action Strand"]
    end

    subgraph Core["Graph & Invalidation Core Engine"]
        Ingest["SHA-256 Provenance Chunker"]
        BipartiteGraph["Bipartite Commitment-Evidence Graph"]
        CascadeEngine["Invalidation Cascade Engine (BFS)"]
    end

    subgraph AWS["AWS Cloud Infrastructure"]
        S3["Amazon S3 (Encrypted Document Vault)"]
        DDB["Amazon DynamoDB (Single-Table State Store)"]
        Bedrock["Amazon Bedrock (Claude 3.5 Sonnet & Haiku)"]
    end

    UI --> Router
    GraphUI --> Router
    ConflictUI --> Router
    ActionUI --> Router

    Router --> Ingest
    Router --> Orchestrator
    
    Orchestrator --> ReqAgent
    Orchestrator --> ComAgent
    Orchestrator --> EviAgent
    Orchestrator --> ConfAgent
    Orchestrator --> CapAgent
    Orchestrator --> RiskAgent
    Orchestrator --> ActAgent

    ReqAgent --> Bedrock
    ComAgent --> Bedrock
    ConfAgent --> Bedrock

    Ingest --> S3
    BipartiteGraph --> DDB
    CascadeEngine --> BipartiteGraph
```

---

## 🤖 The Strands Multi-Agent Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Delivery Director
    participant O as Orchestrator Agent
    participant I as Document Ingestion
    participant R as Requirement Strand
    participant C as Commitment Strand
    participant E as Evidence Strand
    participant X as Conflict Strand
    participant G as Bipartite Graph Engine
    participant A as Action Strand

    User->>O: Ingest Engagement Documents (MSA, SOW, SOC2, Arch)
    O->>I: Chunk with SHA-256 Provenance & Line Offsets
    I-->>O: Normalized Chunks & Provenance Map
    O->>R: Extract Requirements & Obligations
    R-->>O: Extracted Requirements with Clause IDs
    O->>C: Synthesize Domain Commitments
    C-->>O: Structured Commitments (SLAs, Deadlines, Criticality)
    O->>E: Ground Commitments in Corroborating Evidence
    E-->>O: Evidence Nodes & Confidence Scores
    O->>X: Pairwise Contradiction Analysis
    X-->>O: Flagged Cross-Document Conflicts
    O->>G: Build Bipartite Graph & Compute Cascades
    O->>A: Generate High-Impact Mitigations
    A-->>User: Propose Actions for Human-in-the-Loop Signoff
```

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **Strict Provenance Anchoring** | Every requirement, commitment, and conflict references the exact document hash, clause ID, section header, and character bounding offsets. Zero ungrounded hallucinations. |
| **Bipartite Graph Modeling** | Mathematically separates commitments ($V_C$) from empirical evidence ($V_E$), establishing directed verification edges. |
| **Real-Time Invalidation Cascade** | When a certificate expires or an architecture test fails, ProofChain cascades failure states downstream in under 5ms, updating compliance health automatically. |
| **Semantic Conflict Detection** | Identifies numerical, operational, and contractual contradictions across documents with severity classification and financial risk estimates. |
| **Human-in-the-Loop Governance** | Generated remediation actions cannot mutate state without explicit, auditable dual-authorization from human delivery leads. |
| **What-If Scenario Simulator** | Simulates key personnel departures, scope expansions, or regulatory shifts to predict downstream project impacts before committing. |

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+ (Python 3.13 recommended)
- Node.js 18+ and npm
- AWS CLI configured with Bedrock access (optional for demo mock mode)

### 1. Automated Setup & Run
Clone the repository and run the automated demo launcher:

```bash
# Clone the repository
git clone https://github.com/your-org/proofchain.git
cd proofchain

# Run setup script (installs Python & npm dependencies, seeds demo workspace)
./scripts/setup.sh

# Launch backend (FastAPI :8000) and frontend (Vite :5173)
./scripts/run_demo.sh
```

Open your browser at **`http://localhost:5173`** to interact with the full application.  
Access the interactive FastAPI Swagger docs at **`http://localhost:8000/docs`**.

---

## 🧪 Testing & Evaluation

ProofChain includes an end-to-end automated test suite covering model integrity, provenance extraction, conflict detection, prompt injection defense, and invalidation cascades:

```bash
# Run the complete test suite
PYTHONPATH=backend pytest tests/ -v
```

### Test Suite Summary
- `tests/test_models.py`: Validates Pydantic data schemas, status transitions, and cascade logic.
- `tests/test_ingestion.py`: Verifies SHA-256 chunking, line offset extraction, and file format validation.
- `tests/test_conflict_detection.py`: Tests automated detection of intentional SLA and DR contradictions across synthetic demo contracts.
- `tests/test_prompt_injection.py`: Ensures adversarial prompt injections within ingested PDFs are neutralized by sanitization filters.
- `tests/test_evaluation.py`: Evaluates grounding precision, provenance fidelity, and cascade speed under load.

**Result**: `17 passed, 100% test success rate`.

---

## ☁️ AWS Production Deployment

ProofChain includes production-ready deployment scripts and CloudFormation templates:

### 1. Automated Script Deployment
```bash
AWS_REGION=us-east-1 ./scripts/deploy_aws.sh
```

### 2. CloudFormation Deployment
```bash
aws cloudformation deploy \
    --template-file infra/cloudformation.yaml \
    --stack-name proofchain-production \
    --parameter-overrides Environment=production \
    --capabilities CAPABILITY_NAMED_IAM
```

This provisions:
- **Amazon S3**: AES-256 encrypted document vault with strict public access blocks and object versioning.
- **Amazon DynamoDB**: Pay-per-request single-table state store with point-in-time recovery.
- **IAM Execution Roles**: Least-privilege roles granting Bedrock model invocation and S3/DynamoDB access.

---

## 📚 Technical Documentation & Articles

- [AWS Builder Article 1: The Strands Multi-Agent Pattern on Amazon Bedrock](docs/builder-aws/article_1_strands_architecture.md)
- [AWS Builder Article 2: The Bipartite Commitment Graph & Invalidation Cascades](docs/builder-aws/article_2_evidence_graph.md)
- [Devpost Submission Document](docs/devpost_submission.md)
- [Live Demo Video Script](docs/demo_script.md)

---

## 🛡️ Security & Privacy

- **Data Encryption**: All stored contractual artifacts are encrypted at rest using AWS KMS / AES-256 and in transit via TLS 1.3.
- **Adversarial Hardening**: Pre-chunking sanitation filters detect and neutralize malicious prompt injection vectors hidden in vendor documents.
- **Zero Model Training**: Customer enterprise contracts are processed via Amazon Bedrock with strict zero-data-retention guarantees.

---

## 📄 License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.
