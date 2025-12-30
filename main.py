
# ---------- CONFIG ----------
BOT_TOKEN = "MTQ1NTY0NDc5MjA4NzExODAzMA.Gl9-ij.rOtZRa0LG-kgMI8_QbEQGxOqzOfg7jPl3Lffm4"

# Guild/User Selection
GUILD_ID = 123456789012345678   # The server to look for the user in
USER_ID = 123456789012345678    # The user you want to pull info about

# Trigger / DM settings
TRIGGER = "!userinfo"           # Command trigger (False = always run automatically on startup)
BOT_DM = False                  # If True, DM the command user instead of sending in channel
DM_USER_IDS = []                # List of user IDs to DM the info result (can be multiple)

# Display Toggles
SHOW_USERNAME = True
SHOW_USER_ID = True
SHOW_ACCOUNT_AGE = True
SHOW_PROFILE_IMAGE = True
SHOW_PROFILE_BANNER = True

SHOW_JOINED_DATE = True          # Joined server date
SHOW_MEMBER_NUMBER = True        # Member # position in guild
SHOW_USER_ROLES = True
SHOW_ROLE_IDS = True
SHOW_ROLE_PERMISSIONS = True

# Embed and formatting
USE_EMBED = True                 # Fancy embed with colors/images
EMBED_COLOR = 0x5865F2           # Default Discord blurple
EMBED_TITLE_PREFIX = "User Info"
EMBED_FOOTER = "Requested via Bot"

# Console / Logging
LOG_MISSING_GUILD = True         # Print to logs if bot isn’t in guild
LOG_MISSING_USER = True          # Print to logs if user isn’t in guild
LOG_TO_CONSOLE = True            # Print fetched info in console
# ----------------------------

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def get_user_info(user: discord.User, member: discord.Member = None):
    """Build info about a user. Uses member if available, otherwise global user info."""
    info_lines = []

    if SHOW_USERNAME:
        info_lines.append(f"**Username:** {user} (`{user.name}#{user.discriminator}`)")

    if SHOW_USER_ID:
        info_lines.append(f"**User ID:** `{user.id}`")

    if SHOW_ACCOUNT_AGE:
        created_at = user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        age = (datetime.datetime.utcnow() - user.created_at).days
        info_lines.append(f"**Account Age:** {age} days (Created {created_at})")

    if member:
        if SHOW_JOINED_DATE and member.joined_at:
            joined = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")
            info_lines.append(f"**Joined Server:** {joined}")

        if SHOW_MEMBER_NUMBER:
            joined_list = sorted(
                member.guild.members,
                key=lambda m: m.joined_at or datetime.datetime.utcnow()
            )
            position = joined_list.index(member) + 1
            info_lines.append(f"**Member Number:** {position}")

        if SHOW_USER_ROLES:
            roles = [r.mention for r in member.roles if r.name != "@everyone"]
            info_lines.append(f"**Roles:** {', '.join(roles) if roles else 'None'}")

        if SHOW_ROLE_IDS:
            role_ids = [str(r.id) for r in member.roles if r.name != "@everyone"]
            info_lines.append(f"**Role IDs:** {', '.join(role_ids) if role_ids else 'None'}")

        if SHOW_ROLE_PERMISSIONS:
            perms = [name for name, value in member.guild_permissions if value]
            info_lines.append(f"**Permissions:** {', '.join(perms) if perms else 'None'}")

    return "\n".join(info_lines)


async def build_embed(user: discord.User, info: str):
    embed = discord.Embed(
        title=f"{EMBED_TITLE_PREFIX}: {user}",
        description=info,
        color=EMBED_COLOR
    )

    if SHOW_PROFILE_IMAGE and user.avatar:
        embed.set_thumbnail(url=user.avatar.url)

    if SHOW_PROFILE_BANNER:
        try:
            u = await bot.fetch_user(user.id)
            if u.banner:
                embed.set_image(url=u.banner.url)
        except Exception:
            pass

    embed.set_footer(text=EMBED_FOOTER)
    return embed


async def send_info(target_channel, user_id):
    guild = bot.get_guild(GUILD_ID)
    user = await bot.fetch_user(user_id)

    member = guild.get_member(user_id) if guild else None

    # Logging
    if guild and not member and LOG_MISSING_USER:
        print(f"[INFO] User {user.id} is not in Guild {guild.id}")
    elif not guild and LOG_MISSING_GUILD:
        print(f"[INFO] Bot is not in Guild {GUILD_ID}")

    info_text = await get_user_info(user, member)

    if LOG_TO_CONSOLE:
        print(f"[INFO] User info for {user}:\n{info_text}\n{'-'*40}")

    if USE_EMBED:
        embed = await build_embed(user, info_text)
        await target_channel.send(embed=embed)
    else:
        await target_channel.send(f"```yaml\n{info_text}\n```")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not TRIGGER:
        # Auto-run if trigger is disabled
        for uid in ([USER_ID] + DM_USER_IDS):
            user = bot.get_user(uid)
            if user:
                await send_info(user, USER_ID)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if TRIGGER and message.content.strip().lower() == TRIGGER.lower():
        # Send to command user
        if BOT_DM:
            try:
                await send_info(message.author, USER_ID)
            except Exception:
                await message.channel.send("Couldn't DM user info.")
        else:
            await send_info(message.channel, USER_ID)

        # Also DM specific user IDs if configured
        for uid in DM_USER_IDS:
            user = bot.get_user(uid)
            if user:
                try:
                    await send_info(user, USER_ID)
                except Exception:
                    print(f"Could not DM info to {uid}")

bot.run(BOT_TOKEN)
