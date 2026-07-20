import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from google import genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=GOOGLE_API_KEY)

VECTOR_DB = "vectorstore"

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"
)


def process_pdf(pdf_path):
    """
    Load PDF, split text into chunks,
    generate embeddings and save to FAISS.
    """

    loader = PyPDFLoader(pdf_path)

    documents = loader.load()

    if len(documents) == 0:
        raise Exception("No text found inside PDF.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300
    )

    chunks = splitter.split_documents(documents)

    if len(chunks) == 0:
        raise Exception("Could not create chunks.")

    vectorstore = FAISS.from_documents(
        chunks,
        embedding_model
    )

    vectorstore.save_local(VECTOR_DB)


def ask_question(question):

    if not os.path.exists(VECTOR_DB):
        return "Please upload a PDF first."

    vectorstore = FAISS.load_local(
        VECTOR_DB,
        embedding_model,
        allow_dangerous_deserialization=True
    )

    retriever = vectorstore.as_retriever(
       search_kwargs={"k":10}
    )

    docs = retriever.invoke(question)

    if len(docs) == 0:
        return "No relevant information found."

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
You are an expert research assistant.

Your job is to answer questions based ONLY on the uploaded PDF.

Instructions:
- Write natural, human-like answers.
- Explain concepts clearly.
- Combine information from multiple retrieved sections when appropriate.
- If the document contains enough information, provide a detailed explanation.
- Do not invent facts that are not supported by the document.
- If the document truly does not contain the answer, say:
  "I couldn't find sufficient information in the uploaded PDF."

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text