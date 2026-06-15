"""
integrations/template_platform/bot.py
───────────────────────────────────────────
Template platform bot implementation.

This template demonstrates how to create a custom platform bot by
inheriting from BasePlatformBot (defined in integrations.base).
BasePlatformBot provides a basic structure but leaves the run method
abstract.

You must implement the run method to start your platform's messaging
loop and process incoming messages using the provided MessageProcessor.

For a real platform, you would:
- Set up a connection to the platform's API (e.g., using websockets, polling).
- Listen for incoming messages.
- For each message, call processor.process(message) to get a reply.
- Send the reply back to the user on the platform.

This template provides a simple example that runs a loop and prints
a message, simulating a bot that is ready to receive messages.
"""

import time
from integrations.base import BasePlatformBot
from core.processor import MessageProcessor


class TemplatePlatformBot(BasePlatformBot):
    """
    A template platform bot that inherits from BasePlatformBot.

    BasePlatformBot requires you to implement the run method.
    This template implementation does not actually connect to any
    platform; it simply prints a message and sleeps in a loop.
    Replace this with your platform-specific logic.
    """

    def __init__(self, token: str, processor: MessageProcessor):
        """
        Initialize the template platform bot.

        Args:
            token: Authentication token for the platform.
            processor: MessageProcessor instance to process incoming messages.
        """
        self.token = token
        self.processor = processor
        self._running = False

    def run(self) -> None:
        """
        Start the bot and block until stopped.

        This template implementation prints a status message and then
        enters a loop that sleeps, simulating a bot that is running.
        In a real implementation, you would:
        - Connect to the platform's API.
        - Listen for incoming messages.
        - For each message, call self.processor.process(message) to get a reply.
        - Send the reply back to the user.

        To stop the bot, you would typically set a flag (e.g., self._running)
        to False and break out of the loop.
        """
        self._running = True
        print(f"[Template Platform] Bot started with token: {self.token[:10]}...")
        print("[Template Platform] Replace this with your platform-specific logic.")
        print("[Template Platform] To stop the bot, interrupt the process (Ctrl+C).")

        try:
            while self._running:
                # Simulate doing work (e.g., checking for new messages)
                time.sleep(1)
                # In a real bot, you would process incoming messages here.
                # For example:
                #   updates = self.platform.get_new_updates()
                #   for update in updates:
                #       reply = self.processor.process(update.message)
                #       self.platform.send_reply(update.chat.id, reply)
        except KeyboardInterrupt:
            print("[Template Platform] Received interrupt, stopping...")
        finally:
            self._running = False
            print("[Template Platform] Bot stopped.")


__all__ = ["TemplatePlatformBot"]