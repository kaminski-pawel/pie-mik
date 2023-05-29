import logging


def handler(event, context):
    _set_logger()
    logging.info("got event{}".format(event))


def _set_logger():
    if logging.getLogger().hasHandlers():
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
