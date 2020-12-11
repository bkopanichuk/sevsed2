from apps.document.models.task_model import Task


class ChangeTaskOrder:
    """Змінити порядок виконання завдань"""

    ## TODO Додати функціональність зміни порядку виконання завдан
    def __init__(self, task: Task, order: str):
        self.task: Task = task
        self.order = order

    def run(self):
        self.change_order()

    def change_order(self):
        """змінити порядок
        dwadawda dwadwad dwaad aw"""

        pass

    def down_order(self):
        """підняти задачу на пункт вище"""
        pass

    def up_order(self):
        """опустити задачу на пункт нижче"""
        pass