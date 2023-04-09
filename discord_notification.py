import logging
import discord
from logger import setup_logger
from config import DISCORD_TOKEN, CHANNEL_ID

logging = setup_logger(__name__)


async def send_messages(messages: list, channel_id: int = CHANNEL_ID):
    client = discord.Client(intents=discord.Intents.default())
    try:
        await client.login(DISCORD_TOKEN)
        channel = await client.fetch_channel(channel_id)
        for message in messages:
            await channel.send(message)
        logging.info(f"Messages sent to Discord channel {channel_id}")
    except Exception as e:
        logging.error(
            f"Error sending messages to Discord channel {channel_id}: {e}")
    finally:
        await client.close()
