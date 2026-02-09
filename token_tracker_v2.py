#!/usr/bin/env python3
"""
OpenClaw Token Tracker V2
Simpler version - reads from a token count file
"""

import tkinter as tk
from tkinter import ttk
import json
import time
from datetime import datetime
import os

class TokenTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("🦅 OpenClaw Token Tracker")
        self.root.geometry("500x350")
        self.root.configure(bg='#1a1a2e')
        
        self.token_file = os.path.join(os.path.dirname(__file__), 'token_count.json')
        self.total_tokens = 200000
        
        # Create UI
        self.create_widgets()
        
        # Start monitoring
        self.running = True
        self.update_display()
        
    def create_widgets(self):
        # Title
        title = tk.Label(
            self.root,
            text="🦅 crypticClaw Token Usage",
            font=("Arial", 20, "bold"),
            bg='#1a1a2e',
            fg='#00d4ff'
        )
        title.pack(pady=20)
        
        # Token usage frame
        self.usage_frame = tk.Frame(self.root, bg='#1a1a2e')
        self.usage_frame.pack(pady=10, padx=20, fill='x')
        
        # Current tokens
        self.current_label = tk.Label(
            self.usage_frame,
            text="Current: --",
            font=("Arial", 14),
            bg='#1a1a2e',
            fg='#ffffff'
        )
        self.current_label.pack()
        
        # USD cost (money green)
        self.cost_label = tk.Label(
            self.usage_frame,
            text="Cost: $0.00",
            font=("Arial", 16, "bold"),
            bg='#1a1a2e',
            fg='#00ff00'
        )
        self.cost_label.pack(pady=5)
        
        # Progress bar style
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor='#0f0f1e',
            bordercolor='#1a1a2e',
            background='#00d4ff',
            lightcolor='#00d4ff',
            darkcolor='#00d4ff'
        )
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.root,
            length=400,
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=20)
        
        # Stats frame
        stats_frame = tk.Frame(self.root, bg='#1a1a2e')
        stats_frame.pack(pady=10)
        
        self.total_label = tk.Label(
            stats_frame,
            text="Total: 200,000",
            font=("Arial", 11),
            bg='#1a1a2e',
            fg='#a0a0a0'
        )
        self.total_label.grid(row=0, column=0, padx=20)
        
        self.remaining_label = tk.Label(
            stats_frame,
            text="Remaining: --",
            font=("Arial", 11),
            bg='#1a1a2e',
            fg='#a0a0a0'
        )
        self.remaining_label.grid(row=0, column=1, padx=20)
        
        self.percent_label = tk.Label(
            stats_frame,
            text="0.0%",
            font=("Arial", 16, "bold"),
            bg='#1a1a2e',
            fg='#00ff88'
        )
        self.percent_label.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="✓ Connected",
            font=("Arial", 9),
            bg='#1a1a2e',
            fg='#00ff88'
        )
        self.status_label.pack(pady=10)
        
        # Last update
        self.update_label = tk.Label(
            self.root,
            text="Last update: --",
            font=("Arial", 8),
            bg='#1a1a2e',
            fg='#606060'
        )
        self.update_label.pack()
        
    def read_token_count(self):
        """Read token count from file"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    return data.get('tokens', 0)
            return 0
        except Exception as e:
            print(f"Error reading token file: {e}")
            return 0
    
    def update_display(self):
        """Update the display with current token count"""
        if not self.running:
            return
            
        current = self.read_token_count()
        remaining = self.total_tokens - current
        percent = (current / self.total_tokens) * 100
        
        # Calculate cost (Claude Sonnet 4.5: ~$3/1M input, ~$15/1M output)
        # Using average estimate of $0.01 per 1000 tokens
        cost_usd = (current / 1000) * 0.01
        
        # Format numbers
        current_str = f"{current:,}"
        remaining_str = f"{remaining:,}"
        
        # Update labels
        self.current_label.config(text=f"Current: {current_str} tokens")
        self.cost_label.config(text=f"Cost: ${cost_usd:.2f}")
        self.remaining_label.config(text=f"Remaining: {remaining_str}")
        self.percent_label.config(text=f"{percent:.1f}%")
        
        # Update progress bar
        self.progress['value'] = percent
        
        # Change color based on usage
        if percent < 50:
            color = '#00ff88'  # Green
        elif percent < 80:
            color = '#ffd700'  # Yellow
        else:
            color = '#ff4444'  # Red
        
        self.percent_label.config(fg=color)
        
        # Update timestamp
        now = datetime.now().strftime("%H:%M:%S")
        self.update_label.config(text=f"Last update: {now}")
        
        # Schedule next update
        self.root.after(1000, self.update_display)  # Update every second
    
    def on_closing(self):
        """Clean shutdown"""
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TokenTracker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
