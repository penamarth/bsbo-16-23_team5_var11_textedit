@startuml
class Context {
    +composite_text : TextComposite
    -highligher : ISyntaxHighlighter
    +void setHighlighter(highlighter : ISyntaxHighlighter)
    +render(raw_text : String)
}



interface ISyntaxHighlighter {
    +TextComposite highlight(raw_text : String)
}
class BadWordHighligher {
    TextComposite highlight(raw_text : String)
}
BadWordHighligher ..> ISyntaxHighlighter
Context --> ISyntaxHighlighter


interface ITextComponent{
    +void display()
}
class TextLeaf{
    +color : String
    +void display()
}
class TextComposite{
    -childrens: ITextComponent[]
    +void add(children: ITextComponent)
    +void display()
}
ITextComponent<..TextLeaf
ITextComponent<..TextComposite
TextComposite o-- ITextComponent

BadWordHighligher --> TextComposite
Context --> ITextComponent

@enduml

