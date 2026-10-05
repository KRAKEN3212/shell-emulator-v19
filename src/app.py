"""Графический интерфейс эмулятора на Tkinter."""

import tkinter as tk
from tkinter import scrolledtext

from src.script import ScriptError, read_script

FONT = ("Consolas", 11)
BACKGROUND = "#1e1e1e"
FOREGROUND = "#d4d4d4"
PROMPT_COLOR = "#6a9955"
ERROR_COLOR = "#f44747"
DEBUG_COLOR = "#808080"
WINDOW_SIZE = "860x520"


class EmulatorApp:
    """Окно эмулятора: область вывода и строка ввода."""

    def __init__(self, shell):
        """Создаёт окно для сеанса shell."""
        self.shell = shell
        self.history = []
        self.history_pos = 0
        self.root = tk.Tk()
        self.root.title(shell.title())
        self.root.geometry(WINDOW_SIZE)
        self._build_output()
        self._build_input()

    def _build_output(self):
        """Создаёт область вывода только для чтения."""
        self.output = scrolledtext.ScrolledText(
            self.root, font=FONT, bg=BACKGROUND, fg=FOREGROUND,
            state=tk.DISABLED, wrap=tk.WORD)
        self.output.tag_config("prompt", foreground=PROMPT_COLOR)
        self.output.tag_config("error", foreground=ERROR_COLOR)
        self.output.tag_config("debug", foreground=DEBUG_COLOR)
        self.output.pack(fill=tk.BOTH, expand=True)

    def _build_input(self):
        """Создаёт строку ввода с приглашением."""
        frame = tk.Frame(self.root, bg=BACKGROUND)
        frame.pack(fill=tk.X)
        self.prompt_label = tk.Label(
            frame, text=self.shell.prompt(), font=FONT,
            bg=BACKGROUND, fg=PROMPT_COLOR)
        self.prompt_label.pack(side=tk.LEFT)
        self.entry = tk.Entry(
            frame, font=FONT, bg=BACKGROUND, fg=FOREGROUND,
            insertbackground=FOREGROUND, relief=tk.FLAT)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Up>", lambda _event: self._browse_history(-1))
        self.entry.bind("<Down>", lambda _event: self._browse_history(1))
        self.entry.focus_set()

    def write(self, text, tag=None):
        """Добавляет текст в область вывода."""
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text, tag)
        self.output.configure(state=tk.DISABLED)
        self.output.see(tk.END)

    def write_lines(self, lines, tag=None):
        """Выводит несколько строк с одним тегом оформления."""
        for line in lines:
            self.write(line + "\n", tag)

    def schedule_script(self, path):
        """Запускает стартовый скрипт после открытия окна."""
        self.root.after(0, lambda: self.run_script(path))

    def run_script(self, path):
        """Выполняет команды скрипта, показывая ввод и вывод.

        Ошибка в команде не прерывает скрипт, чтобы в одном скрипте
        можно было продемонстрировать несколько ошибочных ситуаций.
        Команда exit завершает скрипт и эмулятор.
        """
        try:
            lines = read_script(path)
        except ScriptError as error:
            self.write(f"emulator: {error}\n", "error")
            return
        for line in lines:
            self.run_line(line)
            if not self.shell.running:
                return

    def run_line(self, line):
        """Показывает введённую строку, выполняет её и выводит результат."""
        self.write(self.shell.prompt(), "prompt")
        self.write(line + "\n")
        result = self.shell.execute(line)
        if result:
            tag = "error" if self.shell.last_failed else None
            self.write(result + "\n", tag)
        self.prompt_label.configure(text=self.shell.prompt())
        if not self.shell.running:
            self.root.after_idle(self.root.destroy)

    def _on_enter(self, _event):
        """Обработчик нажатия Enter в строке ввода."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        if line.strip():
            self.history.append(line)
        self.history_pos = len(self.history)
        self.run_line(line)
        return "break"

    def _browse_history(self, step):
        """Листает историю команд стрелками вверх/вниз."""
        if not self.history:
            return "break"
        last = len(self.history)
        self.history_pos = max(0, min(last, self.history_pos + step))
        text = self.history[self.history_pos] \
            if self.history_pos < last else ""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        return "break"

    def run(self):
        """Запускает главный цикл окна."""
        self.root.mainloop()
        return self.shell.exit_code
