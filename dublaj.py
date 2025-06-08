import os
import subprocess
import tempfile
from tkinter import Tk, filedialog, messagebox, StringVar, Entry, Button, Label

try:
    from argostranslate import package, translate
except ImportError:
    translate = None

try:
    import pywhispercpp
except ImportError:
    pywhispercpp = None


def extract_audio(input_path: str, audio_path: str) -> None:
    """Extract audio from video or copy if already audio."""
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        audio_path,
    ]
    subprocess.run(cmd, check=True)


def transcribe_audio(audio_path: str) -> tuple[str, str]:
    """Transcribe audio to text using Whisper."""
    if not pywhispercpp:
        raise RuntimeError("pywhispercpp is not installed")
    model = pywhispercpp.Whisper.from_pretrained("base")
    result = model.transcribe(audio_path)
    return result["text"], result["language"]


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translate text using Argos Translate."""
    if not translate:
        raise RuntimeError("argos-translate is not installed")

    installed_languages = translate.get_installed_languages()
    from_lang = next((l for l in installed_languages if l.code == source_lang), None)
    to_lang = next((l for l in installed_languages if l.code == target_lang), None)
    if not from_lang or not to_lang:
        raise RuntimeError("Required translation languages not installed")

    translation = from_lang.get_translation(to_lang)
    return translation.translate(text)


def synthesize_speech(text: str, output_mp3: str) -> None:
    """Generate speech with Balabolka."""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as tmp:
        tmp.write(text)
        tmp_path = tmp.name
    try:
        subprocess.run(["balabolka.exe", "-if", tmp_path, "-w", output_mp3], check=True)
    finally:
        os.remove(tmp_path)


def pipeline(input_file: str, target_lang: str, output_mp3: str) -> str:
    """Run the full dubbing pipeline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.wav")
        extract_audio(input_file, audio_path)
        text, src_lang = transcribe_audio(audio_path)
        translated = translate_text(text, src_lang, target_lang)
        synthesize_speech(translated, output_mp3)
    return output_mp3


def run_gui() -> None:
    root = Tk()
    root.title("Dublajör")

    file_var = StringVar()
    lang_var = StringVar(value="tr")

    def browse():
        path = filedialog.askopenfilename(filetypes=[("Media", "*.mp4 *.mp3 *.wav")])
        if path:
            file_var.set(path)

    def start():
        if not file_var.get():
            messagebox.showerror("Error", "Input file required")
            return
        try:
            out_path = pipeline(file_var.get(), lang_var.get(), "output.mp3")
            messagebox.showinfo("Success", f"Output saved to {out_path}")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    Entry(root, textvariable=file_var, width=50).pack(fill="x", padx=5, pady=5)
    Button(root, text="Browse", command=browse).pack(pady=5)
    Label(root, text="Target language code (e.g. tr)").pack(pady=(10, 0))
    Entry(root, textvariable=lang_var).pack(pady=5)
    Button(root, text="Start", command=start).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    run_gui()
