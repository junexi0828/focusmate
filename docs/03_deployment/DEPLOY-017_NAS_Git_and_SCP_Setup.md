# NAS Git & SCP Setup Guide

이 문서는 시놀로지 NAS에서 Git을 사용하여 코드를 관리하고, SCP를 통해 파일을 전송하기 위한 설정 방법을 다룹니다.

## 1. 개요 (Overview)
*   **Git**: NAS에 접속하여 직접 `git pull`을 수행하거나 코드를 관리하기 위해 필요합니다.
*   **SCP**: 로컬(Mac)에서 NAS로 설정 파일(`.env` 등)을 안전하고 빠르게 전송하기 위해 필요합니다.

---

## 2. SCP (파일 전송) 설정

SSH 접속이 되어도 SCP 전송이 실패하는 경우가 있습니다. 이는 시놀로지 보안 설정에서 SFTP가 꺼져있기 때문일 수 있습니다.

### 2.1 SFTP 활성화 (Enable SFTP)
1.  **시놀로지 DSM** (웹 인터페이스)에 접속합니다.
2.  **제어판 (Control Panel)** > **파일 서비스 (File Services)** 로 이동합니다.
3.  **FTP** 탭을 클릭합니다.
4.  **SFTP 서비스 활성화 (Enable SFTP service)** 체크박스를 켭니다.
5.  **적용** 버튼을 누릅니다.

### 2.2 접속 테스트
Mac 터미널에서 다음 명령어로 테스트 파일을 보내봅니다.
```bash
# 로컬(Mac)에서 실행
touch test.txt
scp test.txt juns@192.168.45.58:/volume1/homes/juns/
```
에러 없이 전송되면 성공입니다.

---

## 3. Git 설정 (Git Configuration)

NAS 터미널(SSH)에 접속하여 진행합니다.

### 3.1 Git 설치 확인
```bash
git --version
# git version 2.x.x 형식으로 뜨면 설치된 상태입니다.
# 'command not found'가 뜨면 패키지 센터에서 'Git Server'를 설치하세요.
```

### 3.2 사용자 정보 설정
커밋 기록에 남을 이름과 이메일을 설정합니다.
```bash
git config --global user.name "Junexi"
git config --global user.email "junexi0828@gmail.com"
```

---

## 4. GitHub 연동 (SSH Key Setup)

NAS가 GitHub 저장소에 접근할 수 있도록 인증 키(SSH Key)를 생성하고 등록해야 합니다.

### 4.1 SSH 키 생성
NAS 터미널에서 실행합니다. (비밀번호 등은 엔터를 눌러 기본값 사용)
```bash
ssh-keygen -t ed25519 -C "nas_deploy_key"
```

### 4.2 공개키(Public Key) 확인 및 복사
생성된 키의 내용을 화면에 출력합니다.
```bash
cat ~/.ssh/id_ed25519.pub
```
`ssh-ed25519 AAAA...` 로 시작하는 긴 문자열 전체를 복사합니다.

### 4.3 GitHub에 등록
1.  [GitHub Settings > SSH and GPG keys](https://github.com/settings/keys)로 이동합니다.
2.  **New SSH key** 버튼 클릭.
3.  **Title**: `Synology NAS` (식별 가능한 이름).
4.  **Key**: 복사한 공개키 붙여넣기.
5.  **Add SSH key** 클릭.

### 4.4 연결 확인
NAS 터미널에서 연결을 테스트합니다.
```bash
ssh -T git@github.com
```
*   처음 실행 시 `Are you sure you want to continue connecting (yes/no/[fingerprint])?` 라고 물으면 **yes** 입력.
*   `Hi junexi0828! You've successfully authenticated...` 메시지가 뜨면 성공입니다.
