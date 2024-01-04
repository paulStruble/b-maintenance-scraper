# configurable settings for various program features
# TODO: add print and logging options for all functions (maybe add Log class)
# TODO: add parallel processing
# TODO: comments + standardize comments
# TODO: implement log path

class Settings:
    def __init__(self):
        log_path = '../'
        generate_logs = True
        console_output = True
        headless = True
        parallel = False
        cores = 1