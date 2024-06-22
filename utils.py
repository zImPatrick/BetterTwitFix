import re
import io

pathregex = re.compile("\\w{1,15}\\/(status|statuses)\\/(\\d{2,20})")
endTCOregex = re.compile("(^.*?) +https:\/\/t.co\/.*?$")

def getTweetIdFromUrl(url):
    match = pathregex.search(url)
    if match is not None:
        return match.group(2)
    else:
        return None
    
def stripEndTCO(text):
    # remove t.co links at the end of a string
    match = endTCOregex.search(text)
    if match is not None:
        return match.group(1)
    else:
        return text
    
# https://stackoverflow.com/a/55977438
class BytesIOWrapper(io.BufferedReader):
    """Wrap a buffered bytes stream over TextIOBase string stream."""

    def __init__(self, text_io_buffer, encoding=None, errors=None, **kwargs):
        super(BytesIOWrapper, self).__init__(text_io_buffer, **kwargs)
        self.encoding = encoding or text_io_buffer.encoding or 'utf-8'
        self.errors = errors or text_io_buffer.errors or 'strict'

    def _encoding_call(self, method_name, *args, **kwargs):
        raw_method = getattr(self.raw, method_name)
        val = raw_method(*args, **kwargs)
        return val.encode(self.encoding, errors=self.errors)

    def read(self, size=-1):
        return self._encoding_call('read', size)

    def read1(self, size=-1):
        return self._encoding_call('read1', size)

    def peek(self, size=-1):
        return self._encoding_call('peek', size)