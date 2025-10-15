# 자주 묻는 질문 (FAQ)

영상 가이드 [https://search.bilibili.com/all?keyword=三月七小助手](https://search.bilibili.com/all?keyword=%E4%B8%89%E6%9C%88%E4%B8%83%E5%B0%8F%E5%8A%A9%E6%89%8B)

### Q: 도우미가 계속 업데이트에 실패하거나 다운로드 속도가 느립니다. 어떻게 해야 하나요?

A: March7thAssistant는 서드파티 서비스인 [Mirror酱](https://mirrorchyan.com/?source=m7a-faq)(오픈 소스 커뮤니티를 위한 유료 콘텐츠 배포 플랫폼)과 연동되어 있습니다.

이 서비스는 무료 업데이트 확인 기능을 제공하지만, 다운로드는 유료 서비스로 사용자가 비용을 지불해야 합니다.

하지만 Mirror酱의 다운로드 서비스를 구매하지 않아도, 업데이트가 감지된 후 설정에서 해외 소스(GitHub)로부터 다운로드하도록 선택할 수 있습니다~

만약 CDK를 구매하여 입력했다면, 업데이트 시 더 이상 네트워크 문제로 골치 아플 필요 없이 더 빠르고 안정적으로 다운로드할 수 있습니다!

또한, 이 CDK는 MAA 등 Mirror酱와 연동된 다른 프로젝트에서도 사용할 수 있습니다.

[첫 다운로드는 여기를 클릭하여 Mirror酱 고속 다운로드를 이용하세요](https://mirrorchyan.com/zh/download?rid=March7thAssistant&os=&arch=&channel=stable&source=m7a-faq)

### Q: 도우미 시작이 느리거나, 오류 2147942402가 발생하거나, 자꾸 백신 프로그램에 의해 삭제됩니다. 어떻게 해야 하나요?

A: `도우미 폴더`를 백신 프로그램의 예외 항목/허용 목록/신뢰 영역에 추가한 후, `March7th Updater.exe`를 사용해 자동 업데이트하거나 수동으로 한 번 업데이트하세요.

* **Windows Defender:** `바이러스 및 위협 방지` → `설정 관리` → `제외 추가 또는 제거`. [#373](https://github.com/moesnow/March7thAssistant/issues/373)의 스크린샷을 참고하세요.
* **훠룽(火绒) 백신:** `메인 화면` → `우측 상단 메뉴` → `신뢰 영역`. [가이드](https://cs.xunyou.com/html/282/15252.shtml)의 스크린샷을 참고하세요.

### Q: 듀얼(다중) 모니터 사용으로 인해 인식 오류 등 다른 문제가 발생합니다.

A: **설정 → 기타 → 다중 모니터에서 스크린샷 찍기** 옵션을 켜거나 꺼보세요.

관련 토론: [#383](https://github.com/moesnow/March7thAssistant/issues/383) [#710](https://github.com/moesnow/March7thAssistant/issues/710)

### Q: 새로 추가된 던전이 없거나, 전략 훈련에 신규 캐릭터가 없습니다.

A: `던전 이름` 인터페이스에서 직접 이름을 입력하거나, `assets\config\instance_names.json` 파일을 수정하여 수동으로 추가할 수 있습니다.

망각의 정원 인터페이스의 경우, 도우미의 툴박스에 있는 `스크린샷 캡처` 기능을 사용하여 캐릭터 프로필을 선택하고 `선택한 스크린샷 저장`을 클릭한 후, `assets\images\share\character` 폴더에 넣고 `assets\config\character_names.json` 파일을 수정하세요.

추가로, [Issue](https://github.com/moesnow/March7thAssistant/issues)에 압축 파일처럼 `압축하지 않은` 방식으로 업로드해 주시거나, [PR](https://github.com/moesnow/March7thAssistant/pulls)을 보내주시는 것도 환영합니다.

### Q: '전체 실행'은 어떤 기능인가요?

A: `일일 임무`→`개척력 소모`→`필드 파밍`→`시뮬레이션 우주`→`전략 훈련`→`보상 수령` 순서로 순차적으로 실행됩니다.

완료된 것으로 판단된 작업은 반복 실행되지 않습니다. 일일 임무와 필드 파밍은 매일 새벽 4시에 초기화되며, 시뮬레이션 우주와 전략 훈련은 매주 월요일 새벽 4시에 초기화됩니다.

### Q: 실행을 시작하면 키보드와 마우스를 움직이거나 백그라운드로 전환하면 안 되나요?

A: 네, 그렇습니다. 백그라운드 실행이 필요하다면 [원격 로컬 다중 사용자 데스크톱](https://m7a.top/#/assets/docs/Background)을 사용해 보세요.

### Q: 사용자 지정 알림은 어떻게 추가하나요?

A: 그래픽 인터페이스(GUI) 내에서는 `Windows 기본 알림`만 활성화할 수 있습니다. 다른 알림 방식이 필요하면 `config.yaml` 파일에서 직접 활성화해야 합니다.

### Q: 시뮬레이션 우주에서 몇 번째 세계, 캐릭터, 운명의 길, 난이도를 수정할 수 있나요?

A: 원하는 세계와 캐릭터를 선택하여 한 번 진입했다가 나오면 설정이 저장됩니다. 운명의 길과 난이도는 **설정 → 시뮬레이션 우주 → 원본 실행**을 클릭하여 그래픽 인터페이스 내에서 수정할 수 있습니다.

### Q: 시뮬레이션 우주 관련 기타 문제는 어떻게 해결하나요?

A: 빠른 시작을 원하시면 [프로젝트 문서](https://github.com/Night-stars-1/Auto_Simulated_Universe_Docs/blob/docs/docs/guide/index.md)를 방문하세요.

문제가 발생하면 질문하기 전에 [Q&A](https://github.com/Night-stars-1/Auto_Simulated_Universe_Docs/blob/docs/docs/guide/qa.md)를 확인하세요.

### Q: 필드 파밍이 중간에 멈추거나 제대로 작동하지 않습니다.

A: 활성화하지 않은 차원 고정 장치나 열지 않은 문, 완료하지 않은 기교새 임무 등이 있는지 확인해 주세요.

### Q: 필드 파밍이 중간에 중단되었는데, 특정 맵부터 다시 시작하려면 어떻게 하나요?

A: **설정 → 필드 파밍 → 원본 실행**을 클릭한 후, 디버그 모드를 선택하여 원하는 맵을 고를 수 있습니다.