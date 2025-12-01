using System;
using System.IO;
using Windows.Data.Xml.Dom;
using Windows.UI.Notifications;

namespace Notifier
{
    class Program
    {
        static void Main(string[] args)
        {
            try
            {
                if (args.Length < 2)
                {
                    Console.Error.WriteLine("Usage: notify.exe <title> <message>");
                    return;
                }

                string title = args[0];
                string message = args[1];

                var toastXml = ToastNotificationManager.GetTemplateContent(ToastTemplateType.ToastText02);
                var textNodes = toastXml.GetElementsByTagName("text");
                textNodes[0].AppendChild(toastXml.CreateTextNode(title));
                textNodes[1].AppendChild(toastXml.CreateTextNode(message));

                var toast = new ToastNotification(toastXml);
                var notifier = ToastNotificationManager.CreateToastNotifier("GoogleCalendarSync");
                notifier.Show(toast);
            }
            catch (Exception ex)
            {
                LogError(ex);
            }
        }

        private static void LogError(Exception ex)
        {
            try
            {
                string exeDir = AppContext.BaseDirectory;
                string logPath = Path.Combine(exeDir, "errors.log");

                File.AppendAllText(
                    logPath,
                    $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] {ex.Message}\n{ex.StackTrace}\n\n"
                );
            }
            catch
            {
                // If logging fails, do nothing to avoid recursive failure loops.
            }
        }
    }
}
