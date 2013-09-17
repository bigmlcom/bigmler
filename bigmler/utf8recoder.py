import codecs


class UTF8Recoder:
    """Iterator that reads an encoded stream and reencodes the input to UTF-8

    """
    def __init__(self, file_name, encoding):
        """Iterator constructor given a file and encoding

        """
        self.reader = codecs.getreader(encoding)(file_name)

    def __iter__(self):
        """Iterator member

        """
        return self

    def next(self):
        """Iterator next method

        """
        return self.reader.next().encode("utf-8")
