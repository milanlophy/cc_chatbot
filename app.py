import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
import chromadb

load_dotenv()

app = Flask(__name__)

# Gemini
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

client = genai.Client(api_key=api_key)

# ChromaDB
chroma_client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = chroma_client.get_collection(
    name="college_information"
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    question = data.get("message", "").strip()

    if not question:
        return jsonify({
            "error": "Please enter a question."
        }), 400

    # -----------------------------
    # Create question embedding
    # -----------------------------

    embedding_response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=question
    )

    question_embedding = embedding_response.embeddings[0].values

    # -----------------------------
    # Search ChromaDB
    # -----------------------------

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=5
    )

    documents = results["documents"][0]

    context = "\n\n".join(documents)

    # -----------------------------
    # Ask Gemini
    # -----------------------------

    prompt = f"""
    You are a college information assistant.

    Your job is to answer the student's question using the
    college information provided below.

    IMPORTANT RULES:

    1. Carefully read ALL the provided college information.
    2. Answer the student's question directly.
    3. Do not repeat unrelated information.
    4. Do not invent or guess facts.
    5. If the information truly cannot be found in the provided
    context, say:
    "I don't have that information in the college database."
    6. Give a short, natural answer.

    COLLEGE INFORMATION:
    {context}

    STUDENT QUESTION:
    {question}

    ANSWER:
    """

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return jsonify({
        "reply": response.text
    })


if __name__ == "__main__":
    app.run(debug=True)