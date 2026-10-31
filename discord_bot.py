import discord
from discord.ext import commands
import os
import json
from datetime import datetime

# Load configuration
with open('discord_config.json', 'r') as f:
    config = json.load(f)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    """
    Called when the bot is ready
    """
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    print(f'Bot is watching {len(bot.users)} user(s)')
    
    # Sync slash commands
    await bot.tree.sync()
    

@bot.slash_command(description="Get information about the GitHub integration")
async def github_info(ctx):
    """
    Slash command to get information about the GitHub integration
    """
    embed = discord.Embed(
        title="GitHub Integration Info",
        description="This bot connects GitHub activity to Discord",
        color=0x181717  # GitHub's black color
    )
    embed.add_field(
        name="Connected Repositories", 
        value=f"Monitoring: {config.get('repositories', ['Not configured'])}", 
        inline=False
    )
    embed.add_field(
        name="Activity Channels", 
        value=f"Commits: #{config['channels']['activity_log']}", 
        inline=True
    )
    embed.add_field(
        name="Feedback Channel", 
        value=f"#{config['channels']['feedback']}", 
        inline=True
    )
    embed.timestamp = datetime.utcnow()
    
    await ctx.respond(embed=embed)


@bot.slash_command(description="Get latest GitHub activity")
async def github_activity(ctx):
    """
    Slash command to get latest GitHub activity
    """
    # This would typically fetch from a database or cache of recent activity
    # For now, we'll just send a message indicating where to find activity
    embed = discord.Embed(
        title="Recent GitHub Activity",
        description="Check the following channels for GitHub activity:",
        color=0x181717
    )
    
    for event_type, webhook_config in config['webhooks'].items():
        embed.add_field(
            name=event_type.title(),
            value=f"<#{webhook_config.get('channel_id', 'Channel ID not set')}>",
            inline=True
        )
    
    embed.set_footer(text="GitHub-Discord Integration")
    embed.timestamp = datetime.utcnow()
    
    await ctx.respond(embed=embed)


@bot.slash_command(description="Submit feedback about the GitHub project")
async def feedback(ctx, message: str):
    """
    Slash command to submit feedback that gets posted to GitHub
    """
    # Get the feedback channel
    feedback_channel_name = config['channels']['feedback']
    feedback_channel = discord.utils.get(ctx.guild.channels, name=feedback_channel_name)
    
    if feedback_channel:
        embed = discord.Embed(
            title="New Feedback Submitted",
            description=message,
            color=0x0096cf  # Discord brand color
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.timestamp = datetime.utcnow()
        
        await feedback_channel.send(embed=embed)
        await ctx.respond("Thank you for your feedback! It has been posted in the feedback channel.", ephemeral=True)
    else:
        await ctx.respond("Feedback channel not found. Please contact an admin.", ephemeral=True)


@bot.event
async def on_message(message):
    """
    Handle regular messages (not slash commands)
    """
    # Don't respond to the bot's own messages
    if message.author == bot.user:
        return
    
    # Check if the message contains GitHub-related keywords
    content_lower = message.content.lower()
    
    if 'github' in content_lower and ('repo' in content_lower or 'repository' in content_lower):
        embed = discord.Embed(
            title="GitHub Repository Information",
            description="Check out our GitHub repository for the Hackathon Completion Engine!",
            color=0x181717
        )
        embed.add_field(
            name="Repository Link",
            value="[Hackathon Completion Engine](https://github.com/your-repo-link)",
            inline=False
        )
        embed.add_field(
            name="Contribute",
            value="Feel free to fork, star, and contribute to the project!",
            inline=False
        )
        embed.set_footer(text="GitHub-Discord Integration")
        embed.timestamp = datetime.utcnow()
        
        await message.channel.send(embed=embed)
    
    # Process commands
    await bot.process_commands(message)


def run_bot():
    """
    Run the Discord bot
    """
    token = config.get('bot_token')
    if not token:
        raise ValueError("Discord bot token not found in config")
    
    bot.run(token)


if __name__ == "__main__":
    run_bot()