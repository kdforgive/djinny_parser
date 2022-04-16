from bs4 import BeautifulSoup
from bs4.element import Tag
import requests
from typing import Generator, Union, Optional, List


def count_pages_amount(items_amount: int, items_per_page: int = 15):
    pages_amount = items_amount // items_per_page + 1 \
        if items_amount % items_per_page != 0 \
        else items_amount // items_per_page
    return pages_amount


def parse_pages_amount(page) -> int:
    soup = BeautifulSoup(page, 'lxml')
    items_amount_tag = soup.find('span', class_='text-muted')
    items_amount = int(items_amount_tag.text)
    return count_pages_amount(items_amount)


def parse_main_page(page: str) -> Generator[dict, None, None]:
    '''что сделать:
    1 кастомная ошибка для парсера, должна характеризовать, что в парсере ошибка
    2 отдельная функция формирования айтема(как минимкм 2 функции)
        * main_page_create_item
        * subpage_update_item
    3 обработать исключительные ситуации при взятии полей айтема (.find, .text)
    4 на выходе json файл, каждый айтем записывается сразу
    '''

    soup = BeautifulSoup(page, 'lxml')
    jobs_items = soup.find_all('li', class_='list-jobs__item')  # после названия переменной добавть тип данных которой
    # она соответствует
    for job_item in jobs_items:
        job_name: str = job_item.find('div', class_='list-jobs__title').find('span').text.strip()
        job_url: str = job_item.find('div', class_='list-jobs__title').find('a', class_='profile').get('href')
        salary_tag = job_item.find('span', class_='public-salary-item')
        salary = None
        if salary_tag is not None:
            salary: Union[str, None] = salary_tag.text.strip()
        short_description: str = job_item.find('div', class_='list-jobs__description').text.strip()
        yield create_item_main_page(job_name, job_url, salary, short_description)


def parse_salary(raw_salary: str) -> Optional[float]:
    if not isinstance(raw_salary, str):
        return  # если нужно вернуть None просто пишем пустой return
    stripped_salary = raw_salary.strip('до $ € up to from от')
    salary_range = stripped_salary.split('-')
    if salary_range[0].isdigit():
        return float(salary_range[0])
    print('wrong salary data')
    return


def create_item_main_page(job_name: str, job_url: str, salary: str, short_description: str):
    if not isinstance(job_url, str) or not job_url:
        return {}
    item = create_empty_item()
    item['job_url'] = create_full_url(job_url)
    item['main_job_name'] = job_name if isinstance(job_name, str) else ''
    item['main_description'] = short_description if isinstance(short_description, str) else ''
    parsed_salary = parse_salary(salary)
    item['main_salary'] = parsed_salary if parsed_salary is not None else ''
    return item


def parse_subpage(page: str, item: dict):
    soup = BeautifulSoup(page, 'lxml')
    full_description = soup.find_all('div', class_='profile-page-section')
    description_tags = [tag for tag in full_description if 'text-small' not in tag.attrs.get('class', [])]
    return subpage_update_item(item, description_tags)


def subpage_update_item(item: dict, description_tags: List[Tag]) -> dict:
    descriptions = [remove_special_symbols(tag.text) for tag in description_tags]
    description = '\n'.join(descriptions)
    item['subpage_description'] = description
    return item


def remove_special_symbols(string: str) -> str:
    if not string:
        return ''
    stripped_string = string.strip()
    splitted_string = stripped_string.split()
    return ' '.join(splitted_string)


def create_empty_item():
    return {
        'main_job_name': '',
        'job_url': '',
        'main_salary': '',
        'main_description': '',
        'subpage_description': ''
    }


def create_full_url(url) -> str:
    # take part of url for subpage and make full and working URL
    return f'http://djinni.co{url}'
