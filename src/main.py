from src.applications import Application


def main():
    success_f = Application().run()

    if not success_f:
        raise RuntimeError('application failure')


if __name__ == '__main__':
    main()
