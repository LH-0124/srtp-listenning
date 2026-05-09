param(
    [Parameter(Mandatory=$true)]
    [string]$TaskFile
)

# 用法示例：
#   powershell -ExecutionPolicy Bypass -File scripts/codex_run_one.ps1 .codex/tasks/T00_repo_audit.md
#
# 说明：
# 1. PowerShell 版本适合 Windows 用户。
# 2. 任务文件内容会作为 prompt 传给 codex exec。
# 3. 默认允许工作区写入；如果只是审查任务，可以把 workspace-write 改成 read-only。

New-Item -ItemType Directory -Force -Path ".codex/logs" | Out-Null

$taskName = [System.IO.Path]::GetFileNameWithoutExtension($TaskFile)
$outFile = ".codex/logs/$taskName`_codex_output.md"
$prompt = Get-Content $TaskFile -Raw

codex exec --sandbox workspace-write $prompt --output-last-message $outFile

Write-Host "完成：$TaskFile"
Write-Host "输出：$outFile"
Write-Host "下一步建议：git diff; python -m py_compile data_pipeline/*.py server/*.py"
