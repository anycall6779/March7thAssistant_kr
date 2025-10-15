from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QStackedWidget, QSpacerItem
from qfluentwidgets import qconfig, ScrollArea, Pivot
from .common.style_sheet import StyleSheet
import markdown
import sys


class HelpInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)

        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)

        self.helpLabel = QLabel(self.tr("도움말"), self)
        self.tutorialLabel = QLabel(parent)
        self.faqLabel = QLabel(parent)
        self.tasksLabel = QLabel(parent)
        self.changelogLabel = QLabel(parent)

        self.__initWidget()
        self.__initCard()
        self.__initLayout()

    def __initWidget(self):
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setViewportMargins(0, 140, 0, 5)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setObjectName('helpInterface')
        self.scrollWidget.setObjectName('scrollWidget')
        self.helpLabel.setObjectName('helpLabel')
        StyleSheet.HELP_INTERFACE.apply(self)

    def __initCard(self):
        tutorial_style = """
<style>
a {
    color: #f18cb9;
    font-weight: bold;
}
</style>
"""
        try:
            with open("./assets/docs/Tutorial.md", 'r', encoding='utf-8') as file:
                self.content = file.read().replace('/assets/docs/Background.md', 'https://m7a.top/#/assets/docs/Background')
                self.content = '\n'.join(self.content.split('\n')[1:])
        except FileNotFoundError:
            sys.exit(1)
        tutorial_content = tutorial_style + markdown.markdown(self.content).replace('<h2>', '<br><h2>').replace('</h2>', '</h2><hr>').replace('<br>', '', 1) + '<br>'
        self.tutorialLabel.setText(tutorial_content)
        self.tutorialLabel.setOpenExternalLinks(True)
        self.tutorialLabel.linkActivated.connect(self.open_url)

        faq_style = """
<style>
a {
    color: #f18cb9;
    font-weight: bold;
}
</style>
"""
        try:
            with open("./assets/docs/FAQ.md", 'r', encoding='utf-8') as file:
                self.content = file.read()
                self.content = '\n'.join(self.content.split('\n')[2:])
        except FileNotFoundError:
            sys.exit(1)
        faq_content = faq_style + markdown.markdown(self.content).replace('<h3>', '<br><h3>').replace('</h3>', '</h3><hr>').replace('<br>', '', 1) + '<br>'
        self.faqLabel.setText(faq_content)
        self.faqLabel.setOpenExternalLinks(True)
        self.faqLabel.linkActivated.connect(self.open_url)

        qconfig.themeChanged.connect(self.__themeChanged)
        tasks_style = """
<style>
table {
  border-collapse: collapse;
  width: 100%;
}

th, td {
  border: 1px solid black;
  padding: 1px 30px 1px 30px;
  text-align: left;
  font-size: 15px;
}
</style>
"""
        self.content = """
| 임무 설명                                       | 지원 여부 | 완료 방법         |
| :---------------------------------------------- | :-------: | :---------------- |
| 게임 로그인                                     |     ✅    |                   |
| 일일 임무 1개 완료                              |     ❌    |                   |
| 개척력 120pt 누적 소모                          |     ✅    |                   |
| 「의식의 고치(금)」 1회 클리어                  |     ✅    |                   |
| 「의식의 고치(적)」 1회 클리어                  |     ✅    |                   |
| 「정체된 허영」 1회 클리어                      |     ✅    |                   |
| 「부식의 동굴」 1회 클리어                      |     ✅    |                   |
| 단일 전투에서 3가지 속성의 약점 격파 발동       |     ✅    | 망각의 정원 1층   |
| 약점 격파 누적 5회 발동                         |     ✅    | 망각의 정원 1층   |
| 적 20기 누적 처치                               |     ✅    | 망각의 정원 1층   |
| 약점을 이용해 전투 진입 후 3회 승리             |     ✅    | 망각의 정원 1층   |
| 비술 누적 2회 사용                              |     ✅    | 히메코 체험       |
| 의뢰 1회 파견                                   |     ✅    |                   |
| 사진 촬영 1회                                   |     ✅    |                   |
| 파괴 가능한 오브젝트 3개 누적 파괴              |     ✅    | 히메코 체험       |
| 「망각의 정원」 1회 클리어                      |     ✅    | 망각의 정원 1층   |
| 「고치(歷戰餘響)」 1회 클리어                    |     ✅    |                   |
| 「시뮬레이션 우주」(임의의 세계) 1개 구역 클리어 |     ✅    |                   |
| 「시뮬레이션 우주」 1회 클리어                  |     ✅    |                   |
| 지원 캐릭터를 사용하여 전투 1회 승리            |     ✅    | 개척력 소모       |
| 필살기를 사용하여 마지막 일격 1회 가하기        |     ✅    | 망각의 정원 1층   |
| 임의의 캐릭터 레벨 1회 승급                     |     ❌    |                   |
| 임의의 광추 레벨 1회 승급                       |     ❌    |                   |
| 임의의 유물 레벨 1회 승급                       |     ❌    |                   |
| 임의의 유물 1개 분해                            |     ❌    |                   |
| 「만능 합성기」 1회 사용                        |     ✅    |                   |
| 소모품 1회 합성                                 |     ✅    |                   |
| 재료 1회 합성                                   |     ✅    |                   |
| 소모품 1개 사용                                 |     ✅    |                   |
        """
        self.tasks_content = tasks_style + markdown.markdown(self.content, extensions=['tables'])

        if qconfig.theme.name == "DARK":
            self.tasksLabel.setText(self.tasks_content.replace("border: 1px solid black;", "border: 1px solid white;"))
        else:
            self.tasksLabel.setText(self.tasks_content)

        changelog_style = """
<style>
a {
    color: #f18cb9;
    font-weight: bold;
}
</style>
"""
        try:
            with open("./assets/docs/Changelog.md", 'r', encoding='utf-8') as file:
                self.content = file.read()
                self.content = '\n'.join(self.content.split('\n')[1:])
        except FileNotFoundError:
            sys.exit(1)
        changelog_content = changelog_style + markdown.markdown(self.content).replace('<h2>', '<br><h2>').replace('</h2>', '</h2><hr>').replace('<br>', '', 1) + '<br>'
        self.changelogLabel.setText(changelog_content)
        self.changelogLabel.setOpenExternalLinks(True)
        self.changelogLabel.linkActivated.connect(self.open_url)

    def __initLayout(self):
        self.helpLabel.move(36, 30)
        self.pivot.move(40, 80)
        # self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.stackedWidget, 0, Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 0, 36, 0)

        # self.vBoxLayout.addWidget(self.tutorialLabel, 0, Qt.AlignTop)
        self.addSubInterface(self.tutorialLabel, 'tutorialLabel', self.tr('사용 가이드'))
        self.addSubInterface(self.faqLabel, 'faqLabel', self.tr('자주 묻는 질문'))
        self.addSubInterface(self.tasksLabel, 'tasksLabel', self.tr('일일 훈련'))
        self.addSubInterface(self.changelogLabel, 'changelogLabel', self.tr('업데이트 로그'))

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.pivot.setCurrentItem(self.stackedWidget.currentWidget().objectName())
        self.stackedWidget.setFixedHeight(self.stackedWidget.currentWidget().sizeHint().height())

    def addSubInterface(self, widget: QLabel, objectName, text):
        def remove_spacing(layout):
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if isinstance(item, QSpacerItem):
                    layout.removeItem(item)
                    break

        # remove_spacing(widget.vBoxLayout)
        # widget.titleLabel.setHidden(True)

        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())

        self.verticalScrollBar().setValue(0)
        self.stackedWidget.setFixedHeight(self.stackedWidget.currentWidget().sizeHint().height())

    def open_url(self, url):
        QDesktopServices.openUrl(QUrl(url))

    def __themeChanged(self):
        if qconfig.theme.name == "DARK":
            self.tasksLabel.setText(self.tasks_content.replace("border: 1px solid black;", "border: 1px solid white;"))
        else:
            self.tasksLabel.setText(self.tasks_content)
