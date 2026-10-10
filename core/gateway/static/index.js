let isAuthenticated = false;
let apiKey = "";

window.onload = function () {
    setTimeout(() => {
        addMessage("🔑 Please enter your API key to begin.", "bot");
    }, 500);
};

// ✅ MAIN CHAT FUNCTION
async function sendMessage() {

    const input = document.getElementById("message");
    const text = input.value.trim();

    if (!text) return;

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
            if (!res.ok) {
                throw new Error("Authentication request failed");
            }

            isAuthenticated = true;

            addMessage("✅ Authentication successful! What can I help you with?", "bot");
            return;

        } catch (err) {
            addMessage("❌ Server error", "bot");
            return;
        }
    }

    addMessage(text, "user");

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
        addResponse(data);

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
    msg.textContent = text;

    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
}

function addResponse(response) {
    const chat = document.getElementById("chat");
    const message = document.createElement("div");
    message.className = "message bot";

    if (response.error || response.detail) {
        addCard(message, `❌ ${response.error || response.detail}`);
    } else {
        for (const item of Object.values(response)) {
            if (!item) continue;

            if (item.error) {
                addCard(message, `❌ ${item.error}`);
            } else if (item.research_output) {
                addCard(message, `🔍 ${item.research_output}`);
            } else if (item.identified_language) {
                addCard(
                    message,
                    `📌 ${item.task || ""}\n💻 ${item.identified_language}`,
                );
            }
        }
    }

    if (!message.childElementCount) {
        message.textContent = "⚠️ No valid response received";
    }
    chat.appendChild(message);
    chat.scrollTop = chat.scrollHeight;
}

function addCard(parent, text) {
    const card = document.createElement("div");
    card.className = "card";
    card.textContent = text;
    parent.appendChild(card);
}

// Loader
function showLoader() {
    document.getElementById("loader").classList.remove("hidden");
}

function hideLoader() {
    document.getElementById("loader").classList.add("hidden");
}
document.getElementById("message").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});
