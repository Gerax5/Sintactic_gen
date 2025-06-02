from __future__ import annotations

import io
import os
import sys
import traceback
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

try:
    from src.helpers.Utils import (
        leerYapar,
        verificar_tokens,
        verificar_tokens_usados_no_declarados,
        pre_process_regex,
    )
    from src.helpers.first import First
    from src.helpers.follow import Follow
    from src.Automata.Automata import Create_automata
    from src.AutomataLR0.automata import AutomataLR0
    from src.SLRParsing.SLR import SLR
    from src.helpers.Lex import Lexer
except ModuleNotFoundError as e:
    print("Módulos no encontrados:", e)


def human_readable_path(path: str | Path | None) -> str:
    if path is None:
        return ""
    path = Path(path)
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


@dataclass
class AnalysisResult:
    lexer_tokens: List[List[Tuple[str, str]]]
    parser_logs: str
    lr0_image_path: str | None


class AnalyzerWorker(QThread):

    finished = Signal(object)

    def __init__(self, yalex: str, yapar: str, input_txt: str):
        super().__init__()
        self.yalex = yalex
        self.yapar = yapar
        self.input_txt = input_txt


    @staticmethod
    def build_lexer(yalex_path: str):
        lex = Lexer()
        aut = Create_automata()
        with open(yalex_path, "r", encoding="utf-8") as fh:
            lex.indentify(fh.readlines())
        lex.parseLets()
        regex = pre_process_regex(lex.lets)
        aut.convertRegex(regex, lex.tokens)
        return lex, aut

    @staticmethod
    def run_lexer(lex: Lexer, aut: Create_automata, input_string: str):
        initial_state = next(
            st for st, info in aut.ddfa.transitions.items() if info.get("initial")
        )
        tokens_en_linea: List[List[Tuple[str, str]]] = []
        tokens_linea_actual: List[Tuple[str, str]] = []
        line_number = 1
        i = 0
        longitud = len(input_string)
        replace_map = {"\n": "\\n", "\t": "\\t", "\r": "\\r", " ": " "}
        specials = set(replace_map)
        while i < longitud:
            # Saltar espacios y contar líneas
            while i < longitud and input_string[i].isspace():
                if input_string[i] == "\n":
                    line_number += 1
                    if tokens_linea_actual:
                        tokens_en_linea.append(tokens_linea_actual)
                        tokens_linea_actual = []
                i += 1
            if i >= longitud:
                break
            current_state = initial_state
            lexema_actual = ""
            accion_aceptada = None
            lexema_aceptado = ""
            pos_aceptada = -1
            j = i
            while j < longitud:
                c = input_string[j]
                lexema_actual += c
                if c not in aut.ddfa.alphabet:
                    c = replace_map.get(c, f"\\{c}")
                    if c not in aut.ddfa.alphabet:
                        break
                trans = aut.ddfa.transitions[current_state]["transitions"]
                if c in trans:
                    if c == "\\n":
                        line_number += 1
                    current_state = trans[c]
                    if aut.ddfa.transitions[current_state]["accept"]:
                        accion_info = aut.ddfa.transitions[current_state].get("action", "")
                        accion_aceptada = (
                            accion_info.get("action", "")
                            if isinstance(accion_info, dict)
                            else accion_info
                        )
                        lexema_aceptado = lexema_actual
                        pos_aceptada = j + 1
                    j += 1
                else:
                    break
            if accion_aceptada and accion_aceptada.strip():
                tokens_linea_actual.append((accion_aceptada, lexema_aceptado))
                i = pos_aceptada
            else:
                tokens_linea_actual.append((f"ERROR(line {line_number})", input_string[i]))
                i += 1
        if tokens_linea_actual:
            tokens_en_linea.append(tokens_linea_actual)
        return tokens_en_linea


    def run(self):
        try:
            # === ANALIZADOR LÉXICO =================================================== #
            lex, aut = self.build_lexer(self.yalex)
            with open(self.input_txt, "r", encoding="utf-8") as fh:
                entrada = fh.read()
            tokens_por_linea = self.run_lexer(lex, aut, entrada)

            # === ANALIZADOR SINTÁCTICO =============================================== #
            tokens_decl, producciones, initial_sym = leerYapar(self.yapar)
            undeclared = verificar_tokens_usados_no_declarados(tokens_decl, producciones)
            missing = verificar_tokens(lex.tokens_definidos, set(tokens_decl))
            if undeclared or missing:
                raise ValueError(
                    "Inconsistencias entre YALex y YAPar:\n" +
                    f"  • Tokens usados y no declarados: {undeclared}\n" +
                    f"  • Tokens declarados en YAPar pero ausentes en YALex: {missing}\n"
                )
            no_terminales = list(producciones.keys())
            terminales = sorted(set(tokens_decl))
            first = First(producciones)
            follow = Follow(producciones, first.first, initial_sym)
            automata = AutomataLR0(producciones, initial_sym)
            automata.build()
            automata.graph() 
            lr0_img = "AAAutmoataLR0/automata_LR0.png" if Path("AAAutmoataLR0/automata_LR0.png").exists() else None
            slr = SLR(
                producciones,
                no_terminales,
                automata.states,
                automata.transiciones,
                automata.estados_id,
                automata.estado_aceptacion,
                automata.startSymbolPrime,
                follow.follow_set,
                terminales,
            )
            slr.build_slr_tables()

            parser_output = io.StringIO()
            with redirect_stdout(parser_output):
                for linea in tokens_por_linea:
                    to_parse = [tk for tk, _ in linea]
                    slr.parse(to_parse)
                    print("\n\n")
            result = AnalysisResult(
                lexer_tokens=tokens_por_linea,
                parser_logs=parser_output.getvalue(),
                lr0_image_path=lr0_img,
            )
            self.finished.emit(result)
        except Exception as exc:
            traceback.print_exc()
            self.finished.emit(exc)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador SLR")
        self.resize(1000, 700)
        self.yalex_path: str | None = None
        self.yapar_path: str | None = None
        self.input_path: str | None = None
        self.worker: AnalyzerWorker | None = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.yalex_line = QLineEdit(); self.yalex_line.setReadOnly(True)
        self.yapar_line = QLineEdit(); self.yapar_line.setReadOnly(True)
        self.input_line = QLineEdit(); self.input_line.setReadOnly(True)
        for le in (self.yalex_line, self.yapar_line, self.input_line):
            le.setPlaceholderText("(Archivo no seleccionado)")

        def make_row(text: str, btn_txt: str, slot):
            row = QWidget(); l = QVBoxLayout(row); l.setContentsMargins(0,0,0,0)
            lbl = QLabel(text); lbl.setStyleSheet("font-weight:600")
            hl = QWidget(); hlayout = QVBoxLayout(hl); hlayout.setContentsMargins(0,0,0,0)
            hlayout.addWidget(btn := QPushButton(btn_txt))
            btn.clicked.connect(slot)
            l.addWidget(lbl)
            l.addWidget(hl)
            return row

        layout.addWidget(make_row("Especificación YALex", "Seleccionar .yalex", self.pick_yalex))
        layout.addWidget(self.yalex_line)
        layout.addWidget(make_row("Especificación YAPar", "Seleccionar .yapar", self.pick_yapar))
        layout.addWidget(self.yapar_line)
        layout.addWidget(make_row("Archivo de prueba", "Seleccionar .txt", self.pick_input))
        layout.addWidget(self.input_line)

        self.run_btn = QPushButton("Ejecutar análisis")
        self.run_btn.clicked.connect(self.run_analysis)
        self.run_btn.setEnabled(False)
        layout.addWidget(self.run_btn)

        self.tabs = QTabWidget(); layout.addWidget(self.tabs)
        # Tab 0: Autómata LR(0)
        self.lr0_label = QLabel("Genera el autómata para verlo aquí …")
        self.lr0_label.setAlignment(Qt.AlignCenter)
        self.lr0_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tabs.addTab(self.lr0_label, "Autómata LR(0)")
        # Tab 1: Tokens por línea
        self.token_text = QTextEdit(); self.token_text.setReadOnly(True)
        self.tabs.addTab(self.token_text, "Tokens")
        # Tab 2: Log del parser
        self.parser_text = QTextEdit(); self.parser_text.setReadOnly(True)
        self.tabs.addTab(self.parser_text, "Salida del parser")


    def pick_generic(self, attr: str, lineedit: QLineEdit, filter_str: str):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo", os.getcwd(), filter_str)
        if path:
            setattr(self, attr, path)
            lineedit.setText(human_readable_path(path))
        self.run_btn.setEnabled(all([self.yalex_path, self.yapar_path, self.input_path]))

    def pick_yalex(self):
        self.pick_generic("yalex_path", self.yalex_line, "Archivos YALex (*.yalex *.yal)")

    def pick_yapar(self):
        self.pick_generic("yapar_path", self.yapar_line, "Archivos YAPar (*.yapar *.yalp)")

    def pick_input(self):
        self.pick_generic("input_path", self.input_line, "Archivos de texto (*.txt)")


    def run_analysis(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "En progreso", "Ya hay un análisis en ejecución.")
            return
        self.token_text.clear(); self.parser_text.clear(); self.lr0_label.clear()
        self.lr0_label.setText("Procesando… Por favor espera…")
        self.worker = AnalyzerWorker(self.yalex_path, self.yapar_path, self.input_path)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def on_worker_finished(self, payload):
        if isinstance(payload, Exception):
            QMessageBox.critical(self, "Error en el análisis", str(payload))
            self.lr0_label.setText("Falló la generación del autómata.")
            return
        result: AnalysisResult = payload
        # --- Autómata LR(0) --------------------------------------------- #
        if result.lr0_image_path and Path(result.lr0_image_path).exists():
            pix = QPixmap(result.lr0_image_path)
            if pix.isNull():
                self.lr0_label.setText("No se pudo cargar la imagen del LR(0).")
            else:
                scaled = pix.scaled(QSize(800,600), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lr0_label.setPixmap(scaled)
        else:
            self.lr0_label.setText("No se generó imagen del LR(0).")
        # --- Tokens ------------------------------------------------------- #
        token_lines = []
        for idx, linea in enumerate(result.lexer_tokens, 1):
            token_lines.append(f"Línea {idx}:")
            for tok, lexema in linea:
                token_lines.append(f"  {tok:15} → {lexema}")
            token_lines.append("")
        self.token_text.setPlainText("\n".join(token_lines) or "(sin tokens)")
        # --- Parser log --------------------------------------------------- #
        self.parser_text.setPlainText(result.parser_logs or "(sin salida)")
        self.tabs.setCurrentIndex(0)



def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()