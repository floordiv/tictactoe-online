from traceback import format_exc


"""
this is a light module for safe functions calls

call example:
> result = safecall.call(read_from_file, args=('myfile.txt',), errs=FileNotFoundError, on_catch=None)
> result = safecall.call(create_file, args=('myfile.txt',), kwargs={'text': 'text here'},
                         errs=(OSError, FileExistsError), on_catch=None)

if file is not found, exception won't be raised, but on_catch will be returned, and result will contain None

on_catch may be any type
"""


def call(func, args=(), kwargs={}, errs=(), on_catch=None):
    if not isinstance(errs, tuple) and not isinstance(errs, list):
        errs = (errs,)

    if len(errs) == 0:
        return func()

    try:
        return func(*args, **kwargs)
    except errs:
        return on_catch
