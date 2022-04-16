from parser import parse_pages_amount, parse_main_page, parse_subpage
import requests
import pprint
import json

BASE_URL = 'https://djinni.co/jobs/keyword-python/{city}/?exp_level={exp}&salary={salary}&page={page}'


def generate_url(city: str, exp: str, salary: int, page: int, url_template: str = BASE_URL) -> str:
    return url_template.format(city=city, exp=exp, salary=salary, page=page)


def crawl_main_page(page_number: int = 1):  # -> text
    main_page_url = generate_url('kyiv', 'no_exp', 500, page_number)
    resp = requests.get(url=main_page_url)
    return resp.text


def crawl_subpage(url: str):  # -> text
    resp = requests.get(url=url)
    return resp.text


def handler():  # generator of items
    pages_amount = None
    current_page = 1
    while True:
        first_page_raw = crawl_main_page(current_page)
        if pages_amount is None:
            pages_amount = parse_pages_amount(first_page_raw)
        main_page_items_gen = parse_main_page(first_page_raw)
        for item in main_page_items_gen:
            item_subpage_raw = crawl_subpage(item.get('job_url'))
            updated_item = parse_subpage(item_subpage_raw, item)
            yield updated_item
        if current_page >= pages_amount:
            break
        current_page += 1


def write_item_to_json(item: dict, file_name: str = 'data.json') -> None:
    with open(file_name, 'r', encoding='UTF-8') as r_file:
        data = json.load(r_file)
    data.append(item)
    with open(file_name, 'w', encoding='UTF-8') as w_file:
        json.dump(data, w_file, indent=4, ensure_ascii=False)


def main():
    counter = 1
    for item in handler():
        write_item_to_json(item)
        print(f'item #{counter}')
        counter += 1


if __name__ == '__main__':
    main()
