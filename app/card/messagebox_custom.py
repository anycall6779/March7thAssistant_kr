from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap, QDesktopServices, QFont
from qfluentwidgets import MessageBox, LineEdit, ComboBox, EditableComboBox, DateTimeEdit, BodyLabel, FluentStyleSheet, TextEdit
from typing import Optional
from module.config import cfg
import datetime
import json


class MessageBoxImage(MessageBox):
    def __init__(self, title: str, content: str, image: Optional[str | QPixmap], parent=None):
        super().__init__(title, content, parent)
        if image is not None:
            self.imageLabel = QLabel(parent)
            if isinstance(image, QPixmap):
                self.imageLabel.setPixmap(image)
            elif isinstance(image, str):
                self.imageLabel.setPixmap(QPixmap(image))
            else:
                raise ValueError("지원되지 않는 이미지 유형입니다.")
            self.imageLabel.setScaledContents(True)

            imageIndex = self.vBoxLayout.indexOf(self.textLayout) + 1
            self.vBoxLayout.insertWidget(imageIndex, self.imageLabel, 0, Qt.AlignCenter)


class MessageBoxSupport(MessageBoxImage):
    def __init__(self, title: str, content: str, image: str, parent=None):
        super().__init__(title, content, image, parent)

        self.yesButton.setText('다음에 할게요')
        self.cancelButton.setHidden(True)


class MessageBoxAnnouncement(MessageBoxImage):
    def __init__(self, title: str, content: str, image: Optional[str | QPixmap], parent=None):
        super().__init__(title, content, image, parent)

        self.yesButton.setText('확인')
        self.cancelButton.setHidden(True)
        self.setContentCopyable(True)


class MessageBoxHtml(MessageBox):
    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content, parent)

        self.buttonLayout.removeWidget(self.yesButton)
        self.buttonLayout.removeWidget(self.cancelButton)
        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.contentLabel = BodyLabel(content, parent)
        self.contentLabel.setObjectName("contentLabel")
        self.contentLabel.setOpenExternalLinks(True)
        self.contentLabel.linkActivated.connect(self.open_url)
        self.contentLabel.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        FluentStyleSheet.DIALOG.apply(self.contentLabel)

        self.buttonLayout.addWidget(self.cancelButton, 1, Qt.AlignVCenter)
        self.buttonLayout.addWidget(self.yesButton, 1, Qt.AlignVCenter)
        self.textLayout.addWidget(self.contentLabel, 0, Qt.AlignTop)

    def open_url(self, url):
        QDesktopServices.openUrl(QUrl(url))


class MessageBoxUpdate(MessageBoxHtml):
    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content, parent)

        self.yesButton.setText('다운로드')
        self.cancelButton.setText('확인')


class MessageBoxDisclaimer(MessageBoxHtml):
    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content, parent)

        self.yesButton.setText('나가기')
        self.cancelButton.setText('내용을 확인했습니다')
        self.setContentCopyable(True)


class MessageBoxEdit(MessageBox):
    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content, parent)

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText('확인')
        self.cancelButton.setText('취소')

        self.lineEdit = LineEdit(self)
        self.lineEdit.setText(self.content)
        self.textLayout.addWidget(self.lineEdit, 0, Qt.AlignTop)

        self.buttonGroup.setMinimumWidth(480)

    def getText(self):
        return self.lineEdit.text()


class MessageBoxEditMultiple(MessageBox):
    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content, parent)

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText('확인')
        self.cancelButton.setText('취소')

        self.textEdit = TextEdit(self)
        self.textEdit.setFixedHeight(250)
        self.textEdit.setText(self.content)
        self.textLayout.addWidget(self.textEdit, 0, Qt.AlignTop)

        self.buttonGroup.setMinimumWidth(480)

    def getText(self):
        return self.textEdit.toPlainText()


class MessageBoxDate(MessageBox):
    def __init__(self, title: str, content: datetime, parent=None):
        super().__init__(title, "", parent)

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText('확인')
        self.cancelButton.setText('취소')

        self.datePicker = DateTimeEdit(self)
        self.datePicker.setDateTime(content)

        self.textLayout.addWidget(self.datePicker, 0, Qt.AlignTop)

        self.buttonGroup.setMinimumWidth(480)

    def getDateTime(self):
        return self.datePicker.dateTime().toPyDateTime()


class MessageBoxInstance(MessageBox):
    def __init__(self, title: str, content: dict, configtemplate: str, parent=None):
        super().__init__(title, "", parent)
        self.content = content

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText('확인')
        self.cancelButton.setText('취소')

        self.buttonGroup.setMinimumWidth(480)

        font = QFont()
        font.setPointSize(11)

        with open(configtemplate, 'r', encoding='utf-8') as file:
            self.template = json.load(file)

        self.comboBox_dict = {}
        for type, names in self.template.items():
            titleLabel = QLabel(type, parent)
            titleLabel.setFont(font)
            self.textLayout.addWidget(titleLabel, 0, Qt.AlignTop)

            # comboBox = ComboBox()
            comboBox = EditableComboBox()

            has_default = False
            for name, info in names.items():
                item_name = f"{name} ({info})"
                comboBox.addItem(item_name)
                if self.content[type] == name:
                    comboBox.setCurrentText(item_name)
                    has_default = True
            if not has_default:
                comboBox.setText(self.content[type])

            self.textLayout.addWidget(comboBox, 0, Qt.AlignTop)
            self.comboBox_dict[type] = comboBox

        self.titleLabelInfo = QLabel("설명: 업데이트되지 않은 던전은 수동으로 이름을 입력할 수 있습니다. 개척력 소모는 선택한 던전 유형에 따라 결정됩니다.\n여기서 설정한 던전 이름은 이벤트나 일일 훈련의 해당 임무를 완료하는 데에도 사용됩니다.\n만약 해당 임무가 있더라도 완료하고 싶지 않다면, 해당 던전 이름을 '없음'으로 변경할 수 있습니다.", parent)
        self.textLayout.addWidget(self.titleLabelInfo, 0, Qt.AlignTop)


class MessageBoxNotify(MessageBox):
    def __init__(self, title: str, configlist: dict, parent=None):
        super().__init__(title.capitalize(), "", parent)
        self.configlist = configlist

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText('확인')
        self.cancelButton.setText('취소')

        self.buttonGroup.setMinimumWidth(480)

        font = QFont()
        font.setPointSize(10)
        self.textLayout.setSpacing(4)

        self.lineEdit_dict = {}
        for name, config in self.configlist.items():
            titleLabel = QLabel(name.capitalize(), parent)
            titleLabel.setFont(font)
            self.textLayout.addWidget(titleLabel, 0, Qt.AlignTop)

            lineEdit = LineEdit(self)
            lineEdit.setText(str(cfg.get_value(config)))
            lineEdit.setFont(font)

            self.textLayout.addWidget(lineEdit, 0, Qt.AlignTop)
            self.lineEdit_dict[config] = lineEdit


class MessageBoxNotifyTemplate(MessageBox):
    def __init__(self, title: str, content: dict, parent=None):
        super().__init__(title, "", parent)
        self.content = content

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText('확인')
        self.cancelButton.setText('취소')

        self.buttonGroup.setMinimumWidth(480)

        font = QFont()
        font.setPointSize(9)
        self.textLayout.setSpacing(4)

        self.lineEdit_dict = {}
        for id, template in self.content.items():
            lineEdit = LineEdit(self)
            lineEdit.setText(template.replace("\n", r"\n"))
            lineEdit.setFont(font)

            lineEdit.setFixedHeight(22)
            self.buttonLayout.setContentsMargins(24, 10, 24, 10)
            self.textLayout.setContentsMargins(24, 24, 24, 6)
            self.textLayout.addWidget(lineEdit, 0, Qt.AlignTop)

            self.lineEdit_dict[id] = lineEdit

        self.titleLabelInfo = QLabel("설명: { } 안의 내용은 실제 전송 시 대체되며, \\n은 줄 바꿈을 의미합니다.", parent)
        self.textLayout.addWidget(self.titleLabelInfo, 0, Qt.AlignTop)


class MessageBoxTeam(MessageBox):
    def __init__(self, title: str, content: dict, template: dict, parent=None):
        super().__init__(title, "", parent)
        self.content = content

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText('확인')
        self.cancelButton.setText('취소')

        self.buttonGroup.setMinimumWidth(400)

        font = QFont()
        font.setPointSize(12)

        self.template = template

        self.tech_map = {
            -1: "비술 / 전투 시작",
            0: "동작 없음",
            1: "비술 1회",
            2: "비술 2회",
        }

        self.comboBox_list = []
        for i in range(1, 5):
            titleLabel = QLabel(f"{i}번 캐릭터", parent)
            titleLabel.setFont(font)
            self.textLayout.addWidget(titleLabel, 0, Qt.AlignTop)

            charComboBox = ComboBox()
            charComboBox.setMaximumWidth(150)
            charComboBox.addItems(self.template.values())
            charComboBox.setCurrentText(self.template[self.content[i - 1][0]])

            techComboBox = ComboBox()
            techComboBox.setMaximumWidth(150)
            techComboBox.addItems(self.tech_map.values())
            techComboBox.setCurrentText(self.tech_map[self.content[i - 1][1]])

            horizontalLayout = QHBoxLayout()
            horizontalLayout.addWidget(charComboBox)
            horizontalLayout.addWidget(techComboBox)
            self.textLayout.addLayout(horizontalLayout)

            self.comboBox_list.append((charComboBox, techComboBox))

        self.titleLabelInfo = QLabel("설명: 각 파티에서는 한 명의 캐릭터만 '비술 / 전투 시작'으로 설정할 수 있습니다.\n숫자는 비술 사용 횟수를 의미하며, -1은 마지막으로 비술을 사용하고 전투를 시작하는 캐릭터를 의미합니다.", parent)
        self.textLayout.addWidget(self.titleLabelInfo, 0, Qt.AlignTop)


class MessageBoxFriends(MessageBox):
    def __init__(self, title: str, content: dict, template: dict, parent=None):
        super().__init__(title, "", parent)
        self.content = content

        self.textLayout.removeWidget(self.contentLabel)
        self.contentLabel.clear()

        self.yesButton.setText('확인')
        self.cancelButton.setText('취소')

        self.buttonGroup.setMinimumWidth(400)

        font = QFont()
        font.setPointSize(12)

        self.template = template

        self.comboBox_list = []
        for i in range(1, 7):

            charComboBox = ComboBox()
            charComboBox.setMaximumWidth(150)
            charComboBox.addItems(self.template.values())
            charComboBox.setCurrentText(self.template[self.content[i - 1][0]])

            nameLineEdit = LineEdit()
            nameLineEdit.setMaximumWidth(150)
            nameLineEdit.setText(self.content[i - 1][1])

            horizontalLayout = QHBoxLayout()
            horizontalLayout.addWidget(charComboBox)
            horizontalLayout.addWidget(nameLineEdit)
            self.textLayout.addLayout(horizontalLayout)

            self.comboBox_list.append((charComboBox, nameLineEdit))

        self.titleLabelInfo = QLabel("설명: 왼쪽에서 캐릭터를 선택한 후, 오른쪽 해당 텍스트 상자에 친구 이름을 입력하세요.\n예를 들어 친구 이름이 '홍길동전'일 경우, '홍길동'만 입력해도 매칭에 성공할 수 있습니다.\n친구 이름 칸을 비워두면 선택한 캐릭터만 검색합니다.", parent)
        self.textLayout.addWidget(self.titleLabelInfo, 0, Qt.AlignTop)