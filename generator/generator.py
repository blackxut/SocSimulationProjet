import httpx
import random
import time
import os

# URL to use for sending the logs to the API
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/alerts")

# all scenarios used for now
# is_malicious determines if the alert is real or not
ATTACK_SCENARIOS = [
    {
        "event_type": "SSH Brute-Force",
        "score": 8.5,
        "message": "Multiple failed login attempts detected from unauthorized IP.",
        "is_malicious": True
    },
    {
        "event_type": "Port Scan",
        "score": 3.0,
        "message": "Nmap TCP SYN scan detected across common ports (Benign administrative scan).",
        "is_malicious": False
    },
    {
        "event_type": "SQL Injection",
        "score": 9.2,
        "message": "Suspicious SQL syntax payload found in HTTP GET parameter.",
        "is_malicious": True
    },
    {
        "event_type": "Malware C2 Beacon",
        "score": 9.8,
        "message": "Outbound connection to known command and control domain.",
        "is_malicious": True
    },
    {
        "event_type": "Privilege Escalation",
        "score": 7.5,
        "message": "Unauthorized sudo execution attempt by non-admin user.",
        "is_malicious": True
    },
    {
        "event_type": "Normal User Login",
        "score": 0.5,
        "message": "Standard authentication success from corporate subnet.",
        "is_malicious": False
    }
]

def generate_random_ip():
    return f"{random.randint(1,126)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"

def main():
    print("Starting the logs generator (Ctrl + C to stop)")
    
    while True:
        # picking a random scenario each time
        scenario = random.choice(ATTACK_SCENARIOS)

        # payload schema
        payload = {
            "ip_source": generate_random_ip(),
            "event_type": scenario["event_type"],
            "message": scenario["message"],
            "score": scenario["score"],
            "is_malicious": scenario["is_malicious"]
        }

        try:
            response = httpx.post(API_URL, json=payload)
            if response.status_code in [200, 201]:
                status_label = "Malicious" if scenario["is_malicious"] else "Benign"
                print(f"[+] Alert sent [{status_label}] : {scenario['event_type']} from {payload['ip_source']} (Score: {scenario['score']})")
            else:
                print(f"[-] API Error ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"[!] Cannot reach API: {e}")

        time.sleep(random.randint(2, 5))

if __name__ == "__main__":
    main()