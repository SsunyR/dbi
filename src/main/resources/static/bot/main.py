import discord
from discord.ext import commands
import os
import sys
import importlib.util
from pathlib import Path
import logging
from datetime import datetime

# Set up logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_resource_path(relative_path):
    """Get the resource path that works for both development and PyInstaller"""
    try:
        # Handle PyInstaller's temporary directory structure
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)
    except Exception as e:
        logger.error(f"Error resolving path: {e}")
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# Update COGS_DIR path handling
COGS_DIR = get_resource_path("cogs")

def load_cog_from_file(file_path, module_name):
    """Load a cog module from file path with enhanced error handling"""
    try:
        logger.info(f"Attempting to load cog from: {file_path}")
        
        # Verify file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Cog file not found: {file_path}")
            
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            raise ImportError(f"Could not find module spec for {file_path}")
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module  # Register the module in sys.modules
        
        if spec.loader is None:
            raise ImportError(f"Spec loader is None for {file_path}")
            
        spec.loader.exec_module(module)
        logger.info(f"Successfully loaded module: {module_name}")
        return module
    except Exception as e:
        logger.error(f"Failed to load module {module_name} from {file_path}: {e}")
        return None

async def load_all_cogs(bot):
    """Load all cogs with enhanced error handling and logging"""
    logger.info(f"Loading cogs from directory: {COGS_DIR}")
    
    if not os.path.exists(COGS_DIR):
        logger.error(f"Cogs directory not found: {COGS_DIR}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Directory contents: {os.listdir(os.getcwd()) if os.path.exists(os.getcwd()) else 'N/A'}")
        return
    
    # List and log all files in cogs directory
    try:
        cog_files = [f for f in os.listdir(COGS_DIR) if f.endswith('.py') and not f.startswith('_')]
        logger.info(f"Found cog files: {cog_files}")
    except Exception as e:
        logger.error(f"Error listing cog directory: {e}")
        return
    
    for cog_file in cog_files:
        cog_path = os.path.join(COGS_DIR, cog_file)
        module_name = f"cogs.{cog_file[:-3]}"
        
        try:
            if getattr(sys, 'frozen', False):
                logger.info(f"Loading cog in frozen environment: {cog_file}")
                module = load_cog_from_file(cog_path, module_name)
                
                if module is not None:
                    # Find and load all cog classes in the module
                    cog_loaded = False
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, commands.Cog) and attr != commands.Cog:
                            try:
                                await bot.add_cog(attr(bot))
                                logger.info(f"Successfully loaded cog: {attr_name} from {cog_file}")
                                cog_loaded = True
                            except Exception as e:
                                logger.error(f"Error initializing cog {attr_name}: {e}")
                    
                    if not cog_loaded:
                        logger.warning(f"No valid cog classes found in {cog_file}")
            else:
                logger.info(f"Loading cog in development environment: {module_name}")
                await bot.load_extension(module_name)
                logger.info(f"Successfully loaded extension: {module_name}")
                
        except Exception as e:
            logger.error(f"Failed to load cog {cog_file}: {e}")
            logger.exception("Full traceback:")

def run():
    # Get token from environment variable
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        raise ValueError("No token provided. Please set the DISCORD_TOKEN environment variable.")

    # Set up intents
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"Logged in as {bot.user.name}")
        logger.info(f"Bot ID: {bot.user.id}")
        logger.info(f"Discord.py Version: {discord.__version__}")
        
        # Load all cogs
        await load_all_cogs(bot)
        
        # Sync command tree
        try:
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync command tree: {e}")

        # Set bot status
        await bot.change_presence(activity=discord.Game(name="!help for commands"))

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            return  # Ignore command not found errors
        logger.error(f"Command error: {str(error)}")
        await ctx.send(f"An error occurred: {str(error)}")

    @bot.command()
    async def ping(ctx):
        """Check the bot's latency"""
        latency = round(bot.latency * 1000)
        await ctx.send(f"Pong! Latency: {latency}ms")

    @bot.command()
    async def 핑(ctx):
        """한국어 ping 명령어"""
        latency = round(bot.latency * 1000)
        await ctx.send(f"퐁! 지연 시간: {latency}ms")

    @bot.command(hidden=True)
    @commands.is_owner()
    async def load(ctx, cog: str):
        """Load a cog (Owner only)"""
        cog_path = os.path.join(COGS_DIR, f"{cog.lower()}.py")
        module_name = f"cogs.{cog.lower()}"
        
        try:
            if getattr(sys, 'frozen', False):
                module = load_cog_from_file(cog_path, module_name)
                if module is not None:
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, commands.Cog) and attr != commands.Cog:
                            await bot.add_cog(attr(bot))
                            await ctx.send(f'✅ Loaded {cog}')
                            return
            else:
                await bot.load_extension(f"cogs.{cog.lower()}")
                await ctx.send(f'✅ Loaded {cog}')
        except Exception as e:
            await ctx.send(f'❌ Error loading {cog}: {str(e)}')
            logger.error(f"Failed to load cog {cog}: {e}")

    @bot.command(hidden=True)
    @commands.is_owner()
    async def unload(ctx, cog: str):
        """Unload a cog (Owner only)"""
        try:
            if getattr(sys, 'frozen', False):
                cog_name = cog.lower()
                for loaded_cog in bot.cogs.copy():
                    if loaded_cog.lower() == cog_name:
                        await bot.remove_cog(loaded_cog)
                        await ctx.send(f'✅ Unloaded {cog}')
                        return
                await ctx.send(f'❌ Cog {cog} not found')
            else:
                await bot.unload_extension(f"cogs.{cog.lower()}")
                await ctx.send(f'✅ Unloaded {cog}')
        except Exception as e:
            await ctx.send(f'❌ Error unloading {cog}: {str(e)}')
            logger.error(f"Failed to unload cog {cog}: {e}")

    @bot.command(hidden=True)
    @commands.is_owner()
    async def reload(ctx, cog: str):
        """Reload a cog (Owner only)"""
        try:
            if getattr(sys, 'frozen', False):
                # First unload the cog
                cog_name = cog.lower()
                for loaded_cog in bot.cogs.copy():
                    if loaded_cog.lower() == cog_name:
                        await bot.remove_cog(loaded_cog)
                        break
                
                # Then load it again
                cog_path = os.path.join(COGS_DIR, f"{cog_name}.py")
                module_name = f"cogs.{cog_name}"
                module = load_cog_from_file(cog_path, module_name)
                if module is not None:
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, commands.Cog) and attr != commands.Cog:
                            await bot.add_cog(attr(bot))
                            await ctx.send(f'✅ Reloaded {cog}')
                            return
                await ctx.send(f'❌ Failed to reload {cog}')
            else:
                await bot.reload_extension(f"cogs.{cog.lower()}")
                await ctx.send(f'✅ Reloaded {cog}')
        except Exception as e:
            await ctx.send(f'❌ Error reloading {cog}: {str(e)}')
            logger.error(f"Failed to reload cog {cog}: {e}")

    @bot.command(hidden=True)
    @commands.is_owner()
    async def debugcogs(ctx):
        """Debug command to check cog loading status"""
        debug_info = [
            f"```",
            f"Debug Information:",
            f"----------------",
            f"Cogs directory: {COGS_DIR}",
            f"Directory exists: {os.path.exists(COGS_DIR)}",
        ]
        
        if os.path.exists(COGS_DIR):
            try:
                contents = os.listdir(COGS_DIR)
                debug_info.append(f"Directory contents: {contents}")
            except Exception as e:
                debug_info.append(f"Error listing directory: {e}")
        
        debug_info.extend([
            f"",
            f"Loaded Cogs:",
            f"------------",
            *[f"- {cog}" for cog in bot.cogs.keys()],
            f"",
            f"Bot Information:",
            f"---------------",
            f"Logged in as: {bot.user.name if bot.user else 'Not logged in'}",
            f"Bot ID: {bot.user.id if bot.user else 'N/A'}",
            f"Discord.py Version: {discord.__version__}",
            f"Latency: {round(bot.latency * 1000)}ms",
            f"```"
        ])
        
        await ctx.send("\n".join(debug_info))

    # Run the bot
    try:
        logger.info("Starting bot...")
        bot.run(TOKEN, log_handler=None)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    run()