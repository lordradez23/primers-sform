
import requests
import json
import sys
import time

API_URL = "http://localhost:8000"

def type_writer(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def main():
    print("\nInitializing Neural Link...")
    try:
        res = requests.get(f"{API_URL}/")
        print(f"Connected to {res.json()['system']} v{res.json()['version']}")
    except:
        print("Backend offline. Please start 'run_backend.bat' first.")
        return

    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("USER> ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            payload = {"message": user_input, "mode": "default"}
            
            print("Thinking...", end="\r")
            try:
                start = time.time()
                resp = requests.post(f"{API_URL}/chat", json=payload)
                elapsed = time.time() - start
                
                if resp.status_code == 200:
                    data = resp.json()["response"]
                    
                    sys.stdout.write("\033[K") # Clear line
                    print(f"ENGINE ({elapsed:.2f}s)> ", end="")
                    type_writer(data["content"])
                    
                    # Show intent/confidence briefly
                    meta = f"[{data['intent'].upper()} | {data['confidence']:.2f}]"
                    print(f"\033[90m{meta}\033[0m\n")
                    
                else:
                    print(f"Error: {resp.text}")
            except Exception as e:
                print(f"Request failed: {e}")

        except KeyboardInterrupt:
            break
            
    print("\nSession terminated.")

if __name__ == "__main__":
    main()
