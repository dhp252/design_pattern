import socket
import syslog

# The initial class.


class Logger(object):
    def __init__(self, file):
        self.file = file

    def log(self, message):
        self.file.write(message + "\n")  # checkpoint
        self.file.flush()  # checkpoint


class FilteredLogger(Logger):
    def __init__(self, pattern, file):
        self.pattern = pattern
        super().__init__(file)

    def log(self, message):
        if self.pattern in message:
            super().log(message)


# ADAPTER: overwrite write and flush function in Looger
class FileLikeSocket:
    # ADAPTER for Socket
    def __init__(self, sock):
        self.sock = sock

    def write(self, message_and_newline):
        self.sock.sendall(message_and_newline.encode("ascii"))  # checkpoint

    def flush(self):
        pass  # checkpoint


class FileLikeSyslog:
    # ADAPTER for Syslog
    def __init__(self, priority):
        self.priority = priority

    def write(self, message_and_newline):
        message = message_and_newline.rstrip("\n")  # checkpoint
        syslog.syslog(self.priority, message)

    def flush(self):
        pass  # checkpoint


if __name__ == "__main__":
    sock1, sock2 = socket.socketpair()
    fs = FileLikeSocket(sock1)  # checkpoint
    logger = FilteredLogger("Error", fs)
    logger.log("Warning: message number one")
    logger.log("Error: message number two")

    fs = FileLikeSyslog(syslog.LOG_ERR)  # checkpoint
    logger = FilteredLogger("Error", fs)
    logger.log("Warning: message number one")
    logger.log("Error: message number two")
