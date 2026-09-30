from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from hindsight_client import Hindsight


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# CONNECT TO HINDSIGHT CLOUD
# ==========================================

hindsight = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=os.getenv("HINDSIGHT_API_KEY")
)


# Hindsight memory bank
BANK_ID = "incident-response-agent"


# ==========================================
# CREATE FASTAPI APP
# ==========================================

app = FastAPI(
    title="Incident Response Agent",
    description="An AI agent that learns from past incidents",
    version="1.0.0"
)


# ==========================================
# ENABLE FRONTEND CONNECTION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# LOCAL INCIDENT STORAGE
# ==========================================

incident_history = []


# ==========================================
# INCIDENT INPUT MODEL
# ==========================================

class Incident(BaseModel):
    description: str


# ==========================================
# HOME PAGE
# ==========================================

@app.get("/")
def home():

    return {
        "message": "Incident Response Agent is running!",
        "status": "success"
    }


# ==========================================
# ANALYZE INCIDENT
# ==========================================

def analyze_incident(description: str):

    text = description.lower()


    # SERVER OUTAGE
    if "server" in text and "down" in text:

        return {
            "type": "Server Outage",
            "severity": "High",
            "action": "Check server health and restart the affected service."
        }


    # LOGIN / AUTHENTICATION
    elif "login" in text or "password" in text:

        return {
            "type": "Authentication Issue",
            "severity": "Medium",
            "action": "Check authentication service and user account status."
        }


    # PAYMENT
    elif "payment" in text or "transaction" in text:

        return {
            "type": "Payment Service Failure",
            "severity": "High",
            "action": "Check payment service, transaction logs, payment gateway and database connectivity."
        }


    # NETWORK
    elif "network" in text or "internet" in text:

        return {
            "type": "Network Issue",
            "severity": "High",
            "action": "Check network connectivity, router, switch and DNS."
        }


    # UNKNOWN
    else:

        return {
            "type": "Unknown",
            "severity": "Medium",
            "action": "Investigate the incident and collect more information."
        }


# ==========================================
# CREATE RECOMMENDATION
# ==========================================

def create_recommendation(
    incident_description,
    analysis,
    memories
):

    # Get Hindsight memories
    memory_results = memories.results

    # Number of memories
    memory_count = len(memory_results)

    # Store useful memory text
    past_memory_text = []


    # Only show first 5 recalled memories
    for memory in memory_results[:5]:

        if hasattr(memory, "text"):

            past_memory_text.append(
                memory.text
            )


    # Default recommendation

    root_cause = (
        "Root cause is not yet known."
    )

    resolution = (
        "Collect additional information "
        "and investigate the incident."
    )


    runbook = [

        "1. Collect incident details.",

        "2. Check system logs.",

        "3. Identify the affected component.",

        "4. Investigate possible causes.",

        "5. Apply the appropriate fix.",

        "6. Verify the system."
    ]


    # ======================================
    # SERVER OUTAGE
    # ======================================

    if analysis["type"] == "Server Outage":

        root_cause = (
            "Possible server or service failure."
        )

        resolution = (
            "Previous incidents indicate that checking "
            "server health and restarting the affected "
            "service can help resolve the outage."
        )

        runbook = [

            "1. Check whether the server is reachable.",

            "2. Check CPU and memory usage.",

            "3. Check the affected service status.",

            "4. Review recent server logs.",

            "5. Compare the current issue with previous server outages.",

            "6. Restart the affected service if necessary.",

            "7. Verify that the service is working again."
        ]


    # ======================================
    # AUTHENTICATION
    # ======================================

    elif analysis["type"] == "Authentication Issue":

        root_cause = (
            "Possible authentication service "
            "or user account issue."
        )

        resolution = (
            "Check the authentication service and compare "
            "the issue with previous authentication incidents."
        )

        runbook = [

            "1. Check authentication service status.",

            "2. Verify the affected user account.",

            "3. Check recent authentication logs.",

            "4. Compare with previous authentication incidents.",

            "5. Reset credentials if required.",

            "6. Test login again."
        ]


    # ======================================
    # PAYMENT
    # ======================================

    elif analysis["type"] == "Payment Service Failure":

        root_cause = (
            "Possible payment service, payment gateway, "
            "transaction processing or database issue."
        )

        resolution = (
            "Check the payment service and transaction logs, "
            "then compare the current incident with previous payment incidents."
        )

        runbook = [

            "1. Check payment service status.",

            "2. Check payment gateway connectivity.",

            "3. Review failed transaction logs.",

            "4. Check database connectivity.",

            "5. Compare with previous payment incidents.",

            "6. Fix the affected payment component.",

            "7. Test a transaction successfully."
        ]


    # ======================================
    # NETWORK
    # ======================================

    elif analysis["type"] == "Network Issue":

        root_cause = (
            "Possible network connectivity, DNS, "
            "router or switch issue."
        )

        resolution = (
            "Check network connectivity and compare "
            "the current problem with previous network incidents."
        )

        runbook = [

            "1. Check network connectivity.",

            "2. Check router and switch status.",

            "3. Check DNS resolution.",

            "4. Review network logs.",

            "5. Compare with previous network incidents.",

            "6. Restore network connectivity.",

            "7. Verify the affected service."
        ]


    # ======================================
    # RETURN RECOMMENDATION
    # ======================================

    return {

        "root_cause": root_cause,

        "resolution": resolution,

        "runbook": runbook,

        "past_memories_used": memory_count,

        "memory_influenced_recommendation":
            memory_count > 0,

        "relevant_past_memory":
            past_memory_text
    }


# ==========================================
# CREATE NEW INCIDENT
# ==========================================

@app.post("/incident")
def create_incident(incident: Incident):


    # STEP 1
    # Analyze incident

    analysis = analyze_incident(
        incident.description
    )


    # STEP 2
    # Store locally

    incident_record = {

        "incident":
            incident.description,

        "analysis":
            analysis
    }

    incident_history.append(
        incident_record
    )


    # STEP 3
    # Store in Hindsight

    hindsight.retain(

        bank_id=BANK_ID,

        content=f"""
Incident: {incident.description}

Type: {analysis['type']}

Severity: {analysis['severity']}

Recommended Action: {analysis['action']}
""",

        metadata={

            "type":
                analysis["type"],

            "severity":
                analysis["severity"]
        }
    )


    # STEP 4
    # Recall previous incidents

    recalled_memories = hindsight.recall(

        bank_id=BANK_ID,

        query=incident.description
    )


    # STEP 5
    # Create recommendation

    recommendation = create_recommendation(

        incident.description,

        analysis,

        recalled_memories
    )


    # STEP 6
    # Return result

    return {

        "incident":
            incident.description,

        "analysis":
            analysis,

        "hindsight_memories":
            recalled_memories,

        "recommendation":
            recommendation,

        "status":
            "analyzed",

        "memory":
            "stored, recalled and used for recommendation"
    }


# ==========================================
# VIEW ALL INCIDENTS
# ==========================================

@app.get("/incidents")
def get_incidents():

    return {

        "total_incidents":
            len(incident_history),

        "incidents":
            incident_history
    }