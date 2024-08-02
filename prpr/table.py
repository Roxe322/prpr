import re
from datetime import datetime
from typing import Optional, TypeVar, cast

from loguru import logger
from rich import box
from rich.console import Console
from rich.padding import Padding, PaddingDimensions
from rich.table import Table

from prpr.config import get_config
from prpr.filters import FilterMode
from prpr.homework import Homework, Status

DISPLAYED_TAIL_LENGTH = None

T = TypeVar('T')
def _split_student_info(student: str) -> tuple[str, str]:
    """
    Split the student's information into name and email.

    Args:
        student (str): The student's information in the format 'name lastname (email)'.

    Returns:
        tuple[str, str]: A tuple containing the student's name and email.
    """
    if match := re.match(r"^(?P<name>.*?) \((?P<email>.*)\)$", student):
        # e.g. 'name lastname (email)'
        student_name = match.group("name").strip()
        student_email = match.group("email").strip()
    else:
        student_name = student
        student_email = ""
    return student_name, student_email

def retrieve_table_appearance():
    config = get_config()
    table_appearance = config.get("table_appearance") or {}
    return table_appearance


def retrieve_box_style(table_appearance, style_key, default):
    value = table_appearance.get(style_key, default)
    if not isinstance(value, str):
        return value
    try:
        return getattr(box, value)
    except (ValueError, AttributeError):
        logger.warning(f"Box style '{value}' from config not found. used default")
        return default


def retrieve_padding(table_appearance, style_key: str, default: PaddingDimensions) -> PaddingDimensions:
    value = table_appearance.get(style_key, default)
    if isinstance(value, str):
        return Padding.unpack(get_padding(value))
    return default

def get_padding(value: str) -> PaddingDimensions:
    return cast(PaddingDimensions, tuple(int(x) for x in value.split(',')))

def print_issue_table(homeworks: list[Homework], mode: FilterMode, last=None, last_processed=None, title: Optional[str] = None):
    if not homeworks:
        logger.warning("No homeworks for chosen filter combination.")
        return
    is_short_table = mode in {FilterMode.STANDARD, FilterMode.OPEN}
    table_appearance = retrieve_table_appearance()
    table = setup_table(homeworks, table_appearance, is_short_table, title)

    start_from = -last if last else last
    for table_number, homework in enumerate(homeworks[start_from:], 1):
        # Construct the student_display with name and email on separate lines if email exists
        student_name, student_email = _split_student_info(homework.student)
        student_display = student_name
        if student_email:
            email_style = table_appearance.get("email_style", "")
            student_display += f"\n{email_style}{student_email}"

        # Construct the issue URL with lesson name if it exists
        issue_url_with_lesson = homework.issue_url
        if homework.lesson_name:
            lesson_name_style = table_appearance.get("lesson_name_style", "")
            issue_url_with_lesson += (f"\n{lesson_name_style}"
                                      f"{homework.lesson_name}")

        row_columns = [  # TODO: Move to Homework
            str(table_number),
            issue_url_with_lesson,
            ]

        if not is_short_table:
            row_columns.append(str(homework.number))

        row_columns += [
            str(homework.problem),
            homework.iteration and str(homework.iteration),
            student_display,
            homework.cohort,
            homework.pretty_status,
            homework.deadline_string,
            homework.left,
            homework.updated_string,
        ]
        table.add_row(
            *row_columns,
            style=compute_style(homework, last_processed=last_processed),
        )

    console = Console()
    console.print(table)


def compute_style(homework: Homework, last_processed=None):  # TODO: consider moving to Homework
    if homework == last_processed:
        return "dim"
    if homework.deadline_missed:
        return "red"  # TODO: Move to dotfile
    if homework.deadline and homework.deadline.date() == datetime.now().date():
        return "bold"
    if homework.status == Status.ON_THE_SIDE_OF_USER:
        return "dim"


def setup_table(homeworks: list[Homework], table_appearance: dict, is_short_table: bool, title: Optional[str] = None) -> Table:
    table = Table(title=title, box=retrieve_box_style(table_appearance, "box_style", default=box.MINIMAL_HEAVY_HEAD))
    table.add_column("#", justify="right", style=table_appearance.get("number_style", ""))
    min_ticket_width = max(len(hw.issue_url) for hw in homeworks) if homeworks else None
    table.add_column("ticket", min_width=min_ticket_width)
    if not is_short_table:
        table.add_column("no", justify="right")
    table.add_column("pr", justify="right")
    table.add_column("i")
    table.add_column("student")
    table.add_column("co", justify="right")
    table.add_column("st")
    table.add_column("deadline", justify="right")
    table.add_column("left", justify="right")
    table.add_column("updated")
    table.leading = table_appearance.get("leading", False)
    table.padding = retrieve_padding(table_appearance,"padding", default=(0, 1))
    table.header_style = table_appearance.get("header_style", "")  # Стиль текста в заголовке таблице (первой строке)
    table.border_style = table_appearance.get("border_style", "")  # Стиль границ таблицы
    table.title_style = table_appearance.get("title_style", "") # Стиль текста в заголовке таблицы, My Praktikum Review Tickets

    # Меньше расстояние между границами если False. True по умолчанию, оставил дефолт как было, чтобы не портить внешний вид кто не задал в настройках
    table.pad_edge = table_appearance.get("pad_edge", True)
    # Другие стили тут https://rich.readthedocs.io/en/stable/tables.html#table-options
    # TODO: column count should always match tuple length; configure together.
    return table
