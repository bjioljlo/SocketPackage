# Feature Gap Implementation

從 `docs/feature-gaps.md` 中挑選最高優先項目，透過 OpenSpec 完成完整流程：propose → apply → 整合測試 → commit。

**Input**: 可選，可指定要處理的 gap 編號（例如 gap 2），否則從最高優先未完成項目開始。

## Steps

### 1. 確認當前分支與狀態

```bash
git branch --show-current
git status --short
```

確保在 `develop` 分支且工作目錄乾淨。

### 2. 閱讀 feature-gaps.md，選擇項目

讀取 `docs/feature-gaps.md`，從 🔴 高優先開始，找第一個尚未實作的項目。

記錄該項目的：
- 編號與標題（如 `1. 🫀 自動心跳與斷線偵測`）
- 核心需求摘要
- 轉換為 kebab-case change name（如 `auto-heartbeat-detection`）

### 3. OpenSpec Propose

使用 openspec-propose skill 建立 change artifacts。執行順序：

```bash
openspec new change "<change-name>"
openspec instructions proposal --change "<change-name>" --json   # 產出 proposal.md
openspec instructions specs --change "<change-name>" --json      # 產出 specs
openspec instructions design --change "<change-name>" --json     # 產出 design.md
openspec instructions tasks --change "<change-name>" --json      # 產出 tasks.md
```

產出 artifacts 時需仔細閱讀現有程式碼以確保設計準確。

### 4. 建立功能分支

```bash
git checkout develop
git pull origin develop
git checkout -b feature/<change-name>
```

### 5. 實作（OpenSpec Apply）

使用 openspec-apply skill 逐一實作 tasks.md 中的任務：

- 修改核心原始碼（`src/socket_package/`）
- 根據 specs 中的 scenarios 撰寫單元測試（`tests/`）
- 撰寫整合測試（`tests/integration/`）

### 6. 測試驗證

```bash
uv run pytest -q                    # 全部測試（含整合）
uv run pytest -q -m "not integration"  # 僅單元測試
```

確認所有測試通過、無 regression。

### 7. Commit

```bash
git add -A
git commit -m "feat: <簡短描述>

<詳細變更說明>

Closes feature-gap #<number>: <change-name>"
```

使用 Conventional Commits 格式（feat/fix/refactor/chore/docs）。

## 注意事項

- 每個 gap 從 develop 開新分支，不要累積在同一個分支
- 整合測試應使用 `@pytest.mark.integration` 標記
- 避免修改不相關的檔案
- 若實作中發現設計問題，先更新 OpenSpec artifacts 再繼續