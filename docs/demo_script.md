# ProofChain — Video Demo & Judge Walkthrough Script

**Duration**: 3 to 4 Minutes  
**Presenter**: Principal AI Architect / Full Stack Lead  
**Target Audience**: AWS Hackathon Judges, Professional Services Directors, Enterprise Delivery Leads

---

## 🎬 Section 1: The Hook & The Problem (0:00 - 0:45)

**[Visual: Presenter on camera or Title Slide: ProofChain — "Know what you promised. Prove you can deliver it."]**

> *"In enterprise consulting, IT delivery, and major SaaS contracts, the gap between what sales promises and what engineering can deliver costs organizations billions every single year in SLA penalties and lost clients.*
>
> *Today, commitments are buried across hundreds of pages: Master Services Agreements, SOWs, RFP responses, SOC 2 reports, and architecture diagrams. No human can track them all, and when an outage or breach happens, everyone asks: 'Who committed to this, and did we ever have the architecture to prove it?'*
>
> *Meet **ProofChain**: an evidence-grounded autonomous professional agent built on Amazon Bedrock. ProofChain extracts every commitment from your contracts, links each promise to mathematical and empirical evidence, catches hidden cross-document contradictions, and predicts delivery failure before it happens."*

---

## 🖥️ Section 2: Ingestion & Autonomous Extraction (0:45 - 1:30)

**[Visual: Transition screen to ProofChain Dashboard at `http://localhost:5173` -> Click 'Documents']**

> *"Let's see ProofChain in action. Here we have an enterprise workspace for 'Acme Cloud Transformation' with 7 ingested legal and technical documents: the Master Services Agreement, the Primary Statement of Work, a Security Questionnaire, our AWS Cloud Architecture Specification, and SOC 2 Type II audit report.*
>
> *ProofChain doesn't just parse text — it executes a cluster of specialized Strands Agents powered by Amazon Bedrock. Every extracted requirement and commitment is permanently tagged with exact character provenance: document hash, clause ID, and page offsets.*
>
> *Let's look at the Dashboard: ProofChain has identified 24 distinct commitments, 31 requirements, and computed an overall Compliance Health Score of 78%."*

---

## 🕸️ Section 3: Bipartite Commitment Graph & The Invalidation Cascade (1:30 - 2:30)

**[Visual: Click 'Commitment Graph' in the sidebar]**

> *"Here is ProofChain's signature feature: the Bipartite Commitment-Evidence Graph. Blue nodes represent commitments; green and amber nodes represent supporting evidence — ranging from architectural blueprints to empirical uptime logs and third-party certifications.*
>
> *Notice commitment `COM-001`: '99.99% Availability Commitment'. It is currently supported by two evidence nodes: our Multi-AZ AWS architecture design and our quarterly uptime audit.*
>
> *Now, watch what happens when reality changes. Suppose our compliance officer revokes or updates our SOC 2 Type II certificate because a re-audit found open findings.*
>
> *[Action: Click on Evidence Node EVI-003 or toggle status to INVALID]*
>
> *Instantly, ProofChain triggers an **Invalidation Cascade**. In sub-milliseconds, the graph propagates the failure downstream. Every single dependent commitment shifts from `VERIFIED` to `AT RISK` or `BREACHED`, alerting delivery leadership before the customer ever files a complaint."*

---

## 🚨 Section 4: Cross-Document Conflict Engine (2:30 - 3:15)

**[Visual: Click 'Conflicts' in the sidebar]**

> *"Next, let's look at ProofChain's Conflict Detection Engine. Here is a classic enterprise disaster caught autonomously:*
>
> *In `SOW-001`, Section 4.2, our commercial team promised a **15-Minute Disaster Recovery RTO**.*
> *However, in `ARCH-SPEC-AWS`, Section 7.1, engineering specified standard S3 cross-region replication with asynchronous sync, which only guarantees a **4-Hour RTO**.*
>
> *Human reviewers missed this discrepancy across 150 pages of PDFs. ProofChain caught the semantic and numerical contradiction immediately, highlighted the contradictory text snippets with provenance, and flagged it as a **Critical Severity Risk** with a potential SLA penalty of $150,000."*

---

## ⚡ Section 5: Autonomous Actions with Human-in-the-Loop Governance (3:15 - 3:45)

**[Visual: Click 'Actions' in the sidebar]**

> *"ProofChain doesn't just report problems — its Action Agent synthesizes concrete mitigations.*
>
> *Here, ProofChain has generated three suggested actions:
> 1. 'Draft SOW Amendment aligning DR RTO to 4 hours with commercial tier adjustment'
> 2. 'Deploy Aurora Global Database multi-region replication to satisfy 15-minute RTO'
> 3. 'Schedule expedited ISO-27001 surveillance audit'
>
> *Crucially, ProofChain follows strict **Human-in-the-Loop** governance. Agents cannot execute contractual or infrastructure changes without explicit, cryptographic human review and approval. Let's approve the Aurora deployment action right now.*
>
> *[Action: Click 'Approve Action' button -> Toast confirms state transition to APPROVED]"*

---

## ☁️ Section 6: AWS Native Architecture & Conclusion (3:45 - 4:15)

**[Visual: Architecture diagram or AWS Console showing S3 bucket & DynamoDB table]**

> *"ProofChain is built AWS-native from the ground up:
> - **Amazon Bedrock** provides enterprise-grade Claude 3.5 Sonnet and Haiku foundation models.
> - **Amazon S3** with AES-256 server-side encryption vaults customer contractual documents.
> - **Amazon DynamoDB** provides sub-millisecond graph state retrieval with pay-per-request scaling.
> - And automated CloudFormation scripts enable any enterprise to deploy ProofChain in under 5 minutes.
>
> *Know what you promised. Prove you can deliver it. That's ProofChain. Thank you!"*
