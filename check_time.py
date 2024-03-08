def milliseconds_to_datetime(milliseconds=1709814960416):
    import datetime
    seconds, milliseconds = divmod(milliseconds, 1000)
    time = datetime.datetime.utcfromtimestamp(seconds)
    milliseconds_str = str(milliseconds).zfill(3)
    return time.strftime('%Y-%m-%d %H:%M:%S') + '.' + milliseconds_str
print(milliseconds_to_datetime())
