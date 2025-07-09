import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per-monitor DPI aware
except Exception:
    pass

import winsound
import customtkinter as ctk
import threading
import time
import pygame
from datetime import datetime, timedelta

class ModernTimerApp:
    def __init__(self):
        # Initialize pygame for audio
        pygame.mixer.init()
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Timer")
        # self.root.overrideredirect(True)
        self.root.resizable(True, True)
        # Enable window dragging
        self.offset_x = 0
        self.offset_y = 0
        self.root.bind("<Button-1>", self.click_window)
        self.root.bind("<Button-3>", self.right_click_window)
        self.root.bind("<B1-Motion>", self.drag_window)
        self.root.bind("<Return>", self.enter_pressed)
        
        # Timer state
        self.minutes = 5
        self.seconds = 0
        self.is_running = False
        self.is_expired = False
        self.alarm_enabled = True
        self.timer_thread = None
        self.stop_timer_flag = False
        
        # Create UI
        self.create_widgets()
        self.update_display()
        
    def create_widgets(self):
        # Main container
        self.main_frame = ctk.CTkFrame(
            self.root, 
            fg_color="#273a50")
        self.main_frame.pack(fill="both", expand=True,)
        
        
        # Time display
        self.time_frame = ctk.CTkFrame(
            self.main_frame,
            width = 120,
            height = 80,
            fg_color="transparent",)
        self.time_frame.pack(side="left", padx=10, fill="x")
        self.time_frame.pack_propagate(False) 
        
        
        # Time input/display
        self.time_input_frame = ctk.CTkFrame(self.time_frame, fg_color="transparent")
        self.time_input_frame.pack( fill=None, expand=True)
        
        
        # Minutes input
        self.minutes_entry = ctk.CTkEntry(
            self.time_input_frame,
            width=40,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            justify="center"
        )
        self.minutes_entry.pack( side="left", padx=1)
        self.minutes_entry.insert(0, "5")
        

        # Colon separator
        self.colon_label = ctk.CTkLabel(
            self.time_input_frame,
            text=":",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.colon_label.pack(side="left", padx=1)
        
        # Seconds input
        self.seconds_entry = ctk.CTkEntry(
            self.time_input_frame,
            width=40,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            justify="center"
        )
        self.seconds_entry.pack(side="left", padx=1)
        self.seconds_entry.insert(0, "00")
        

        # Time display (when running)
        self.time_display = ctk.CTkLabel(
            self.time_frame,
            text="05:00",
            text_color="black",
            font=ctk.CTkFont(family="Courier New", size=36, weight="bold", )
        )
        
        # Control buttons frame
        self.controls_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.controls_frame.pack(side="left", pady=10)
        
        # Start/Pause button
        self.start_pause_btn = ctk.CTkButton(
            self.controls_frame,
            text="▶",
            width=25,
            height=25,
            fg_color="transparent",
            font=ctk.CTkFont(size=10, weight="bold"),
            command=self.toggle_timer
        )
        self.start_pause_btn.pack(side="left", padx=1)
        
        # Reset button
        self.reset_btn = ctk.CTkButton(
            self.controls_frame,
            text="⟲",
            width=25,
            height=25,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="transparent",
            hover_color="darkgray",
            command=self.reset_timer
        )
        self.reset_btn.pack(side="left", padx=1)
        
        # Alarm toggle
        self.alarm_btn = ctk.CTkButton(
            self.controls_frame,
            text="🔊",
            width=25,
            height=25,
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            hover_color="darkgreen",
            command=self.toggle_alarm
        )
        self.alarm_btn.pack(side="left", padx=1)
        
        # # Status label
        # self.status_label = ctk.CTkLabel(
        #     self.main_frame,
        #     text="Ready to start",
        #     font=ctk.CTkFont(size=14)
        # )
        # self.status_label.pack(pady=10)
        
    def update_display(self):
        """Update the timer display"""
        if self.is_running:
            # Show time display, hide inputs
            self.time_input_frame.pack_forget()
            self.time_display.pack(side="left",pady=15, fill=None, expand=True,)
            
            # Update display colors based on state
            if self.is_expired:
                self.time_display.configure(text_color="red")
                #self.time_frame.configure(fg_color="red")
                self.time.configure(text="⏰ Time's Up!", text_color="red")
            else:
                self.time_display.configure(text_color="white")
                #self.time_frame.configure(fg_color=("gray10", "gray90"))
                # self.status_label.configure(text="Timer running...", text_color="green")
        elif self.is_expired:
            # Update display colors based on state
            self.main_frame.configure(fg_color="red")
            self.time_frame.configure(fg_color="red")

        
        else:
            # Show inputs, hide time display
            self.time_display.pack_forget()
            self.time_input_frame.pack(pady=15)
            self.time_frame.configure(fg_color="transparent")
            
            # if self.is_expired:
            #     self.status_label.configure(text="Timer completed!", text_color="blue")
            # else:
            #     self.status_label.configure(text="Ready to start", text_color="gray")
        
        # Update time display
        time_str = f"{self.minutes:02d}:{self.seconds:02d}"
        self.time_display.configure(text=time_str,)
        
        # Update button states
        if self.is_running:
            self.start_pause_btn.configure(text="⏸")
        else:
            self.start_pause_btn.configure(text="▶")
            
        # Update alarm button
        if self.alarm_enabled:
            self.alarm_btn.configure(text="🔊", fg_color="green")

        else:
            self.alarm_btn.configure(text="🔇", fg_color="gray")
    
    def toggle_timer(self):
        """Start or pause the timer"""
        if not self.is_running:
            if self.is_expired:
                self.reset_timer()

            else:    
                # Get time from inputs if not running
                try:
                    self.minutes = int(self.minutes_entry.get() or 0)
                    self.seconds = int(self.seconds_entry.get() or 0)
                except ValueError:
                    self.minutes = 5
                    self.seconds = 0

                if self.minutes == 0 and self.seconds == 0:
                    return

                self.is_running = True
                self.is_expired = False
                self.stop_timer_flag = False

                # Start timer thread
                self.timer_thread = threading.Thread(target=self.run_timer)
                self.timer_thread.daemon = True
                self.timer_thread.start()

        else:
            # Pause timer
            self.is_running = False
            self.stop_timer_flag = True
        
        self.update_display()
    
    def run_timer(self):
        """Timer countdown logic"""
        while self.is_running and not self.stop_timer_flag:
            if self.seconds > 0:
                self.seconds -= 1
            elif self.minutes > 0:
                self.minutes -= 1
                self.seconds = 59
            else:
                # Timer expired
                self.is_expired = True
                self.is_running = False
                
                # Play alarm
                if self.alarm_enabled:
                    self.play_alarm()
                
                # Update UI in main thread
                self.root.after(0, self.update_display)
                break
            
            # Update display in main thread
            self.root.after(0, self.update_display)
            time.sleep(1)
    
    def reset_timer(self):
        """Reset the timer"""
        self.is_running = False
        self.is_expired = False
        self.stop_timer_flag = True

        self.main_frame.configure(fg_color="#273a50")
        self.time_frame.configure(fg_color="transparent")
        
        # Reset to input values or defaults
        try:
            self.minutes = int(self.minutes_entry.get() or 5)
            self.seconds = int(self.seconds_entry.get() or 0)
        except ValueError:
            self.minutes = 5
            self.seconds = 0
            self.minutes_entry.delete(0, 'end')
            self.minutes_entry.insert(0, "5")
            self.seconds_entry.delete(0, 'end')
            self.seconds_entry.insert(0, "00")
        
        self.update_display()
    
    def toggle_alarm(self):
        """Toggle alarm on/off"""
        self.alarm_enabled = not self.alarm_enabled
        self.update_display()
    
    def play_alarm(self):
        """Play alarm sound"""
        try:
            self.update_display()
            # Create a simple beep sound
            duration = 500  # ms
            frequency = 800  # Hz

            for _ in range(3):
                winsound.Beep(800, 500)  # frequency, duration(ms)

        except Exception as e:
            print(f"Could not play alarm: {e}")
    
    def right_click_window(self, event):
            # Create a simple popup menu with a "Close" option
        menu = ctk.CTkToplevel(self.root)
        menu.overrideredirect(True)
        menu.geometry(f"120x40+{event.x_root}+{event.y_root}")

        def close_app():
            self.root.destroy()

        close_btn = ctk.CTkButton(menu, text="Close", command=close_app, width=100, height=30)
        close_btn.pack(padx=10, pady=5)

        # Close popup if focus is lost or user clicks elsewhere
        menu.after(3000, menu.destroy)  # auto-close after 3 seconds
        menu.focus_force()
        menu.bind("<FocusOut>", lambda e: menu.destroy())
    
    def click_window(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def drag_window(self, event):
        x = self.root.winfo_pointerx() - self.offset_x
        y = self.root.winfo_pointery() - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def enter_pressed(self, event):
        self.toggle_timer()

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernTimerApp()
    app.run()
