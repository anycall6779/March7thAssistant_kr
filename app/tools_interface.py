from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSpacerItem
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import SettingCardGroup, PushSettingCard, ScrollArea, InfoBar, InfoBarPosition, MessageBox
from .card.messagebox_custom import MessageBoxEditMultiple
from .card.pushsettingcard1 import PushSettingCardCode
from .common.style_sheet import StyleSheet
from utils.registry.star_rail_setting import get_game_fps, set_game_fps, get_graphics_setting
import tasks.tool as tool
import base64
import subprocess
import pyperclip
from module.config import cfg
import os


class ToolsInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)

        self.toolsLabel = QLabel(self.tr("툴박스"), self)

        self.ToolsGroup = SettingCardGroup(self.tr('툴박스'), self.scrollWidget)
        self.automaticPlotCard = PushSettingCard(
            self.tr('실행'),
            FIF.IMAGE_EXPORT,
            self.tr("자동 대화"),
            ''
        )
        self.gameScreenshotCard = PushSettingCard(
            self.tr('캡처'),
            FIF.CLIPPING_TOOL,
            self.tr("게임 스크린샷"),
            self.tr("프로그램이 이미지를 올바르게 가져오는지 확인하고, OCR 문자 인식을 지원합니다 (던전 이름 복사에 사용 가능)")
        )
        self.unlockfpsCard = PushSettingCard(
            self.tr('해제'),
            FIF.SPEED_HIGH,
            self.tr("프레임 속도 해제"),
            self.tr("레지스트리 수정을 통해 120프레임을 해제합니다. 이미 해제된 경우 다시 클릭하면 60프레임으로 복원됩니다 (글로벌 서버는 테스트되지 않음)")
        )
        self.redemptionCodeCard = PushSettingCardCode(
            self.tr('실행'),
            FIF.BOOK_SHELF,
            self.tr("리딤 코드"),
            "redemption_code",
            self
        )
        self.cloudTouchCard = PushSettingCard(
            self.tr('시작'),
            FIF.CLOUD,
            self.tr("터치스크린 모드 (현재 사용 불가)"),
            self.tr("클라우드 게임 모바일 UI로 게임을 시작하며, Sunshine 및 Moonlight와 함께 사용할 수 있습니다. 시작 후 명령어가 클립보드에 복사됩니다")
        )
        self.cloudTouchCard.setDisabled(True)

        self.__initWidget()

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('toolsInterface')

        self.scrollWidget.setObjectName('scrollWidget')
        self.toolsLabel.setObjectName('toolsLabel')
        StyleSheet.TOOLS_INTERFACE.apply(self)

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.toolsLabel.move(36, 30)

        self.ToolsGroup.addSettingCard(self.automaticPlotCard)
        self.ToolsGroup.addSettingCard(self.gameScreenshotCard)
        self.ToolsGroup.addSettingCard(self.unlockfpsCard)
        self.ToolsGroup.addSettingCard(self.redemptionCodeCard)
        self.ToolsGroup.addSettingCard(self.cloudTouchCard)

        self.ToolsGroup.titleLabel.setHidden(True)

        self.vBoxLayout.setSpacing(28)
        self.vBoxLayout.setContentsMargins(36, 10, 36, 0)
        self.vBoxLayout.addWidget(self.ToolsGroup)

        for i in range(self.ToolsGroup.vBoxLayout.count()):
            item = self.ToolsGroup.vBoxLayout.itemAt(i)
            if isinstance(item, QSpacerItem):
                self.ToolsGroup.vBoxLayout.removeItem(item)
                break

    def __onUnlockfpsCardClicked(self):
        try:
            fps = get_game_fps()
            if fps == 120:
                set_game_fps(60)
                InfoBar.success(
                    title=self.tr('60프레임 복원 성공 (＾∀＾●)'),
                    content="",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=1000,
                    parent=self
                )
            else:
                set_game_fps(120)
                InfoBar.success(
                    title=self.tr('120프레임 해제 성공 (＾∀＾●)'),
                    content="",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=1000,
                    parent=self
                )
        except:
            InfoBar.warning(
                title=self.tr('해제 실패'),
                content="게임 그래픽 품질을 '사용자 정의'로 변경한 후 다시 시도하세요",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

    def __onCloudTouchCardClicked(self):
        try:
            if not os.path.exists(cfg.game_path):
                InfoBar.warning(
                    title=self.tr('게임 경로 설정 오류(╥╯﹏╰╥)'),
                    content="'설정' --> '프로그램'에서 경로를 설정해주세요",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
                return
            graphics_setting = get_graphics_setting()
            if graphics_setting is None:
                raise Exception("게임 그래픽 품질을 '사용자 정의'로 변경한 후 다시 시도하세요")
            args = ["-is_cloud", "1", "-platform_type", "CLOUD_WEB_TOUCH", "-graphics_setting", base64.b64encode(graphics_setting).decode("utf-8")]
            subprocess.Popen([cfg.game_path] + args)
            pyperclip.copy(f'"{cfg.game_path}" {" ".join(args)}')
            InfoBar.success(
                title=self.tr('시작 성공(＾∀＾●)'),
                content="명령어가 클립보드에 복사되었습니다",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        except Exception as e:
            InfoBar.warning(
                title=self.tr('시작 실패'),
                content=str(e),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

    def __connectSignalToSlot(self):
        self.gameScreenshotCard.clicked.connect(lambda: tool.start("screenshot"))
        self.automaticPlotCard.clicked.connect(lambda: tool.start("plot"))
        self.unlockfpsCard.clicked.connect(self.__onUnlockfpsCardClicked)
        self.cloudTouchCard.clicked.connect(self.__onCloudTouchCardClicked)