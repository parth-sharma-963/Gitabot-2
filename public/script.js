/**
 * BhagavadGPT Frontend Script
 * Handles chat interaction and API communication
 */

class BhagavadGPT {
    constructor() {
        this.userInput = document.getElementById("user-input");
        this.sendBtn = document.getElementById("send-btn");
        this.chatMessages = document.getElementById("chat-messages");
        this.baseUrl = window.location.origin;
        
        this.initializeEventListeners();
        this.sendInitialGreeting();
    }

    initializeEventListeners() {
        this.sendBtn.addEventListener("click", () => this.sendMessage());
        this.userInput.addEventListener("keypress", (event) => {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                this.sendMessage();
            }
        });
    }

    sendInitialGreeting() {
        const greeting = `Welcome to BhagavadGPT! 🙏

I'm here to help you find wisdom from the Bhagavad Gita that relates to your questions and challenges.

Try asking:
• "I feel anxious"
• "How do I find peace?"
• "What should I do when facing difficulty?"
• "How can I manage work and life balance?"

Ask your question and I'll share relevant verses with you.`;
        
        this.addMessage(greeting, "bot");
    }

    addMessage(text, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");
        messageDiv.textContent = text;
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    addLoadingMessage() {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", "bot-message", "loading");
        messageDiv.textContent = "🔍 Searching for relevant verses...";
        messageDiv.id = "loading-message";
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    removeLoadingMessage() {
        const loadingMsg = document.getElementById("loading-message");
        if (loadingMsg) {
            loadingMsg.remove();
        }
    }

    async sendMessage() {
        const messageText = this.userInput.value.trim();
        if (messageText === "") return;

        // Add user message to chat
        this.addMessage(messageText, "user");
        this.userInput.value = "";
        this.sendBtn.disabled = true;

        // Show loading state
        this.addLoadingMessage();

        try {
            const response = await fetch(`${this.baseUrl}/api/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: messageText }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Remove loading message
            this.removeLoadingMessage();
            
            // Add bot response
            this.addMessage(data.reply || "No response received", "bot");
            
        } catch (error) {
            this.removeLoadingMessage();
            console.error("Error:", error);
            this.addMessage(
                "Sorry, something went wrong. Please try again.\n\nError: " + error.message,
                "bot"
            );
        } finally {
            this.sendBtn.disabled = false;
            this.userInput.focus();
        }
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    new BhagavadGPT();
});
