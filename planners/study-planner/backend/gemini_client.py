import logging
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from ddgs import DDGS
from google import genai

load_dotenv()

logger = logging.getLogger("gemini_api.client")


def perform_web_search(query: str, max_results: int = 6) -> List[Dict[str, str]]:
    """Perform a DuckDuckGo search and return a list of results.

    Each result contains: title, href, body.
    """
    results: List[Dict[str, str]] = []
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
            for result in raw_results:
                if not isinstance(result, dict):
                    continue
                title = result.get("title", "").strip()
                href = result.get("href", "").strip()
                body = result.get("body", "").strip()
                if title and href:
                    results.append({"title": title, "href": href, "body": body})
        return results
    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}", exc_info=True)
        return []


class GeminiClient:
    """Manages interaction with the Gemini API and optional web-search agent workflows."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

        if not api_key:
            logger.warning("GEMINI_API_KEY is not set in environment variables.")

        try:
            self.client = genai.Client(api_key=api_key)
            self.chat = self.client.chats.create(model=model_name)
            logger.info(f"Initialized Gemini Client with model: {model_name}")
        except Exception as e:
            logger.error(f"Error configuring Gemini API: {e}", exc_info=True)
            self.chat = None

    def generate_response(self, user_input: str) -> str:
        """Generate an AI response with optional web search when prefixed.

        Triggers:
        - "search: <query>"
        - "/search <query>"
        """
        if not self.chat:
            return "AI service is not configured correctly. Please check your GEMINI_API_KEY."

        try:
            text = (user_input or "").strip()
            lower = text.lower()

            # Parse search commands
            search_query: Optional[str] = None
            if lower.startswith("search:"):
                search_query = text.split(":", 1)[1].strip()
            elif lower.startswith("/search "):
                search_query = text.split(" ", 1)[1].strip()

            if search_query:
                logger.info(f"Performing web search for query: '{search_query}'")
                web_results = perform_web_search(search_query, max_results=6)

                if not web_results:
                    return f"I performed a search for '{search_query}', but could not retrieve web results right now."

                # Format search references
                refs_lines = [
                    f"[{idx}] {item['title']} — {item['href']}\n{item['body']}"
                    for idx, item in enumerate(web_results, start=1)
                ]
                refs_block = "\n\n".join(refs_lines)

                system_prompt = (
                    "You are an AI research and study assistant. Use the provided web search results "
                    "to answer the user's request accurately. Synthesize concisely, cite sources "
                    "inline using [1], [2] where applicable, and provide clear learning insights."
                )
                composed_prompt = (
                    f"<system>\n{system_prompt}\n</system>\n"
                    f"<user_query>\n{search_query}\n</user_query>\n"
                    f"<web_results>\n{refs_block}\n</web_results>"
                )

                response = self.chat.send_message(composed_prompt)
                return response.text

            # Standard chat interaction
            response = self.chat.send_message(text)
            return response.text

        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}", exc_info=True)
            return "I'm sorry, I encountered an error processing your request."









# import os
# from typing import List, Dict
# from dotenv import load_dotenv
# from google import genai
# from duckduckgo_search import DDGS


# load_dotenv()

# # function uses a query string and duckduckgo_search library to perform a web search
# def perform_web_search(query: str, max_results: int = 6) -> List[Dict[str, str]]:
#     """Perform a DuckDuckGo search and return a list of results.

#     Each result contains: title, href, body.
#     """
#     results: List[Dict[str, str]] = []
#     try:
#         with DDGS() as ddgs:
#             for result in ddgs.text(query, max_results=max_results):
#                 # result keys typically include: title, href, body
#                 if not isinstance(result, dict):
#                     continue
#                 title = result.get('title') or ''
#                 href = result.get('href') or ''
#                 body = result.get('body') or ''
#                 if title and href:
#                     results.append({
#                         'title': title,
#                         'href': href,
#                         'body': body,
#                     })
#         return results
#     except Exception as e:
#         print(f"DuckDuckGo search error: {e}")
#         return []

# # A class that manages the interaction with the Gemini API and core agent logic 
# class GeminiClient:
#     def __init__(self):
#         try:
#             self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
#             self.chat = self.client.chats.create(model='gemini-3.6-flash')
#         except Exception as e:
#             print(f"Error configuring Gemini API: {e}")
#             self.chat = None

#     def generate_response(self, user_input: str) -> str:
#         """Generate an AI response with optional web search when prefixed.

#         To trigger web search, start your message with one of:
#         - "search: <query>"
#         - "/search <query>"
#         Otherwise, the model responds directly using chat history.
#         """
#         if not self.chat:
#             return "AI service is not configured correctly."

#         try:
#             text = user_input or ""
#             lower = text.strip().lower()

#             # Search trigger
#             search_query = None
#             if lower.startswith("search:"):
#                 search_query = text.split(":", 1)[1].strip()
#             elif lower.startswith("/search "):
#                 search_query = text.split(" ", 1)[1].strip()

#             if search_query:
#                 web_results = perform_web_search(search_query, max_results=6)
#                 if not web_results:
#                     return "I could not retrieve web results right now. Please try again."

#                 # Build context with numbered references
#                 refs_lines = []
#                 for idx, item in enumerate(web_results, start=1):
#                     refs_lines.append(f"[{idx}] {item['title']} — {item['href']}\n{item['body']}")
#                 refs_block = "\n\n".join(refs_lines)

#                 system_prompt = (
#                     "You are an AI research assistant. Use the provided web search results to answer the user query. "
#                     "Synthesize concisely, cite sources inline like [1], [2] where relevant, and include a brief summary."
#                 )
#                 composed = (
#                     f"<system>\n{system_prompt}\n</system>\n"
#                     f"<user_query>\n{search_query}\n</user_query>\n"
#                     f"<web_results>\n{refs_block}\n</web_results>"
#                 )
#                 response = self.chat.send_message(composed)
#                 return response.text

#             # Default: normal chat
#             response = self.chat.send_message(text)
#             return response.text
#         except Exception as e:
#             print(f"Error generating response: {e}")
#             return "I'm sorry, I encountered an error processing your request."