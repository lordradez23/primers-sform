
import requests
import json
import time
import os

API_URL = "http://localhost:8000"

def chat(msg):
    print(f"\nUser> {msg}")
    try:
        start = time.time()
        res = requests.post(f"{API_URL}/chat", json={"message": msg, "mode": "default"})
        elapsed = time.time() - start
        
        if res.status_code == 200:
            data = res.json()["response"]
            content = data['content']
            
            # Formatting for display
            print(f"Engine ({elapsed:.2f}s)>")
            print(content)
                
            print(f"\033[90m[Meta: Intent={data['intent']} Conf={data['confidence']}]\033[0m")
        else:
            print(f"Error: {res.text}")
    except Exception as e:
        print(f"Failed: {e}")

def main():
    print("\n--- 1. AST Analysis of Core System ---")
    chat("analyze corpus")
    
    print("\n--- 2. Logic Comparison ---")
    sep = os.sep
    target_a = f"backend{sep}core{sep}engine.py"
    target_b = f"backend{sep}cognition{sep}comparator.py"
    chat(f"compare {target_a} vs {target_b}")

    print("\n--- 3. GitHub Learning ---")
    chat("learn from github octocat")
    
    print("\n--- 4. Explanation (Simulated LLM) ---")
    chat("explain architecture")

if __name__ == "__main__":
    time.sleep(1) 
    main()
