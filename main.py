import tkinter as tk
from tkinter import messagebox, StringVar
import yt_dlp
import customtkinter as ctk
from threading import Thread

class YouTubeInfoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("YouTube Video Information - Preview")
        self.geometry("600x525")
        self.resizable(False, False)

        self.create_widgets()
        self.yt = None
        self.downloaded_mb = 0
        self.max_speed = 0

    def create_widgets(self):
        self.label = ctk.CTkLabel(self, text="Enter YouTube Link:")
        self.label.pack(pady=10)

        self.entry = ctk.CTkEntry(self, width=400)
        self.entry.pack(pady=10)

        self.get_info_button = ctk.CTkButton(self, text="Get Information", command=self.get_info)
        self.get_info_button.pack(pady=10)

        self.download_button = ctk.CTkButton(self, text="Download Video", command=self.show_download_options)
        self.download_button.pack(pady=10)
        self.download_button.pack_forget()

        self.info_text = ctk.CTkTextbox(self, width=500, height=300)
        self.info_text.pack(pady=10)

        self.footer = ctk.CTkLabel(self, text="© 2024 by Nizhenets.com Instagram.com/Nizhenets")
        self.footer.pack(side="bottom", pady=5)

    def get_info(self):
        link = self.entry.get()
        if link:
            try:
                self.yt = yt_dlp.YoutubeDL().extract_info(link, download=False)
                self.display_info()
                self.download_button.pack()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while retrieving information: {e}")
        else:
            messagebox.showwarning("Warning", "Please enter a YouTube link.")

    def display_info(self):
        if self.yt:
            info = (
                f"Title: {self.yt.get('title', 'No information')}\n"
                f"View Count: {self.yt.get('view_count', 'No information')}\n"
                f"Duration: {self.yt.get('duration', 'No information')} seconds\n"
                f"Like Count: {self.yt.get('like_count', 'No information')}\n"
                f"Average Rating: {self.yt.get('average_rating', 'No information')}\n"
                f"Upload Date: {self.yt.get('upload_date', 'No information')}\n"
                f"Author: {self.yt.get('uploader', 'No information')}\n"
                f"Channel URL: {self.yt.get('uploader_url', 'No information')}\n"
                f"Video ID: {self.yt.get('id', 'No information')}\n"
                f"Thumbnail URL: {self.yt.get('thumbnail', 'No information')}\n\n"
                f"Description: {self.yt.get('description', 'No information')}"
            )
            self.info_text.delete("1.0", tk.END)
            self.info_text.insert(tk.END, info)

    def show_download_options(self):
        if not self.yt:
            messagebox.showerror("Error", "You need to get the video information first.")
            return

        self.clear_widgets()
        
        ctk.CTkLabel(self, text="Select Quality:").pack(pady=10)
        self.quality_var = StringVar()
        self.quality_var.set("Select")
        qualities = [f"{f['format_id']} - {f.get('resolution', 'N/A')} - {f.get('fps', 'N/A')}fps" for f in self.yt['formats']]
        self.quality_menu = ctk.CTkOptionMenu(self, variable=self.quality_var, values=qualities)
        self.quality_menu.pack(pady=10)

        ctk.CTkLabel(self, text="Select Format:").pack(pady=10)
        self.format_var = StringVar()
        self.format_var.set("mp4")
        formats = ["mp4", "webm"]
        self.format_menu = ctk.CTkOptionMenu(self, variable=self.format_var, values=formats)
        self.format_menu.pack(pady=10)

        self.progress = ctk.CTkProgressBar(self, mode='determinate')
        self.progress.pack(pady=20, padx=20, fill='x')

        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack(pady=10)

        ctk.CTkButton(self, text="Download", command=self.start_download_thread).pack(pady=20)
        ctk.CTkButton(self, text="Go Back", command=self.back_to_main_view).pack(pady=10)

    def back_to_main_view(self):
        self.clear_widgets()
        self.create_widgets()
        if self.yt:
            self.display_info()
            self.download_button.pack()

    def clear_widgets(self):
        for widget in self.winfo_children():
            widget.pack_forget()

    def start_download_thread(self):
        download_thread = Thread(target=self.download_video)
        download_thread.start()

    def download_video(self):
        selected_quality = self.quality_var.get().split(" - ")[0]
        file_format = self.format_var.get()
        if selected_quality and file_format:
            ydl_opts = {
                'format': selected_quality,
                'progress_hooks': [self.progress_hook],
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.yt['webpage_url']])
                messagebox.showinfo("Success", "Video downloaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Video could not be downloaded: {e}")
        else:
            messagebox.showerror("Error", "Selected quality or format not found.")
        self.back_to_main_view()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes', 0) or 1  # assume 1 if total bytes not available
            downloaded = d.get('downloaded_bytes', 0) or 0
            speed = d.get('speed', 0) or 0
            if speed > self.max_speed:
                self.max_speed = speed
            progress_percent = (downloaded / total) * 100
            self.progress.set(progress_percent / 100)
            self.status_label.configure(text=f"Downloaded: {downloaded / (1024 * 1024):.2f} MB / {total / (1024 * 1024): .2f} MB\n"
                                             f"Download Speed: {speed / (1024 * 1024):.2f} MB/s\n"
                                             f"Maximum Speed: {self.max_speed / (1024 * 1024):.2f} MB/s\n"
                                             f"Progress: %{progress_percent:.2f}")

if __name__ == "__main__":
    app = YouTubeInfoApp()
    app.mainloop()
