import requests

try:
    r = requests.get("https://api.veo3gen.ai/v1/generate")
    print(r.status_code)
except Exception as e:
    print("Error:", e)
