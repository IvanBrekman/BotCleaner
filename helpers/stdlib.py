from datetime import datetime, timezone

DEBUG_LEVEL = 4
NEW_LINE    = "\n"


class Colors:
    BLACK   = "\033[1;30m"
    RED     = "\033[1;31m"
    GREEN   = "\033[1;32m"
    ORANGE  = "\033[1;33m"
    BLUE    = "\033[1;34m"
    PURPLE  = "\033[1;35m"
    CYAN    = "\033[1;36m"
    GRAY    = "\033[1;37m"

    NATURAL = "\033[0m"

    SWAPS   = {
        BLACK:      "<span style='color:black'>",
        RED:        "<span style='color:red'>",
        GREEN:      "<span style='color:green'>",
        ORANGE:     "<span style='color:orange'>",
        BLUE:       "<span style='color:blue'>",
        PURPLE:     "<span style='color:purple'>",
        CYAN:       "<span style='color:cyan'>",
        GRAY:       "<span style='color:gray'>",

        NATURAL:    "</span>",
        NEW_LINE:   "<br>"
    }


def LOGN(*args, level, **kwargs) -> None:
    assert isinstance(level, int), f"level: ({level}) is not integer"
    assert -1 <= level <= 9,        f"level value should be -1..9, got ({level})"

    skip, skip_up, skip_down = kwargs.pop("skip", 0), kwargs.pop("skipu", 0), kwargs.pop("skipd", 0)
    if skip > 0:
        skip_up = skip_down = skip
    print("\n" * skip_up, end='')

    if level == -1:
        print(Colors.RED, "!!! ATTENTION !!!", Colors.NATURAL, sep="")

    color    = Colors.CYAN if level == 1 else Colors.ORANGE if level == 2 else ""
    log_time = f"({level if level != -1 else 'e'})[{date_to_str(utc_to_local(datetime.utcnow()))}]"

    if DEBUG_LEVEL >= level:
        print(color + log_time + (Colors.NATURAL if level in (1, 2) else ""), end=" ")

    color = kwargs.get("color")
    if DEBUG_LEVEL >= level:
        if color:
            kwargs.pop("color")
            print(color, end="")

        if kwargs.get("sep") is not None and "\n" in kwargs["sep"]:
            kwargs["sep"] = kwargs["sep"].replace("\n", "\n" + " " * (len(log_time) + 1))
        if kwargs.get("end") is not None and "\n" in kwargs["end"]:
            kwargs["end"] = kwargs["end"].replace("\n", "\n" + " " * (len(log_time) + 1))

        args = list(args)
        for i, arg in enumerate(args):
            args[i] = arg.__str__().replace("\n", "\n" + " " * (len(log_time) + 1))
            args[i] = arg.__str__().replace(Colors.NATURAL, Colors.NATURAL + (color or ""))

        print(*args, **kwargs)
        print("\n" * skip_down, end='')

        if color:
            print(Colors.NATURAL, end="")

    if level == -1:
        print(Colors.RED, "!!! ATTENTION !!!", Colors.NATURAL, sep="")


def LOG1(*args, **kwargs) -> None:
    LOGN(level=1, *args, **kwargs)


def LOG2(*args, **kwargs) -> None:
    LOGN(level=2, *args, **kwargs)


def utc_to_local(utc_dt: datetime) -> datetime:
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None).replace(tzinfo=None)


def date_to_str(date: datetime, format_="%d.%m.%Y %H:%M:%S.%f"):
    return date.strftime(format_)


def colored(string: str, color: str) -> str:
    string = string.replace(Colors.NATURAL, Colors.NATURAL + color)
    return f"{color}{string}{Colors.NATURAL}"
