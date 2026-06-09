from rich.progress import ProgressColumn, Task, TaskProgressColumn
from rich.text import Text


class SpeedColumn(ProgressColumn):
    def render(self, task: Task) -> Text:
        return TaskProgressColumn.render_speed(task.finished_speed or task.speed)
