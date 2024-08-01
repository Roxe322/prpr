import re
from datetime import datetime
from typing import Optional

from loguru import logger
from rich import box
from rich.console import Console
from rich.table import Table

from prpr.homework import Homework, Status

DISPLAYED_TAIL_LENGTH = None

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

def print_issue_table(homeworks: list[Homework], last=None, last_processed=None, title: Optional[str] = None):
    if not homeworks:
        logger.warning("No homeworks for chosen filter combination.")
        return
    table = setup_table(homeworks, title)

    start_from = -last if last else last
    for table_number, homework in enumerate(homeworks[start_from:], 1):
        # Construct the student_display with name and email on separate lines if email exists
        student_name, student_email = _split_student_info(homework.student)
        student_display = student_name
        if student_email:
            student_display += f"\n{student_email}"

        # Construct the issue URL with lesson name if it exists
        issue_url_with_lesson = homework.issue_url
        if homework.lesson_name:
            issue_url_with_lesson += f"\n[green]{homework.lesson_name}"

        row_columns = (  # TODO: Move to Homework
            str(table_number),
            issue_url_with_lesson,
            # str(homework.number), # TODO: Лишняя колонка если берем список только используемых работ с сервера
            str(homework.problem),
            homework.iteration and str(homework.iteration),
            student_display,
            homework.cohort,
            homework.pretty_status,
            homework.deadline_string,
            homework.left,
            homework.updated_string,
        )
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


def setup_table(homeworks: list[Homework], title: Optional[str] = None) -> Table:
    table = Table(title=title, box=box.MINIMAL_HEAVY_HEAD)
    table.add_column("#", justify="right", style="green")
    min_ticket_width = max(len(hw.issue_url) for hw in homeworks) if homeworks else None
    table.add_column("ticket", min_width=min_ticket_width)
    # table.add_column("no", justify="right") # TODO: Лишняя колонка если берем список только используемых работ с сервера
    table.add_column("pr", justify="right")
    table.add_column("i")
    table.add_column("student")
    table.add_column("co", justify="right")
    table.add_column("st")
    table.add_column("deadline", justify="right")
    table.add_column("left", justify="right")
    table.add_column("updated")
    table.header_style = "yellow"  # Стиль текста в заголовке таблице (первой строке)
    table.border_style = "dim blue"  # Стиль границ таблицы
    table.title_style = "bold blue" # Стиль текста в заголовке таблицы, My Praktikum Review Tickets
    table.pad_edge = False  # меньше расстояние между границами
    # Другие стили тут https://rich.readthedocs.io/en/stable/tables.html#table-options
    # TODO: column count should always match tuple length; configure together.
    return table
