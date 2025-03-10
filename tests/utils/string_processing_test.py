from utils.string_processing import get_matched_string_index, \
    format_decimal, \
    get_price_value, \
    remove_single_letters_for_search, \
    tokenize_for_search


def test_get_matched_string_index():
    assert get_matched_string_index(
        'karl marx',
        ['henri guillemin', 'groucho marx', 'kroutchev', 'emmanuel macron']
    ) == 1


def test_get_price_value():
    assert type(get_price_value('')) == int


def test_remove_special_character():
    assert tokenize_for_search("Læetitia a mangé's'") == ['læetitia', 'a', 'mangé', 's', '']


def test_remove_special_character():
    assert tokenize_for_search("L'histoire sans fin") == ['l', 'histoire', 'sans', 'fin']


def test_tokenize_url():
    assert tokenize_for_search('http://www.t_est-toto.fr') == ['http', 'www', 't', 'est', 'toto', 'fr']


def test_tokenize_url():
    assert remove_single_letters_for_search(['http', 'www', 't', 'est', 'toto', 'fr']) == ['http', 'www', 'est', 'toto',
                                                                                           'fr']


def test_format_decimal():
    assert format_decimal(1.22) == '1,22'
