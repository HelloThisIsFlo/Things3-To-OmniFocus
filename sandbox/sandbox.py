START_YEAR = 16
START_MONTH = 12
START_DAY = 7


def day(bin_date):
    return (((1 << START_MONTH) - 1) & bin_date) >> START_DAY


def month(bin_date):
    return (((1 << START_YEAR) - 1) & bin_date) >> START_MONTH


def year(bin_date):
    return bin_date >> START_YEAR


if __name__ == "__main__":
    y = 2023
    m = 4
    d = 14
    integer_value = (y << 16) | (m << 12) | (d << 7)

    print(integer_value)

    print(bin(d))
    print(bin(d << 7))
    print(bin(integer_value & 0b111111111111))
    print(bin(0b111111111111))
    print(bin((1 << 12) - 1))

    print(day(integer_value))
    integer_value = 132598144
    print(f"{day(integer_value)}-{month(integer_value)}-{year(integer_value)}")
    import datetime

    timestamp = 1681465136.887539
    dt = datetime.datetime.fromtimestamp(timestamp)
    print(dt)

    timestamp = 1507852288
    dt = datetime.datetime.fromtimestamp(timestamp)
    print(dt)
    print(201326592.0 / (3 * 60))
