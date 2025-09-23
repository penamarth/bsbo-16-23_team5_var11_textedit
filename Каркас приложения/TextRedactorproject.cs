using System;

public class File
{
    private string _path;
    private string _extension;

    public File()
    {
        _path = null;
        _extension = null;
    }

    public void SetFile(string path, string extension)
    {
        _path = path;
        _extension = extension;
    }

    public string GetFilePath()
    {
        if (_path == null || _extension == null)
        {
            return null;
        }
        return _path + _extension;
    }
}

public class OpeningFile : File
{
    private bool _open;
    public string Text { get; set; }

    public OpeningFile()
    {
        _open = false;
        Text = "";
    }

    public void OpenFile()
    {
        _open = true;
        Console.WriteLine($"Файл {GetFilePath()} открыт");
    }

    public bool GetStatusOpen()
    {
        return _open;
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

public class FormattingStyles : OpeningFile
{
    private int _fontSize;
    private string _fontStyle;

    public FormattingStyles()
    {
        _fontSize = 14;
        _fontStyle = "TimesNewRoman";
    }

    public void SetSize(int fontSize)
    {
        if (GetStatusOpen())
        {
            _fontSize = fontSize;
            Console.WriteLine($"Размер шрифта установлен: {_fontSize}");
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
            _fontStyle = fontStyle;
            Console.WriteLine($"Стиль шрифта установлен: {_fontStyle}");
        }
        else
        {
            Console.WriteLine("Ошибка: файл не открыт");
        }
    }
}

public class AdditionalTools : OpeningFile
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

public class Printer : OpeningFile
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

public class SavingFile : EditingFile
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