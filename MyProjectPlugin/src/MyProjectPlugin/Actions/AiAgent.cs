namespace Loupedeck.MyProjectPlugin
{
    using System;
    using System.Net.Http;

    public class AiCommand : PluginDynamicCommand
    {
        // Initializes the command class.
        private const Int32 NumberOfSwitches = 8;
        private readonly Boolean[] _switches = new Boolean[NumberOfSwitches + 1];

        public AiCommand()
            : base()
        {
            for (var i = 1; i <= NumberOfSwitches; i++)
            {
                // parameter is the switch index
                var actionParameter = i.ToString();

                // add parameter
                this.AddParameter(actionParameter, $"AI Agent {i}", "AI Agent");
            }
        }

        // This method is called when the user executes the command.
        protected override void RunCommand(String actionParameter)
        {
            // Replace with your agent ID
            var agentId = actionParameter;
            var url = $"http://127.0.0.1:5000/api/console/{agentId}";

            if (Int32.TryParse(actionParameter, out var i))
            {
                // Turn the switch
                this._switches[i] = !this._switches[i];

                // Inform Loupedeck that command display name and/or image has changed
                this.ActionImageChanged();
            }

            using (var client = new HttpClient())
            {
                try
                {
                    HttpResponseMessage response = client.GetAsync(url).GetAwaiter().GetResult();

                    if (response.IsSuccessStatusCode)
                    {
                        var responseBody = response.Content.ReadAsStringAsync().GetAwaiter().GetResult();
                        Console.WriteLine("Server Response: " + responseBody);
                    }
                    else
                    {
                        Console.WriteLine($"Error: {response.StatusCode} - {response.ReasonPhrase}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine("Exception: " + ex.Message);
                }
            }

        }

        protected override BitmapImage GetCommandImage(String actionParameter, PluginImageSize imageSize) 
        {
            return Int32.TryParse(actionParameter, out var i)
                ? this._switches[i]
                    ? EmbeddedResources.ReadImage(EmbeddedResources.FindFile($"{i}-{i}.png"))
                    : EmbeddedResources.ReadImage(EmbeddedResources.FindFile($"{i}.png"))
                : null;
        }
    }
}