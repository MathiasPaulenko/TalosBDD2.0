import string
import random

from faker import Faker


def generate_string(min_chars=3, max_chars=10, chars_set=string.ascii_letters + ' ' + string.digits) -> str:
    return ''.join(random.choice(chars_set) for _ in range(0, random.randint(min_chars, max_chars)))


def generate_email() -> str:
    return generate_string(max_chars=random.randint(3, 15), chars_set=string.ascii_letters + string.digits) + "@" + \
           generate_string(max_chars=random.randint(3, 15), chars_set=string.ascii_letters + string.digits) + "." + \
           generate_string(min_chars=1, max_chars=random.randint(1, 3), chars_set=string.ascii_letters)


def generate_phone() -> str:
    if random.randint(0, 1):
        first_digit = "6"
    else:
        first_digit = "9"
    return first_digit + generate_string(min_chars=8, max_chars=8, chars_set=string.digits)


def get_faker_datas(list_keys: list, locale="en_IN", count: int = 1):
    fake = Faker(locale)
    fake_general_list = []
    for i in range(count):
        fake_dict = {}
        for key in list_keys:
            if key == "address":
                fake_dict["address"] = fake.address()
            elif key == "building_number":
                fake_dict["building_number"] = fake.building_number()
            elif key == "city":
                fake_dict["city"] = fake.city()
            elif key == "city_suffix":
                fake_dict["city_suffix"] = fake.city_suffix()
            elif key == "country":
                fake_dict["country"] = fake.country()
            elif key == "country_code":
                fake_dict["country_code"] = fake.country_code()
            elif key == "postcode":
                fake_dict["postcode"] = fake.postcode()
            elif key == "street_address":
                fake_dict["street_address"] = fake.street_address()
            elif key == "street_name":
                fake_dict["street_name"] = fake.street_name()
            elif key == "street_suffix":
                fake_dict["street_suffix"] = fake.street_suffix()
            elif key == "license_plate":
                fake_dict["license_plate"] = fake.license_plate()
            elif key == "bank_country":
                fake_dict["bank_country"] = fake.bank_country()
            elif key == "bban":
                fake_dict["bban"] = fake.bban()
            elif key == "iban":
                fake_dict["iban"] = fake.iban()
            elif key == "swift":
                fake_dict["swift"] = fake.swift()
            elif key == "ean":
                fake_dict["ean"] = fake.ean()
            elif key == "ean13":
                fake_dict["ean13"] = fake.ean13()
            elif key == "ean8":
                fake_dict["ean8"] = fake.ean8()
            elif key == "localized_ean":
                fake_dict["localized_ean"] = fake.localized_ean()
            elif key == "localized_ean13":
                fake_dict["localized_ean13"] = fake.localized_ean13()
            elif key == "localized_ean8":
                fake_dict["localized_ean8"] = fake.localized_ean8()
            elif key == "hex_color":
                fake_dict["hex_color"] = fake.hex_color()
            elif key == "color_name":
                fake_dict["color_name"] = fake.color_name()
            elif key == "rgb_color":
                fake_dict["rgb_color"] = fake.rgb_color()
            elif key == "rgb_css_color":
                fake_dict["rgb_css_color"] = fake.rgb_css_color()
            elif key == "safe_color_name":
                fake_dict["safe_color_name"] = fake.safe_color_name()
            elif key == "safe_hex_color":
                fake_dict["safe_hex_color"] = fake.safe_hex_color()
            elif key == "bs":
                fake_dict["bs"] = fake.bs()
            elif key == "catch_phrase":
                fake_dict["catch_phrase"] = fake.catch_phrase()
            elif key == "company":
                fake_dict["company"] = fake.company()
            elif key == "company_suffix":
                fake_dict["company_suffix"] = fake.company_suffix()
            elif key == "credit_card_expire":
                fake_dict["credit_card_expire"] = fake.credit_card_expire()
            elif key == "credit_card_full":
                fake_dict["credit_card_full"] = fake.credit_card_full()
            elif key == "credit_card_number":
                fake_dict["credit_card_number"] = fake.credit_card_number()
            elif key == "credit_card_provider":
                fake_dict["credit_card_provider"] = fake.credit_card_provider()
            elif key == "credit_card_security_code":
                fake_dict["credit_card_security_code"] = fake.credit_card_security_code()
            elif key == "cryptocurrency":
                fake_dict["cryptocurrency"] = fake.cryptocurrency()
            elif key == "cryptocurrency_code":
                fake_dict["cryptocurrency_code"] = fake.cryptocurrency_code()
            elif key == "cryptocurrency_name":
                fake_dict["cryptocurrency_name"] = fake.cryptocurrency_name()
            elif key == "currency":
                fake_dict["currency"] = fake.currency()
            elif key == "currency_code":
                fake_dict["currency_code"] = fake.currency_code()
            elif key == "currency_name":
                fake_dict["currency_name"] = fake.currency_name()
            elif key == "currency_symbol":
                fake_dict["currency_symbol"] = fake.currency_symbol()
            elif key == "am_pm":
                fake_dict["am_pm"] = fake.am_pm()
            elif key == "century":
                fake_dict["century"] = fake.century()
            elif key == "date":
                fake_dict["date"] = fake.date()
            elif key == "date_between":
                fake_dict["date_between"] = fake.date_between()
            elif key == "date_between_dates":
                fake_dict["date_between_dates"] = fake.date_between_dates()
            elif key == "date_object":
                fake_dict["date_object"] = fake.date_object()
            elif key == "date_of_birth":
                fake_dict["date_of_birth"] = fake.date_of_birth()
            elif key == "date_this_century":
                fake_dict["date_this_century"] = fake.date_this_century()
            elif key == "date_this_decade":
                fake_dict["date_this_decade"] = fake.date_this_decade()
            elif key == "date_this_month":
                fake_dict["date_this_month"] = fake.date_this_month()
            elif key == "date_this_year":
                fake_dict["date_this_year"] = fake.date_this_year()
            elif key == "date_time":
                fake_dict["date_time"] = fake.date_time()
            elif key == "date_time_ad":
                fake_dict["date_time_ad"] = fake.date_time_ad()
            elif key == "date_time_between_dates":
                fake_dict["date_time_between_dates"] = fake.date_time_between_dates()
            elif key == "date_time_this_century":
                fake_dict["date_time_this_century"] = fake.date_time_this_century()
            elif key == "date_time_this_decade":
                fake_dict["date_time_this_decade"] = fake.date_time_this_decade()
            elif key == "date_time_this_month":
                fake_dict["date_time_this_month"] = fake.date_time_this_month()
            elif key == "date_time_this_year":
                fake_dict["date_time_this_year"] = fake.date_time_this_year()
            elif key == "day_of_month":
                fake_dict["day_of_month"] = fake.day_of_month()
            elif key == "day_of_week":
                fake_dict["day_of_week"] = fake.day_of_week()
            elif key == "future_date":
                fake_dict["future_date"] = fake.future_date()
            elif key == "future_datetime":
                fake_dict["future_datetime"] = fake.future_datetime()
            elif key == "iso8601":
                fake_dict["iso8601"] = fake.iso8601()
            elif key == "month":
                fake_dict["month"] = fake.month()
            elif key == "month_name":
                fake_dict["month_name"] = fake.month_name()
            elif key == "past_date":
                fake_dict["past_date"] = fake.past_date()
            elif key == "past_datetime":
                fake_dict["past_datetime"] = fake.past_datetime()
            elif key == "pytimezone":
                fake_dict["pytimezone"] = fake.pytimezone()
            elif key == "time_delta":
                fake_dict["time_delta"] = fake.time_delta()
            elif key == "time":
                fake_dict["time"] = fake.time()
            elif key == "time_object":
                fake_dict["time_object"] = fake.time_object()
            elif key == "time_series":
                fake_dict["time_series"] = fake.time_series()
            elif key == "timezone":
                fake_dict["timezone"] = fake.timezone()
            elif key == "unix_time":
                fake_dict["unix_time"] = fake.unix_time()
            elif key == "year":
                fake_dict["year"] = fake.year()
            elif key == "file_extension":
                fake_dict["file_extension"] = fake.file_extension()
            elif key == "file_name":
                fake_dict["file_name"] = fake.file_name()
            elif key == "file_path":
                fake_dict["file_path"] = fake.file_path()
            elif key == "mime_type":
                fake_dict["mime_type"] = fake.mime_type()
            elif key == "mime_type":
                fake_dict["mime_type"] = fake.mime_type()
            elif key == "unix_device":
                fake_dict["unix_device"] = fake.unix_device()
            elif key == "unix_device":
                fake_dict["unix_device"] = fake.unix_device()
            elif key == "unix_partition":
                fake_dict["unix_partition"] = fake.unix_partition()
            elif key == "coordinate":
                fake_dict["coordinate"] = fake.coordinate()
            elif key == "latitude":
                fake_dict["latitude"] = fake.latitude()
            elif key == "latlng":
                fake_dict["latlng"] = fake.latlng()
            elif key == "local_latlng":
                fake_dict["local_latlng"] = fake.local_latlng()
            elif key == "location_on_land":
                fake_dict["location_on_land"] = fake.location_on_land()
            elif key == "longitude":
                fake_dict["longitude"] = fake.longitude()
            elif key == "ascii_company_email":
                fake_dict["ascii_company_email"] = fake.ascii_company_email()
            elif key == "ascii_email":
                fake_dict["ascii_email"] = fake.ascii_email()
            elif key == "ascii_free_email":
                fake_dict["ascii_free_email"] = fake.ascii_free_email()
            elif key == "ascii_safe_email":
                fake_dict["ascii_safe_email"] = fake.ascii_safe_email()
            elif key == "company_email":
                fake_dict["company_email"] = fake.company_email()
            elif key == "dga":
                fake_dict["dga"] = fake.dga()
            elif key == "domain_name":
                fake_dict["domain_name"] = fake.domain_name()
            elif key == "domain_word":
                fake_dict["domain_word"] = fake.domain_word()
            elif key == "email":
                fake_dict["email"] = fake.email()
            elif key == "free_email":
                fake_dict["free_email"] = fake.free_email()
            elif key == "free_email_domain":
                fake_dict["free_email_domain"] = fake.free_email_domain()
            elif key == "hostname":
                fake_dict["hostname"] = fake.hostname()
            elif key == "http_method":
                fake_dict["http_method"] = fake.http_method()
            elif key == "image_url":
                fake_dict["image_url"] = fake.image_url()
            elif key == "ipv4":
                fake_dict["ipv4"] = fake.ipv4()
            elif key == "ipv4_network_class":
                fake_dict["ipv4_network_class"] = fake.ipv4_network_class()
            elif key == "ipv4_private":
                fake_dict["ipv4_private"] = fake.ipv4_private()
            elif key == "ipv4_public":
                fake_dict["ipv4_public"] = fake.ipv4_public()
            elif key == "ipv6":
                fake_dict["ipv6"] = fake.ipv6()
            elif key == "mac_address":
                fake_dict["mac_address"] = fake.mac_address()
            elif key == "port_number":
                fake_dict["port_number"] = fake.port_number()
            elif key == "safe_domain_name":
                fake_dict["safe_domain_name"] = fake.safe_domain_name()
            elif key == "safe_email":
                fake_dict["safe_email"] = fake.safe_email()
            elif key == "slug":
                fake_dict["slug"] = fake.slug()
            elif key == "tld":
                fake_dict["tld"] = fake.tld()
            elif key == "uri":
                fake_dict["uri"] = fake.uri()
            elif key == "uri_extension":
                fake_dict["uri_extension"] = fake.uri_extension()
            elif key == "uri_page":
                fake_dict["uri_page"] = fake.uri_page()
            elif key == "uri_path":
                fake_dict["uri_path"] = fake.uri_path()
            elif key == "url":
                fake_dict["url"] = fake.url()
            elif key == "user_name":
                fake_dict["user_name"] = fake.user_name()
            elif key == "isbn10":
                fake_dict["isbn10"] = fake.isbn10()
            elif key == "isbn13":
                fake_dict["isbn13"] = fake.isbn13()
            elif key == "job":
                fake_dict["job"] = fake.job()
            elif key == "paragraph":
                fake_dict["paragraph"] = fake.paragraph(nb_sentences=5)
            elif key == "paragraphs":
                fake_dict["paragraphs"] = fake.paragraphs(nb=5)
            elif key == "sentences":
                fake_dict["sentences"] = fake.sentences()
            elif key == "texts":
                fake_dict["texts"] = fake.texts(nb_texts=5)
            elif key == "word":
                fake_dict["word"] = fake.word()
            elif key == "words":
                fake_dict["words"] = fake.words()
            elif key == "binary":
                fake_dict["binary"] = fake.binary(length=64)
            elif key == "boolean":
                fake_dict["boolean"] = fake.boolean(chance_of_getting_true=50)
            elif key == "md5":
                fake_dict["md5"] = fake.md5(raw_output=False)
            elif key == "null_boolean":
                fake_dict["null_boolean"] = fake.null_boolean()
            elif key == "password":
                fake_dict["password"] = fake.password(length=12)
            elif key == "sha1":
                fake_dict["sha1"] = fake.sha1(raw_output=False)
            elif key == "sha256":
                fake_dict["sha256"] = fake.sha256(raw_output=False)
            elif key == "uuid4":
                fake_dict["uuid4"] = fake.uuid4()
            elif key == "first_name":
                fake_dict["first_name"] = fake.first_name()
            elif key == "first_name_female":
                fake_dict["first_name_female"] = fake.first_name_female()
            elif key == "first_name_male":
                fake_dict["first_name_male"] = fake.first_name_male()
            elif key == "first_name_nonbinary":
                fake_dict["first_name_nonbinary"] = fake.first_name_nonbinary()
            elif key == "language_name":
                fake_dict["language_name"] = fake.language_name()
            elif key == "last_name":
                fake_dict["last_name"] = fake.last_name()
            elif key == "last_name_female":
                fake_dict["last_name_female"] = fake.last_name_female()
            elif key == "last_name_male":
                fake_dict["last_name_male"] = fake.last_name_male()
            elif key == "last_name_nonbinary":
                fake_dict["last_name_nonbinary"] = fake.last_name_nonbinary()
            elif key == "name":
                fake_dict["name"] = fake.name()
            elif key == "name_female":
                fake_dict["name_female"] = fake.name_female()
            elif key == "name_male":
                fake_dict["name_male"] = fake.name_male()
            elif key == "name_nonbinary":
                fake_dict["name_nonbinary"] = fake.name_nonbinary()
            elif key == "prefix":
                fake_dict["prefix"] = fake.prefix()
            elif key == "prefix_female":
                fake_dict["prefix_female"] = fake.prefix_female()
            elif key == "prefix_male":
                fake_dict["prefix_male"] = fake.prefix_male()
            elif key == "prefix_nonbinary":
                fake_dict["prefix_nonbinary"] = fake.prefix_nonbinary()
            elif key == "suffix":
                fake_dict["suffix"] = fake.suffix()
            elif key == "suffix_female":
                fake_dict["suffix_female"] = fake.suffix_female()
            elif key == "suffix_male":
                fake_dict["suffix_male"] = fake.suffix_male()
            elif key == "suffix_nonbinary":
                fake_dict["suffix_nonbinary"] = fake.suffix_nonbinary()
            elif key == "country_calling_code":
                fake_dict["country_calling_code"] = fake.country_calling_code()
            elif key == "msisdn":
                fake_dict["msisdn"] = fake.msisdn()
            elif key == "phone_number":
                fake_dict["phone_number"] = fake.phone_number()
            elif key == "profile":
                fake_dict["profile"] = fake.profile()
            elif key == "simple_profile":
                fake_dict["simple_profile"] = fake.simple_profile()
            elif key == "pybool":
                fake_dict["pybool"] = fake.pybool()
            elif key == "pybool":
                fake_dict["pybool"] = fake.pybool()
            elif key == "pydict":
                fake_dict["pydict"] = fake.pydict()
            elif key == "pyfloat":
                fake_dict["pyfloat"] = fake.pyfloat()
            elif key == "pyint":
                fake_dict["pyint"] = fake.pyint()
            elif key == "pyiterable":
                fake_dict["pyiterable"] = fake.pyiterable()
            elif key == "pylist":
                fake_dict["pylist"] = fake.pylist()
            elif key == "pyset":
                fake_dict["pyset"] = fake.pyset()
            elif key == "pystr":
                fake_dict["pystr"] = fake.pystr()
            elif key == "pystr_format":
                fake_dict["pystr_format"] = fake.pystr_format()
            elif key == "pystruct":
                fake_dict["pystruct"] = fake.pystruct()
            elif key == "pytuple":
                fake_dict["pytuple"] = fake.pytuple()
            elif key == "ssn":
                fake_dict["ssn"] = fake.ssn()
            elif key == "android_platform_token":
                fake_dict["android_platform_token"] = fake.android_platform_token()
            elif key == "chrome":
                fake_dict["chrome"] = fake.chrome()
            elif key == "firefox":
                fake_dict["firefox"] = fake.firefox()
            elif key == "internet_explorer":
                fake_dict["internet_explorer"] = fake.internet_explorer()
            elif key == "ios_platform_token":
                fake_dict["ios_platform_token"] = fake.ios_platform_token()
            elif key == "linux_platform_token":
                fake_dict["linux_platform_token"] = fake.linux_platform_token()
            elif key == "linux_processor":
                fake_dict["linux_processor"] = fake.linux_processor()
            elif key == "mac_platform_token":
                fake_dict["mac_platform_token"] = fake.mac_platform_token()
            elif key == "mac_processor":
                fake_dict["mac_processor"] = fake.mac_processor()
            elif key == "opera":
                fake_dict["opera"] = fake.opera()
            elif key == "safari":
                fake_dict["safari"] = fake.safari()
            elif key == "user_agent":
                fake_dict["user_agent"] = fake.user_agent()
            elif key == "windows_platform_token":
                fake_dict["windows_platform_token"] = fake.windows_platform_token()
        fake_general_list.append(fake_dict)
    return fake_general_list
