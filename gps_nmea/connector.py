from serial import Serial


class GPS_connector():
    """Class for connecting with the gps garmin 18x using NMEA protocol
    https://www.sparkfun.com/datasheets/GPS/NMEA%20Reference%20Manual-Rev2.1-Dec07.pdf
    """
    _fix_type = {"0": "No Fix", "1": "GPS", "2": "DGPS"}
    _status = {"A": "valid", "V": "invalid"}
    _latitude_sn = {"S": -1, "N": 1}
    _longitude_we = {"W": -1, "E": 1}

    def __init__(self, src="/dev/ttyACM0", baudrate: int = 4800, message_type: str = "GGA"):
        """ Initialization function
        Args:
            src (str): Location of the device in the filesystem
            baudrate (int): Baudrate for communication
            message_type (str): Type of message in the NMEA protocol to decode (only GGA and RMC sopported)
        Return:
            None
        """
        message_function_mapping = {"GGA": self.get_gga_data, "RMC": self.get_rmc_data}
        integrity_function_mapping = {"GGA": self.check_gga_integrity, "RMC": self.check_rmc_integrity}

        self.gps = Serial(src, baudrate)
        self.decode_data = message_function_mapping[message_type]
        self.check_integrity = integrity_function_mapping[message_type]

    def get_data(self) -> dict:
        """ Function for reading a line from the stream and decode it into a dictionary
        Args:
            None
        Return:
            (dict) : Dictionary with human readable information
        """
        data_line = self.gps.readline()
        data = self.decode_line(data_line)
        return data

    def decode_line(self, line: str) -> dict:
        """ Function for decoding a NMEA protocol line and decode it into a dictionary
        Args:
            line (str) : A line with information compliant with NMEA protocol
        Return:
            (dict) : Dictionary with human readable information
        """
        try:
            line = line.decode("utf8").strip("\n\r")
        except (UnicodeError, UnicodeDecodeError) as e:
            print(f"Error decoding line from gps: {e}")
            return {}
        line_data = line.split(",")
        if not self.check_integrity(line_data):
            return {}
        return self.decode_data(line_data)

    @staticmethod
    def check_gga_integrity(line_data: list[str]) -> bool:
        """ Function for checking integrity of gga data
        before parsing it to the decoder method get_gga_data
        """
        #         0      1      2         3 4          5 6 7  8   9    1011   121314
        # Example $GPGGA,184952,3453.7005,S,05604.9932,W,1,09,1.0,28.1,M,10.1,M,,*78
        try:
            if len(line_data) < 7:
                return False

            # This data should be 'S', 'N' | 'W', 'E'
            if line_data[3].isnumeric() or line_data[5].isnumeric():
                return False

            # This data should be numeric, but #2 and #4 have a decimal dot
            if not line_data[1].isnumeric() or \
               not any([data.isnumeric() for data in line_data[2].split('.')]) or \
               not any([data.isnumeric() for data in line_data[4].split('.')]) or \
               not line_data[6].isnumeric():
                return False

            return True

        except Exception as e: # noqa
            return False

    @staticmethod
    def check_rmc_integrity(line_data: list[str]) -> bool:
        """ Function for checking integrity of rmc data
        before parsing it to the decoder method get_rmc_data
        """
        #         0      1      2 3         4 5          6 7     8     9      10    11
        # Example $GPRMC,184953,A,3453.7004,S,05604.9933,W,000.0,164.2,130824,010.1,W*61

        try:
            if len(line_data) < 7:
                return False

            # This data should be 'A', 'V' | 'S', 'N' | 'W', 'E'
            if line_data[2].isnumeric() or line_data[4].isnumeric() or line_data[6].isnumeric():
                return False

            # This data should be numeric, but #3 and #7 have a decimal dot
            if not line_data[1].isnumeric() or \
               not any([data.isnumeric() for data in line_data[3].split('.')]) or \
               not any([data.isnumeric() for data in line_data[7].split('.')]) or \
               not line_data[5].isnumeric():
                return False

            return True

        except Exception as e: # noqa
            return False

    @staticmethod
    def get_gga_data(line_data: list[str]) -> dict:
        """ Function for decoding a GGA type NMEA line and decode it into a dictionary
        Args:
            line_data (list[str]) : A line with information compliant with NMEA protocol tokenize over the commas
        Return:
            (dict) : Dictionary with human readable information
        """
        data_dict = {}
        if line_data[0] == "$GPGGA":
            data_dict["time"] = line_data[1]
            data_dict["latitude"] = GPS_connector.get_latitude_degrees(line_data[2], line_data[3])
            data_dict["longitude"] = GPS_connector.get_longitude_degrees(line_data[4], line_data[5])
            try:
                data_dict["fix type"] = GPS_connector._fix_type[line_data[6]]
                data_dict["num_satellites"] = line_data[7]
            except KeyError:
                print("Error decoding fix type from GGA data")
                
        return data_dict

    @staticmethod
    def get_rmc_data(line_data: list[str]) -> dict:
        """ Function for decoding an RMC type NMEA line and decode it into a dictionary
        Args:
            line_data (list[str]) : A line with information compliant with NMEA protocol tokenize over the commas
        Return:
            (dict) : Dictionary with human readable information
        """
        data_dict = {}
        if line_data[0] == "$GPRMC":
            data_dict["time"] = line_data[1]
            data_dict["status"] = GPS_connector._status[line_data[2]]
            data_dict["latitude"] = GPS_connector.get_latitude_degrees(line_data[3], line_data[4])
            data_dict["longitude"] = GPS_connector.get_longitude_degrees(line_data[5], line_data[6])
            data_dict["speed"] = line_data[7]
            data_dict["heading"] = line_data[8]
        return data_dict

    @staticmethod
    def get_latitude_degrees(latitudeDDMM_MMMM: str, direction_sn: str) -> float:
        """ Function for transforming a latitude in DDMM.MMMM string format to Degrees
        Args:
            latitudeDDMM_MMMM (str) : latitude in DDMM.MMMM format
            direction_sn (str) : Either S or N. Indicating in wich directions are measured the
                degrees in latitudeDDMM_MMMM
        Return:
            (float) : Latitude in degress
        """
        latitude = GPS_connector._latitude_sn[direction_sn] * (int(latitudeDDMM_MMMM[0:2]) +
                                                               float(latitudeDDMM_MMMM[2:]) * 100 / 60 * 0.01)
        return latitude

    @staticmethod
    def get_longitude_degrees(longitudeDDDMM_MMMM: str, direction_we: str) -> float:
        """ Function for transforming a longitude in DDDMM.MMMM string format to Degrees
        Args:
            longitudeDDDMM_MMMM (str) : latitude in DDDMM.MMMM format
            direction_we (str) : Either W or E. Indicating in wich directions are measured the
                degrees in longitudeDDDMM_MMMM
        Return:
            (float) : Longitude in degress
        """
        longitude = GPS_connector._longitude_we[direction_we] * (int(longitudeDDDMM_MMMM[0:3]) +
                                                                 float(longitudeDDDMM_MMMM[3:]) * 100 / 60 * 0.01)
        return longitude