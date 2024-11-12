import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
import subprocess
import threading
import atexit
from datetime import datetime
from pathlib import Path
import platform
import os
import importlib.util

def resource_path(relative_path):
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    except Exception:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


TOKEN_PATH = resource_path("./docs/token.txt")
MAIN_PATH = resource_path("./main.py")
COGS_DIR = resource_path("cogs")


class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state='disabled')

    def flush(self):
        pass

class BotLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Bot Launcher")
        self.root.geometry("800x600")
        
        self.bot_process = None
        self.bot_thread = None
        self.is_closing = False  # Added missing attribute
        
        self.setup_ui()
        self.load_token()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        # Token Frame
        token_frame = ttk.Frame(self.root)
        token_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(token_frame, text="Bot Token:").pack(side='left')
        self.token_entry = ttk.Entry(token_frame, show="*", width=50)
        self.token_entry.pack(side='left', padx=5)

        # Buttons Frame
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill='x', padx=5, pady=5)

        self.run_btn = ttk.Button(btn_frame, text="Run Bot", command=self.run_bot)
        self.run_btn.pack(side='left', padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop Bot", command=self.stop_bot, state='disabled')
        self.stop_btn.pack(side='left', padx=5)

        # Console Output
        console_frame = ttk.LabelFrame(self.root, text="Console Output")
        console_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, height=20)
        self.console.pack(fill='both', expand=True, padx=5, pady=5)
        self.console.configure(state='disabled')

    def load_token(self):
        try:
            # Create docs directory if it doesn't exist
            os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)  # Added missing directory creation
            
            if os.path.exists(TOKEN_PATH) and os.path.getsize(TOKEN_PATH) > 0:
                with open(TOKEN_PATH, 'r') as f:  # Using with statement for file handling
                    token = f.read().strip()
                self.token_entry.insert(0, token)
        except Exception as e:
            self.log_message(f"Error loading token: {str(e)}")

    def save_token(self):
        try:
            # Create docs directory if it doesn't exist
            os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)  # Added missing directory creation
            
            with open(TOKEN_PATH, 'w') as f:  # Using with statement for file handling
                f.write(self.token_entry.get())
            self.log_message("Token saved.")
        except Exception as e:
            self.log_message(f"Error saving token: {str(e)}")

    def run_bot(self):
        if not self.token_entry.get():
            self.log_message("Error: Please enter a bot token.")
            return

        self.save_token()
        
        if self.root.winfo_exists():  # Added check for window existence
            self.run_btn.configure(state='disabled')
            self.stop_btn.configure(state='normal')
        
        sys.stdout = ConsoleRedirector(self.console)
        
        def run():
            try:
                os.environ['DISCORD_TOKEN'] = self.token_entry.get()
                
                if getattr(sys, 'frozen', False):
                    self.log_message("Starting bot in executable mode...")
                    main_path = resource_path('main.py')
                    
                    spec = importlib.util.spec_from_file_location("main", main_path)
                    main_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(main_module)
                    
                    main_module.run()
                else:
                    self.log_message("Starting bot in development mode...")
                    python_cmd = 'python' if platform.system().lower() == 'windows' else 'python3'
                    main_path = resource_path('main.py')
                    
                    env = os.environ.copy()
                    env['DISCORD_TOKEN'] = self.token_entry.get()
                    
                    self.bot_process = subprocess.Popen(
                        [python_cmd, main_path],
                        env=env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True
                    )
                    
                    while self.bot_process and not self.is_closing:  # Added is_closing check
                        output = self.bot_process.stdout.readline()
                        if output:
                            self.log_message(output.strip())
                        if not output and self.bot_process.poll() is not None:
                            break

            except Exception as e:
                if not self.is_closing:  # Added is_closing check
                    self.log_message(f"Error: {str(e)}")
                    self.stop_bot()

        self.bot_thread = threading.Thread(target=run, daemon=True)
        self.bot_thread.start()

    def stop_bot(self):
        print("Stopping bot...")

        if self.bot_process:
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.bot_process.kill()
            finally:
                self.bot_process = None
                if not self.is_closing:  # Added is_closing check
                    self.log_message("Bot stopped.")
        
        if not self.is_closing:  # Added is_closing check
            sys.stdout = sys.__stdout__
            
            if self.root.winfo_exists():  # Added check for window existence
                self.run_btn.configure(state='normal')
                self.stop_btn.configure(state='disabled')

    def cleanup(self):
        if self.bot_process:
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=2)
            except (subprocess.TimeoutExpired, Exception):
                if self.bot_process:
                    self.bot_process.kill()
            finally:
                self.bot_process = None

    def on_closing(self):
        self.is_closing = True
        self.cleanup()
        sys.stdout = sys.__stdout__
        
        if self.root.winfo_exists():
            self.root.destroy()

    def log_message(self, message):
        """Thread-safe logging to the console widget"""
        if not self.is_closing and self.root.winfo_exists():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.console.configure(state='normal')
            self.console.insert(tk.END, f"[{timestamp}] {message}\n")
            self.console.see(tk.END)
            self.console.configure(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = BotLauncher(root)
    root.mainloop()