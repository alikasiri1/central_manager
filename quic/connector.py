import time

# Utility function to get the current time in milliseconds
def millis():
    return int(time.time() * 1000)


class client:
    def __init__(self, host, port, use_json):
        """
        Base class for a client.
        :param host: Server hostname or IP
        :param port: Server port
        :param use_json: Whether to use JSON for data (unused in this example)
        """
        self.host = host
        self.port = port
        self.use_json = use_json
        self.quic_payload_size = 1024  # Default payload size in bytes

    def _infomessage(self, message, is_error=False):
        """
        Logs information messages.
        :param message: Message to display
        :param is_error: Whether it's an error message
        """
        if is_error:
            print(f"[ERROR] {message}")
        else:
            print(f"[INFO] {message}")

    # def run_test(self):
    #     """
    #     Starts the client's main task for the specified duration.
    #     :param time: Duration in seconds
    #     """
    #     # self._infomessage(f"Starting test for {time} seconds...")


class server:
    def __init__(self, port, interval, use_json):
        """
        Base class for a server.
        :param port: Port to listen on
        :param interval: Interval in seconds for reporting data transfer
        :param use_json: Whether to use JSON for data (unused in this example)
        """
        self.port = port
        self.interval = interval
        self.use_json = use_json
        self.quic_payload_size = 1024  # Default payload size in bytes

    def _infomessage(self, message, is_error=False):
        """
        Logs information messages.
        :param message: Message to display
        :param is_error: Whether it's an error message
        """
        if is_error:
            print(f"[ERROR] {message}")
        else:
            print(f"[INFO] {message}")

    def _datamessage(self, bps_value):
        """
        Logs data transfer rate.
        :param bps_value: Bits per second
        """
        print(f"[DATA] Current transfer rate: {bps_value:.2f} bps")

    def listen(self):
        """
        Prepares the server to start listening for connections.
        """
        self._infomessage(f"Listening on port {self.port}...")
