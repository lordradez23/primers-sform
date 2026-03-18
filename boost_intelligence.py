import os
import sys
import subprocess

def boost():
    print("--- PRIMERS S-FORM INTELLIGENCE BOOSTER ---")
    print("This script will set up a local LLM environment for the Sovereign Intelligence.")
    
    # 1. Check for Ollama
    try:
        subprocess.run(["ollama", "--version"], capture_output=True, check=True)
        print("[FOUND] Ollama detected. Pulling recommended model (Llama3)...")
        subprocess.run(["ollama", "pull", "llama3"])
        print("[SUCCESS] Llama3 is ready. Sovereign Intelligence is now at full capacity.")
        return
    except:
        print("[MISSING] Ollama not found in path.")

    # 2. Offer to install via Winget or provide link
    print("\nTo run truly Sovereign (Local) Intelligence, I recommend installing Ollama.")
    print("Download it here: https://ollama.com/download/windows")
    print("\nAlternatively, I can try to install it for you via Winget if available.")
    
    choice = input("Attempt Winget installation? (y/n): ")
    if choice.lower() == 'y':
        try:
            subprocess.run(["winget", "install", "Ollama.Ollama"], check=True)
            print("[SUCCESS] Ollama installed. Please restart your terminal and run this booster again.")
        except:
            print("[FAILED] Winget not available or installation failed.")
    
    print("\n--- Current Status: Symbolic Reflex Mode active. ---")
    print("The system is currently using a 3-layer cognitive fallback. For full natural language, install Ollama.")

if __name__ == "__main__":
    boost()
