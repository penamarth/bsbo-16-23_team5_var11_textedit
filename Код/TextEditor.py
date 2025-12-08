import abc
from functools import wraps
from typing import Any, List, Optional, Tuple


def log_method_call(func):
    """Декоратор для логирования вызовов."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        cls_name = func.__qualname__.split(".")[0]
        if args:
            first_arg = args[0]
            if hasattr(first_arg, "__name__"):
                cls_name = first_arg.__name__
            elif hasattr(first_arg, "__class__"):
                cls_name = first_arg.__class__.__name__
        print(f"[CALL] Class: {cls_name} | Method: {func.__name__}()")
        return func(*args, **kwargs)

    return wrapper


def log_class_methods(cls):
    """Декоратор класса для логирования публичных методов."""
    for attr_name, attr_value in cls.__dict__.items():
        if attr_name.startswith("_") and not attr_name.endswith("__"):
            continue

        if isinstance(attr_value, staticmethod):
            setattr(cls, attr_name, staticmethod(log_method_call(attr_value.__func__)))
        elif isinstance(attr_value, classmethod):
            setattr(cls, attr_name, classmethod(log_method_call(attr_value.__func__)))
        elif callable(attr_value):
            setattr(cls, attr_name, log_method_call(attr_value))
    return cls


# ============================================================
#                         COMPOSITE
# ============================================================


class IComponent(abc.ABC):
    """Интерфейс компонента документа."""

    @abc.abstractmethod
    def gettext(self) -> str:
        pass

    @abc.abstractmethod
    def apply_highlight(self, strategy: "IHighlightStrategy"):
        pass


@log_class_methods
class WordComponent(IComponent):
    """Лист дерева - Слово."""

    def __init__(self, word: str):
        self._content = word
        self._color = "black"
        self._back_color = None

    def gettext(self) -> str:
        return self._content

    def apply_highlight(self, strategy: "IHighlightStrategy"):
        strategy.check_and_apply(self)

    def set_color(self, color: str):
        self._color = color

    def set_back_color(self, color: Optional[str]):
        self._back_color = color

    def get_render_style(self) -> Tuple[str, Optional[str]]:
        return self._color, self._back_color


@log_class_methods
class SentenceComponent(IComponent):
    """Предложение, содержит слова."""

    def __init__(self):
        self._content: List[WordComponent] = []

    def add(self, text: str):
        list_word = text.split()
        for word in list_word:
            self._content.append(WordComponent(word))

    def gettext(self) -> str:
        text = [i.gettext() for i in self._content]
        return " ".join(text)

    def get_components(self) -> List[WordComponent]:
        return self._content

    def apply_highlight(self, strategy: "IHighlightStrategy"):
        for child in self._content:
            child.apply_highlight(strategy)


@log_class_methods
class ParagraphComponent(IComponent):
    """Абзац, содержит предложения."""

    def __init__(self):
        self._content: List[SentenceComponent] = []

    def add(self, text: str):
        text = text.replace(".", ".<sen>")
        text = text.replace("!", "!<sen>")
        text = text.replace("?", "?<sen>")
        list_sentence = text.split("<sen>")
        for sentence in list_sentence:
            if sentence.strip():
                sentence_obj = SentenceComponent()
                sentence_obj.add(sentence.strip())
                self._content.append(sentence_obj)

    def gettext(self) -> str:
        text = [i.gettext() for i in self._content]
        return " ".join(text)

    def get_components(self) -> List[SentenceComponent]:
        return self._content

    def apply_highlight(self, strategy: "IHighlightStrategy"):
        for child in self._content:
            child.apply_highlight(strategy)


@log_class_methods
class Document:
    """Документ, содержит абзацы."""

    def __init__(self, file_name: str, path: str):
        self._name = file_name
        self._path = path
        self._content: List[ParagraphComponent] = []

    @property
    def name(self):
        return self._name

    def insert_text(self, text: str):
        parts = text.split("<p>")

        if parts[0] == "":
            for part in parts[1:]:
                para = ParagraphComponent()
                para.add(part)
                self._content.append(para)
        elif not self._content:
            for part in parts:
                para = ParagraphComponent()
                para.add(part)
                self._content.append(para)
        else:
            self._content[-1].add(parts[0])
            for part in parts[1:]:
                para = ParagraphComponent()
                para.add(part)
                self._content.append(para)

    def gettext(self) -> str:
        text = [i.gettext() for i in self._content]
        return "\n".join(text)

    def get_components(self) -> List[ParagraphComponent]:
        return self._content

    def apply_highlight(self, strategy: "IHighlightStrategy"):
        for child in self._content:
            child.apply_highlight(strategy)

    def clear_search_results(self):
        for paragraph in self._content:
            for sentence in paragraph.get_components():
                for word in sentence.get_components():
                    word.set_back_color(None)

    def view_text(self):
        print(f"\n--- ДОКУМЕНТ: {self._name} ---")
        if not self._content:
            print("[Пустой документ]")
            return

        for paragraph in self._content:
            visual_line = []
            for sentence in paragraph.get_components():
                for word in sentence.get_components():
                    color, back_color = word.get_render_style()

                    prefix = ""
                    suffix = "\033[0m"

                    if back_color == "orange":
                        prefix += "\033[43m"
                    elif back_color == "red":
                        prefix += "\033[41m"

                    if color == "blue":
                        prefix += "\033[34m"
                    elif color == "green":
                        prefix += "\033[32m"
                    elif color == "black":
                        prefix += "\033[37m"

                    visual_line.append(f"{prefix}{word.gettext()}{suffix}")

            print(" ".join(visual_line))
            print("")
        print("------------------------------\n")


# ============================================================
#                         HIGHLIGHT STRATEGIES
# ============================================================


class IHighlightStrategy(abc.ABC):
    name: str

    @abc.abstractmethod
    def check_and_apply(self, word: WordComponent):
        pass


@log_class_methods
class SearchStrategy(IHighlightStrategy):
    _instance = None
    name = "search"

    def __init__(
        self, query: str, is_case_sensitive: bool = False, is_whole_word: bool = False
    ):
        if not self._instance:
            self._instance = self
        else:
            self = self._instance

        self.query = query
        self.is_case_sensitive = is_case_sensitive
        self.is_whole_word = is_whole_word

        self.target = query if is_case_sensitive else query.lower()

    def check_and_apply(self, word: WordComponent):
        text = word.gettext()
        clean = text.strip(".,!?;:")
        check = clean if self.is_case_sensitive else clean.lower()

        match = False
        if self.is_whole_word:
            match = check == self.target
        else:
            match = self.target in check

        if match:
            word.set_back_color("orange")
        else:
            word.set_back_color(None)


@log_class_methods
class SyntaxStrategy(IHighlightStrategy):
    def __init__(self, strategy_name: str, keywords: List[str], color: str):
        self.name = strategy_name
        self.keywords = keywords
        self.color = color

    def check_and_apply(self, word: WordComponent):
        clean_word = word.gettext().strip(".,!?;:")
        if clean_word in self.keywords:
            word.set_color(self.color)
        else:
            word.set_color("black")


@log_class_methods
class HighlightStrategyFactory:
    def __init__(self):
        self.strategies: List[IHighlightStrategy] = []
        self._selected_strategy: Optional[IHighlightStrategy] = None

    @property
    def selected_strategy(self) -> Optional[IHighlightStrategy]:
        return self._selected_strategy

    def create_strategy(self, type_str: str, params: dict) -> IHighlightStrategy:
        if type_str.lower() == "search":
            return SearchStrategy(
                query=params.get("query", ""),
                is_case_sensitive=params.get("case", False),
                is_whole_word=params.get("whole", False),
            )
        return SyntaxStrategy(
            strategy_name=type_str,
            keywords=params.get("keywords", []),
            color=params.get("color", "blue"),
        )

    def add_strategy(self, strategy: IHighlightStrategy):
        self.strategies.append(strategy)

    def show_strategies(self):
        print("Доступные стратегии:")
        for idx, s in enumerate(self.strategies, 1):
            print(f"{idx}. {s.name}")

    def select_strategy(self, idx: int) -> bool:
        if 1 <= idx <= len(self.strategies):
            self._selected_strategy = self.strategies[idx - 1]
            return True
        return False


# ============================================================
#                         EXPORT STRATEGIES
# ============================================================


class IExportStrategy(abc.ABC):
    @property
    @abc.abstractmethod
    def extension(self) -> str:
        pass

    @abc.abstractmethod
    def export(self, doc: Document, path: str):
        pass


@log_class_methods
class PdfExportStrategy(IExportStrategy):
    extension = "pdf"

    def export(self, doc: Document, path: str):
        _ = doc.get_components()
        print(f"✅ [PDF] Файл успешно сгенерирован: {path}")


@log_class_methods
class JsonExportStrategy(IExportStrategy):
    extension = "json"

    def export(self, doc: Document, path: str):
        data = {"doc": doc.name, "content": []}
        for p in doc.get_components():
            data["content"].append(p.gettext())
        print(f"✅ [JSON] Файл успешно сериализован: {path}")


@log_class_methods
class ExportStrategyFabric:
    def create_strategy(self, format_str: str) -> IExportStrategy:
        fmt = format_str.lower()
        if fmt == "pdf":
            return PdfExportStrategy()
        elif fmt == "json":
            return JsonExportStrategy()
        else:
            raise ValueError(f"Неизвестный формат: {format_str}")


@log_class_methods
class ExportManager:
    def export(self, strategy: IExportStrategy, doc: Document):
        full_path = f"{doc.name}_export.{strategy.extension}"
        strategy.export(doc, full_path)


# ============================================================
#                         PRINT SYSTEM
# ============================================================


@log_class_methods
class PrintSettings:
    def __init__(self, printer_name: str, copies: int, duplex: bool):
        self.printer_name = printer_name
        self.copies = copies
        self.duplex = duplex


@log_class_methods
class Printer:
    def send_to_print(self, document: Document, settings: PrintSettings):
        print(f"[PRINTER] Получено задание: '{document.name}'")
        print(
            f"[PRINTER] Принтер: {settings.printer_name} | Копий: {settings.copies} | Duplex: {settings.duplex}"
        )
        print("[PRINTER] Печать... OK.")
        return "JOB_ID_001"


@log_class_methods
class PrintPreview:
    def generate_preview(self, doc: Document, settings: PrintSettings):
        print(f"📄 [PREVIEW] Предварительный просмотр для {settings.printer_name}")
        doc.view_text()


@log_class_methods
class PrintManager:
    def __init__(self):
        self._preview = PrintPreview()
        self._printer = Printer()

    def show_preview(self, doc: Document, settings: PrintSettings):
        self._preview.generate_preview(doc, settings)

    def print(self, doc: Document, settings: PrintSettings):
        self._printer.send_to_print(doc, settings)


# ============================================================
#                         CONTROLLER (EDITOR)
# ============================================================


@log_class_methods
class Editor:
    def __init__(self):
        self._document: Optional[Document] = None
        self._export_fabric = ExportStrategyFabric()
        self._export_manager = ExportManager()

        self._print_manager = PrintManager()
        self._print_settings: Optional[PrintSettings] = None

        self._highlight_factory = HighlightStrategyFactory()

        self._highlight_factory.add_strategy(SyntaxStrategy("None", [], "black"))
        self._highlight_factory.add_strategy(
            SyntaxStrategy(
                "Python", ["def", "class", "return", "print", "if", "else"], "blue"
            )
        )

    def new_document(self, name: str, path: str):
        self._document = Document(name, path)

    def insert_text(self, text: str):
        if self._document:
            self._document.insert_text(text)
        else:
            print("Ошибка: Документ не создан.")

    def get_content(self):
        if self._document:
            self._document.clear_search_results()
            self._document.view_text()

    def search_text(
        self, query: str, is_case_sensitive: bool = False, is_whole_word: bool = False
    ):
        if not self._document:
            print("Ошибка: Документ не создан.")
            return

        params = {"query": query, "case": is_case_sensitive, "whole": is_whole_word}

        search_strat = self._highlight_factory.create_strategy("search", params)
        self._document.apply_highlight(search_strat)
        self._document.view_text()

    def apply_syntax_highlight(self):
        if not self._document:
            return

        self._highlight_factory.show_strategies()
        try:
            idx = int(input("Выберите номер стратегии > "))
            if self._highlight_factory.select_strategy(idx):
                strat = self._highlight_factory.selected_strategy
                if strat:
                    self._document.apply_highlight(strat)
                    self._document.view_text()
        except ValueError:
            print("Ошибка ввода.")

    def export(self, format_str: str):
        if not self._document:
            print("Ошибка: Документ не создан.")
            return
        try:
            strategy = self._export_fabric.create_strategy(format_str)
            self._export_manager.export(strategy, self._document)
        except ValueError as e:
            print(f"Ошибка экспорта: {e}")

    def set_print_settings(self, printer_name: str, copies: int, duplex: bool = False):
        self._print_settings = PrintSettings(printer_name, copies, duplex)
        print("✅ Настройки печати сохранены.")

    def show_preview(self):
        if not self._document or not self._print_settings:
            print("Ошибка: Нет документа или настроек печати.")
            return
        self._print_manager.show_preview(self._document, self._print_settings)

    def print_document(self):
        if not self._document or not self._print_settings:
            print("Ошибка: Сначала настройте печать (set_print_settings).")
            return

        self._print_manager.print(self._document, self._print_settings)


# ============================================================
#                         MAIN LOOP
# ============================================================

if __name__ == "__main__":
    editor = Editor()

    print("=== Text Editor System ===")

    while True:
        print("\n" + "=" * 30)
        print("1. Новый документ")
        print("2. Вставить текст (поддержка <p> и <sen>)")
        print("3. Показать текст (сброс поиска)")
        print("4. Поиск по тексту")
        print("5. Подсветка синтаксиса")
        print("6. Экспорт (PDF/JSON)")
        print("7. Печать")
        print("0. Выход")
        print("=" * 30)

        cmd = input("Ваш выбор > ")
        print()

        if cmd == "1":
            name = input("Название файла: ")
            editor.new_document(name, "txt")
            print("Документ создан.")

        elif cmd == "2":
            txt = input("Введите текст: ")
            editor.insert_text(txt)
            print("Текст добавлен.")

        elif cmd == "3":
            editor.get_content()

        elif cmd == "4":
            q = input("Поисковый запрос: ")
            case = input("Учитывать регистр? (y/n): ").strip().lower() == "y"
            whole = input("Только слово целиком? (y/n): ").strip().lower() == "y"
            editor.search_text(q, is_case_sensitive=case, is_whole_word=whole)

        elif cmd == "5":
            editor.apply_syntax_highlight()

        elif cmd == "6":
            fmt = input("Формат (pdf/json): ")
            editor.export(fmt)

        elif cmd == "7":
            print("--- Настройка печати ---")
            prn = input("Имя принтера: ")
            try:
                cp = int(input("Количество копий: "))
            except ValueError:
                cp = 1
            dup = input("Двусторонняя печать? (y/n): ").strip().lower() == "y"

            editor.set_print_settings(prn, cp, dup)

            if input("Показать предпросмотр? (y/n): ").lower() == "y":
                editor.show_preview()

            if input("Отправить на печать? (y/n): ").lower() == "y":
                editor.print_document()

        elif cmd == "0":
            print("Выход.")
            break
        else:
            print("Неверная команда.")
