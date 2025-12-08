import abc


class IHighlightStrategy(abc.ABC):
    name: str

    @abc.abstractmethod
    def check_and_apply(self, word: "WordComponent"):
        pass


# -------------------------------------------------------
# Стратегия поиска (SearchStrategy)
# -------------------------------------------------------
class SearchStrategy(IHighlightStrategy):
    """
    Проходит по структуре документа и меняет back_color найденных слов.
    """
    _instance = None
    name = "search"

    def __init__(
        self,
        query: str,
        is_case_sensitive: bool = False,
        is_whole_word: bool = False,
    ):
        if not self._instance:
            self._instance = self
        else:
            self = self._instance

        self.search_query = query
        self.is_case_sensitive = is_case_sensitive
        self.is_whole_word = is_whole_word

        self.target = self.search_query
        if not self.is_case_sensitive:
            self.target = self.target.lower()

    def check_and_apply(self, leaf: "WordComponent"):
        """Проверяет слово на соответствие поисковому запросу."""
        word_text = leaf.gettext()
        clean_word = word_text.strip(".,!?;:")

        check_text = clean_word
        if not self.is_case_sensitive:
            check_text = check_text.lower()

        match_found = False

        if self.is_whole_word:
            if check_text == self.target:
                match_found = True
        else:
            if self.target in check_text:
                match_found = True

        if match_found:
            leaf.set_back_color("orange")
        else:
            leaf.set_back_color(None)


class SyntaxStrategy(IHighlightStrategy):
    def __init__(self, strategy_name: str, keywords: list, color: str):
        self.name = strategy_name
        self.keywords = keywords
        self.color = color

    def check_and_apply(self, word: "WordComponent"):
        if word.gettext() in self.keywords:
            word.set_color(self.color)


class HighlightStrategyFactory:

    @staticmethod
    def create_strategy(strategy_name: str, **kwargs: dict) -> IHighlightStrategy:
        if strategy_name.lower() == "search":
            return SearchStrategy(**kwargs)
    
        return SyntaxStrategy(
            strategy_name=strategy_name,
            keywords=kwargs.get("keywords"),
            color=kwargs.get("color", "blue")
        )

    def __init__(self):
        self.strategies: list[IHighlightStrategy] = []
        self.selected_strategy: IHighlightStrategy = None

    def show_strategies(self):
        """Показать доступные стратегии подсветки."""
        for idx, strategy in enumerate(self.strategies, start=1):
            print(f"{idx}) Паттерн: {strategy.name}")

    def select_strategy(self, index: int) -> bool:
        """Выбрать стратегию подсветки по индексу."""
        if 1 <= index <= len(self.strategies):
            self.selected_strategy = self.strategies[index - 1]
            return True
        else:
            print("Ошибка: Неверный индекс стратегии.")
            return False

    def add_strategy(self, strategy: IHighlightStrategy):
        """Добавить стратегию подсветки."""
        self.strategies.append(strategy)

    def check_and_apply(self, leaf: "WordComponent"):
        """Применяет выбранную стратегию к слову."""
        if self.selected_strategy:
            self.selected_strategy.check_and_apply(leaf)


# ============================================================
#                         AGGREGATE (COMPOSITE)
# ============================================================

class IComponent(abc.ABC):
    """Интерфейс для всех компонентов документа (Composite pattern)."""

    @abc.abstractmethod
    def gettext(self) -> str:
        """Возвращает текстовое содержимое компонента."""
        pass

    @abc.abstractmethod
    def highlight(self, strategy: IHighlightStrategy):
        pass


class WordComponent(IComponent):
    """Представляет отдельное слово в документе."""

    def __init__(self, word: str):
        self.content = word
        self.color = "black"
        self.back_color = None

    def gettext(self) -> str:
        return self.content

    def highlight(self, strategy: IHighlightStrategy):
        strategy.check_and_apply(self)

    def set_color(self, color: str):
        self.color = color

    def set_back_color(self, color: str):
        self.back_color = color

    def get_word(self) -> str:
        return self.content


class SentenceComponent(IComponent):
    """Представляет предложение, состоящее из слов."""

    def __init__(self):
        self.content: list[WordComponent] = []

    def add(self, text: str):
        list_word = text.split()
        for word in list_word:
            self.content.append(WordComponent(word))

    def gettext(self) -> str:
        text = [i.gettext() for i in self.content]
        return " ".join(text)

    def get_components(self) -> list[WordComponent]:
        return self.content

    def highlight(self, strategy: IHighlightStrategy):
        for child in self.content:
            child.highlight(strategy)

class ParagraphComponent(SentenceComponent):
    """Представляет абзац, состоящий из предложений."""

    def __init__(self):
        self.content: list[SentenceComponent] = []

    def add(self, text: str):
        text = text.replace(".", ".<sen>")
        text = text.replace("!", "!<sen>")
        text = text.replace("?", "?<sen>")
        list_sentence = text.split("<sen>")
        for sentence in list_sentence:
            if sentence.strip():
                sentence_obj = SentenceComponent()
                sentence_obj.add(sentence.strip())
                self.content.append(sentence_obj)

    def gettext(self) -> str:
        text = [i.gettext() for i in self.content]
        return " ".join(text)

    def get_components(self) -> list[SentenceComponent]:
        return self.content


class Document(ParagraphComponent):
    """Главный класс документа, хранящий структуру абзацев."""

    def __init__(self, file_name: str, path: str):
        self.name = file_name
        self.path = path
        self.content: list[ParagraphComponent] = []

    def insert_text(self, text: str):
        """Вставляет текст в документ, разбивая его на абзацы."""
        parts = text.split("<p>")
        for part in parts:
            if part.strip():
                para = ParagraphComponent()
                para.add(part)
                self.content.append(para)

    def gettext(self) -> str:
        """Возвращает полный текст документа."""
        text = [i.gettext() for i in self.content]
        return "\n".join(text)

    def get_components(self) -> list[ParagraphComponent]:
        return self.content

    def clear_search_results(self):
        """Сбрасывает фоновую подсветку поиска у всех слов."""
        if not self.content:
            return
        for paragraph in self.content:
            for sentence in paragraph.get_components():
                for word in sentence.get_components():
                    word.set_back_color(None)

    def view_text(self):
        """Отображает документ в консоли с учетом цветов текста и фона."""
        print("\n--- ОТОБРАЖЕНИЕ ДОКУМЕНТА ---")
        if not self.content:
            print("[Пустой документ]")
            return

        for paragraph in self.content:
            visual_line = []
            for sentence in paragraph.get_components():
                for word in sentence.get_components():
                    prefix = ""
                    suffix = "\033[0m"

                    if word.back_color == "orange":
                        prefix += "\033[43m"
                    elif word.back_color == "red":
                        prefix += "\033[41m"

                    if word.color == "blue":
                        prefix += "\033[34m"
                    elif word.color == "green":
                        prefix += "\033[32m"

                    visual_line.append(f"{prefix}{word.gettext()}{suffix}")

            print(" ".join(visual_line))
            print("")
        print("------------------------------\n")


# ============================================================
#                         EXPORT
# ============================================================

class IExportStrategy(abc.ABC):
    """Интерфейс для стратегий экспорта."""

    @abc.abstractmethod
    def export(self, doc: Document, path: str):
        pass


class PdfExportStrategy(IExportStrategy):
    """Стратегия экспорта в PDF."""

    def export(self, doc: Document, path: str):
        print(f"✅ Экспорт в PDF завершен. Имитация создания файла: {path}")


class JsonExportStrategy(IExportStrategy):
    """Стратегия экспорта в JSON."""

    def export(self, doc: Document, path: str):
        data = {
            "document": doc.name,
            "content": []
        }
        for p_idx, para in enumerate(doc.get_components()):
            para_data = {"paragraph_id": p_idx, "sentences": []}
            for s_idx, sent in enumerate(para.get_components()):
                sent_data = {"sentence_id": s_idx, "words": []}
                for word in sent.get_components():
                    sent_data["words"].append({
                        "text": word.gettext(),
                        "color": word.color,
                        "back_color": word.back_color
                    })
                para_data["sentences"].append(sent_data)
            data["content"].append(para_data)

        print(f"✅ Экспорт в JSON завершен. Имитация создания файла: {path}")


class ExportStrategyFabric:
    """Фабрика для создания стратегий экспорта."""

    def create_strategy(self, format_str: str) -> IExportStrategy:
        fmt = format_str.lower()
        if fmt == "pdf":
            return PdfExportStrategy()
        elif fmt == "json":
            return JsonExportStrategy()
        else:
            raise ValueError(f"Неизвестный формат: {format_str}")


class ExportManager:
    """Менеджер экспорта документов."""

    def export(self, strategy: IExportStrategy, doc: Document):
        ext = "txt"
        if isinstance(strategy, PdfExportStrategy):
            ext = "pdf"
        elif isinstance(strategy, JsonExportStrategy):
            ext = "json"

        full_path = f"{doc.name}_export.{ext}"
        strategy.export(doc, full_path)


# ============================================================
#                         PRINT (заглушки)
# ============================================================
class PrintSettings:
    def __init__(self, printer_name: str, copies: int = 1, page_range: str = "all", duplex: bool = False, orientation: str = "portrait"):
        self.printer_name = printer_name
        self.copies = copies
        self.page_range = page_range
        self.duplex = duplex
        self.orientation = orientation
        print(f"[PrintSettings] Настройки: принтер={printer_name}, копий={copies}, страницы={page_range}")
        
class Printer:
    def send_to_print(self, document, settings):
        """Имитация печати"""
        print(f"[Printer] Отправка на печать: '{document.name}' → {settings.printer_name}")
        print(f"[Printer] Параметры: {settings.copies} копий, дуплекс={settings.duplex}, ориентация={settings.orientation}")
        print("[Printer] ✅ Документ успешно отправлен на печать!")

class PrintPreview:
    """Предпросмотр печати."""

    def generate_preview(self, doc: Document, settings: dict):
        print(f"📄 Предпросмотр документа: {doc.name}")
        doc.view_text()

class PrintManager:
    def show_preview(self, document):
        return PrintPreview().generate_preview(document)

    def print_document(self, document, settings):
        Printer().send_to_print(document, settings)



class PrintManager:
    """Менеджер печати."""

    def __init__(self):
        self.preview = PrintPreview()

    def print(self, doc: Document, printer_name: str, copies: int):
        print(f"🖨️ Печать документа '{doc.name}' на принтере '{printer_name}' ({copies} копий)")

    def show_preview(self, doc: Document, settings: dict):
        self.preview.generate_preview(doc, settings)
    def print_document(self, document, settings):
        Printer().send_to_print(document, settings)
        


# ============================================================
#                         CONTROLLER
# ============================================================

class Editor:
    """Класс-контроллер для управления документом."""

    def __init__(self):
        self.document: Document = None
        self.export_fabric = ExportStrategyFabric()
        self.export_manager = ExportManager()
        self.print_manager = PrintManager()

    def new_document(self, name: str, path: str):
        """Создает новый документ."""
        self.document = Document(name, path)

    def insert_text(self, text: str):
        """Вставляет текст в текущий документ."""
        if self.document:
            self.document.insert_text(text)
        else:
            print("Ошибка: Документ не создан.")

    def get_content(self):
        """Очищает результаты поиска и отображает документ."""
        if self.document:
            self.document.clear_search_results()
            self.document.view_text()

    def search_text(self, query: str, is_case_sensitive: bool = False, is_whole_word: bool = False):
        """Выполняет поиск текста и обновляет отображение с подсветкой."""
        if not self.document:
            print("Ошибка: Документ не создан.")
            return

        search_highlighter = HighlightStrategyFactory.create_strategy('search', query=query, is_case_sensitive=is_case_sensitive, is_whole_word=is_whole_word)
        self.document.highlight(search_highlighter)
        self.document.view_text()

    def apply_highlight(self, strategy: IHighlightStrategy):
        """Применяет произвольный visitor к документу."""
        if not self.document:
            print("Ошибка: Документ не создан.")
            return

        self.document.highlight(strategy)
        self.document.view_text()

    def export(self, format_str: str):
        """Экспортирует документ в указанный формат."""
        if not self.document:
            print("Ошибка: Нет документа.")
            return

        try:
            strategy = self.export_fabric.create_strategy(format_str)
            self.export_manager.export(strategy, self.document)
        except ValueError as e:
            print(f"Ошибка: {e}")

    def print_document(self, printer_name: str, copies: int = 1):
        """Печатает документ."""
        if not self.document:
            print("Ошибка: Нет документа.")
            return

        self.print_manager.print(self.document, printer_name, copies)


# ============================================================
#                         MAIN
# ============================================================

if __name__ == "__main__":
    session = Editor()

    highlighter_factory = HighlightStrategyFactory()
    python_strategy = highlighter_factory.create_strategy(
        strategy_name="Python Definition", keywords=['class', 'def'], color="green")
    highlighter_factory.add_strategy(python_strategy)

    print("Текстовый редактор запущен.")

    while True:
        print("\n" + "═" * 30)
        print("       ПАНЕЛЬ УПРАВЛЕНИЯ")
        print("═" * 30)

        print("1 - [Создать] новый документ")
        print("2 - [Вставить] текст")
        print("3 - [Найти] и подсветить")
        print("4 - [Показать] содержимое")
        print("5 - Применить стратегию подсветки")
        print("6 - Экспорт (PDF/JSON)")
        print("7 - Печать документа")
        print("0 - [Выход]")
        print("-" * 30)

        command = input("Ваш выбор > ")
        print()

        if command == "1":
            name = input("Название: ")
            path = input("Расширение: ")
            session.new_document(name, path)
            print(f"✅ Документ {name}.{path} создан.")

        elif command == "2":
            text = input("Введите текст: ")
            session.insert_text(text)
            print("✅ Текст добавлен.")

        elif command == "3":
            query = input("Поисковый запрос: ")
            case = input("Учитывать регистр? (y/n): ").lower() == "y"
            whole = input("Только слово целиком? (y/n): ").lower() == "y"
            session.search_text(query, case, whole)

        elif command == "4":
            session.get_content()

        elif command == "5":
            highlighter_factory.show_strategies()
            try:
                idx = int(input("Ваш выбор > "))
                if highlighter_factory.select_strategy(idx):
                    session.apply_highlight(highlighter_factory)
            except ValueError:
                print("Ошибка ввода.")

        elif command == "6":
            fmt = input("Формат (pdf/json): ")
            session.export(fmt)

        elif command == "7":
            printer = input("Имя принтера: ")
            try:
                copies = int(input("Количество копий: "))
                session.print_document(printer, copies)
            except ValueError:
                print("Ошибка: введите число.")

        elif command == "0":
            print("Выход.")
            break

        else:
            print("❌ Неверная команда.")
