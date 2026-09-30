# ========== 只需修改这一行 ==========
$CoreSpec = "0-15"          # 核心范围，例如 "0-15"、"0-7"、"0,2,4,6" 或 "0-3,8-11"
# ====================================

$ProcessName = "xymain.bin"

# 解析核心范围为掩码
function Get-AffinityMask {
    param([string]$Spec)
    [int64]$mask = 0
    $parts = $Spec -split ','
    foreach ($part in $parts) {
        $part = $part.Trim()
        if ($part -match '^(\d+)-(\d+)$') {
            $start = [int]$matches[1]
            $end   = [int]$matches[2]
            for ($i = $start; $i -le $end; $i++) {
                $mask = $mask -bor ([int64]1 -shl $i)
            }
        } elseif ($part -match '^\d+$') {
            $i = [int]$part
            $mask = $mask -bor ([int64]1 -shl $i)
        }
    }
    return $mask
}

$TargetMask = Get-AffinityMask -Spec $CoreSpec
Write-Host "Core spec: $CoreSpec  =>  Mask: 0x$($TargetMask.ToString('X'))" -ForegroundColor Cyan

# 查找进程
$procs = Get-Process | Where-Object {
    $_.Name -eq $ProcessName -or
    $_.Name -eq "xymain" -or
    $_.Path -like "*xymain.bin*"
}

if (-not $procs) {
    Write-Host "Process not found: $ProcessName" -ForegroundColor Red
    exit
}

foreach ($p in $procs) {
    try {
        $p.ProcessorAffinity = $TargetMask
        Write-Host "OK: $($p.Name) (PID: $($p.Id)) bound to cores $CoreSpec" -ForegroundColor Green
    } catch {
        Write-Host "FAIL: $($p.Name) (PID: $($p.Id)) - $($_.Exception.Message)" -ForegroundColor Yellow
    }
}