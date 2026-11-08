import os
from pathlib import Path
from typing import Optional
from pypdf import PdfReader
import docx2txt
import openpyxl

class DocumentReaderSkill:
    """
    Скилл умного чтения и анализа документов (как в Kira):
    Поддерживает: PDF, Word (.docx), Excel (.xlsx), текстовые файлы (.txt, .md, .csv).
    """

    @classmethod
    def read_document(cls, file_path: str, max_chars: int = 5000) -> str:
        """
        Извлекает текст из документа для последующего анализа и пересказа голосом
        """
        p = Path(file_path)
        if not p.is_absolute():
            # Проверяем на рабочем столе и в папке загрузок
            desktop_p = Path.home() / "Desktop" / file_path
            downloads_p = Path.home() / "Downloads" / file_path
            if desktop_p.exists():
                p = desktop_p
            elif downloads_p.exists():
                p = downloads_p

        if not p.exists():
            return f"Сэр, файл «{file_path}» не найден на диске."

        ext = p.suffix.lower()
        extracted_text = ""

        try:
            if ext == ".pdf":
                reader = PdfReader(str(p))
                for page in reader.pages[:10]:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
            elif ext in [".docx", ".doc"]:
                extracted_text = docx2txt.process(str(p))
            elif ext in [".xlsx", ".xls"]:
                wb = openpyxl.load_workbook(str(p), data_only=True)
                for sheet in wb.worksheets[:3]:
                    extracted_text += f"\n--- Лист: {sheet.title} ---\n"
                    for row in sheet.iter_rows(values_only=True):
                        row_vals = [str(v) for v in row if v is not None]
                        if row_vals:
                            extracted_text += " | ".join(row_vals[:8]) + "\n"
            else:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    extracted_text = f.read()

            if not extracted_text.strip():
                return f"Сэр, документ «{p.name}» открыт, но текста в нем не обнаружено (возможно, сканы)."

            trimmed = extracted_text[:max_chars]
            return f"Документ «{p.name}» прочитан. Содержимое:\n\n{trimmed}"
        except Exception as e:
            return f"Сэр, произошла ошибка при чтении документа: {str(e)}"
