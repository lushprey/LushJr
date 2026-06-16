"""
integrations/my_platform/bot.py
────────────────────────────────
Custom messaging platform bot implementation.

This template shows how to create a bot for any messaging platform:
- Discord, Slack, WhatsApp, Matrix, Mattermost, etc.
- Web-based chat UI
- Terminal/CLI interface
- Custom protocols

Key responsibilities:
1. Initialize connection to your platform
2. Implement run() to start the bot and listen for messages
3. For each incoming message, call processor.process(text)
4. Send the reply back to the user

To use:
1. Copy to integrations/my_platform/
2. Implement platform-specific connection logic
3. Implement the message loop in run()
4. Handle chunking if your platform has message size limits
"""

import logging
from core.processor import MessageProcessor
from integrations.base import BasePlatformBot

logger = logging.getLogger(__name__)


class MyPlatformBot(BasePlatformBot):
    """
    Bot implementation for [YOUR_PLATFORM_NAME].

    Parameters
    ----------
    token : str
        Authentication token for the platform
    processor : MessageProcessor
        Central message processor (AI + tools)
    other_config : str, optional
        Add whatever configuration your platform needs
    """

    def __init__(self, token: str, processor: MessageProcessor, **kwargs) -> None:
        super().__init__(processor=processor)

        self.token = token
        # TODO: Add any other configuration parameters your platform needs
        # Examples:
        #   self.workspace_id = workspace_id
        #   self.api_base = api_base
        #   self.channel_id = channel_id

        self._running = False
        self._client = None

        logger.info(f"Initialized {self.__class__.__name__} bot")

    # ──────────────────────────────────────────────────────────────────────
    # PlatformBot interface (REQUIRED)
    # ──────────────────────────────────────────────────────────────────────

    def run(self) -> None:
        """
        Start the bot and block until stopped.

        This is the main entry point. Implement the message loop for your
        platform here.

        General pattern:
        1. Connect to platform API
        2. Enter a loop that:
           a. Polls or waits for new messages
           b. Calls processor.process(message_text)
           c. Sends the reply back to the user
        3. Handle disconnection/reconnection gracefully
        """
        self._running = True
        logger.info("🤖 Bot started")

        try:
            # TODO: Implement your platform's connection and message loop
            # Example pseudo-code:
            # self._client = self._connect()
            # while self._running:
            #     updates = self._client.get_updates()
            #     for update in updates:
            #         user_message = update.message.text
            #         user_id = update.user.id
            #         try:
            #             reply = self.processor.process(user_message)
            #         except Exception as e:
            #             reply = f"Error: {e}"
            #         self._send_reply(user_id, reply)
            #     time.sleep(0.1)  # Prevent busy-waiting

            # For this template, we'll raise an error to indicate not implemented
            raise NotImplementedError(
                "Implement run() for your specific platform. "
                "See docstring for pattern."
            )

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.exception("Fatal error in bot loop")
            raise
        finally:
            self._running = False
            self._disconnect()
            logger.info("Bot stopped")

    # ──────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────

    def _connect(self) -> "PlatformClient":
        """
        Establish connection to the platform.

        Returns the client object you'll use in run().

        TODO: Implement for your platform.
        """
        # Example:
        # import httpx
        # return httpx.AsyncClient(
        #     base_url="https://api.platform.com",
        #     headers={"Authorization": f"Bearer {self.token}"}
        # )

        raise NotImplementedError("Implement _connect() for your platform")

    def _disconnect(self) -> None:
        """
        Clean up resources and disconnect from the platform.

        TODO: Implement if needed for your platform.
        """
        # Example:
        # if self._client:
        #     self._client.close()

        pass

    def _send_reply(self, user_id: str, message: str) -> None:
        """
        Send a reply message to a specific user.

        Most platforms have message size limits — this method should
        handle chunking automatically.

        Args:
            user_id: Platform-specific user identifier
            message: Reply text (may be long)

        TODO: Implement for your platform.
        """
        # Example with chunking (Telegram max is 4096 chars):
        # MAX_LENGTH = 4096
        # for i in range(0, len(message), MAX_LENGTH):
        #     chunk = message[i : i + MAX_LENGTH]
        #     self._client.send_message(user_id, chunk)

        raise NotImplementedError("Implement _send_reply() for your platform")

    # ──────────────────────────────────────────────────────────────────────
    # Optional: Add platform-specific methods as needed
    # ──────────────────────────────────────────────────────────────────────

    def stop(self) -> None:
        """Stop the bot gracefully."""
        self._running = False
        logger.info("Stop signal sent to bot")


__all__ = ["MyPlatformBot"]