#!/usr/bin/env python3
"""
ProofChain — Hackathon Video Production Pipeline
Records live browser sessions in 1080p, generates professional voiceovers,
renders architecture and title slides, and composes a seamless 1080p demo video.
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

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
        "nav_label": "Documents",
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
        "nav_label": "Dashboard",
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
        "nav_label": "Graph",
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
        "nav_label": "Conflicts",
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
        "nav_label": "Actions",
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

def ensure_audio():
    print("\n=== Phase 1: Generating Audio Assets ===")
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    for scene in SCENES:
        mp3_path = VIDEO_DIR / f"{scene['id']}.mp3"
        if not mp3_path.exists():
            aiff_path = VIDEO_DIR / f"{scene['id']}.aiff"
            run(["say", "-v", "Daniel", "-r", "175", scene["script"], "-o", str(aiff_path)])
            run(["ffmpeg", "-y", "-i", str(aiff_path), "-codec:a", "libmp3lame", "-q:a", "2", str(mp3_path)])
        dur = get_duration(mp3_path)
        scene["audio_path"] = mp3_path
        scene["audio_dur"] = dur
        scene["target_dur"] = dur + 1.2  # 1.2s padding
        print(f"[{scene['id']}] Audio duration: {dur:.2f}s -> Scene target: {scene['target_dur']:.2f}s")

def render_image_scene(scene):
    print(f"\n=== Rendering Image Scene: {scene['id']} ===")
    raw_mp4 = VIDEO_DIR / f"{scene['id']}_video.mp4"
    final_mp4 = VIDEO_DIR / f"{scene['id']}_final.mp4"
    
    dur = scene["target_dur"]
    img = str(scene["image"])
    
    # Render 1080p 30fps video with subtle slow zoom
    filter_expr = f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.0002,1.05)':d=750:s=1920x1080:fps=30"
    cmd_vid = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", img,
        "-vf", filter_expr,
        "-t", f"{dur:.2f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        str(raw_mp4)
    ]
    run(cmd_vid)
    
    # Merge video and audio
    cmd_merge = [
        "ffmpeg", "-y",
        "-i", str(raw_mp4),
        "-i", str(scene["audio_path"]),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(final_mp4)
    ]
    run(cmd_merge)
    scene["final_mp4"] = final_mp4
    print(f"Rendered image scene: {final_mp4}")

def record_browser_scenes():
    print("\n=== Phase 2: Recording Live Browser Scenes ===")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path='/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome',
            headless=True
        )
        
        for scene in SCENES:
            if scene["type"] != "browser":
                continue
                
            sid = scene["id"]
            target_dur = scene["target_dur"]
            print(f"\n>>> Recording {sid} ({scene['title']}) for ~{target_dur:.1f}s...")
            
            rec_dir = VIDEO_DIR / f"rec_{sid}"
            if rec_dir.exists():
                shutil.rmtree(rec_dir)
            rec_dir.mkdir(parents=True, exist_ok=True)
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                record_video_dir=str(rec_dir),
                record_video_size={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            page.goto('http://localhost:5174/')
            page.wait_for_selector('.sidebar')
            
            # Navigate to scene page
            nav_btn = page.locator('.nav-item', has_text=scene["nav_label"])
            nav_btn.click()
            page.wait_for_timeout(2000)
            
            start_t = time.time()
            
            if sid == "scene_03_documents":
                # Documents choreography
                time.sleep(2)
                page.evaluate('window.scrollBy({top: 300, behavior: "smooth"})')
                time.sleep(3)
                page.evaluate('window.scrollBy({top: -300, behavior: "smooth"})')
                time.sleep(2)
                # Click first doc row
                rows = page.locator('table.data-table tbody tr')
                if rows.count() > 0:
                    rows.first.click()
                    time.sleep(4)
                    # Scroll modal content
                    page.evaluate('document.querySelector(".card pre")?.scrollBy({top: 250, behavior: "smooth"})')
                    time.sleep(4)
                    page.keyboard.press('Escape')
                    time.sleep(2)
                # Search
                search = page.locator('input[placeholder*="Search"]')
                if search.count() > 0:
                    search.fill('AWS')
                    time.sleep(3)
                    search.fill('')
                    time.sleep(2)
                    
            elif sid == "scene_04_dashboard":
                # Dashboard choreography
                time.sleep(2)
                page.evaluate('window.scrollBy({top: 450, behavior: "smooth"})')
                time.sleep(5)
                page.evaluate('window.scrollBy({top: 400, behavior: "smooth"})')
                time.sleep(5)
                page.evaluate('window.scrollBy({top: -850, behavior: "smooth"})')
                time.sleep(3)
                # Hover cards
                cards = page.locator('.kpi-card, .metric-card, .card')
                if cards.count() > 0:
                    cards.first.hover()
                    time.sleep(2)
                    
            elif sid == "scene_05_graph":
                # Graph choreography
                time.sleep(3)
                # Zoom in
                zoom_btn = page.locator('button[title*="Zoom In"], button:has-text("+")')
                if zoom_btn.count() > 0:
                    zoom_btn.first.click()
                    time.sleep(2)
                    zoom_btn.first.click()
                    time.sleep(2)
                # Hover SVG circles
                circles = page.locator('svg circle')
                if circles.count() > 5:
                    circles.nth(3).hover()
                    time.sleep(3)
                    circles.nth(3).click()
                    time.sleep(5)
                time.sleep(3)
                
            elif sid == "scene_06_conflicts":
                # Conflicts choreography
                time.sleep(2)
                page.evaluate('window.scrollBy({top: 250, behavior: "smooth"})')
                time.sleep(4)
                # Hover / inspect conflict card
                conflict_cards = page.locator('.card, .conflict-item')
                if conflict_cards.count() > 1:
                    conflict_cards.nth(1).hover()
                    time.sleep(4)
                page.evaluate('window.scrollBy({top: 350, behavior: "smooth"})')
                time.sleep(4)
                page.evaluate('window.scrollBy({top: -600, behavior: "smooth"})')
                time.sleep(3)
                
            elif sid == "scene_07_actions":
                # Actions choreography
                time.sleep(2)
                page.evaluate('window.scrollBy({top: 200, behavior: "smooth"})')
                time.sleep(3)
                # Approve action button
                approve_btn = page.locator('button:has-text("Approve")')
                if approve_btn.count() > 0:
                    approve_btn.first.hover()
                    time.sleep(2)
                    approve_btn.first.click()
                    time.sleep(3)
                time.sleep(4)
                page.evaluate('window.scrollBy({top: -200, behavior: "smooth"})')
                time.sleep(2)

            # Ensure minimum duration matching target_dur
            elapsed = time.time() - start_t
            if elapsed < target_dur:
                rem = target_dur - elapsed
                print(f"Padding {rem:.1f}s to reach target {target_dur:.1f}s...")
                time.sleep(rem)
                
            context.close()
            
            webms = list(rec_dir.glob('*.webm'))
            if not webms:
                raise RuntimeError(f"No webm recorded for {sid}")
            raw_webm = webms[0]
            
            # Transcode webm to 1920x1080 30fps H.264 MP4 matching audio duration
            final_mp4 = VIDEO_DIR / f"{sid}_final.mp4"
            audio_path = scene["audio_path"]
            
            cmd_transcode = [
                "ffmpeg", "-y",
                "-i", str(raw_webm),
                "-i", str(audio_path),
                "-vf", f"scale=1920:1080,fps=30",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-b:v", "3500k",
                "-c:a", "aac", "-b:a", "192k",
                "-t", f"{target_dur:.2f}",
                str(final_mp4)
            ]
            run(cmd_transcode)
            scene["final_mp4"] = final_mp4
            print(f"Finished browser scene: {final_mp4}")
            
        browser.close()

def assemble_final_video():
    print("\n=== Phase 3: Concatenating All Scenes into Final Video ===")
    concat_txt = VIDEO_DIR / "concat_list.txt"
    lines = []
    for scene in SCENES:
        fpath = scene["final_mp4"]
        lines.append(f"file '{fpath}'")
        
    with open(concat_txt, "w") as f:
        f.write("\n".join(lines) + "\n")
        
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_txt),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-b:v", "4000k",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(OUTPUT_VIDEO)
    ]
    run(cmd_concat)
    
    total_dur = get_duration(OUTPUT_VIDEO)
    size_mb = os.path.getsize(OUTPUT_VIDEO) / (1024 * 1024)
    print(f"\n SUCCESS: Final video produced at {OUTPUT_VIDEO}")
    print(f" Duration: {total_dur:.2f}s ({total_dur/60:.2f} minutes)")
    print(f" File size: {size_mb:.2f} MB")

if __name__ == "__main__":
    ensure_audio()
    
    # Render image scenes (1, 2, 8)
    for scene in SCENES:
        if scene["type"] == "image":
            render_image_scene(scene)
            
    # Record browser scenes (3, 4, 5, 6, 7)
    record_browser_scenes()
    
    # Assemble final video
    assemble_final_video()
