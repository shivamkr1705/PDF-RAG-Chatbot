const chatBox = document.getElementById("chatBox");
const uploadStatus = document.getElementById("uploadStatus");

// Add message to chat
function addMessage(text, sender) {

    const msg = document.createElement("div");

    msg.className = `message ${sender}`;

    msg.innerText = text;

    chatBox.appendChild(msg);

    chatBox.scrollTop = chatBox.scrollHeight;
}


// Upload PDF
async function uploadPDF() {

    const fileInput = document.getElementById("pdfFile");

    if (fileInput.files.length === 0) {

        alert("Please choose a PDF.");

        return;
    }

    uploadStatus.innerText = "Uploading...";

    const formData = new FormData();

    formData.append("pdf", fileInput.files[0]);

    try {

        const response = await fetch("/upload", {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        uploadStatus.innerText = data.message;

        if (data.success) {

            addMessage(
                "✅ PDF uploaded successfully. Ask me anything!",
                "bot"
            );

        } else {

            addMessage(
                "❌ " + data.message,
                "bot"
            );

        }

    }

    catch (err) {

        console.error(err);

        uploadStatus.innerText = "Upload Failed";

        addMessage(
            "Upload failed.",
            "bot"
        );

    }

}



// Ask Question
async function sendQuestion() {

    const input = document.getElementById("question");

    const question = input.value.trim();

    if (question === "")
        return;

    addMessage(question, "user");

    input.value = "";

    // Thinking message
    const thinking = document.createElement("div");

    thinking.className = "message bot";

    thinking.innerText = "Thinking...";

    chatBox.appendChild(thinking);

    chatBox.scrollTop = chatBox.scrollHeight;

    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                question: question

            })

        });

        const data = await response.json();

        thinking.remove();

        addMessage(
            data.answer,
            "bot"
        );

    }

    catch (err) {

        thinking.remove();

        addMessage(
            "Something went wrong.",
            "bot"
        );

        console.error(err);

    }

}



// Press Enter
document
.getElementById("question")
.addEventListener("keypress", function(e){

    if(e.key==="Enter"){

        sendQuestion();

    }

});