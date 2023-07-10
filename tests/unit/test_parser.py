from module import parser, enums


def test_parser_get_trains():
    departure_date = '2023-07-16'
    results = parser.get_trains(enums.CityEnum.lviv, enums.CityEnum.kyiv, departure_date=departure_date)
    print(results.json())
    assert results.json().get('data') is not None


def test_parser_get_train_wagons():
    departure_date = '2023-07-16'
    train_num = '008Л'
    results = parser.get_train_wagons(train_num, enums.CityEnum.lviv, enums.CityEnum.kyiv, departure_date=departure_date)
    print(results.json())
    assert results.json().get('data') is not None
