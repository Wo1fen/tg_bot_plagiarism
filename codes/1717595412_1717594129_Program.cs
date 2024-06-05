
using System;
using System.Collections.Generic;


namespace DesignPatterns
{

    // Одиночка паттерн
    public class Books
    {
        private static Books instance;
        private List<Book> books;

        private Books()
        {
            books = new List<Book>();
        }

        public static Books Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = new Books();
                }
                return instance;
            }
        }

        public void Add(Book book)
        {
            books.Add(book);
        }

        public Book FindKniga(string title)
        {
            foreach (var book in books)
            {
                if (book.Title.Equals(title, StringComparison.OrdinalIgnoreCase))
                {
                    return book;
                }
            }
            return null;
        }
    }

    // Фабричный паттерн
    public abstract class Book
    {
        public string Title { get; protected set; }
    }

    public class Hudozhka : Book
    {
        public Hudozhka(string title)
        {
            Title = title;
        }
    }

    public class NeHudozka : Book
    {
        public NeHudozka(string title)
        {

            Title = title;
        }

    }


    class Program
    {
        public static void Napisat(string message)
        {
            Console.WriteLine(message);
        }
        static void Main(string[] args)


        {

            Console.ForegroundColor = ConsoleColor.Green;
            Console.BackgroundColor = ConsoleColor.Black;



            Books.Instance.Add(new Hudozhka("Mazambik"));
            Books.Instance.Add(new NeHudozka("Pushkin"));
            Books.Instance.Add(new Hudozhka("Dazik"));





            while (true)
            {
                Napisat("Введите название книги для поиска (чтобы выйти напиши exit):");
                string searchQuery = Console.ReadLine();

                switch (searchQuery.ToLower())
                {
                    case "exit":
                        Napisat("Выход из программы");
                        return;
                    case "HamitovChampion":
                        Napisat("ПАСХАЛКА");
                        return;


                    default:
                        Book bookFound = Books.Instance.FindKniga(searchQuery);
                        if (bookFound == null)
                        {
                            Napisat($"Книги с названия '{searchQuery}' нет в библиотеке");
                        }
                        else
                        {
                            Napisat($"Книга с названия '{searchQuery}' найдена");
                        }
                        break;

                }
            }
        }
    }
}