import requests, sys, json, time

QUESTIONS = [
 "What are the biggest mistakes in early pricing?",
 "Which 3 experiments lift retention in the first 60 days?",
 "Non-discount tactics to close deals at quarter-end?",
 "How do you prioritize a roadmap with no usage data?",
]

base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"

def score(ans):
    ok = 0
    ok += 1 if "•" in ans or "-" in ans else 0
    ok += 1 if "[1]" in ans or "[2]" in ans else 0
    ok += 1 if "Takeaway" in ans or "takeaway" in ans else 0
    return ok

report = []
for q in QUESTIONS:
    r = requests.get(f"{base}/ask", params={"question": q, "top_k": 5}, timeout=30)
    j = r.json()
    s = score(j.get("answer",""))
    report.append({"q": q, "score": s, "len": len(j.get("answer","")), "refs": len(j.get("references",[]))})
    time.sleep(0.3)

print(json.dumps(report, indent=2))
