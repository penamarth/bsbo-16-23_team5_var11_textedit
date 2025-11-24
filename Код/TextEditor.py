import abc
import re


class IComponent(abc.ABC):
    """Интерфейс для всех компонентов документа (Composite pattern)."""

    @abc.abstractmethod
    def gettext(self):
        """Возвращает текстовое содержимое компонента."""
        pass
    
    @abc.abstractmethod
    def highlight(self, visitor): pass


class IHighlighter(abc.ABC):
    """Интерфейс для стратегий подсветки текста."""

    @abc.abstractmethod
    def highlight(self, document):
        """Применяет подсветку к переданному документу."""
        pass


class WordComponent(IComponent):
    """Представляет отдельное слово в документе."""

    def __init__(self, word: str):
        self.content = word
        self.color = "black"
        self.back_color = None

    def highlight(self, visitor):
        visitor.visit_leaf(self)

    def gettext(self):
        """Возвращает слово."""
        return self.content

    def set_color(self, color: str):
        """Устанавливает цвет текста (для синтаксической подсветки)."""
        self.color = color

    def set_back_color(self, color: str):
        """Устанавливает цвет фона (для результатов поиска)."""
        self.back_color = color

    def get_word(self):
        """Возвращает строковое значение слова."""
        return self.content


class SentenceComponent(IComponent):
    """Представляет предложение, состоящее из слов."""

    def __init__(self):
        self.content = []

    def add(self, text):
        """Разбивает текст на слова и добавляет их в предложение."""
        list_word = text.split()
        for word in list_word:
            self.content.append(WordComponent(word))

    def gettext(self):
        """Собирает текст предложения из слов."""
        text = [i.gettext() for i in self.content]
        return " ".join(text)

    def get_components(self):
        """Возвращает список компонентов-слов."""
        return self.content
    
    def highlight(self, visitor):
        for child in self.content:
            child.highlight(visitor)


class ParagraphComponent(IComponent):
    """Представляет абзац, состоящий из предложений."""

    def __init__(self):
        self.content = []

    def add(self, text):
        """Разбивает текст на предложения и добавляет их в абзац."""
        text = text.replace(".", ".<sen>")
        text = text.replace("!", "!<sen>")
        text = text.replace("?", "?<sen>")
        list_sentence = text.split("<sen>")
        for sentence in list_sentence:
            if sentence.strip():
                sentence_obj = SentenceComponent()
                sentence_obj.add(sentence.strip())
                self.content.append(sentence_obj)

    def gettext(self):
        """Собирает текст абзаца из предложений."""
        text = [i.gettext() for i in self.content]
        return " ".join(text)

    def get_components(self):
        """Возвращает список компонентов-предложений."""
        return self.content

    def highlight(self, visitor):
        for child in self.content:
            child.highlight(visitor)


class Document:
    """Главный класс документа, хранящий структуру абзацев."""

    def __init__(self, file_name, path):
        self.name = file_name
        self.path = path
        self.content: list[ParagraphComponent] = []

    def insert_text(self, text):
        """Вставляет текст в документ, разбивая его на абзацы."""
        parts = text.split("<p>")
        for part in parts:
            if part.strip():
                para = ParagraphComponent()
                para.add(part)
                self.content.append(para)

    def gettext(self):
        """Возвращает полный текст документа."""
        text = [i.gettext() for i in self.content]
        return "\n".join(text)

    def get_components(self):
        """Возвращает список компонентов-абзацев."""
        return self.content

    def clear_search_results(self):
        """Сбрасывает фоновую подсветку поиска у всех слов."""
        if not self.content:
            return

        for paragraph in self.content:
            for sentence in paragraph.get_components():
                for word in sentence.get_components():
                    word.set_back_color(None)
    
    def highlight(self, visitor):
        for child in self.content:
            child.highlight(visitor)

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


class SearchHighlighter(IHighlighter):
    """Класс, реализующий логику поиска и выделения текста."""

    def __init__(
        self,
        search_query: str,
        is_case_sensitive: bool = False,
        is_whole_word: bool = False,
    ):
        self.search_query = search_query
        self.is_case_sensitive = is_case_sensitive
        self.is_whole_word = is_whole_word

    def highlight(self, document: Document):
        """Проходит по структуре документа и подсвечивает найденные совпадения."""
        target = self.search_query
        if not self.is_case_sensitive:
            target = target.lower()

        for paragraph in document.get_components():
            for sentence in paragraph.get_components():
                for word_obj in sentence.get_components():

                    word_text = word_obj.gettext()
                    clean_word = word_text.strip(".,!?;:")

                    check_text = clean_word
                    if not self.is_case_sensitive:
                        check_text = check_text.lower()

                    match_found = False

                    if self.is_whole_word:
                        if check_text == target:
                            match_found = True
                    else:
                        if target in check_text:
                            match_found = True

                    if match_found:
                        word_obj.set_back_color("orange")
                    else:
                        word_obj.set_back_color(None)


class Editor:
    """Класс-контроллер для управления документом."""

    def __init__(self):
        self.document = None

    def new_document(self, name, path):
        """Создает новый документ."""
        self.document = Document(name, path)

    def insert_text(self, text):
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

    def search_text(self, query, case_sensitive=False, whole_word=False):
        """Выполняет поиск текста и обновляет отображение с подсветкой."""
        if not self.document:
            return

        highlighter = SearchHighlighter(query, case_sensitive, whole_word)
        highlighter.highlight(self.document)
        self.document.view_text()


class IHighlightStrategy(abc.ABC):
    COUNT: int = 0
    def __init__(self, pattern, color, pattern_name = f'Pattern_{COUNT}'):
        self.pattern_name = pattern_name
        if pattern_name.startswith('Pattern_') and pattern_name[:-1].isdigit():
            IHighlightStrategy.COUNT += 1
        self.pattern = pattern
        self.color = color

    @abc.abstractmethod
    def apply(self, leaf): pass

class HighlightStrategy(IHighlightStrategy):
    def apply(self, leaf):
        if re.search(self.pattern, leaf.content):
            leaf.color = self.color
        return leaf
        
class HighlighterVisitor:
    def __init__(self):
        self.strategies: list[HighlightStrategy] = []
        self.selected_strategy: HighlightStrategy = None

    def show_strategies(self):
        """Показать доступные стратегии подсветки"""
        for idx, strategy in enumerate(self.strategies, start=1):
            print(f"{idx}) Паттерн: {strategy.pattern_name}")
    
    def select_strategy(self, index: int):
        """Выбрать стратегию подсветки по индексу"""
        if 1 <= index <= len(self.strategies):
            self.selected_strategy = self.strategies[index-1]
        else:
            print("Ошибка: Неверный индекс стратегии.")
            return False
            
        return True
    
    def add_strategy(self, strategy):
        """Добавить стратегию подсветки"""
        self.strategies.append(strategy)

    def visit_leaf(self, leaf):
        leaf: IComponent = self.selected_strategy.apply(leaf)

if __name__ == "__main__":
    session = Editor()
    highligher_visitor = HighlighterVisitor()
    highligher_visitor.add_strategy(HighlightStrategy(r'\bdef\b', 'blue', 'Function Definition'))
    highligher_visitor.add_strategy(HighlightStrategy(r'\bclass\b', 'green', 'Class Definition'))

    print("Текстовый редактор запущен.")

    while True:
        print("\n" + "═" * 30)
        print("       ПАНЕЛЬ УПРАВЛЕНИЯ")
        print("═" * 30)

        print("1 - [Создать] новый документ")
        print("2 - [Вставить] текст")
        print("3 - [Найти] и подсветить")
        print("4 - [Показать] содержимое")
        print('5 - Применить стратегию подсветки')
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
            highligher_visitor.show_strategies()
            idx = int(input("Ваш выбор > "))
            if highligher_visitor.select_strategy(idx):
                session.document.highlight(highligher_visitor)
                session.get_content()


        elif command == "0":
            print("Выход.")
            break
        else:
            print("❌ Неверная команда.")
