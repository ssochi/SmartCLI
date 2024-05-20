import os
import json
import time
from tempfile import NamedTemporaryFile
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer
from prompt_toolkit.shortcuts import CompleteStyle
from config import get_config
from command_executor import execute_command
from ai_handler import AIHandler
from completer import GeneralCompleter
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.spinner import Spinner

def main():
    config = get_config()
    ai_handler = AIHandler(config["api_key"], config["api_base"])
    
    completer = GeneralCompleter()
    session = PromptSession(completer=completer, complete_style=CompleteStyle.MULTI_COLUMN)

    history = []
    # 定义初始 prompt
    prompt = "You are a macOS console assistant. Users typically ask you questions related to macOS. If a user simply wants a command, then you should provide the command directly. If a user is asking about something more detailed, you can provide a comprehensive answer:"

    welcome = """
    ╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
    ┃                                                                              ┃
    ┃                            🚀 Super Shell v1.0 🚀                            ┃
    ┃                                                                              ┃
    ┃  A powerful macOS console assistant powered by AI.                           ┃
    ┃                                                                              ┃
    ┃  Commands:                                                                   ┃
    ┃    [command]              Execute shell command                              ┃
    ┃    ? [question]           Ask macOS-related questions (streaming response)   ┃
    ┃    ! [request]            Request to generate and execute Bash/Python script ┃
    ┃                                                                              ┃
    ┃  Utilities:                                                                  ┃
    ┃    debug                  Print conversation history                         ┃
    ┃    cls                    Clear conversation history                         ┃
    ┃                                                                              ┃
    ┃  Exit:                                                                       ┃
    ┃    Ctrl+C, Ctrl+D         Exit the program                                   ┃
    ┃                                                                              ┃
    ╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
    """
    ai_handler.console.print(Markdown(welcome))
    # 初始 history 包含系统消息
    history = [{"role": "system", "content": prompt}]
    while True:
        try:
            user_input = session.prompt('> ', complete_in_thread=True)
            if user_input == "debug":
                ai_handler.console.print(json.dumps(history, indent=4))
                continue
            if user_input == "cls":
                history = [{"role": "system", "content": prompt}]
                continue
            if user_input.startswith("?"):
                query = user_input[1:].strip()
                ai_handler.handle_ai_request(query, history)
            elif user_input.startswith("!"):
                command = user_input[1:].strip()
                
                with Live(Spinner('dots', text=Text('Thinking... ', style='cyan')), refresh_per_second=10, console=ai_handler.console) as live:
                    start_time = time.time()
                    ai_response = ai_handler.handle_temporary_file_request(command, history)
                    end_time = time.time()
                    live.stop()
                
                if ai_response:
                    response_data = json.loads(ai_response)
                    action = response_data.get("action")
                    desc = response_data.get("desc")
                    filename = response_data.get("filename")
                    content = response_data.get("content")

                    elapsed_time = end_time - start_time
                    action_type = action.capitalize() if action in ["bash", "python"] else "File " + action
                    file_info = f"File: {filename}" if filename else ""

                    ai_handler.console.print(Panel(
                        Markdown(f"AI 将执行以下操作:\n\n操作类型: {action_type}\n{file_info}\n描述: {desc}\n耗时: {elapsed_time:.2f}s"),
                        expand=False,
                        style="bold green"
                    ))
                    
                    if action == "bash":
                        with NamedTemporaryFile(delete=False, mode='w', suffix='.sh') as temp_file:
                            temp_file.write(content)
                            temp_file_name = temp_file.name
                        os.chmod(temp_file_name, 0o755)
                        output = execute_command(f'bash {temp_file_name}')
                        os.remove(temp_file_name)
                    elif action == "python":
                        output = execute_command(f'python -c "{content}"')
                    elif action in ["rewrite", "write"]:
                        with open(filename, "w" if action == "write" else "w+") as file:
                            file.write(content)
                        output = f"File {'created' if action == 'write' else 'updated'}: {filename}"
                    else:
                        output = f"Unknown action: {action}"

                    history.append({"role": "user", "content": user_input})
                    history.append({"role": "assistant", "content": output})
                    ai_handler.console.print(output)
            else:
                output = execute_command(user_input)
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": output})
                ai_handler.console.print(output)
        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    main()