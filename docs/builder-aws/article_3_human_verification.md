# Agents for Humans: Deploying a Human-in-the-Loop Verification Agent with Amazon Bedrock AgentCore

*By the ProofChain Engineering Team — AWS Agents for Humans Hackathon*

---

## The Enterprise Imperative: Human-in-the-Loop Governance

In mission-critical professional domains (such as government contracting, healthcare IT, financial systems, and cloud migrations), an AI agent that takes autonomous actions without human review is an unacceptable liability.

Imagine an autonomous agent discovering that an IT vendor cannot satisfy a 24/7 disaster recovery SLA, and automatically executing a binding contract amendment without executive sign-off!

To make AI agents truly suitable for human collaboration ("Agents for Humans"), the system must support **Strict Dual-Authorization Human Governance**:
1. Agents perform the heavy cognitive lifting: reading hundreds of pages of contracts, synthesizing commitments, calculating risks, and formulating concrete remediation proposals.
2. The agent transitions the proposed action to a pending review state (`status="PROPOSED"`).
3. Delivery Directors and Compliance Officers inspect the exact mathematical and textual provenance before cryptographically approving or rejecting the change.

---

## Deploying Strands with Amazon Bedrock AgentCore

Amazon Bedrock AgentCore provides a dedicated serverless runtime environment purpose-built for hosting production AI agents with enterprise-grade isolation, session persistence, and built-in observability.

### AgentCore Runtime Architecture

```
                               ┌────────────────────────────────┐
                               │  Client / Management Console   │
                               └───────────────┬────────────────┘
                                               │ HTTPS Request
                               ┌───────────────▼────────────────┐
                               │    Bedrock AgentCore Gateway   │
                               │    (Session State & Routing)   │
                               └───────────────┬────────────────┘
                                               │
               ┌───────────────────────────────┴───────────────────────────────┐
               ▼                                                               ▼
┌──────────────────────────────┐                               ┌──────────────────────────────┐
│  BedrockAgentCoreApp Runtime │                               │   CloudWatch Observability   │
│   • Strands Agent Instances  │                               │   • Latency Metrics          │
│   • Tool Execution Harness   │                               │   • Invocations & Errors     │
│   • Session LRU Cache        │                               │   • Distributed Trace Spans  │
└──────────────┬───────────────┘                               └──────────────────────────────┘
               │
               ▼
┌──────────────────────────────┐
│    Amazon Bedrock Models     │
│   (Claude 3.5 Sonnet/Haiku)  │
└──────────────────────────────┘
```

### Implementing the BedrockAgentCoreApp Entrypoint

Using the official `@aws/agentcore` CLI and `bedrock-agentcore` Python runtime, we define the agent application in `app/proofchain_agent/main.py`:

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
import json
import uuid

app = BedrockAgentCoreApp()
log = app.logger

@tool
def detect_conflicts(requirement: str, evidence: str) -> str:
    """Detect factual contradictions between contractual promises and internal policies."""
    req_lower = requirement.lower()
    evi_lower = evidence.lower()

    if "24/7" in req_lower and "business hours" in evi_lower:
        return json.dumps({
            "conflict_id": f"CNF-{uuid.uuid4().hex[:8].upper()}",
            "conflict_type": "SLA_DISCREPANCY",
            "severity": "CRITICAL",
            "can_claim_compliance": False,
            "compliance_directive": "DO NOT CLAIM COMPLIANCE",
            "recommended_action": "Retain 24/7 third-party AWS MSP on-call rotation or amend proposal to business-hours coverage."
        })
    return json.dumps({"conflict_detected": False, "can_claim_compliance": True})

@tool
def create_mitigation_action(title: str, description: str, owner: str) -> str:
    """Create a Human-in-the-Loop mitigation action requiring delivery lead sign-off."""
    return json.dumps({
        "action_id": f"ACT-{uuid.uuid4().hex[:8].upper()}",
        "title": title,
        "description": description,
        "owner": owner,
        "status": "PROPOSED",
        "human_approval_required": True
    })

tools = [detect_conflicts, create_mitigation_action]

@app.entrypoint
async def invoke(payload, context):
    session_id = getattr(context, 'session_id', 'default-session')
    agent = Agent(
        model="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        system_prompt="You are ProofChain's Commitment Intelligence Agent on Bedrock AgentCore.",
        tools=tools
    )
    prompt = payload.get("prompt", "")
    async for event in agent.stream_async(prompt):
        yield event

if __name__ == "__main__":
    app.run()
```

---

## Infrastructure as Code via CDK

Bedrock AgentCore natively compiles to AWS Cloud Development Kit (CDK) constructs using `@aws/agentcore-cdk`. The `AgentCoreApplication` construct provisions:
1. **Isolated Lambda / Container Execution Runtimes** with least-privilege IAM execution roles.
2. **Bedrock Model Invocation Policies** scoped strictly to authorized foundation models.
3. **Session State Managers** preventing cross-tenant history contamination.
4. **CloudWatch Metrics and X-Ray Distributed Tracing** with zero manual instrumentation.

```typescript
import { AgentCoreApplication } from '@aws/agentcore-cdk';
import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class AgentCoreStack extends Stack {
  public readonly application: AgentCoreApplication;

  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    this.application = new AgentCoreApplication(this, 'Application', {
      spec: {
        name: 'proofchain',
        runtimes: [{
          name: 'proofchain_agent',
          build: 'CodeZip',
          entrypoint: 'main.py',
          codeLocation: 'app/proofchain_agent/',
          protocol: 'HTTP',
        }]
      }
    });
  }
}
```

---

## The Human-in-the-Loop Approval Workflow in Action

When ProofChain detects a critical conflict (such as our killer demo scenario where an RFP mandates 24/7 technical support while internal support policy guarantees business-hours only):
1. **Conflict Detection**: `ConflictAgent` immediately tags the finding:
   ```
   ⛔ DO NOT CLAIM COMPLIANCE
   Conflict Type: SLA_DISCREPANCY
   Severity: CRITICAL
   ```
2. **Action Synthesis**: `ActionAgent` produces remediation proposal `ACT-001`:
   - *"Retain 24/7 third-party AWS MSP on-call rotation ($4,500/mo) or amend proposal to business-hours coverage."*
   - Status: `PROPOSED`
   - Owner: `Operations & Legal`
3. **Human Gate**: The action cannot execute automatically. It appears on the ProofChain Actions Approval dashboard.
4. **Executive Sign-off**: Once the Operations Director reviews the blast radius and clicks `Approve`, ProofChain updates the Commitment Graph, links the approved mitigation edge, and recalculates the workspace Compliance Health Score.

---

## Conclusion

Amazon Bedrock AgentCore provides the missing link between experimental AI prototypes and enterprise-grade multi-agent deployments. By combining **Strands Agents**, **Amazon Bedrock**, and **AgentCore runtimes** with **Human-in-the-Loop governance**, ProofChain delivers an agent that professionals can genuinely trust with their most critical commitments.
