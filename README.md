# 🚀 Simple RAG: Chat With Your Documents!

Hey there! Welcome to **Simple RAG**, a neat little application that lets you upload text or PDF files and literally chat with them. It combines the power of open-source embeddings, FAISS (for blazing-fast document searching), and Groq's super-fast LLMs to generate answers based *only* on the documents you provide. 

This isn't a bloated, overly complex system—it's designed to be lightweight, easy to run, and fun to play with. Whether you're trying to build your own personal research assistant, or just want to learn how Retrieval-Augmented Generation (RAG) works, you're in the right place!

## ✨ What Does It Do?

- **Talk to Your Docs**: Just upload a PDF or text file, and start asking questions. Let the AI do the reading for you.
- **Fast as Lightning ⚡**: Uses local Hugging Face embeddings and FAISS for instant search, while Groq handles the heavy lifting of generating an answer in milliseconds.
- **Sleek Interface**: Comes out-of-the-box with a custom, modern web interface. No clunky notebooks here!
- **Developer Friendly**: It's all glued together with FastAPI, so you can easily plug your own frontend or integrations into it.

## 🛠️ What You Need to Get Started

Before you run the code, you'll need just two things:
- Python 3.8 or newer installed on your machine.
- A **Groq API Key**. It's super easy (and currently free) to get—just head over to the [Groq Console](https://console.groq.com), create an account, and grab your key.

## 🚀 How to Run It!

Let's get this thing up and running on your local machine.

**1. Clone the project**
```bash
git clone <your-repository-url>
cd simple_rag
```

**2. Make a cozy home for your Python packages (Virtual Environment)**
We don't want to mess up your system's global Python setup, so let's use a virtual environment:
```bash
python -m venv venv

# If you're using Windows run this:
venv\Scripts\activate

# If you're on a Mac or Linux run this:
source venv/bin/activate
```

**3. Install the good stuff**
```bash
pip install -r requirements.txt
```

**4. Set up your secret key**
Create a new file in the root folder named exactly `.env` and paste your Groq API key inside like this:
```env
GROQ_API_KEY=your_super_secret_groq_api_key_here
```

**5. Start the engine! 🏎️**
```bash
uvicorn main:app --reload
```

Boom. You're done! Open up your browser and go to `http://127.0.0.1:8000`. You'll see the frontend pop right up. Drop a file in, wait a few seconds for it to process, and ask away!

## 📂 Project Structure (For the curious)

Wondering where everything lives? Here's a quick tour:

```text
simple_rag/
├── frontend/             # All the HTML, CSS, and JS that makes the UI look pretty.
├── rag_engine.py         # The brain! Handles the LangChain logic, embeddings, and talkin' to Groq.
├── main.py               # The FastAPI server connecting the frontend to the engine.
├── requirements.txt      # The list of Python libraries we need.
├── .env                  # Your secret API key (Don't ever upload this to GitHub!)
└── README.md             # You are here.
```

## 👩‍💻 Built With Love &...

- **Python & FastAPI**: For the backend Web server.
- **LangChain & Groq**: The AI pipelining magic.
- **HuggingFace & FAISS**: For reading and searching through your documents locally.
- **Vanilla HTML/CSS/JS**: Because keeping it simple works beautifully!

---
Feel free to fork this, break it, fix it, and build something awesome. Happy coding! 🎉
