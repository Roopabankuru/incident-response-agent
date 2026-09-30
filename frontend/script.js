async function analyzeIncident() {

    const input = document.getElementById("incidentInput");
    const description = input.value.trim();

    const results = document.getElementById("results");
    const loading = document.getElementById("loading");
    const error = document.getElementById("error");

    // Check input
    if (!description) {
        error.textContent = "Please describe the incident first.";
        error.classList.remove("hidden");
        return;
    }

    // Reset messages
    error.classList.add("hidden");
    results.classList.add("hidden");
    loading.classList.remove("hidden");

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/incident",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    description: description
                })
            }
        );

        if (!response.ok) {
            throw new Error("Backend returned an error.");
        }

        const data = await response.json();

        // -------------------------
        // Incident Analysis
        // -------------------------

        document.getElementById("incidentType").textContent =
            data.analysis.type;

        document.getElementById("severity").textContent =
            data.analysis.severity;

        document.getElementById("action").textContent =
            data.analysis.action;


        // -------------------------
        // Hindsight Memory
        // -------------------------

        const recommendation = data.recommendation;

        document.getElementById("memoryCount").textContent =
            recommendation.past_memories_used;

        document.getElementById("memoryInfluenced").textContent =
            recommendation.memory_influenced_recommendation
                ? "Yes"
                : "No";


        // -------------------------
        // Past Memories
        // -------------------------

        const memoryContainer =
            document.getElementById("pastMemories");

        memoryContainer.innerHTML = "";

        const memories =
            recommendation.relevant_past_memory || [];

        if (memories.length === 0) {

            memoryContainer.innerHTML =
                "<p>No relevant past memories found.</p>";

        } else {

            memories.forEach(memory => {

                const memoryBox =
                    document.createElement("div");

                memoryBox.className = "memory-item";

                memoryBox.textContent = memory;

                memoryContainer.appendChild(memoryBox);

            });

        }


        // -------------------------
        // Root Cause
        // -------------------------

        document.getElementById("rootCause").textContent =
            recommendation.root_cause;


        // -------------------------
        // Resolution
        // -------------------------

        document.getElementById("resolution").textContent =
            recommendation.resolution;


        // -------------------------
        // Runbook
        // -------------------------

        const runbook =
            document.getElementById("runbook");

        runbook.innerHTML = "";

        recommendation.runbook.forEach(step => {

            const li =
                document.createElement("li");

            li.textContent = step;

            runbook.appendChild(li);

        });


        // Show results
        results.classList.remove("hidden");

    }

    catch (err) {

        console.error(err);

        error.textContent =
            "Unable to connect to the Incident Response Agent backend. Make sure FastAPI is running on port 8000.";

        error.classList.remove("hidden");

    }

    finally {

        loading.classList.add("hidden");

    }
}


// -------------------------
// Clear Results
// -------------------------

function clearResults() {

    document.getElementById("incidentInput").value = "";

    document.getElementById("results").classList.add("hidden");

    document.getElementById("error").classList.add("hidden");

}