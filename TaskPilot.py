"""Punto de entrada de TaskPilot."""

from taskpilot.app import TaskPilot


def main():
    app = TaskPilot()
    app.mainloop()


if __name__ == "__main__":
    main()
