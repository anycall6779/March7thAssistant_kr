import os
import sys
# 현재 작업 디렉토리를 프로그램이 위치한 디렉토리로 설정합니다.
# 어디서 실행하든 작업 디렉토리가 올바르게 설정되어 경로 오류를 방지합니다.
os.chdir(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False)else os.path.dirname(os.path.abspath(__file__)))

import pyuac
if not pyuac.isUserAdmin():
    try:
        pyuac.runAsAdmin(False)
        sys.exit(0)
    except Exception:
        sys.exit(1)

import atexit
import base64

from module.config import cfg
from module.logger import log
from module.notification import notif
from module.ocr import ocr

import tasks.game as game
import tasks.reward as reward
import tasks.challenge as challenge
import tasks.tool as tool
import tasks.version as version

from tasks.daily.daily import Daily
from tasks.daily.fight import Fight
from tasks.power.power import Power
from tasks.weekly.universe import Universe
from tasks.daily.redemption import Redemption


def first_run():
    if not cfg.get_value(base64.b64decode("YXV0b191cGRhdGU=").decode("utf-8")):
        log.error("처음 사용하는 경우, 먼저 그래픽 인터페이스인 March7th Launcher.exe를 실행해주세요.")
        input("엔터 키를 누르면 창이 닫힙니다. . .")
        sys.exit(0)


def run_main_actions():
    while True:
        version.start()
        game.start()
        reward.start_specific("dispatch")
        Daily.start()
        reward.start()
        game.stop(True)


def run_sub_task(action):
    game.start()
    sub_tasks = {
        "daily": lambda: (Daily.run(), reward.start()),
        "power": Power.run,
        "fight": Fight.start,
        "universe": Universe.start,
        "forgottenhall": lambda: challenge.start("memoryofchaos"),
        "purefiction": lambda: challenge.start("purefiction"),
        "apocalyptic": lambda: challenge.start("apocalyptic"),
        "redemption": Redemption.start
    }
    task = sub_tasks.get(action)
    if task:
        task()
    game.stop(False)


def run_sub_task_gui(action):
    gui_tasks = {
        "universe_gui": Universe.gui,
        "fight_gui": Fight.gui
    }
    task = gui_tasks.get(action)
    if task and not task():
        input("엔터 키를 누르면 창이 닫힙니다. . .")
    sys.exit(0)


def run_sub_task_update(action):
    update_tasks = {
        "universe_update": Universe.update,
        "fight_update": Fight.update
    }
    task = update_tasks.get(action)
    if task:
        task()
    input("엔터 키를 누르면 창이 닫힙니다. . .")
    sys.exit(0)


def run_notify_action():
    notif.notify(cfg.notify_template['TestMessage'], "./assets/app/images/March7th.jpg")
    input("엔터 키를 누르면 창이 닫힙니다. . .")
    sys.exit(0)


def main(action=None):
    first_run()

    # 전체 실행
    if action is None or action == "main":
        run_main_actions()

    # 하위 작업
    elif action in ["daily", "power", "fight", "universe", "forgottenhall", "purefiction", "apocalyptic", "redemption"]:
        run_sub_task(action)

    # 하위 작업 네이티브 GUI
    elif action in ["universe_gui", "fight_gui"]:
        run_sub_task_gui(action)

    # 하위 작업 프로젝트 업데이트
    elif action in ["universe_update", "fight_update"]:
        run_sub_task_update(action)

    elif action in ["screenshot", "plot"]:
        tool.start(action)

    elif action == "game":
        game.start()

    elif action == "notify":
        run_notify_action()

    else:
        log.error(f"알 수 없는 작업: {action}")
        input("엔터 키를 누르면 창이 닫힙니다. . .")
        sys.exit(1)


# 프로그램 종료 시 핸들러
def exit_handler():
    """프로그램 종료 시 처리 함수를 등록하여 OCR 리소스를 정리합니다."""
    ocr.exit_ocr()


if __name__ == "__main__":
    try:
        atexit.register(exit_handler)
        main(sys.argv[1]) if len(sys.argv) > 1 else main()
    except KeyboardInterrupt:
        log.error("오류 발생: 수동으로 강제 중지됨")
        if not cfg.exit_after_failure:
            input("엔터 키를 누르면 창이 닫힙니다. . .")
        sys.exit(1)
    except Exception as e:
        log.error(cfg.notify_template['ErrorOccurred'].format(error=e))
        notif.notify(cfg.notify_template['ErrorOccurred'].format(error=e))
        if not cfg.exit_after_failure:
            input("엔터 키를 누르면 창이 닫힙니다. . .")
        sys.exit(1)