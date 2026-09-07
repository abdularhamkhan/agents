import os
from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client()


file_path = input("Enter the path to your file: ")

if not os.path.exists(file_path):
    print("File not found.")
    exit()


uploaded_file = client.files.upload(file=file_path)

print("Uploaded file:", uploaded_file.name)


# instructions = """
# You are a file analysis assistant.

# Your job is to carefully analyze the file provided by the user.

# Answer questions using information from the file.

# If the answer can't be found in the file, clearly say that the information is not available in the file.

# Do not invent facts.

# When useful, organize your answer with headings and bullet points.
# """


instructions = """
You are an AI file analysis assistant.

Your job is to analyze the file provided by the user.

Follow these rules:

1. Use the provided file as your primary source.
2. Answer the user's question directly.
3. Do not invent information that is not supported by the file.
4. If the file does not contain enough information to answer a question, say so.
5. When summarizing, focus on the most important information.
6. When comparing ideas, clearly explain the similarities and differences.
7. When analyzing research, distinguish between results, methods, and conclusions.
8. Use simple language unless the user asks for technical language.
9. Use bullet points when they make the answer easier to understand.
10. If you make an inference, clearly label it as an inference.
"""



while True:
    question = input("\nAsk a question (or type 'exit'): ")

    if question.lower() == "exit":
        break

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=[
            uploaded_file,
            f"{instructions}\n\nUser question:\n{question}"
        ]
    )

    print("\nAgent:\n")
    print(response.text)



############################# For OpenAI API #############################
# try:
#     from openai import OpenAI
# except ImportError as exc:
#     raise ImportError(
#         "The OpenAI package is required. Install it with: pip install openai"
#     ) from exc
# import os
# from dotenv import load_dotenv


# load_dotenv()

# client = OpenAI()


# file_path = input("Enter the path to your file: ")

# if not os.path.exists(file_path):
#     print("File not found.")
#     exit()


# with open(file_path, "rb") as file:
#     uploaded_file = client.files.create(
#         file=file,
#         purpose="user_data"
#     )    


# print("Uploaded file:", uploaded_file.id)



# instructions = """
# You are a file analysis assistant.

# Your job is to carefully analyze the file provided by the user.

# Answer questions using information from the file.

# If the answer can't be found in the file, clearly say that the information is not available in the file.

# Do not invent facts.

# When useful, organize your answer with headings and bullet points.
# """


# while True:
#     question = input("\nAsk a question (or type 'exit'): ")

#     if question.lower() == "exit":
#         break

#     response = client.responses.create(
#         model="gpt-5",
#         instructions=instructions,
#         input=[
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "input_text",
#                         "text": question
#                     },
#                     {
#                         "type": "input_file",
#                         "file_id": uploaded_file.id
#                     }
#                 ]
#             }
#         ]
#     )

#     print("\nAgent:\n")
#     print(response.output_text)