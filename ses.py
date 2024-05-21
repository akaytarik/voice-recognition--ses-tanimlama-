import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
from sklearn.metrics import accuracy_score, f1_score


class SpeechAnalyzerApp:
    def __init__(self, root):
        self.recognizer = sr.Recognizer()
        self.root = root
        self.root.title("Konuşma Tanıma ve Analiz Arayüzü")
        self.root.geometry("800x600")
        self.root.configure(bg='#ececec')
        self.setup_ui()

    def setup_ui(self):
        # Başlık etiketi
        ttk.Label(self.root, text="Konuşma Tanıma ve Analiz Arayüzü", font=("Helvetica", 24, "bold"),
                  background='#ececec').pack(pady=20)

        # Durum etiketi
        self.status_label = ttk.Label(self.root, text="Hazır", font=("Helvetica", 14), foreground="green",
                                      background='#ececec')
        self.status_label.pack(pady=10)

        # Kelime sayısı etiketi
        self.word_count_label = ttk.Label(self.root, text="", font=("Helvetica", 14), background='#ececec')
        self.word_count_label.pack(pady=5)

        # Konuşulan metin etiketi
        ttk.Label(self.root, text="Konuşulan Metin:", font=("Helvetica", 12), background='#ececec').pack(pady=5)

        # Sonuç göstermek için giriş kutusu
        self.result_var = tk.StringVar()
        ttk.Entry(self.root, textvariable=self.result_var, font=("Helvetica", 12), width=60).pack(pady=5)

        # Buton stili
        style = ttk.Style()
        style.configure('TButton', font=("Helvetica", 14), padding=10)

        # Konuşmayı tanı butonu
        ttk.Button(self.root, text="Konuşmayı Tanı", command=self.recognize_speech, style='TButton').pack(pady=20)

        # Histogram için çerçeve
        self.canvas_frame = ttk.Frame(self.root, style='TFrame')
        self.canvas_frame.pack(pady=20)

        # Doğruluk etiketi
        self.acc_label = ttk.Label(self.root, text="", font=("Helvetica", 14), background='#ececec')
        self.acc_label.pack(pady=5)

        # F-Measure etiketi
        self.fm_label = ttk.Label(self.root, text="", font=("Helvetica", 14), background='#ececec')
        self.fm_label.pack(pady=5)

    def count_words(self, text):
        # Kelime sayısını hesapla
        return len(text.split())

    def create_histogram(self, text):
        # Kelime frekans histogramı oluştur
        word_counts = Counter(text.split())
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="whitegrid")
        sns.barplot(x=list(word_counts.keys()), y=list(word_counts.values()), color='skyblue')
        plt.xlabel('Kelimeler')
        plt.ylabel('Frekans')
        plt.title('Kelime Frekansı Histogramı')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(plt.gcf(), master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def recognize_speech(self):
        # Konuşmayı tanı ve sonuçları arayüzde göster
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.status_label.config(text="Konuşma algılanıyor...", foreground="blue")
            self.root.update_idletasks()
            try:
                audio_data = self.recognizer.listen(source, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio_data, language="tr-TR")
                self.result_var.set(text)
                self.word_count_label.config(text=f"Toplam kelime sayısı: {self.count_words(text)}")
                self.create_histogram(text)
                reference_text = "Merhaba, nasılsınız?"  # Doğru transkripsiyonu buraya ekleyin
                self.calculate_metrics(text, reference_text)
                self.status_label.config(text="Başarılı", foreground="green")
                self.root.update_idletasks()
            except sr.UnknownValueError:
                self.show_error("Ne söylediğiniz anlaşılamadı.")
            except sr.RequestError as e:
                self.show_error(f"Sistem hatası: {e}")
            except Exception as e:
                self.show_error(str(e))

    def calculate_metrics(self, recognized_text, reference_text):
        # Doğruluk ve F1 skorunu hesapla ve arayüzde göster
        recognized_words = recognized_text.split()
        reference_words = reference_text.split()
        if len(recognized_words) > len(reference_words):
            reference_words.extend([''] * (len(recognized_words) - len(reference_words)))
        elif len(reference_words) > len(recognized_words):
            recognized_words.extend([''] * (len(reference_words) - len(recognized_words)))
        accuracy = accuracy_score(reference_words, recognized_words)
        f_measure = f1_score(reference_words, recognized_words, average='weighted', zero_division=1)
        self.acc_label.config(text=f"Doğruluk (Accuracy): {accuracy:.2f}")
        self.fm_label.config(text=f"F-Measure (F1-Score): {f_measure:.2f}")

    def show_error(self, message):
        # Hata mesajı göster
        self.status_label.config(text="Hata", foreground="red")
        messagebox.showerror("Hata", message)
        self.clear_ui()

    def clear_ui(self):
        # Arayüzü temizle
        self.result_var.set("")
        self.status_label.config(text="Hazır", foreground="green")
        self.word_count_label.config(text="")
        self.acc_label.config(text="")
        self.fm_label.config(text="")
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechAnalyzerApp(root)
    root.mainloop()
