# Building Resilient Professional Agents: The Strands Multi-Agent Pattern on Amazon Bedrock

*By the ProofChain Engineering Team — AWS Agents for Humans Hackathon*

---

## The Failure of Monolithic Prompts in Enterprise Contracts

When engineers attempt to analyze enterprise contracts (such as Master Services Agreements, Statements of Work, and SOC 2 audits) using LLMs, they often begin with a monolithic prompt:

```python
# The Fragile Monolithic Approach
prompt = """
Analyze these 150 pages of PDFs. Extract all commitments, identify all conflicts,
check our team's engineering capacity, and tell me what risks exist.
"""
```

In mission-critical professional engagements, this pattern fails dramatically:
1. **Context Window Degradation**: As document length expands, the LLM loses attention over critical middle sections ("Lost in the Middle" phenomenon).
2. **Hallucinated Clauses**: Without strict grounding, generative models invent standard SLA remedies or warranty disclaimers that do not exist in the contract.
3. **Lack of Separation of Concerns**: An agent trying to be both a contract lawyer and an AWS cloud architect at the same instant produces mediocre legal advice and questionable architecture plans.

To solve this, we architected **ProofChain** around the **Strands Multi-Agent Pattern** powered by **Amazon Bedrock**.

---

## What is the Strands Agent Pattern?

In a physical rope, thin fibers twisted together form strong yarn, and yarns twisted together form resilient strands. In the **Strands Agent Pattern**, autonomous AI agents are organized into decoupled, specialized strands that each perform one domain-specific task with deterministic inputs and outputs, coordinated by an Orchestrator DAG.

```
                  ┌───────────────────────────────┐
                  │      Orchestrator Agent       │
                  │   (Amazon Bedrock Claude 3.5) │
                  └───────────────┬───────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ Requirement     │      │ Commitment      │      │ Evidence        │
│ Extraction      │      │ Synthesis       │      │ Verifier        │
│ Strand          │      │ Strand          │      │ Strand          │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         │                                                 │
         ▼                                                 ▼
┌─────────────────┐                               ┌─────────────────┐
│ Cross-Document  │                               │ Delivery        │
│ Conflict Strand │                               │ Capability Gap  │
└────────┬────────┘                               └────────┬────────┘
         │                                                 │
         └────────────────────────┬────────────────────────┘
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │    Graph Updater & Action     │
                  │    Remediation Strands        │
                  └───────────────────────────────┘
```

### The 10 Agent Strands in ProofChain

1. **Orchestrator Agent**: Manages the workspace lifecycle, provisions agent scratchpads, tracks execution state, and routes intermediate artifacts.
2. **Requirement Extractor Strand**: Reads segmented document chunks, extracting raw statutory, technical, and commercial requirements with exact clause numbers and character offsets.
3. **Commitment Synthesizer Strand**: Consolidates raw requirements into standardized commitment objects with criticality ratings (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), domains (`LEGAL`, `TECHNICAL`, `SECURITY`, `FINANCIAL`, `OPERATIONAL`), and delivery deadlines.
4. **Evidence Verifier Strand**: Searches the document space for corroborating proof: architectural schematics, test run results, ISO certificates, or benchmark logs. Computes a mathematical grounding confidence score ($C \in [0.0, 1.0]$).
5. **Cross-Document Conflict Strand**: Executes pairwise semantic and numerical comparisons across commitments. For example, comparing SLA uptime guarantees in an SOW against SLA exclusions in the MSA.
6. **Capability Gap Strand**: Inspects current team velocities, sprint allocations, and AWS infrastructure specs to identify whether committed deadlines are technically attainable.
7. **Quantitative Risk Strand**: Computes compound risk vectors:
   $$R = \text{Severity} \times (1 - \text{Confidence}) \times \text{Temporal Urgency}$$
8. **Action Remediation Strand**: Generates structured, actionable mitigation proposals with estimated effort, blast radius, and priority.
9. **Human-in-the-Loop Governance Strand**: Enforces dual-authorization gates before any generated mitigation can alter a contract or deploy infrastructure.
10. **Graph Invalidation Cascade Strand**: Monitors evidence health and propagates invalidation signals downstream through the dependency graph.

---

## Integrating Amazon Bedrock

Amazon Bedrock provides the ideal foundation for enterprise multi-agent architectures:

```python
import boto3
import json

class BedrockAgentClient:
    def __init__(self, region_name="us-east-1"):
        self.client = boto3.client("bedrock-runtime", region_name=region_name)
        self.model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"

    def invoke_agent_strand(self, system_prompt: str, user_content: str, temperature: float = 0.0) -> dict:
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_content}
            ]
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )
        
        response_body = json.loads(response["body"].read().decode("utf-8"))
        return json.loads(response_body["content"][0]["text"])
```

### Why Zero Temperature ($T=0$) is Essential for Contract Agents
In creative writing or chat, temperature introduces variety. In legal and compliance auditing, non-zero temperature introduces catastrophic non-determinism. By fixing $T=0.0$ and enforcing JSON Schema output parsing via Pydantic V2, ProofChain guarantees reproducible outputs across identical document sets.

---

## Results & Lessons Learned

- **68% Reduction in False Positives**: Decoupling the Conflict Agent from the Initial Extraction Agent prevented the model from hallucinating conflicts that were actually governed by standard order-of-precedence clauses.
- **Sub-Second Execution for 95% of Pipeline**: Deterministic local graph updates occur instantaneously in memory/DynamoDB, only invoking Bedrock for deep contextual reasoning and synthesis.
- **Auditability for Compliance**: Because each strand writes its intermediate outputs to an immutable log, compliance auditors can inspect the exact reasoning chain behind every flagged risk.
