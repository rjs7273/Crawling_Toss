### Crawling_stock

---

## 멀티캠퍼스 크롤링

### 파일 설명

- `Toss_list.py` : 실행 코드
- `samsung_comments.csv` : 크롤링 결과물
- `page.html` : 토스증권 페이지 HTML 저장본 (참고용)

---

## Commits 확인 방법

작업한 내용은 Commits에 정리되어 있습니다.  
위쪽에 시계 타이머 이모티콘이 있는 Commits를 확인해 주세요.

---

## 가상환경 설정

- 크롤링 작업에 사용할 수 있는 가상환경을 추가하였습니다.
- 추가 패키지 설치 없이 바로 실행 가능합니다.

### 가상환경 활성화 방법

1. 터미널 실행 후 입력
   ```bash
   crawl_venv\Scripts\Activate
   ```
2. VSCode에서 인터프리터 선택
   - `Ctrl + Shift + P` → `Select Interpreter` 검색
   - `crawl_venv` 선택

### 가상환경 폴더가 GitHub에 없을 경우

- `.gitignore`에 의해 가상환경 폴더가 GitHub에 포함되지 않을 수 있음
- 해결 방법: 가상환경 폴더 내 `.gitignore` 파일을 삭제
