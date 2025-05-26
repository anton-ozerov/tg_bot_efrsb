from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = list(map(lambda x: int(x), env.list("ADMINS")))
EFRSB_TOKEN = env.str("EFRSB_TOKEN")
OSINT_1_TOKEN = env.str("OSINT_1_TOKEN")
OSINT_2_TOKEN = env.str("OSINT_2_TOKEN")
OSINT_3_TOKEN = env.str("OSINT_3_TOKEN")
LOG_FILE = 'bot.log'
DB_NAME = env.str('DB_NAME')
