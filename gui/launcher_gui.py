"""Simple Tkinter GUI launcher."""

import tkinter as tk


def main():
    root = tk.Tk()
    root.title("CleanMedia")
    label = tk.Label(root, text="GUI placeholder")
    label.pack(padx=20, pady=20)
    root.mainloop()


if __name__ == '__main__':
    main()
