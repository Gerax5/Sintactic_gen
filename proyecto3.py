import importlib.util
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk  # Pillow debe estar instalado


def _load_module_from_path(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar el módulo {module_name} desde {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod  # evita duplicados si se recarga
    spec.loader.exec_module(mod)
    return mod


class AnalizadorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador y Evaluador – YALex / YAPar")
        self.minsize(900, 600)

        self.yal_path = tk.StringVar()
        self.yalp_path = tk.StringVar()
        self.test_path = tk.StringVar()
        self.lexer_out = tk.StringVar(value="lexer.py")
        self.parser_out = tk.StringVar(value="sintactic.py")

        self._build_file_selectors()
        self._build_buttons()
        self._build_output_panel()
        self._build_image_panel()

    def _build_file_selectors(self):
        frm = tk.LabelFrame(self, text="Archivos de entrada", padx=6, pady=4)
        frm.pack(fill="x", padx=10, pady=8)

        def _row(parent, label, text_var, cmd):
            row = tk.Frame(parent)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, width=14, anchor="w").pack(side="left")
            tk.Entry(row, textvariable=text_var, width=70).pack(side="left", expand=True, fill="x")
            tk.Button(row, text="Examinar", command=cmd).pack(side="left", padx=4)

        _row(frm, ".yal:", self.yal_path, lambda: self._browse(self.yal_path, ("Archivos YALex", "*.yal")))
        _row(frm, ".yalp:", self.yalp_path, lambda: self._browse(self.yalp_path, ("Archivos YAPar", "*.yalp")))
        _row(frm, "Entrada .txt:", self.test_path, lambda: self._browse(self.test_path, ("Texto", "*.txt")))

        # Archivos de salida
        row_out = tk.Frame(frm)
        row_out.pack(fill="x", pady=2)
        tk.Label(row_out, text="lexer.py:", width=14, anchor="w").pack(side="left")
        tk.Entry(row_out, textvariable=self.lexer_out, width=20).pack(side="left")
        tk.Label(row_out, text="sintactic.py:").pack(side="left", padx=6)
        tk.Entry(row_out, textvariable=self.parser_out, width=20).pack(side="left")

    def _build_buttons(self):
        bar = tk.Frame(self)
        bar.pack(fill="x", padx=10, pady=4)
        tk.Button(bar, text="Generar analizadores", command=self.generar_analyzers).pack(side="left", padx=6)
        tk.Button(bar, text="Analizar entrada", command=self.ejecutar_analisis).pack(side="left", padx=6)
        tk.Button(bar, text="Salir", command=self.destroy).pack(side="right", padx=6)

    def _build_output_panel(self):
        self.text_out = tk.Text(self, wrap="word", height=20)
        self.text_out.pack(fill="both", expand=True, padx=10, pady=(0,8))
        self.text_out.tag_config("error_lex", foreground="red")
        self.text_out.tag_config("error_syn", foreground="orange")
        self.text_out.tag_config("ok", foreground="green")
        self.text_out.config(state="disabled")

    def _build_image_panel(self):
        self.img_label = tk.Label(self)
        self.img_label.pack(pady=4)

    @staticmethod
    def _browse(var: tk.StringVar, filetype):
        path = filedialog.askopenfilename(filetypes=[filetype, ("Todos", "*.*")])
        if path:
            var.set(path)

    def _run_subprocess(self, cmd: list[str]):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return -1, "", str(e)


    def generar_analyzers(self):
        yal = Path(self.yal_path.get())
        yalp = Path(self.yalp_path.get())
        if not yal.is_file() or not yalp.is_file():
            messagebox.showerror("Faltan archivos", "Debes seleccionar un archivo .yal y .yalp válidos.")
            return

        lexer_py = Path(self.lexer_out.get())
        parser_py = Path(self.parser_out.get())

        # ─── Generador léxico ───────────────────────────────
        cmd_lex = [sys.executable, "generador_lexico.py", str(yal), "-o", str(lexer_py)]
        code, out, err = self._run_subprocess(cmd_lex)
        if code != 0:
            messagebox.showerror("Error al generar lexer", err or out)
            return

        # ─── Generador sintáctico ───────────────────────────
        cmd_syn = [sys.executable, "generador_sintactico.py", str(yalp), "-l", str(yal), "-o", str(parser_py)]
        code, out2, err2 = self._run_subprocess(cmd_syn)
        if code != 0:
            messagebox.showerror("Error al generar parser", err2 or out2)
            return

        messagebox.showinfo("Éxito", "Se generaron lexer.py y sintactic.py correctamente.")
        # Cargar la imagen del autómata
        self._mostrar_automata()

    def ejecutar_analisis(self):
        input_file = Path(self.test_path.get())
        lexer_py = Path(self.lexer_out.get())
        parser_py = Path(self.parser_out.get())

        # Validaciones
        for p, lbl in ((lexer_py, "lexer.py"), (parser_py, "sintactic.py"), (input_file, "archivo de prueba")):
            if not p.is_file():
                messagebox.showerror("Falta archivo", f"No se encontró {lbl}: {p}")
                return

        # Importar módulos generados
        lexer_mod = _load_module_from_path("generated_lexer", lexer_py)
        parser_mod = _load_module_from_path("generated_parser", parser_py)

        # Leer entrada y ejecutar lexer
        data = input_file.read_text(encoding="utf-8")
        tokens_raw = lexer_mod.run_lexer(data)  # → [(TOKEN, lexema)]

        # Añadir número de línea
        tokens_en_lineas = []  # list[(token, lexema, linea)]
        linea = 1
        errores_syn = []
        aceptado = True
        skip = ["COMENTARIO", "COMENTARIO_MULTILINEA", ""]
        for lines in tokens_raw:
            for token, lexema in lines:
                if token in skip:
                    continue
                tokens_en_lineas.append((token, lexema, linea))
            
            if tokens_en_lineas:
                aceptadoDefinitivo, errores = parser_mod.parse(tokens_en_lineas)
                if errores:
                    errores_syn.extend(errores)        
                    aceptado = False

            tokens_en_lineas = []

            if not aceptadoDefinitivo:
                aceptado = False
            linea += 1 
        # for token, lexema in tokens_raw:
        #     tokens_en_lineas.append((token, lexema, linea))
        #     if lexema == "\\n":  # en caso el lexer lo retorne explícitamente
        #         linea += 1
        # Al parser le pasamos el flujo completo

        print(tokens_en_lineas)
        
        

        # ---------- Mostrar resultados ----------
        self.text_out.config(state="normal")
        self.text_out.delete("1.0", tk.END)

        # Tokens
        self.text_out.insert(tk.END, "TOKENS OBTENIDOS\n", "bold")
        for lines in tokens_raw:
            for tok, lex in lines:
                start = self.text_out.index(tk.INSERT)
                self.text_out.insert(tk.END, f"{tok:15} -> {lex}\n")
                if tok.startswith("ERROR"):
                    end = self.text_out.index(tk.INSERT)
                    self.text_out.tag_add("error_lex", start, end)

        # for tok, lex in tokens_raw:
        #     start = self.text_out.index(tk.INSERT)
        #     self.text_out.insert(tk.END, f"{tok:15} -> {lex}\n")
        #     if tok.startswith("ERROR"):
        #         end = self.text_out.index(tk.INSERT)
        #         self.text_out.tag_add("error_lex", start, end)
        self.text_out.insert(tk.END, "\n")

        # Parser
        if aceptado and not errores_syn:
            self.text_out.insert(tk.END, "Análisis sintáctico satisfactorio\n", "ok")
        else:
            self.text_out.insert(tk.END, "Errores sintácticos:\n", "error_syn")
            for err in errores_syn:
                self.text_out.insert(tk.END, f"• {err}\n", "error_syn")

        self.text_out.config(state="disabled")

    # -------------------------------------------------------------------
    def _mostrar_automata(self):
        img_path = Path("AAAutmoataLR0/automata_LR0.png")
        if img_path.is_file():
            try:
                img = Image.open(img_path)
                img.thumbnail((600, 400))
                self._tk_img = ImageTk.PhotoImage(img)
                self.img_label.config(image=self._tk_img)
                self.img_label.image = self._tk_img
            except Exception as e:
                messagebox.showwarning("Imagen", f"No se pudo cargar la imagen del autómata: {e}")
        else:
            self.img_label.config(image="")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = AnalizadorGUI()
    app.mainloop()
