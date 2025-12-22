# GitHub Actions 토큰 설정 가이드

## ⚠️ 중요: 토큰 보안

**절대로 토큰을 코드에 직접 넣지 마세요!**

GitHub Personal Access Token은 GitHub Secrets에 저장해야 합니다.

---

## 📝 GitHub Secrets 설정 방법

### 1단계: GitHub 저장소로 이동

1. 브라우저에서 https://github.com/junexi0828/focusmate 접속
2. 상단 메뉴에서 **Settings** 클릭

### 2단계: Secrets 페이지로 이동

1. 왼쪽 사이드바에서 **Secrets and variables** 클릭
2. **Actions** 클릭

### 3단계: 새 Secret 추가

1. **New repository secret** 버튼 클릭
2. 다음 정보 입력:
   - **Name**: `GH_TOKEN` 또는 `GITHUB_TOKEN`
   - **Value**: (실제 토큰 값 입력 - GitHub Personal Access Token)
3. **Add secret** 버튼 클릭

### 4단계: 추가 Secrets (필요한 경우)

다음 Secrets도 추가하세요:

| Name                | Value               | 설명                   |
| ------------------- | ------------------- | ---------------------- |
| `DOCKER_USERNAME`   | Docker Hub 사용자명 | Docker 이미지 푸시용   |
| `DOCKER_PASSWORD`   | Docker Hub 비밀번호 | Docker 이미지 푸시용   |
| `SLACK_WEBHOOK_URL` | Slack Webhook URL   | 빌드 알림용 (선택사항) |

---

## 🔧 워크플로우에서 토큰 사용

### 현재 워크플로우 파일

`.github/workflows/ci-cd.yml` 파일은 이미 Secrets를 사용하도록 설정되어 있습니다:

```yaml
env:
  DOCKER_IMAGE: ${{ secrets.DOCKER_USERNAME }}/focusmate-backend
  SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}

jobs:
  build:
    steps:
      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
```

### 토큰이 필요한 경우 추가 방법

만약 GitHub API 호출이 필요한 경우:

```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v4
    with:
      token: ${{ secrets.GH_TOKEN }}
```

---

## ✅ 설정 확인

### 1. Secrets 확인

1. GitHub 저장소 → Settings → Secrets and variables → Actions
2. 다음 Secrets가 있는지 확인:
   - ✅ `GH_TOKEN` (또는 `GITHUB_TOKEN`)
   - ✅ `DOCKER_USERNAME`
   - ✅ `DOCKER_PASSWORD`
   - ⚠️ `SLACK_WEBHOOK_URL` (선택사항)

### 2. 워크플로우 실행 테스트

```bash
# 코드 푸시하여 워크플로우 트리거
git add .
git commit -m "test: trigger CI/CD workflow"
git push origin main
```

### 3. 워크플로우 상태 확인

1. GitHub 저장소 → **Actions** 탭
2. 최근 워크플로우 실행 확인
3. 각 Job의 로그 확인

---

## 🔒 보안 모범 사례

### ✅ 해야 할 것

1. **Secrets 사용**: 모든 민감한 정보는 GitHub Secrets에 저장
2. **토큰 권한 최소화**: 필요한 권한만 부여
3. **토큰 만료 설정**: 가능하면 만료 기간 설정
4. **정기적 교체**: 토큰을 정기적으로 교체

### ❌ 하지 말아야 할 것

1. **코드에 직접 넣기**: 절대로 토큰을 코드에 하드코딩하지 마세요
2. **커밋하기**: `.env` 파일이나 설정 파일에 토큰 넣고 커밋하지 마세요
3. **공개 저장소**: 토큰이 포함된 파일을 공개 저장소에 올리지 마세요
4. **로그 출력**: 워크플로우에서 토큰을 로그에 출력하지 마세요

---

## 🚨 토큰이 노출된 경우

만약 토큰이 실수로 노출되었다면:

### 즉시 조치

1. **토큰 삭제**:

   - GitHub → Settings → Developer settings → Personal access tokens
   - 노출된 토큰 찾아서 **Delete** 클릭

2. **새 토큰 생성**:

   - **Generate new token** 클릭
   - 필요한 권한만 선택
   - 새 토큰을 GitHub Secrets에 업데이트

3. **Git 히스토리 정리** (필요한 경우):

   ```bash
   # 토큰이 커밋된 경우
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all

   git push origin --force --all
   ```

---

## 📊 현재 워크플로우 상태

### 설정된 Jobs

1. **test**: 테스트 실행 (PostgreSQL, Redis 포함)
2. **build**: Docker 이미지 빌드 및 푸시
3. **security**: 보안 스캔 (Trivy)

### 필요한 Secrets

| Secret              | 상태         | 용도              |
| ------------------- | ------------ | ----------------- |
| `GH_TOKEN`          | ⚠️ 추가 필요 | GitHub API 접근   |
| `DOCKER_USERNAME`   | ⚠️ 추가 필요 | Docker Hub 로그인 |
| `DOCKER_PASSWORD`   | ⚠️ 추가 필요 | Docker Hub 로그인 |
| `SLACK_WEBHOOK_URL` | ⚠️ 선택사항  | Slack 알림        |

---

## 🎯 다음 단계

1. ✅ GitHub Secrets에 토큰 추가
2. ✅ Docker Hub 계정 정보 추가
3. ✅ 코드 푸시하여 워크플로우 테스트
4. ✅ Actions 탭에서 결과 확인

---

## 💡 참고 자료

- [GitHub Secrets 문서](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub Actions 보안](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
