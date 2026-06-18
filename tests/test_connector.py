from gps_nmea import GPS_connector


def test_latitude_conversion():
    lat = GPS_connector.get_latitude_degrees("3453.7005", "S")
    assert lat == -34.89500833333334


def test_longitude_conversion():
    lon = GPS_connector.get_longitude_degrees("05604.9932", "W")
    assert lon == -56.08322


def test_gga_integrity_valid():
    line = [
        "$GPGGA",
        "184952",
        "3453.7005",
        "S",
        "05604.9932",
        "W",
        "1",
        "09",
        "1.0",
        "28.1",
        "M",
        "10.1",
        "M",
        "",
        "*78",
    ]
    assert GPS_connector.check_gga_integrity(line) is True


def test_gga_integrity_invalid_lat():
    line = [
        "$GPGGA",
        "184952",
        "abc",
        "S",
        "05604.9932",
        "W",
        "1",
        "09",
        "1.0",
        "28.1",
        "M",
        "10.1",
        "M",
        "",
        "*78",
    ]
    assert GPS_connector.check_gga_integrity(line) is False
