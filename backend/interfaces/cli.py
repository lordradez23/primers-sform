
import sys
import os
import requests
from typing import List, Dict

# Core Engine Imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.engine import PrimersEngine

def main():
    engine = PrimersEngine()
    print("\n" + "="*60)
    print("   PRIMERS GPT // CLI INTERFACE v3.0 (PHASE 5)")
    print("   STATUS: SOVEREIGN | MEMORY: STRATIFIED (M1/M2/M3)")
    print("-" * 60)
    
    # Show active governance
    status = engine.gov.get_status()
    for cap, state in status.items():
        print(f"   [{state}] {cap}")
    print("="*60 + "\n")

    while True:
        try:
            user_input = input("USER >> ")
            if user_input.lower() in ['exit', 'quit']:
                print("SYSTEM >> Shutting down.")
                break
            
            # Direct Engine Call
            response = engine.process(user_input, mode="cli")
            
            print(f"\nPRIMERS [{response.tone.value.upper()}] >> {response.content}")
            print(f"Confidence: {response.confidence:.2f}")
            print("-" * 30)
            print("[TRACE Log]")
            for step in response.trace.steps:
                 print(f"  > [{step.intent}] {step.action}: {step.output_summary} ({step.confidence:.2f})")
            print("-" * 30 + "\n")
            
        except KeyboardInterrupt:
            print("\nSYSTEM >> Interrupted.")
            break
        except Exception as e:
            print(f"SYSTEM >> Error: {e}")

if __name__ == "__main__":
    main()
