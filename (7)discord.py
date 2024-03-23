import csv
import matplotlib.pyplot as plt
import tempfile
import os
from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed

class Discord:
    """Discord Webhooks for sending market signals based on a CSV file."""
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.sent_symbols_file = "sent_symbols.txt"

    def have_sent_today(self, symbol):
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            with open(self.sent_symbols_file, "r") as file:
                for line in file:
                    sent_date, sent_symbol = line.strip().split(",")
                    if sent_date == today and sent_symbol == symbol:
                        return True
        except FileNotFoundError:
            pass
        return False

    def mark_as_sent(self, symbol):
        today = datetime.now().strftime("%Y-%m-%d")
        with open(self.sent_symbols_file, "a") as file:
            file.write(f"{today},{symbol}\n")

    def send_message_with_image(self, message, image_path):
        webhook = DiscordWebhook(url=self.webhook_url)
        with open(image_path, "rb") as f:
            webhook.add_file(file=f.read(), filename=os.path.basename(image_path))
        embed = DiscordEmbed(title="Market Signal", description=message, color=242424)
        webhook.add_embed(embed)
        try:
            response = webhook.execute()
            if response:
                print("Response status:", response.status_code)
                print("Response body:", response.content)
            else:
                print("No response from Discord API")
        except Exception as e:
            print("Failed to send message to Discord:", e)

    def create_and_send_gauge(self, label, signal):
        if not self.have_sent_today(label):
            message, image_path = self.create_gauge(label, signal)
            self.send_message_with_image(message, image_path)
            self.mark_as_sent(label)
            os.remove(image_path)

    def create_gauge(self, label, signal):
        fig, ax = plt.subplots()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Mapping textual signals to numeric values for visualization
        signal_strength_map = {
            'Strong Buy': 1.0,
            'Buy': 0.75,
            'Sell': 0.25,
            'Strong Sell': 0.0,
        }
        value = signal_strength_map.get(signal, 0.5)  # Default to "Neutral" as 0.5
        color = 'green' if value > 0.5 else 'red' if value < 0.5 else 'gray'
        
        ax.barh(0.5, value, height=0.1, color=color)
        ax.text(0.5, 0.5, f"{label}: {signal} ({value:.2f})", va='center', ha='center', color='white')

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        plt.savefig(temp_file.name)
        plt.close(fig)
        
        return f"{label} {signal} Signal", temp_file.name

def main():
    webhook_url = "https://discord.com/api/webhooks/1218422515676872754/KxW0LTY8yz0UzNGgtuqSM9RW53aRllLrQiUbRjcZtVqKqHocvwztKRd9lD3eXctdQecO"
    discord = Discord(webhook_url)

    try:
        with open("1d_Crypto_Monitor_List.csv", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                symbol = row['Symbol']
                signal = row.get('Signal', 'Neutral')  # Default to "Neutral"
                
                # Filter out "Neutral" signals from CSV
                if signal in ['Strong Buy', 'Buy', 'Sell', 'Strong Sell']:
                    discord.create_and_send_gauge(f"{symbol}", signal)
    except Exception as e:
        print(f"Failed to process the CSV file due to: {e}")
        return  # Stop execution if there's an issue with the CSV file

    print("Signals processed successfully.")

if __name__ == "__main__":
    main()
print("Done")