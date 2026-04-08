"""
Product Launch War Room — Multi-Agent Decision System
======================================================
Simulates a cross-functional war room that analyzes launch metrics and user
feedback to produce a structured Proceed / Pause / Roll Back decision.

Usage:
    python main.py

Requires:
    GOOGLE_API_KEY environment variable set with a valid Google AI API key.
"""

import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv


def main():
    load_dotenv()

    # Validate API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY environment variable is not set.")
        print("Copy .env.example to .env and add your Google AI API key.")
        sys.exit(1)

    # Setup paths
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / "output"
    data_dir = base_dir / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Setup logging
    from utils.logger import setup_logger
    logger = setup_logger(output_dir)
    logger.info("=" * 60)
    logger.info("PRODUCT LAUNCH WAR ROOM — Starting Analysis")
    logger.info("=" * 60)

    # Configure tools with data directory
    from tools import configure_data_dir
    configure_data_dir(data_dir)
    logger.info(f"Data directory: {data_dir}")

    # Initialize LLM
    from crewai import LLM
    llm = LLM(
        model="gemini/gemini-2.5-flash",
        api_key=api_key,
        temperature=0.2,
    )
    logger.info("LLM initialized: gemini/gemini-2.5-flash")

    # Build and run the crew
    from orchestrator.warroom import build_crew
    crew = build_crew(llm=llm, output_dir=output_dir)

    print("\n" + "=" * 60)
    print("  PRODUCT LAUNCH WAR ROOM")
    print("  Feature: Smart Workflow Builder")
    print("  Rollout: 30% of users")
    print("  Agents: 6 (PM, Data Analyst, Marketing, Risk, SRE, CS)")
    print("=" * 60 + "\n")

    start_time = time.time()
    logger.info("Crew kickoff — running 6 agents sequentially...")

    result = crew.kickoff()

    elapsed = time.time() - start_time
    logger.info(f"Crew completed in {elapsed:.1f} seconds")

    # Save structured output
    output_path = output_dir / "launch_decision.json"
    try:
        # CrewAI returns the pydantic model when output_pydantic is set
        if hasattr(result, "pydantic"):
            output_data = result.pydantic.model_dump()
        elif hasattr(result, "json_dict"):
            output_data = result.json_dict
        else:
            # Fallback: try to parse raw output as JSON
            raw = str(result.raw) if hasattr(result, "raw") else str(result)
            output_data = json.loads(raw)

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2, default=str)

        logger.info(f"Decision saved to: {output_path}")
    except (json.JSONDecodeError, AttributeError) as e:
        logger.warning(f"Could not parse structured output: {e}")
        # Save raw output as fallback
        raw_path = output_dir / "launch_decision_raw.txt"
        with open(raw_path, "w") as f:
            f.write(str(result.raw) if hasattr(result, "raw") else str(result))
        logger.info(f"Raw output saved to: {raw_path}")
        output_data = None

    # Print summary
    print("\n" + "=" * 60)
    print("  WAR ROOM COMPLETE")
    print("=" * 60)

    if output_data:
        decision = output_data.get("decision", "UNKNOWN")
        confidence = output_data.get("confidence", {})
        score = confidence.get("score", "N/A") if isinstance(confidence, dict) else "N/A"
        print(f"\n  Decision: {decision}")
        print(f"  Confidence: {score}")
        print(f"  Duration: {elapsed:.1f}s")
    else:
        print("\n  Decision output could not be parsed as JSON.")
        print("  Check output/launch_decision_raw.txt for raw output.")

    print(f"\n  Output files:")
    print(f"    - {output_path}")
    print(f"    - {output_dir / 'warroom_trace.log'}")
    print()


if __name__ == "__main__":
    main()
