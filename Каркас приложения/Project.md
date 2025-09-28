using System;

public class File
{
    private string path;
    private string extension;

    public File()
    {
        path = null;
        extension = null;
    }

    public void SetFile(string path, string extension)
    {
        this.path = path;
        this.extension = extension;
    }

    public string GetFilePath()
    {
        if (path == null || extension == null)
        {
            return null;
        }
        return path + extension;
    }
}

public class OpeningFile : File
{
    private bool open;
    public string Text { get; set; }

    public OpeningFile()
    {
        open = false;
        Text = "";
    }

    public void OpenFile()
    {
        open = true;
        Console.WriteLine($"Файл {GetFilePath()} открыт");
    }

    public bool GetStatusOpen()
    {
        return open;
    }
}

public class EditingFile : OpeningFile
{
    public string CopyText { get; set; }

    public EditingFile()
    {
        CopyText = "";
    }

    public void Input(string text)
    {
        if (GetStatusOpen())
        {
            Text += text;
            Console.WriteLine($"Добавлен текст: {text}");
        }
        else
        {
            Console.WriteLine("Файл не открыт");
        }
    }

    public void Copy(string text)
    {
        if (GetStatusOpen())
        {
            CopyText = text;
            Console.WriteLine($"Скопирован текст: {text}");
        }
        else
        {
            Console.WriteLine("Файл не открыт");
        }
    }

    public void Paste()
    {
        if (GetStatusOpen())
        {
            Input(CopyText);
        }
        else
        {
            Console.WriteLine("Файл не открыт");
        }
    }
}

public class FormattingStyles : EditingFile
{
    private int fontSize;
    private string fontStyle;

    public FormattingStyles()
    {
        fontSize = 14;
        fontStyle = "TimesNewRoman";
    }

    public void SetSize(int fontSize)
    {
        if (GetStatusOpen())
        {
            this.fontSize = fontSize;
            Console.WriteLine($"Размер шрифта установлен: {fontSize}");
        }
        else
        {
            Console.WriteLine("Ошибка: файл не открыт");
        }
    }

    public void SetStyle(string fontStyle)
    {
        if (GetStatusOpen())
        {
            this.fontStyle = fontStyle;
            Console.WriteLine($"Стиль шрифта установлен: {fontStyle}");
        }
        else
        {
            Console.WriteLine("Ошибка: файл не открыт");
        }
    }
}

public class AdditionalTools : FormattingStyles
{
    public string SearchText(string text)
    {
        if (GetStatusOpen())
        {
            if (Text.Contains(text))
            {
                return $"Текст '{text}' найден";
            }
            return $"Текст '{text}' не найден";
        }
        else
        {
            Console.WriteLine("Ошибка: файл не открыт");
            return null;
        }
    }

    public void CountCharacters()
    {
        if (GetStatusOpen())
        {
            Console.WriteLine($"Размер файла: {Text.Length} символов");
        }
        else
        {
            Console.WriteLine("Ошибка: файл не открыт");
        }
    }
}

public class Printer : AdditionalTools
{
    public void PrintDocument()
    {
        if (GetStatusOpen())
        {
            Console.WriteLine($"Документ {GetFilePath()} напечатан");
        }
        else
        {
            Console.WriteLine("Ошибка: файл не открыт");
        }
    }
}

public class SavingFile : Printer
{
    public void SaveFile()
    {
        if (GetStatusOpen())
        {
            Console.WriteLine($"Файл {GetFilePath()} сохранён");
            Console.WriteLine($"Текст файла: {Text}");
        }
        else
        {
            Console.WriteLine("Ошибка: файл не открыт");
        }
    }
}

class Program
{
    static void Main(string[] args)
    {
        SavingFile editor = new SavingFile();
        editor.SetFile("документ", ".txt");
        editor.OpenFile();
        editor.Input("Привет");
        editor.Copy(", Мир!");
        editor.CountCharacters();
        editor.Paste();
        editor.CountCharacters();
        editor.SetSize(14);
        editor.SetStyle("Arial");
        editor.PrintDocument();
        editor.SaveFile();
    }
}