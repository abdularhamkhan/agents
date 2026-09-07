# File Analysis Agent

A small command-line project that lets you upload a local file to Google Gemini and ask questions about its contents.

This project is intentionally simple. It demonstrates the main building blocks of a file-analysis agent:

1. Load configuration from environment variables.
2. Create an API client.
3. Read and validate a file path.
4. Upload the file to the model provider.
5. Accept questions in a loop.
6. Send the uploaded file and instructions with each question.
7. Print the model's response.

## Project Structure

```text
file_analysis_agent/
├── agent.py
├── requirements.txt
└── README.md
```

- `agent.py` contains the complete command-line agent.
- `requirements.txt` lists the Python packages required to run it.
- `README.md` contains setup and usage instructions.

## Requirements

- Python 3.9 or newer
- A Google AI API key
- A file supported by the Google GenAI file upload API

## Setup

From this directory, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file in the same directory as `agent.py`:

```env
GEMINI_API_KEY=your_api_key_here
```

The `python-dotenv` package loads this value, and `google-genai` uses it when creating the client.

Do not commit `.env` or expose your API key. Add `.env` to `.gitignore` if it is not already ignored.

## Run the Agent

```bash
python agent.py
```

When prompted, enter the path to a file. After the upload succeeds, ask questions about the file:

```text
Enter the path to your file: ./sample.pdf
Uploaded file: files/abc123

Ask a question (or type 'exit'): What is the main topic?

Agent:
...
```

Type `exit` to end the program.

## How It Works

### 1. Load configuration

```python
load_dotenv()
client = genai.Client()
```

`load_dotenv()` reads the API key from `.env`. The client uses that key to communicate with Google Gemini.

### 2. Validate and upload the file

```python
if not os.path.exists(file_path):
	print("File not found.")
	exit()

uploaded_file = client.files.upload(file=file_path)
```

The local path is checked before the file is uploaded. The returned file object is then reused for each question.

### 3. Ask questions in a loop

Each question is sent together with the uploaded file and the agent instructions:

```python
response = client.models.generate_content(
	model="gemini-3.7-flash",
	contents=[uploaded_file, f"{instructions}\n\nUser question:\n{question}"]
)
```

The instructions encourage the model to use the file as its primary source, avoid unsupported claims, and say when the answer is not available.

## Limitations

- The program handles one file per run.
- It does not save conversation history between questions or runs.
- It does not retry failed uploads or API requests.
- The API key must be configured before starting the program.
- The model name is currently hard-coded in `agent.py`.

## Possible Next Steps

- Add error handling for upload and API failures.
- Allow the model name to be configured through `.env`.
- Support multiple files in one session.
- Add conversation history for follow-up questions.
- Add tests for file validation and prompt construction.

## Alternative OpenAI Example

The bottom of `agent.py` contains a commented-out OpenAI implementation. It is not part of the active program and requires different dependencies, authentication, and API calls. The active implementation uses Google Gemini with `google-genai`.
