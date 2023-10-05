import settings
import discord
from discord.ext import commands
import random

playerPool = []
team1 = []
team2 = []
vc_list = []
team1vc = "team1"
team2vc = "team2"

class CreateTeamsView(discord.ui.View):

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def on_timeout(self) -> None:
        #await self.message.channel.send("Timedout")
        await self.disable_all_items()

    @discord.ui.button(label="join",
                       style=discord.ButtonStyle.success)
    async def join(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.send_message(f"{interaction.user} just joined the player pool!")
        playerPool.append(interaction.user)

    @discord.ui.button(label="cancel",
                       style=discord.ButtonStyle.red)
    async def cancel(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.send_message("Cancelling")
        playerPool.clear()
        team1.clear()
        team2.clear()
        await self.disable_all_items()

def run():
    intents = discord.Intents.all()
    intents.members = True
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(bot.user)
        print(bot.user.id)
    
    @bot.command()
    async def randomteams(ctx):
        global team1, team2
        await ctx.send(f"15 seconds to join pool!")
        view = CreateTeamsView(timeout=5)

        message = await ctx.send(view=view)
        view.message = message

        await view.wait()
        await view.disable_all_items()

        random.shuffle(playerPool)
        split = len(playerPool) // 2

        team1 = playerPool[:split]
        team2 = playerPool[split:]
        if len(team1) != 0 or len(team2) !=0:
            for player in team1:
                await ctx.send(f"TEAM1: {player.name}")
            for player in team2:
                await ctx.send(f"TEAM2: {player.name}")
        else:
            await ctx.send("No one joined pool")

    @bot.command()
    async def clearteams(ctx):
        playerPool.clear()
        team1.clear()
        team2.clear()
        await ctx.send("teams cleared")

    @bot.command()
    async def moveteams(ctx):
        await ctx.send("moving teams...")
        for guild in bot.guilds:
            for vc in guild.voice_channels:
                vc_list.append(vc)
        for i, vc in enumerate(vc_list):
            if vc.name == "team1":
                team1vc = i
                await ctx.send("team1 vc found")
            if vc.name == "team2":
                team2vc = i
                await ctx.send("team2 vc found")
        vc1 = vc_list[team1vc]
        vc2 = vc_list[team2vc]
        
        for player in team1:
            try:
                await player.move_to(vc1)
            except:
                await ctx.send(f"{player} missing from voice channel")
        for player in team2:
            try:
                await player.move_to(vc2)
            except:
                await ctx.send(f"{player} missing from voice channel")
        vc_list.clear()
    
    @bot.command()
    async def teams(ctx):
        global team1
        global team2
        if len(team1) != 0 or len(team2) != 0:
            for player in team1:
                await ctx.send(f"TEAM1: {player.name}")
            for player in team2:
                await ctx.send(f"TEAM2: {player.name}")
        else:  
            await ctx.send("Teams are currently empty")

    bot.run(settings.API_TOKEN)

if __name__ == "__main__":
    run()