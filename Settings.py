# configurable settings for various program features
# TODO: add print and logging options for all functions
# TODO: add parallel processing
# TODO: comments + standardize comments
# TODO: implement log path
# TODO: create main menu sequence
# TODO: config file (instead of settings)
# TODO: comments in functions as multi-line strings
# TODO: unit tests: generate_add_request_range_parallel_args
# TODO: bypass duo after first login using pickle to dump and load cookies

class Settings:
    def __init__(self):
        log_path = '../'
        generate_logs = True
        console_output = True
        headless = True
        parallel = False
        process_cont = 1