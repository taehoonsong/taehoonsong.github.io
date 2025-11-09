import datetime as dt
import subprocess
import time
from pathlib import Path

from watchdog.events import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileSystemEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer, ObserverType

WATCH_PATHS = [
    Path("content"),
    Path("static"),
    Path("templates"),
    Path("build.sh"),
    Path("generate_website.py"),
]


class Handler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def rebuild(event: FileSystemEvent) -> None:
        print(f"{dt.datetime.now().isoformat()}: {event.src_path} {event.event_type}")  # noqa: T201
        subprocess.call("./build.sh")

    def on_modified(self, event: FileSystemEvent) -> None:
        if not isinstance(event, FileModifiedEvent):
            return
        self.rebuild(event)

    def on_created(self, event: FileSystemEvent) -> None:
        if not isinstance(event, FileCreatedEvent):
            return
        self.rebuild(event)

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not isinstance(event, FileDeletedEvent):
            return
        self.rebuild(event)


def init_observer(paths: list[Path]) -> ObserverType:
    event_handler = Handler()
    obs = Observer()

    for path in paths:
        obs.schedule(event_handler, str(path), recursive=True)

    return obs


if __name__ == "__main__":
    observer = init_observer(WATCH_PATHS)
    print("Starting watchdog...")  # noqa: T201

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
