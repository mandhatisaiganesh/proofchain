#!/usr/bin/env python3
"""
ProofChain — Demo Video Production Pipeline
Produces a judge-ready 1080p MP4 video with real browser recordings of ProofChain,
professional narration audio, title/architecture slides, and seamless transitions.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

VIDEO_DIR = Path("/Users/mandhatisaiganesh/.gemini/antigravity-ide/scratch/proofchain/docs/video")
ARTIFACTS_DIR = Path("/Users/mandhatisaiganesh/.gemini/antigravity-ide/brain/cc99a2a3-d75c-4b98-a9d2-24c7b05b515c")
OUTPUT_VIDEO = VIDEO_DIR / "proofchain_demo_final.mp4"

TITLE_IMG = ARTIFACTS_DIR / "title_card_1788805149233.jpg"
ARCH_IMG = ARTIFACTS_DIR / "architecture_slide_1788805176846.jpg"
CLOSING_IMG = ARTIFACTS_DIR / "closing_card_1788805219750.jpg"

SCENES = [
    {
        "id": "scene_01_intro",
        "title": "Introduction & The Problem",
        "type": "image",
        "image": TITLE_IMG,
        "script": (
            "Welcome to ProofChain. Know what you promised. Prove you can deliver it. "
            "In enterprise IT delivery, major contracts, and cloud modernization, the gap between what sales "
            "promises and what engineering can deliver costs organizations billions every year in SLA penalties "
            "and lost trust. Commitments are buried across hundreds of pages of contracts, statements of work, "
            "and architecture specifications. ProofChain solves this by creating an evidence-grounded commitment "
            "intelligence system powered by Amazon Bedrock and Strands Agents."
        ),
    },
    {
        "id": "scene_02_architecture",
        "title": "AWS Architecture & Multi-Agent Design",
        "type": "image",
        "image": ARCH_IMG,
        "script": (
            "ProofChain is built AWS-native for the AWS Agents for Humans Hackathon. "
            "Our architecture coordinates specialized Strands Agents executed on Amazon Bedrock. "
            "The Requirement and Commitment Agents extract obligations with exact character provenance. "
            "The Evidence and Verification Agents validate commitments against architectural specifications. "
            "Amazon DynamoDB maintains sub-millisecond graph state, Amazon S3 provides an encrypted document vault, "
            "and Amazon Bedrock AgentCore handles autonomous orchestration and human governance."
        ),
    },
    {
        "id": "scene_03_documents",
        "title": "Ingested Documents & Provenance",
        "type": "browser",
        "route": "Documents",
        "script": (
            "Let's look at the live ProofChain application. "
            "In our Federal Cloud Modernization workspace, ProofChain has ingested seven enterprise documents, "
            "including the Request for Proposal, Master Services Agreement, and AWS Cloud Architecture Specification. "
            "Every document is cryptographically hashed with SHA-256. "
            "When we inspect a document, every extracted clause maintains exact character provenance "
            "and source traceability, ensuring that no agent ever hallucinates a contractual requirement."
        ),
    },
    {
        "id": "scene_04_dashboard",
        "title": "Intelligence Dashboard & System Health",
        "type": "browser",
        "route": "Dashboard",
        "script": (
            "The ProofChain Intelligence Dashboard provides an executive command center. "
            "Here, delivery leads and compliance officers see twenty-four active commitments across seven documents, "
            "with a seventy-eight percent Compliance Health Score. "
            "The dashboard tracks verified commitments, unverified obligations, and active conflicts in real time, "
            "backed by continuous monitoring from the Strands multi-agent cluster on Amazon Bedrock."
        ),
    },
    {
        "id": "scene_05_graph",
        "title": "Bipartite Commitment Graph",
        "type": "browser",
        "route": "Graph",
        "script": (
            "ProofChain's core technical innovation is the Bipartite Commitment-Evidence Graph. "
            "Blue nodes represent contractual commitments, while cyan nodes represent architectural and operational evidence. "
            "Here, commitment COM-001—our ninety-nine point nine-nine percent availability guarantee—is linked to both our "
            "Multi-AZ AWS architecture design and our quarterly uptime audit. "
            "When reality shifts, such as an audit expiring, ProofChain executes an Invalidation Cascade, "
            "instantly propagating the failure downstream through the graph."
        ),
    },
    {
        "id": "scene_06_conflicts",
        "title": "Cross-Document Conflict Detection",
        "type": "browser",
        "route": "Conflicts",
        "script": (
            "Next is ProofChain's Conflict Detection Engine, which catches cross-document contradictions that human reviewers miss. "
            "In Statement of Work SOW-001, commercial sales promised a fifteen-minute disaster recovery RTO. "
            "However, in the AWS Architecture Specification, engineering specified standard cross-region replication "
            "guaranteeing only a four-hour RTO. "
            "ProofChain caught this hidden discrepancy across hundreds of pages, pinpointed the conflicting text snippets, "
            "and flagged an estimated one hundred and fifty thousand dollar SLA penalty risk."
        ),
    },
    {
        "id": "scene_07_actions",
        "title": "Human-in-the-Loop Autonomous Actions",
        "type": "browser",
        "route": "Actions",
        "script": (
            "ProofChain doesn't just surface problems; its Action Agent synthesizes actionable mitigations. "
            "To resolve the RTO conflict, ProofChain generated two options: drafting an SOW amendment or deploying "
            "Amazon Aurora Global Database to satisfy the fifteen-minute requirement. "
            "Crucially, ProofChain enforces strict Human-in-the-Loop governance. Autonomous agents cannot alter contracts "
            "or cloud infrastructure without human approval. "
            "With one click, the director approves the Aurora deployment action, logging a cryptographically verified decision."
        ),
    },
    {
        "id": "scene_08_conclusion",
        "title": "Conclusion & Hackathon Submission",
        "type": "image",
        "image": CLOSING_IMG,
        "script": (
            "ProofChain bridges the gap between commercial promises and engineering reality. "
            "Deployed on AWS, powered by Amazon Bedrock, Strands Agents, and AgentCore, "
            "and fully open-source on GitHub under the Apache 2.0 license. "
            "Know what you promised. Prove you can deliver it. "
            "Thank you for reviewing ProofChain for the AWS Agents for Humans Hackathon."
        ),
    },
]

def run(cmd, check=True):
    print(f"Running: {' '.join(str(c) for c in cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if check and res.returncode != 0:
        print(f"Error (code {res.returncode}):\n{res.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return res

def get_duration(media_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(media_path)
    ]
    res = run(cmd)
    return float(res.stdout.strip())

def generate_voiceovers():
    print("\n--- 1. Generating Voiceover Audio ---")
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    
    for scene in SCENES:
        aiff_path = VIDEO_DIR / f"{scene['id']}.aiff"
        mp3_path = VIDEO_DIR / f"{scene['id']}.mp3"
        
        # Use Daniel at rate 175 for professional presentation
        run(["say", "-v", "Daniel", "-r", "175", scene["script"], "-o", str(aiff_path)])
        # Convert to high quality MP3
        run(["ffmpeg", "-y", "-i", str(aiff_path), "-codec:a", "libmp3lame", "-q:a", "2", str(mp3_path)])
        
        dur = get_duration(mp3_path)
        scene["audio_path"] = mp3_path
        scene["duration"] = dur + 1.0  # Add 1s padding for smooth transitions
        print(f"[{scene['id']}] Generated audio: {dur:.2f}s (scene padded: {scene['duration']:.2f}s)")

if __name__ == "__main__":
    generate_voiceovers()
