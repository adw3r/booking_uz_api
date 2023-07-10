from module import __main__, enums, utils


def test_main_parse_trains():
    departure_date = '2023-07-16'
    path = enums.CityEnum.kyiv, enums.CityEnum.lviv
    data_format: utils.ResponseFormatterInterface = utils.MyFormatter()

    results: dict = main.parse_trains(departure_date, path, data_format)
    assert results is not None


def test_check_acceptable_trains():
    ...
