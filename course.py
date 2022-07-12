import requests
import re
from transliterate import translit
from config import error_answer
from print_funcs import error


class Format_var:
    # ? Removes unnecessary nulls in float variable
    def remove_unnecessary_nulls(self, num: float) -> float:
        for _ in range(len(str(num-int(num))[2:])):
            if str(num)[-1] == 0:
                num = str(num)[:len(str(num))-1]
            else:
                break
        return num

    # ? Removes brackets and their content
    def remove_text_between_parens(self, text: str) -> str:
        n = 1
        while n:
            text, n = re.subn(r'\([^()]*\)', '', text)
        return text

    def format_to_file_name(self, text: str) -> str:
        text = text.replace(" ", "_")
        text = (translit(text, language_code="ru", reversed=True)).lower()
        return text


class Course:
    # ? Returns message content for telegram
    def get_course(self, cur: str) -> str:
        try:

            format_var = Format_var()

            url = "https://www.cbr-xml-daily.ru/daily_json.js"

            r = requests.get(url).json()

            if cur is None or cur == "":
                cur = "usd"

            format_var = Format_var()

            match cur.lower():

                case "rub":
                    # ? Currency info

                    cur_abbr = "RUB"

                    cur_name = "Российский Рубль"

                    cur_value = float(format_var.remove_unnecessary_nulls(
                        round(1 / r["Valute"]["USD"]["Value"], 4)))

                    cur_previous_value = float(format_var.remove_unnecessary_nulls(
                        round(1 / r["Valute"]["USD"]["Previous"], 4)))

                    cur_change = abs(format_var.remove_unnecessary_nulls(
                        round(((cur_previous_value - cur_value) / cur_previous_value) * 100, 2)))

                    if cur_previous_value > cur_value:
                        cur_change = f"-{cur_change}"
                        change_emoji = "\U0001F4C9"
                    else:
                        cur_change = f"+{cur_change}"
                        change_emoji = "\U0001F4C8"

                    answer = (f"Курс {cur_abbr} ({cur_name}):  {cur_value}$\n"
                              f"Предыдущее значение:  {cur_previous_value}$\n"
                              f"Изменение:  {cur_change}% {change_emoji}")

                case _:
                    cur_abbr = r["Valute"][cur.upper()]["CharCode"]

                    cur_name = format_var.remove_text_between_parens(
                        r["Valute"][cur.upper()]["Name"].strip())

                    cur_value = format_var.remove_unnecessary_nulls(
                        round(r["Valute"][cur.upper()]["Value"], 2))

                    cur_previous_value = format_var.remove_unnecessary_nulls(
                        round(r["Valute"][cur.upper()]["Previous"], 2))

                    cur_change = abs(format_var.remove_unnecessary_nulls(
                        round(((cur_previous_value - cur_value) / cur_previous_value) * 100, 2)))

                    if cur_previous_value > cur_value:
                        cur_change = f"-{cur_change}"
                        change_emoji = "\U0001F4C9"
                    else:
                        cur_change = f"+{cur_change}"
                        change_emoji = "\U0001F4C8"

                    answer = (f"Курс {cur_abbr} ({cur_name}):  {cur_value}₽\n"
                              f"Предыдущее значение:  {cur_previous_value}₽\n"
                              f"Изменение:  {cur_change}% {change_emoji}")

        except Exception as ex:

            error('CUR', ex)
            answer = error_answer

        return answer


def main():
    cur = input("Введите валюту >>> ")
    course = Course()
    print(course.get_course(cur))


if __name__ == "__main__":
    main()
