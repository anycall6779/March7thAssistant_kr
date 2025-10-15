from typing import Union
from qfluentwidgets import SettingCard, SettingCardGroup, ListWidget, FluentIconBase, CardWidget, FluentStyleSheet
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QListWidgetItem, QVBoxLayout, QMessageBox, QInputDialog, QLineEdit, QLabel
from PyQt5.QtWidgets import QHBoxLayout, QGridLayout, QFrame
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import QPalette
from module.config import cfg
from app.tools.account_manager import accounts, reload_all_account_from_files, dump_current_account, delete_account, \
    save_account_name, import_account, save_acc_and_pwd, clear_reg
from module.logger import log


class AccountsCard(QFrame):

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], title, content=None, texts=None, parent=None):
        super().__init__(parent=parent)
        FluentStyleSheet.SETTING_CARD.apply(self)
        self.setFixedHeight(400)
        #
        self.widget = ListWidget()
        self.wLayout = QGridLayout()
        self.wLayout.addWidget(self.widget)
        # self.widget.setStyleSheet("QListWidget{border: 1px solid #d9d9d9;} QListWidget::item{height: 30px;} QListWidget::item:selected{background-color: #f0f0f0;} QListWidget::item:hover{background-color: #f0f0f0;}")
        #
        self.buttons = QVBoxLayout()
        self.buttons.setContentsMargins(10, 3, 10, 3)
        self.tipsText = QLabel("중요: 게임에 완전히 진입한 후(캐릭터가 보일 때) 내보내기를 진행하세요. 그렇지 않으면 이전 계정의 UID를 읽어 파일과 계정이 일치하지 않을 수 있습니다.")
        self.tipsText.setWordWrap(True)
        self.tipsText.setStyleSheet('color: #f94e9b')
        self.buttons.addWidget(self.tipsText)
        self.tipsText.setFixedHeight(50)
        self.addAccountButton = QPushButton("현재 게임 계정 내보내기", self)
        self.importAccountButton = QPushButton("선택한 계정 가져오기", self)
        self.deleteAccountButton = QPushButton("계정 삭제", self)
        self.renameAccountButton = QPushButton("계정 이름 변경", self)
        self.autologinAccountButton = QPushButton("자동 로그인", self)
        self.refreshAccountButton = QPushButton("새로고침", self)
        self.clearRegButton = QPushButton("레지스트리 초기화", self)
        self.buttons.addWidget(self.addAccountButton)
        self.buttons.addWidget(self.importAccountButton)
        self.buttons.addWidget(self.deleteAccountButton)
        self.buttons.addWidget(self.renameAccountButton)
        self.buttons.addWidget(self.autologinAccountButton)
        self.buttons.addWidget(self.refreshAccountButton)
        self.buttons.addWidget(self.clearRegButton)
        _self = self

        def load_accounts():
            _self.widget.clear()
            for account in accounts:
                item = QListWidgetItem(account.account_name)
                item.setData(Qt.UserRole, account.account_id)
                _self.widget.addItem(item)
            _self.widget.clearSelection()
        try:
            load_accounts()
        except Exception as e:
            log.error(f"load_accounts: {e}")

        def refreshAccountButtonAction(self):
            reload_all_account_from_files()
            load_accounts()
            QMessageBox.information(None, "새로고침", "계정 목록을 새로고침했습니다")

        def addAccountButtonAction(self):
            dump_current_account()
            load_accounts()
            QMessageBox.information(None, "내보내기", "계정을 성공적으로 내보냈습니다")

        def deleteAccountButtonAction(self):
            items = _self.widget.selectedItems()
            if len(items) == 0:
                QMessageBox.warning(None, "계정 삭제", "삭제할 계정을 선택하세요")
                return
            if QMessageBox.question(None, "계정 삭제", "선택한 계정을 정말 삭제하시겠습니까?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                return
            for item in items:
                account_id = item.data(Qt.UserRole)
                delete_account(account_id)
            load_accounts()

        def renameAccountButtonAction(self):
            items = _self.widget.selectedItems()
            if len(items) == 0:
                QMessageBox.warning(None, "계정 이름 변경", "이름을 변경할 계정을 선택하세요")
                return
            if len(items) > 1:
                QMessageBox.warning(None, "계정 이름 변경", "하나의 계정만 선택할 수 있습니다")
                return
            for item in items:
                account_id = item.data(Qt.UserRole)
                account_name, ok = QInputDialog.getText(None, "계정 이름 변경", "새로운 계정 이름을 입력하세요")
                if ok:
                    account_name = account_name.strip()
                    if len(account_name) == 0:
                        QMessageBox.warning(None, "계정 이름 변경", "계정 이름은 비워둘 수 없습니다")
                        return
                    save_account_name(account_id, account_name)
                    load_accounts()

        def autologinAccountButtonAction(self):
            items = _self.widget.selectedItems()
            if len(items) == 0:
                QMessageBox.warning(None, "자동 로그인", "사용할 계정을 선택하세요")
                return
            if len(items) > 1:
                QMessageBox.warning(None, "자동 로그인", "하나의 계정만 선택할 수 있습니다")
                return
            for item in items:
                account_id = item.data(Qt.UserRole)

                disclaimer_result = QMessageBox.question(
                    None,
                    "자동 로그인",
                    "로그인이 만료되었을 때 자동으로 계정과 비밀번호를 다시 입력합니다\n *이 기능은 일정 위험이 있으니 신중하게 사용하세요*",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if disclaimer_result != QMessageBox.Yes:
                    return

                account_name, ok = QInputDialog.getText(None, "자동 로그인", "사용자 이름을 입력하세요")
                if not ok:
                    return
                if not account_name.strip():
                    QMessageBox.warning(None, "자동 로그인", "사용자 이름은 비워둘 수 없습니다")
                    return

                account_pass, ok2 = QInputDialog.getText(None, "자동 로그인", "비밀번호를 입력하세요", QLineEdit.Password)
                if not ok2:
                    return
                if not account_pass.strip():
                    QMessageBox.warning(None, "자동 로그인", "비밀번호는 비워둘 수 없습니다")
                    return

                save_acc_and_pwd(account_id, account_name, account_pass)

        def importAccountButtonAction(self):
            items = _self.widget.selectedItems()
            if len(items) == 0:
                QMessageBox.warning(None, "가져오기", "사용할 계정을 선택하세요")
                return
            if len(items) > 1:
                QMessageBox.warning(None, "가져오기", "하나의 계정만 선택할 수 있습니다")
                return
            for item in items:
                account_id = item.data(Qt.UserRole)
                import_account(account_id)
                QMessageBox.information(None, "가져오기", "계정을 성공적으로 가져왔습니다")

        def clearRegButtonAction(self):
            if QMessageBox.question(None, "레지스트리 초기화", "레지스트리의 계정 정보를 정말 초기화하시겠습니까?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                return
            clear_reg()
            QMessageBox.information(None, "레지스트리 초기화", "레지스트리의 계정 정보가 초기화되었습니다")
            
        
        self.addAccountButton.clicked.connect(addAccountButtonAction)
        self.importAccountButton.clicked.connect(importAccountButtonAction)
        self.refreshAccountButton.clicked.connect(refreshAccountButtonAction)
        self.renameAccountButton.clicked.connect(renameAccountButtonAction)
        self.autologinAccountButton.clicked.connect(autologinAccountButtonAction)
        self.deleteAccountButton.clicked.connect(deleteAccountButtonAction)
        self.clearRegButton.clicked.connect(clearRegButtonAction)
        #
        self.mLayout = QGridLayout()
        self.mLayout.addLayout(self.wLayout, 0, 0, 1, 1)
        self.mLayout.addLayout(self.buttons, 0, 1, 1, 1)
        self.mLayout.setColumnStretch(0, 1)  # 첫 번째 열의 확대 비율을 1로 설정하여 공간을 균등하게 분배합니다
        self.mLayout.setColumnStretch(1, 1)  # 두 번째 열의 확대 비율을 1로 설정하여 공간을 균등하게 분배합니다
        #
        self.setLayout(self.mLayout)


def accounts_interface(tr, scrollWidget) -> SettingCardGroup:
    accountsInterface = SettingCardGroup(tr("계정 설정"), scrollWidget)
    accountsInterface.addSettingCard(AccountsCard(
        FIF.ALBUM, title=tr(""),
    ))
    return accountsInterface