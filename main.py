import tkinter as tk
from gui import AppGUI
import sys
import logging

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    root = tk.Tk()
    root.geometry("800x800")

    try:
        app = AppGUI(root)
        root.mainloop()
    except Exception as e:
        logging.critical(f"Application crashed: {e}", exc_info=True)
        # In a real environment, we might show a message box here if possible
        print(f"Critical error: {e}")

if __name__ == "__main__":
    main()
