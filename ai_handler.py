import requests
import traceback
from rich.console import Console
from rich.markdown import Markdown
import json
import os
from rich.live import Live


class AIHandler:
    def __init__(self, api_key, api_base):
        self.api_key = api_key
        self.api_base = api_base
        self.console = Console()

    def handle_ai_request(self, query, history):
        """Handle AI request using WildCard API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        # Add the new query to history
        history.append({"role": "user", "content": query})
        data = {
            "model": "gpt-4o",
            "messages": history,
            "stream": True
        }
        
        try:
            response = requests.post(f"{self.api_base}/v1/chat/completions", headers=headers, json=data, stream=True)
            response.raise_for_status()
            self.stream_response(response,history)
        except requests.exceptions.HTTPError as http_err:
            self.console.print(f"HTTP error occurred: {http_err}")
            self.console.print("Response content:", response.text)
        except Exception as err:
            self.console.print("Unexpected error:", err)
            traceback.print_exc()

    def handle_temporary_file_request(self, command, history):
        """Handle request to create and execute a temporary file with commands."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Add the new command to history
        history.append({"role": "user", "content": f"!{command}"})

        # Get the current working directory
        current_directory = os.getcwd()

        # Create a detailed system prompt
        system_prompt = (
        f"You are a script assistant(MacOS). Your task is to generate a JSON response to help the user solve their problem based on the given command. "
        f"The JSON response should follow this format:\n"
        f"- If the command is to execute a bash script, return:\n"
        f"{{\n"
        f"    \"action\": \"bash\",\n"
        f"    \"desc\": \"给出简短的描述,你的脚本内容\",\n"
        f"    \"content\": \"bash_script_content_here\"\n"
        f"}}\n"
        f"- If the command is to execute a python script, return:\n"
        f"{{\n"
        f"    \"action\": \"python\",\n"
        f"    \"desc\": \"给出简短的描述,你的脚本内容\",\n"
        f"    \"content\": \"python_script_content_here\"\n"
        f"}}\n"
        f"- If the command is to write to a file, return:\n"
        f"{{\n"
        f"    \"action\": \"write\",\n"
        f"    \"desc\": \"简短的描述,告诉我你编写的内容\",\n"
        f"    \"filename\": \"/path/to/file\",\n"
        f"    \"content\": \"file_content_here\"\n"
        f"}}\n"
        f"- If the command is to rewrite a file, return:\n"
        f"{{\n"
        f"    \"action\": \"rewrite\",\n"
        f"    \"desc\": \"简短的描述告诉我你重写了哪些内容\",\n"
        f"    \"filename\": \"/path/to/file\",\n"
        f"    \"content\": \"file_content_here\"\n"
        f"}}\n"
        f"Please ensure that the JSON response is properly formatted, with no additional characters outside the JSON object. "
        f"Since 'content' is a field in the JSON, ensure that special characters in the 'content' are escaped; otherwise, the JSON will not be able to be parsed ."
        f"For bash and python actions, provide only the script content in the 'content' field without any additional explanations, comments, or Markdown formatting. "
        f"The current working directory is: {current_directory}. "
        f"Here is the command: {command}"
    )

        data = {
            "model": "gpt-4o",
            "messages": history + [{"role": "system", "content": system_prompt}],
            "stream": False
        }

        try:
            response = requests.post(f"{self.api_base}/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()
            if "choices" in response_data and response_data["choices"]:
                ai_response = response_data["choices"][0]["message"]["content"]
                # Remove characters before the first { and after the last }
                ai_response = ai_response[ai_response.find("{"):ai_response.rfind("}")+1]
                return ai_response
            else:
                self.console.print("Unexpected response format:", response_data)
                return ""
        except requests.exceptions.HTTPError as http_err:
            self.console.print(f"HTTP error occurred: {http_err}")
            self.console.print("Response content:", response.text)
            return ""
        except Exception as err:
            self.console.print("Unexpected error:", err)
            traceback.print_exc()
            return ""

    def stream_response(self, response,history):
            """Stream and display the response in real-time as Markdown."""
            markdown_content = ""
            live = Live(console=self.console, refresh_per_second=4)
            live.start()  # Start the live display

            chunkSUM = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        content = decoded_line[6:]
                        if content == "[DONE]":
                            break
                        message = json.loads(content)
                        if "choices" in message and message["choices"]:
                            chunk = message["choices"][0]["delta"].get("content", "")
                            if chunk:
                                # Append the new chunk to the existing Markdown content
                                markdown_content += chunk
                                # Update the Markdown object with new content
                                md = Markdown(markdown_content)
                                live.update(md)  # Update the live display with new Markdown content
                                # Optionally, update the history with the new chunk
                                chunkSUM = chunkSUM + chunk
            history.append({"role": "assistant", "content": chunkSUM})
            live.stop()  # Stop the live display when done