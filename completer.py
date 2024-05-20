import os
from prompt_toolkit.completion import Completer, Completion, WordCompleter

class GeneralCompleter(Completer):
    def __init__(self):
        self.commands = ['cd', 'ls', 'pwd', 'echo', 'cat', 'mkdir', 'rm', 'find', 'grep']
        self.word_completer = WordCompleter(self.commands, ignore_case=True)

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.strip()

        # Skip completions for inputs starting with '?' or '!'
        if text.startswith('?') or text.startswith('!'):
            return

        words = text.split()

        if len(words) == 0:
            return

        # The first word is the command
        command = words[0]

        if command in self.commands:
            if command == "cd":
                yield from self._complete_cd(words, document, complete_event)
            elif command in ["ls", "cat", "rm", "echo"]:
                yield from self._complete_files_and_directories(words, document, complete_event)
            elif command in ["mkdir", "rmdir"]:
                yield from self._complete_directories(words, document, complete_event)
        else:
            yield from self.word_completer.get_completions(document, complete_event)

    def _complete_cd(self, words, document, complete_event):
        partial_path = words[1] if len(words) > 1 else ""
        if not partial_path:
            partial_path = "."
        if not os.path.isabs(partial_path):
            partial_path = os.path.join(os.getcwd(), partial_path)
        dir_path = os.path.dirname(partial_path)
        base_name = os.path.basename(partial_path)
        try:
            for item in os.listdir(dir_path):
                if item.startswith(base_name) and os.path.isdir(os.path.join(dir_path, item)):
                    yield Completion(item, start_position=-len(base_name))
        except Exception:
            pass

    def _complete_files_and_directories(self, words, document, complete_event):
        partial_path = words[1] if len(words) > 1 else ""
        if not partial_path:
            partial_path = "."
        if not os.path.isabs(partial_path):
            partial_path = os.path.join(os.getcwd(), partial_path)
        dir_path = os.path.dirname(partial_path)
        base_name = os.path.basename(partial_path)
        try:
            for item in os.listdir(dir_path):
                if item.startswith(base_name):
                    yield Completion(item, start_position=-len(base_name))
        except Exception:
            pass

    def _complete_directories(self, words, document, complete_event):
        partial_path = words[1] if len(words) > 1 else ""
        if not partial_path:
            partial_path = "."
        if not os.path.isabs(partial_path):
            partial_path = os.path.join(os.getcwd(), partial_path)
        dir_path = os.path.dirname(partial_path)
        base_name = os.path.basename(partial_path)
        try:
            for item in os.listdir(dir_path):
                if item.startswith(base_name) and os.path.isdir(os.path.join(dir_path, item)):
                    yield Completion(item, start_position=-len(base_name))
        except Exception:
            pass