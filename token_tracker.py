#!/usr/bin/env python3
"""
OpenClaw Token Tracker
Real-time token usage monitoring with a pretty GUI
"""

import tkinter as tk
from tkinter import ttk
import requests
import json
import time
from datetime import datetime
import threading

class TokenTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("🦅 OpenClaw Token Tracker")
        self.root.geometry("500x350")
        self.root.configure(bg='#1a1a2e')
        
        # Gateway config
        self.gateway_url = "http://127.0.0.1:18789"
        self.gateway_token = "cb921f4a37f8b44520a24c792ce011d27c1cc554032e9c2e"
        
        # Create UI
        self.create_widgets()
        
        # Start monitoring
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_tokens, daemon=True)
        self.monitor_thread.start()
        
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
            text="Connecting...",
            font=("Arial", 9),
            bg='#1a1a2e',
            fg='#808080'
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
        
        # Configure progress bar style
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
        
    def get_token_usage(self):
        """Fetch token usage from OpenClaw gateway"""
        try:
            headers = {
                'Authorization': f'Bearer {self.gateway_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'{self.gateway_url}/v1/rpc',
                headers=headers,
                json={
                    'jsonrpc': '2.0',
                    'method': 'session.status',
                    'params': {
                        'sessionKey': 'agent:main:main'
                    },
                    'id': 1
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    result = data['result']
                    # Parse the session status response
                    if 'turns' in result:
                        total_tokens = 0
                        for turn in result.get('turns', []):
                            if 'usage' in turn:
                                total_tokens += turn['usage'].get('inputTokens', 0)
                                total_tokens += turn['usage'].get('outputTokens', 0)
                        
                        return {
                            'current': total_tokens,
                            'total': 200000,
                            'remaining': 200000 - total_tokens
                        }
            return None
            
        except Exception as e:
            print(f"Error fetching tokens: {e}")
            return None
    
    def monitor_tokens(self):
        """Background thread to monitor token usage"""
        while self.running:
            usage = self.get_token_usage()
            
            if usage:
                current = usage['current']
                total = usage['total']
                remaining = usage['remaining']
                percent = (current / total) * 100
                
                # Update UI (must be done in main thread)
                self.root.after(0, self.update_ui, current, total, remaining, percent)
            else:
                self.root.after(0, self.update_status, "Connection error")
            
            time.sleep(2)  # Update every 2 seconds
    
    def update_ui(self, current, total, remaining, percent):
        """Update the UI with new token data"""
        # Format numbers with commas
        current_str = f"{current:,}"
        remaining_str = f"{remaining:,}"
        
        # Update labels
        self.current_label.config(text=f"Current: {current_str} tokens")
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
        
        # Update status
        now = datetime.now().strftime("%H:%M:%S")
        self.status_label.config(text=f"✓ Connected", fg='#00ff88')
        self.update_label.config(text=f"Last update: {now}")
    
    def update_status(self, message):
        """Update status message"""
        self.status_label.config(text=message, fg='#ff4444')
    
    def on_closing(self):
        """Clean shutdown"""
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TokenTracker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
