# ProofChain — Hackathon Demo Video Production Suite

This directory contains the production pipeline and final assets for the **AWS Agents for Humans Hackathon** (Track: **Professional Agents**).

## Final Deliverable
- **Video File**: `proofchain_demo_final.mp4`
- **Duration**: 4 minutes 13 seconds (253.78s)
- **Resolution**: 1920x1080 (1080p, 16:9, 30fps)
- **Video Codec**: H.264 / AVC1 (High Profile, progressive)
- **Audio Codec**: AAC 192kbps Stereo (Daniel, en_GB)
- **Streaming**: QuickTime / MP4 with `+faststart` enabled

---

## Production Scripts
- `produce_demo.py`: Autonomous Playwright and ffmpeg script that records live browser interactions at 1080p, generates TTS voiceover matching each scene, applies animations to title/architecture slides, and concatenates scenes into the final video.
- `generate_video.py`: Audio generation and duration timing analyzer using macOS `say` and `ffprobe`.
- `youtube_metadata.md`: YouTube title, description, chapter timestamps, and tags for submission.

---

## Scene Breakdown & Demonstration
1. **Scene 1 (0:00 - 0:34)**: *Introduction & The Problem* — The enterprise contract-delivery gap, billion-dollar SLA penalties.
2. **Scene 2 (0:34 - 1:07)**: *AWS Architecture & Multi-Agent Design* — Strands Multi-Agent cluster, Amazon Bedrock foundation models, DynamoDB, S3, AgentCore.
3. **Scene 3 (1:07 - 1:40)**: *Ingested Documents & Cryptographic Provenance* — 7 enterprise documents with SHA-256 hashes and exact clause offsets.
4. **Scene 4 (1:40 - 2:07)**: *Intelligence Dashboard & System Health* — Real-time metrics, 78% health score, Strands multi-agent status.
5. **Scene 5 (2:07 - 2:41)**: *Bipartite Commitment-Evidence Graph* — 65 connected nodes, COM-001 (99.99% Availability), Invalidation Cascade.
6. **Scene 6 (2:41 - 3:18)**: *Cross-Document Conflict Detection Engine* — Commercial 15-min DR RTO vs. Engineering 4-hr RTO caught across documents.
7. **Scene 7 (3:18 - 3:52)**: *Human-in-the-Loop Autonomous Actions* — Mitigations (Aurora Global Database) with mandatory cryptographic human approval.
8. **Scene 8 (3:52 - 4:13)**: *Conclusion & Open-Source Submission* — GitHub repository under Apache 2.0.

---

## Live Deployments
- **AWS S3 Public Website**: http://proofchain-web-117687871322.s3-website.ap-south-1.amazonaws.com
- **GitHub Repository**: https://github.com/mandhatisaiganesh/proofchain
- **AWS Region**: `ap-south-1`
