#import google.generativeai as genai
#import sys, os, requests
 
#genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
#model = genai.GenerativeModel("gemini-2.0-flash")
 
#def analyze(logs):
#    prompt = f"Analyze these DevSecOps logs for the Hardened Socks Shop app. Explain the failure and suggest a fix.\n\n{logs}"
#    response = model.generate_content(prompt)
#    requests.post(os.environ.get("SLACK_WEBHOOK"), json={"text": f"🚨 *AI Analysis:*\n{response.text}"})
 
#if __name__ == "__main__":
#    analyze(sys.stdin.read())


#import sys
#import os

#try:
    #import google.generativeai as genai
    #genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
    #model = genai.GenerativeModel('gemini-2.0-flash')
    
    #def analyze(text):
     #   prompt = f"Analyze the following Trivy vulnerability scan results for security risks and suggest remediation steps:\n\n{text}"
     #  response = model.generate_content(prompt)
     #   requests.post(os.environ.get("SLACK_WEBHOOK"), json={"text": f"🚨 *AI Analysis:*\n{response.text}"})
     #   print(response.text)
#except Exception as e:
 #   print(f"AI analysis unavailable: {e}")

import os
import sys
import json
import requests

FASTAPI_URL = os.getenv(
    "FASTAPI_URL",
    "http://192.168.189.128:8000/cicd-alert"
)


def analyze(trivy_report):

    payload = {
        "pipeline": os.getenv("JOB_NAME", "Sock Shop"),
        "stage": os.getenv("STAGE_NAME", "Unknown Stage"),
        "status": os.getenv("BUILD_STATUS", "FAILED"),

        "sonar_summary": {
            "bugs": int(os.getenv("SONAR_BUGS", "0")),
            "vulnerabilities": int(os.getenv("SONAR_VULNERABILITIES", "0")),
            "hotspots": int(os.getenv("SONAR_HOTSPOTS", "0"))
        },

        "trivy_report": trivy_report
    }

    response = requests.post(
        FASTAPI_URL,
        json=payload,
        timeout=60
    )

    print(response.text)


if __name__ == "__main__":

    report = sys.stdin.read()

    analyze(report)






