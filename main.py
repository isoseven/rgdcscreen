import tkinter as tk
import subprocess
import threading
import time
import keyboard
import pyautogui

class DisplaySwitchApp:
    def __init__(self, root):
        # create the main window: 240x100
        self.root = root
        self.root.title("RGDC")
        self.root.geometry("240x100+1150+880")
        self.root.resizable(False, False)
        # default delay time in minutes
        # find in time.txt
        try:
            with open("time.txt", "r") as tm:
                value = tm.read().strip()
                if value:
                    self.delay_minutes = int(value)
                else:
                    raise ValueError
        except FileNotFoundError:
            self.delay_minutes = 5
            with open("time.txt", "w+") as tm:
                tm.write(str(self.delay_minutes))
        # desired to/from display:
        # 1: PC screen
        # 2: Duplicate
        # 3: Extend
        # 4: Second screen only
        self.original_display = "3"
        self.target_display = "2"


        # # unused, ignore
        # create a thread for key listener outside of main thread
        # also create a variable is_running to check if the display switch sequence is running
        # self.is_running = False
        # threading.Thread(target=self.key_handler, daemon=True).start()

        # grid gui elements
        self.increase_btn = tk.Button(root, text="+", command=self.increase_time, width=5, height=1, bg="green", font=("Arial", 14), fg="white", activebackground="lightgreen")
        self.increase_btn.grid(row=0, column=0, padx=5, pady=5)

        # create a label to display the delay time
        minutes, seconds = divmod(self.delay_minutes * 60, 60)
        self.label = tk.Label(root, text=f"{minutes:02}:{seconds:02}", font=("Arial", 14))
        self.label.grid(row=0, column=1, padx=5, pady=5)

        self.decrease_btn = tk.Button(root, text="-", command=self.decrease_time, width=5, height=1, bg="red", font=("Arial", 14), fg="white", activebackground="lightcoral")
        self.decrease_btn.grid(row=1, column=0, padx=5, pady=5)

        self.start_btn = tk.Button(root, text="Start", command=self.start_sequence, width=5, height=1, font=("Arial", 14))
        self.start_btn.grid(row=1, column=1, padx=5, pady=5)

        # create two buttons to modulate f1 and f2 keys
        self.f1_btn = tk.Button(root, text="F1", command=self.press_f1, width=5, height=1, font=("Arial", 14))
        self.f1_btn.grid(row=0, column=2, padx=5, pady=5)

        self.f2_btn = tk.Button(root, text="F2", command=self.press_f2, width=5, height=1, font=("Arial", 14))
        self.f2_btn.grid(row=1, column=2, padx=5, pady=5)

    def press_f1(self):
        # minimize window, send F1, then restore window
        try:
            self.root.iconify()
            time.sleep(0.1)  # allow time for window to minimize
            # click on top of tab to focus
            pyautogui.click(x=960, y=12)
            keyboard.press_and_release("f1")
            time.sleep(0.1)  # allow time for key event to register
            # move mouse back to original position
            pyautogui.moveTo(1340, 930)
            self.root.deiconify()
        except Exception as e:
            print("Error pressing F1:", e)
    
    def press_f2(self):
        # minimize window, send F2, then restore window
        try:
            self.root.iconify()
            time.sleep(0.1)
            # click on top of tab to focus
            pyautogui.click(x=960, y=12)
            keyboard.press_and_release("f2")
            time.sleep(0.1)
            # move mouse back to original position
            pyautogui.moveTo(1340, 980)
            self.root.deiconify()
        except Exception as e:
            print("Error pressing F2:", e)
    
    # disable the increase and decrease buttons
    def increase_time(self):
        self.delay_minutes += 1
        self.update_label()

    # decrease the delay time by 1 minute
    def decrease_time(self):
        if self.delay_minutes > 1:
            self.delay_minutes -= 1
        self.update_label()

    # update the label with the current delay time
    def update_label(self):
        # M:SS format
        # write the delay time to time.txt
        with open("time.txt", "w+") as tm:
            tm.write(str(self.delay_minutes))
        minutes, seconds = divmod(self.delay_minutes * 60, 60)
        self.label.config(text=f"{minutes:02}:{seconds:02}")

    # start the display switch sequence
    def start_sequence(self):
        threading.Thread(target=self.run_display_switch_sequence).start()
        # self.is_running = True

    def stop_sequence(self):
        # change start button to "Start"
        self.start_btn.config(text="Start", command=self.start_sequence)
        # enable the increase and decrease buttons
        self.increase_btn.config(state=tk.NORMAL)
        self.decrease_btn.config(state=tk.NORMAL)
        # reset the label to the initial state
        minutes, seconds = divmod(self.delay_minutes * 60, 60)
        self.label.config(text=f"{minutes:02}:{seconds:02}")
        # go back to original display
        subprocess.run(["DisplaySwitch.exe", self.original_display])
        # self.is_running = False

    def run_display_switch_sequence(self):
        # change start button to "Stop"
        self.start_btn.config(text="Stop", command=self.stop_sequence)
        # disable the increase and decrease buttons
        self.increase_btn.config(state=tk.DISABLED)
        self.decrease_btn.config(state=tk.DISABLED)
        # # minimize the window
        # self.root.iconify()
        # switch to the target display
        subprocess.run(["DisplaySwitch.exe", self.target_display])
        # count down on the tkinter label in seconds
        for i in range(self.delay_minutes * 60, 0, -1):
            # stop the display switch sequence if the stop button is pressed
            if not self.start_btn['text'] == "Stop":
                break
            # update the label every second
            time.sleep(1)
            # M:SS format
            minutes, seconds = divmod(i, 60)
            self.label.config(text=f"{minutes:02}:{seconds:02}")
            self.root.update_idletasks()
        # switch to the next display
        # reset the label to the initial state
        minutes, seconds = divmod(self.delay_minutes * 60, 60)
        self.label.config(text=f"{minutes:02}:{seconds:02}")
        subprocess.run(["DisplaySwitch.exe", self.original_display])
        self.start_btn.config(text="Start", command=self.start_sequence)
        # enable the increase and decrease buttons
        self.increase_btn.config(state=tk.NORMAL)
        self.decrease_btn.config(state=tk.NORMAL)
        # # restore the window
        # self.root.deiconify()

    # # unused, ignore
    # def key_handler(self):
    #     # listen for f1 (start) and f2 (stop) keys
    #     while True:
    #         key = keyboard.read_key()
    #         if key == "f7":
    #             if not self.is_running:
    #                 self.start_sequence()
    #         elif key == "f8":
    #             if self.is_running:
    #                 self.stop_sequence()
   
if __name__ == "__main__":
    root = tk.Tk()
    app = DisplaySwitchApp(root)
    root.mainloop()
