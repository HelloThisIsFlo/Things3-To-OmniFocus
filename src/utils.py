from datetime import date


def convert_bin_date(bin_date):
    start_year = 16
    start_month = 12
    start_day = 7

    def day():
        return (((1 << start_month) - 1) & bin_date) >> start_day

    def month():
        return (((1 << start_year) - 1) & bin_date) >> start_month

    def year():
        return bin_date >> start_year

    return date(year(), month(), day())
