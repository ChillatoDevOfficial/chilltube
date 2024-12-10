import tkinter as tk
from ttkbootstrap import Style, ttk
import customtkinter as ctk
from PIL import Image, ImageTk
import yt_dlp
import os
from threading import Thread
import sv_ttk

class YoutubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("ChillTube")
        self.root.geometry("1000x700")
        
        sv_ttk.set_theme("dark")
        self.style = Style(theme='darkly')
        
        self.root.configure(bg='#1a1a1a')

        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
 
        title_frame = ttk.Frame(self.main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky='ew')
        ttk.Label(
            title_frame,
            text="ChillTube",
            font=('Helvetica', 24, 'bold'),
            foreground='#ff0000'
        ).pack(pady=10)
        
        url_card = ttk.LabelFrame(self.main_frame, text="URL Video", padding="10")
        url_card.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(0, 20))
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(
            url_card,
            textvariable=self.url_var,
            font=('Helvetica', 12),
            style='primary.TEntry'
        )
        url_entry.pack(fill='x', pady=5)

        options_frame = ttk.LabelFrame(self.main_frame, text="Opzioni Download", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky='ew', pady=(0, 20))
        
        options_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(options_frame, text="📂 Destinazione:").grid(row=0, column=0, padx=5, pady=10, sticky='w')
        self.output_path_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        ttk.Entry(
            options_frame,
            textvariable=self.output_path_var,
            style='primary.TEntry'
        ).grid(row=0, column=1, padx=5, sticky='ew')
        ttk.Button(
            options_frame,
            text="Sfoglia",
            style='primary.TButton',
            command=self.browse_output
        ).grid(row=0, column=2, padx=5)
 
        ttk.Label(options_frame, text="🎵 Formato:").grid(row=1, column=0, padx=5, pady=10, sticky='w')
        self.format_var = tk.StringVar(value="mp4")
        format_combo = ttk.Combobox(
            options_frame,
            textvariable=self.format_var,
            values=('mp4', 'mp3', 'wav', 'webm'),
            style='primary.TCombobox'
        )
        format_combo.grid(row=1, column=1, padx=5, sticky='ew')

        ttk.Label(options_frame, text="⚙️ Qualità:").grid(row=2, column=0, padx=5, pady=10, sticky='w')
        self.quality_var = tk.StringVar(value="highest")
        quality_combo = ttk.Combobox(
            options_frame,
            textvariable=self.quality_var,
            values=('highest', '1080p', '720p', '480p', '360p'),
            style='primary.TCombobox'
        )
        quality_combo.grid(row=2, column=1, padx=5, sticky='ew')
        
        progress_frame = ttk.LabelFrame(self.main_frame, text="Progresso", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(0, 20))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            style='success.Horizontal.TProgressbar',
            length=200
        )
        self.progress_bar.pack(fill='x', pady=10)
        
        self.status_var = tk.StringVar(value="Pronto per il download")
        status_label = ttk.Label(
            progress_frame,
            textvariable=self.status_var,
            font=('Helvetica', 10)
        )
        status_label.pack()
        
        download_button = ttk.Button(
            self.main_frame,
            text="▶️ Avvia Download",
            style='success.TButton',
            command=self.start_download
        )
        download_button.grid(row=4, column=0, columnspan=3, pady=20)

        list_frame = ttk.LabelFrame(self.main_frame, text="Cronologia Download", padding="10")
        list_frame.grid(row=5, column=0, columnspan=3, sticky='nsew', pady=(0, 20))
        
        self.download_list = ttk.Treeview(
            list_frame,
            columns=('URL', 'Formato', 'Stato'),
            show='headings',
            style='primary.Treeview'
        )
        self.download_list.heading('URL', text='URL', anchor='w')
        self.download_list.heading('Formato', text='Formato', anchor='w')
        self.download_list.heading('Stato', text='Stato', anchor='w')
        
        self.download_list.column('URL', width=400)
        self.download_list.column('Formato', width=100)
        self.download_list.column('Stato', width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.download_list.yview)
        self.download_list.configure(yscrollcommand=scrollbar.set)
        
        self.download_list.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def browse_output(self):
        directory = tk.filedialog.askdirectory()
        if directory:
            self.output_path_var.set(directory)
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.progress_var.set(progress)
                self.status_var.set(f"Scaricamento: {progress:.1f}%")
            except:
                pass
        elif d['status'] == 'finished':
            self.status_var.set("Download completato! ✅")
            self.progress_var.set(100)
    
    def download_video(self):
        url = self.url_var.get()
        output_path = self.output_path_var.get()
        format_option = self.format_var.get()
        quality = self.quality_var.get()
        
        if not url:
            tk.messagebox.showerror("Errore", "Inserisci un URL valido")
            return
        
        try:
            item_id = self.download_list.insert('', 0, values=(url, format_option, "⏳ In corso"))
            
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
            }
            
            if format_option == 'mp3':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            
            if quality != 'highest':
                quality_number = quality.replace('p', '')
                ydl_opts['format'] = f'bestvideo[height<={quality_number}]+bestaudio/best[height<={quality_number}]'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.download_list.item(item_id, values=(url, format_option, "✅ Completato"))
            
        except Exception as e:
            self.status_var.set(f"Errore: {str(e)}")
            self.download_list.item(item_id, values=(url, format_option, "❌ Errore"))
            tk.messagebox.showerror("Errore", f"Si è verificato un errore: {str(e)}")
    
    def start_download(self):
        download_thread = Thread(target=self.download_video)
        download_thread.daemon = True
        download_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = YoutubeDownloader(root)
    root.mainloop()