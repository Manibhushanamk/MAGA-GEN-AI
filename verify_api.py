import urllib.request
import json

def verify_api():
    url = "http://localhost:8000/analyze_project"
    data = {
        "area": 1000,
        "floors": 2,
        "deadline": 150,
        "budget": 500000,
        "workforce_cap": 50,
        "provider": "gemini",
        "api_key": "test_key"
    }
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            body = response.read().decode('utf-8')
            with open("backend_status.txt", "w") as f:
                f.write(f"Status: {status}\nBody: {body}")
            print("Verification successful")
    except Exception as e:
        with open("backend_status.txt", "w") as f:
            f.write(f"Error: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_api()
