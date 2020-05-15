import discord
from discord.ext import commands

prefix = '!'  # change this to whatever prefix you'd like

bot = commands.Bot(command_prefix=prefix)

# add roles that can use some commands
approved_roles = ['reviewer', 'Admin', 'Bot', 'Mod']

def is_approved():
    def predicate(ctx):
        author = ctx.message.author
        if author is ctx.message.guild.owner:
            return True
        if any(role.name in approved_roles for role in author.roles):
            return True
    return commands.check(predicate)


@bot.event
async def on_ready():
    print(bot.user.name)
    print(bot.user.id)

@bot.event
async def on_command_error(ctx, error):
    """The event triggered when an error is raised while invoking a command.
    ctx   : Context
    error : Exception"""

    # This prevents any commands with local handlers being handled here in on_command_error.
    if hasattr(ctx.command, 'on_error'):
        return
        
    ignored = (commands.CommandNotFound, commands.UserInputError)
        
    # Allows us to check for original exceptions raised and sent to CommandInvokeError.
    # If nothing is found. We keep the exception passed to on_command_error.
    error = getattr(error, 'original', error)
        
    # Anything in ignored will return and prevent anything happening.
    if isinstance(error, ignored):
        return

    elif isinstance(error, commands.DisabledCommand):
        return await ctx.send(f'{ctx.command} has been disabled.')

    elif isinstance(error, commands.NoPrivateMessage):
        try:
            return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        except:
            pass

class Queue(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        print("Initialising")
        self.queue = {}
        self.users = {}
        self.qtoggle = False
        print("Bot is ready")

    @commands.command(pass_context=True)
    async def add(self, ctx, arg):
        ''': Add yourself to the queue!'''
        channels = ctx.message.guild.voice_channels
        if not any(arg == chan.name for chan in channels):
            await ctx.send("Sorry, the voice channel {} doesn't exist".format(arg))
            return
        author = ctx.message.author
        if self.qtoggle:
            if arg not in self.queue or author.id not in self.queue[arg]:
                if arg not in self.queue:
                    self.queue[arg] = []
                if author.id in self.users and self.users[author.id]:
                    await ctx.send("You are already in the **{}** queue".format(self.users[author.id]))
                    return
                else:
                    self.users[author.id] = arg
                    self.queue[arg].append(author.id)
                await ctx.send('You have been added to the queue.')
            else:
                await ctx.send('You are already in the queue!')
        else:
            await ctx.send('The queue is closed.')

    @commands.command(pass_context=True)
    async def remove(self, ctx):
        ''': Remove yourself from the queue'''
        author = ctx.message.author
        if author.id not in self.users or not self.users[author.id]:
            await ctx.send('You are currently not in a queue')
            return
        chan = self.users[author.id]
        if author.id in self.queue[chan]:
            self.queue[chan].remove(author.id)
            self.users[author.id] = ""
            await ctx.send('You have been removed from the queue.')
        else:
            await ctx.send('You were not in the queue.')

    @commands.command(name='queue', pass_context=True)
    async def _queue(self, ctx, arg):
        ''': See who's up next!'''
        guild = ctx.message.guild
        if not arg:
            print("garbage")
            return 
        channels = ctx.message.guild.voice_channels
        if not any(arg == chan.name for chan in channels):
            await ctx.send("Sorry, the voice channel {} doesn't exist".format(arg))
            return
        message = ''
        for place, member_id in enumerate(self.queue[arg]):
            member = discord.utils.get(guild.members, id=member_id)
            message += f'**#{place+1}** : {member.mention}\n'
        if message != '':
            await ctx.send(message)
        else:
            await ctx.send('Queue is empty')

    @commands.command(pass_context=True)
    async def position(self, ctx):
        ''': Check your position in the queue'''
        author = ctx.message.author
        if author.id not in self.users or not self.users[author.id]:
            await ctx.send('You are currently not in a queue')
            return
        chan = self.users[author.id]
        if author.id in self.queue[chan]:
            _position = self.queue[chan].index(author.id)+1
            await ctx.send(f'you are **#{_position}** in the {chan} queue.')
        else:
            await ctx.send(f'You are not in the queue, please use {prefix}add to add yourself to the queue.')

    @is_approved()
    @commands.command(pass_context=True, name='next')
    async def _next(self, ctx, arg):
        ''': Call the next member in the queue'''
        channels = ctx.message.guild.voice_channels
        if not any(arg == chan.name for chan in channels):
            await ctx.send("Sorry, the voice channel **{}** doesn't exist".format(arg))
            return
        if len(self.queue[arg]) > 0:
            member = discord.utils.get(
                    ctx.message.guild.members, id=self.queue[arg][0])
            await ctx.send(f'You are up **{member.mention}**! Have fun!')
            user = self.queue[arg][0]
            self.queue[arg].remove(user)
            self.users[user] = ""
        else:
            await ctx.send("The **{arg}** is empty")

    # @is_approved()
    # @commands.command()
    # async def clear(self, ctx):
    #     ''': Clears the queue'''
    #     self.queue = []
    #     await ctx.send('Queue has been cleared')

    @is_approved()
    @commands.command()
    async def toggle(self, ctx):
        ''': Toggles the queue'''
        self.qtoggle = not self.qtoggle
        if self.qtoggle:
            state = 'OPEN'
        else:
            state = 'CLOSED'
        await ctx.send(f'Queue is now {state}')


bot.add_cog(Queue(bot))

bot.run('YOUR SECRET KEY HERE')
