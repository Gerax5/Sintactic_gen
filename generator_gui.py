import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def seleccionar_yalex():
    ruta = filedialog.askopenfilename(
        title="Selecciona un archivo .yal o .txt",
        filetypes=[("Archivos YALex", "*.yal *.txt"), ("Todos los archivos", "*.*")]
    )
    entry_yalex.delete(0, tk.END)
    entry_yalex.insert(0, ruta)

def seleccionar_entrada():
    """Selecciona el archivo de texto que vamos a tokenizar."""
    ruta = filedialog.askopenfilename(
        title="Selecciona un archivo de texto para analizar",
        filetypes=[("Archivos de texto", "*.txt *.dat *.code"), ("Todos los archivos", "*.*")]
    )
    entry_entrada.delete(0, tk.END)
    entry_entrada.insert(0, ruta)

def generar_analizador():
    yalex_file = entry_yalex.get().strip()
    out_file = entry_output.get().strip()
    if not out_file:
        out_file = "lexer.py"

    if not os.path.isfile(yalex_file):
        messagebox.showerror("Error", "Selecciona un archivo YALex válido")
        return

    cmd = ["python", "main.py", yalex_file, "-o", out_file]

    try:
        subprocess.run(cmd, check=True)
        messagebox.showinfo("Éxito", f"Se generó el analizador en {out_file}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Ocurrió un problema generando el analizador")

def ejecutar_analizador():
    lexer_file = entry_output.get().strip()
    if not lexer_file:
        lexer_file = "lexer.py"

    entrada_file = entry_entrada.get().strip()
    if not os.path.isfile(entrada_file):
        messagebox.showerror("Error", "Selecciona un archivo de texto válido")
        return
    
    if not os.path.isfile(lexer_file):
        messagebox.showerror("Error", f"No se encontró el analizador {lexer_file}. Genera primero.")
        return

    cmd = ["python", lexer_file]
    
    try:
        with open(entrada_file, "r", encoding="utf-8") as inp:
            result = subprocess.run(cmd, check=True, text=True, stdin=inp, capture_output=True)

        text_salida.config(state=tk.NORMAL)
        text_salida.delete("1.0", tk.END)
        text_salida.insert(tk.END, result.stdout)
        
        text_salida.tag_config("error", foreground="red")

        lines = result.stdout.splitlines()
        current_index = 1

        for line in lines:
            if line.startswith("ERROR(line "):
                start_pos = f"{current_index}.0"
                end_pos = f"{current_index}.end"
                text_salida.tag_add("error", start_pos, end_pos)
            current_index += 1

        text_salida.config(state=tk.DISABLED)

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Falla al ejecutar el analizador:\n{e}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado:\n{e}")


def main():
    root = tk.Tk()
    root.title("Generador de Analizadores Léxicos")

    frame_yalex = tk.LabelFrame(root, text="Archivo YALex")
    frame_yalex.pack(fill="x", padx=10, pady=5)
    
    lbl_yalex = tk.Label(frame_yalex, text="Archivo YALex:")
    lbl_yalex.pack(side=tk.LEFT, padx=5, pady=5)

    entry_yalex = tk.Entry(frame_yalex, width=50)
    entry_yalex.pack(side=tk.LEFT, padx=5, pady=5)

    btn_yalex = tk.Button(frame_yalex, text="Examinar...", command=seleccionar_yalex)
    btn_yalex.pack(side=tk.LEFT, padx=5, pady=5)

    frame_out = tk.LabelFrame(root, text="Salida del Generador")
    frame_out.pack(fill="x", padx=10, pady=5)

    lbl_out = tk.Label(frame_out, text="Analizador Léxico:")
    lbl_out.pack(side=tk.LEFT, padx=5, pady=5)

    entry_output = tk.Entry(frame_out, width=30)
    entry_output.pack(side=tk.LEFT, padx=5, pady=5)
    entry_output.insert(0, "lexer.py")

    btn_gen = tk.Button(frame_out, text="Generar Analizador", command=generar_analizador)
    btn_gen.pack(side=tk.LEFT, padx=10, pady=5)

    frame_entrada = tk.LabelFrame(root, text="Archivo de texto a tokenizar")
    frame_entrada.pack(fill="x", padx=10, pady=5)

    lbl_entrada = tk.Label(frame_entrada, text="Archivo de entrada:")
    lbl_entrada.pack(side=tk.LEFT, padx=5, pady=5)

    entry_entrada = tk.Entry(frame_entrada, width=50)
    entry_entrada.pack(side=tk.LEFT, padx=5, pady=5)

    btn_entrada = tk.Button(frame_entrada, text="Examinar...", command=seleccionar_entrada)
    btn_entrada.pack(side=tk.LEFT, padx=5, pady=5)

    frame_ejec = tk.LabelFrame(root, text="Ejecutar Analizador Léxico")
    frame_ejec.pack(fill="x", padx=10, pady=5)

    btn_ejecutar = tk.Button(frame_ejec, text="Tokenizar", command=ejecutar_analizador)
    btn_ejecutar.pack(side=tk.LEFT, padx=10, pady=5)

    frame_salida = tk.LabelFrame(root, text="Salida del Analizador")
    frame_salida.pack(fill="both", expand=True, padx=10, pady=5)

    text_salida = tk.Text(frame_salida, wrap="word", height=10)
    text_salida.pack(fill="both", expand=True)

    def _bind_vars():
        globals()["entry_yalex"] = entry_yalex
        globals()["entry_entrada"] = entry_entrada
        globals()["entry_output"] = entry_output
        globals()["text_salida"] = text_salida

    _bind_vars()

    root.mainloop()

if __name__ == "__main__":
    main()
