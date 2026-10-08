async function sendMessage() {

    const input = document.getElementById("message");

    const chatBox = document.getElementById("chat-box");

    const message = input.value.trim();

    if (!message) {
        return;
    }


    // Display user message

    chatBox.innerHTML += `
        <div class="message user">
            ${message}
        </div>
    `;


    input.value = "";


    // Display loading message

    const loading = document.createElement("div");

    loading.className = "message bot";

    loading.innerText = "Thinking...";

    chatBox.appendChild(loading);


    chatBox.scrollTop = chatBox.scrollHeight;


    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })

        });


        const data = await response.json();


        loading.remove();


        if (data.reply) {

            chatBox.innerHTML += `
                <div class="message bot">
                    ${data.reply}
                </div>
            `;

        } else {

            chatBox.innerHTML += `
                <div class="message bot">
                    Sorry, something went wrong.
                </div>
            `;
        }


    } catch (error) {

        loading.remove();

        chatBox.innerHTML += `
            <div class="message bot">
                Unable to connect to the server.
            </div>
        `;

        console.error(error);
    }


    chatBox.scrollTop = chatBox.scrollHeight;
}


function handleKey(event) {

    if (event.key === "Enter") {

        sendMessage();

    }

}
