import subprocess
import time
import sys
import os

def run_project():
    print("--- STEP 1: Starting Local Server ---")
    # Start the server as a background process
    # We use sys.executable to ensure we use the same Python that is running this script
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=os.getcwd() # Ensure we run in the current folder
    )
    
    # Wait for server to boot
    print("Waiting 5 seconds for server to initialize...")
    time.sleep(5)

    try:
        print("\n--- STEP 2: Running Analysis Script ---")
        # Run your client script
        result = subprocess.run(
            [sys.executable, "week2_api_path_impact.py"],
            capture_output=False, # Let it print directly to console
            text=True
        )
        
        if result.returncode == 0:
            print("\nSUCCESS: Script finished cleanly.")
        else:
            print("\nFAILURE: Script crashed.")

    except Exception as e:
        print(f"\nERROR: {e}")

    finally:
        print("\n--- STEP 3: Stopping Server ---")
        server_process.terminate()
        server_process.wait()
        print("Server stopped. Done.")

if __name__ == "__main__":
    run_project()
