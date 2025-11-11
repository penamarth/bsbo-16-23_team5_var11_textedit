### Диаграмма последовательности для поиска по тексту

```mermaid
sequenceDiagram
    actor User
    participant Editor
    participant SearchHighliter
    participant ViewText

    User->>Editor: searchText("data", wholeWord=true, caseSensitive=false, regex=false)

    Editor->>SearchHighliter: highlight(document, wholeWord=true, caseSensitive=false, regex=false)

    Editor->>ViewText: draw()
    ViewText-->>User: обновлённый вид с подсветкой

    alt Нет совпадений
        Editor->>ViewText: draw()
        ViewText-->>User: текст без подсветки (0 совпадений)
    end
```