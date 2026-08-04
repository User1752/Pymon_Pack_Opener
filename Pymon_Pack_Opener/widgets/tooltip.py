import tkinter as tk


class ToolTip:
    """Tooltip simples que segue o rato perto de um widget."""

    def __init__(self, widget, text_func, delay=400):
        self.widget = widget
        self.text_func = text_func
        self.delay = delay
        self._after_id = None
        self.tipwindow = None

        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        widget.bind("<Motion>", self._on_motion)

    def _on_enter(self, event=None):
        self._schedule()

    def _on_leave(self, event=None):
        self._unschedule()
        self._hidetip()

    def _on_motion(self, event):
        if self.tipwindow:
            x = event.x_root + 20
            y = event.y_root + 10
            self.tipwindow.geometry(f"+{x}+{y}")

    def _schedule(self):
        self._unschedule()
        self._after_id = self.widget.after(self.delay, self._showtip)

    def _unschedule(self):
        if self._after_id is not None:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _showtip(self):
        if self.tipwindow or not self.widget.winfo_viewable():
            return
        text = self.text_func() if callable(self.text_func) else str(self.text_func)
        if not text:
            return
        
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.overrideredirect(True)
        tw.attributes("-topmost", True)
        
        label = tk.Label(
            tw, text=text, justify=tk.LEFT,
            bg="#222222", fg="#ffffff",
            relief=tk.SOLID, borderwidth=1,
            font=("Arial", 9)
        )
        label.pack(ipadx=4, ipady=2)
        
        try:
            x = self.widget.winfo_pointerx() + 20
            y = self.widget.winfo_pointery() + 10
            tw.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
