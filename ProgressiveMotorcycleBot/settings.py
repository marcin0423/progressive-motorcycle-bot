
BOT_NAME = 'ProgressiveMotorcycleBot'

SPIDER_MODULES = ['ProgressiveMotorcycleBot.spiders']
NEWSPIDER_MODULE = 'ProgressiveMotorcycleBot.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
