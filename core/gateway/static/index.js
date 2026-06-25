let isAuthenticated = false;
let apiKey = "";

window.onload = function () {
    setTimeout(() => {
        addMessage("🔑 Please enter your API key to begin.", "bot");
    }, 500);
};


// ✅ AUTHENTICATE FIRST
async function authenticate() {

    const apiKey = document.getElementById("apiKeyInput").value;

    if (!apiKey) {
        alert("⚠️ Enter API key");
        return;
    }

    try {
        const res = await fetch("/authenticate", {
            method: "POST",
            headers: {
                "x-api-key": apiKey
            }
        });

        if (res.status === 401) {
            addMessage("❌ Invalid API Key", "bot");
            return;
        }

        isAuthenticated = true;

        addMessage("✅ Authentication successful! You can now chat.", "bot");

    } catch (err) {
        addMessage("❌ Server error", "bot");
    }
}



// ✅ MAIN CHAT FUNCTION
async function sendMessage() {

    const input = document.getElementById("message");
    const text = input.value.trim();

    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    // ✅ STEP 1: AUTHENTICATION
    if (!isAuthenticated) {
        apiKey = text;

        try {
            const res = await fetch("/authenticate", {
                method: "POST",
                headers: {
                    "x-api-key": apiKey
                }
            });

            if (res.status === 401) {
                addMessage("❌ Invalid API Key. Try again.", "bot");
                return;
            }

            isAuthenticated = true;

            addMessage("✅ Authentication successful! What can I help you with?", "bot");
            return;

        } catch (err) {
            addMessage("❌ Server error", "bot");
            return;
        }
    }

    // ✅ STEP 2: NORMAL CHAT
    showLoader();

    try {
        const response = await fetch("/run", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "x-api-key": apiKey
            },
            body: JSON.stringify({ prompt: text })
        });

        if (response.status === 401) {
            isAuthenticated = false;
            apiKey = "";

            hideLoader();
            addMessage("❌ Session expired. Enter API key again.", "bot");
            return;
        }

        const data = await response.json();

        hideLoader();
        addMessage(formatResponse(data), "bot");

    } catch (error) {
        console.error(error);
        hideLoader();
        addMessage("❌ Server error", "bot");
    }
}



// Add message
function addMessage(text, sender) {
    const chat = document.getElementById("chat");

    const msg = document.createElement("div");
    msg.className = "message " + sender;
    msg.innerHTML = text;

    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
}

// Loader
function showLoader() {
    document.getElementById("loader").classList.remove("hidden");
}

function hideLoader() {
    document.getElementById("loader").classList.add("hidden");
}


function formatResponse(res) {

    if (res.error) {
        return `<div class="card">❌ ${res.error}</div>`;
    }

    let output = "";

    for (const key in res) {
        const item = res[key];

        if (!item) continue;

        if (item.error) {
            output += `<div class="card">❌ ${item.error}</div>`;
        } 
        else if (item.research_output) {
            output += `
            <div class="card">
                🔍 ${item.research_output}
            </div>`;
        } 
        else if (item.identified_language) {
            output += `
            <div class="card">
                📌 ${item.task || ""}
                <br>
                💻 <b>${item.identified_language}</b>
            </div>`;
        }
    }

    return output || "⚠️ No valid response received";
}


document.getElementById("message").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});
