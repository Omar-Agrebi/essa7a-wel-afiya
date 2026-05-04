import asyncio
import sys
import os
import json

# --- Path Setup ---
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.tasks import run_full_pipeline

async def main():
    print("\n" + "="*50)
    print("      INTELLIGENT OBSERVATORY: FULL PIPELINE RUN")
    print("="*50 + "\n")
    
    print("Starting full multi-agent pipeline (Scrape -> Process -> Store -> Recommend -> Notify)...")
    try:
        report = await run_full_pipeline()
        
        print("\nPIPELINE EXECUTION COMPLETE")
        print("-" * 30)
        print(f"Status: {report.get('status')}")
        print(f"Duration: {report.get('duration_sec')}s")
        print(f"Raw Items Collected: {report.get('raw_collected')}")
        print(f"Cleaned: {report.get('cleaned')}")
        print(f"Classified: {report.get('classified')}")
        print(f"Clustered: {report.get('clustered')}")
        print(f"Recommendations Generated: {report.get('recommendations_generated')}")
        
        if report.get("pipeline_errors"):
            print("\nERRORS ENCOUNTERED:")
            for err in report["pipeline_errors"]:
                print(f" - {err}")
                
        print("\nAGENT DETAILS:")
        for r in report.get("agent_reports", []):
            agent_name = r.get("agent", "Unknown")
            success = "PASS" if r.get("success") else "FAIL"
            items = r.get("items_processed", 0)
            print(f" [{success}] {agent_name:25s} | Items: {items:3d}")
            
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
