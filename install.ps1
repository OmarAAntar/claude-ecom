$ErrorActionPreference = "Stop"

$SkillDir = "$env:USERPROFILE\.claude\skills\ecom"
$Venv = "$SkillDir\.venv"

Write-Host "Installing Claude ECOM..."

# -- Python version check -----------------------------------------------------
# Claude ECOM uses Python 3.10+ syntax. Fail fast with a clear message
# rather than blowing up partway through `pip install`.
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Error "Error: python is not on PATH. Install Python 3.10+ and re-run."
    exit 1
}

$pyVer = & python -c "import sys; print('{0}.{1}'.format(sys.version_info[0], sys.version_info[1]))"
$pyOk  = & python -c "import sys; print(1 if sys.version_info >= (3, 10) else 0)"
if ($pyOk -ne "1") {
    Write-Error "Error: Claude ECOM requires Python 3.10 or newer. Found Python $pyVer."
    Write-Host  "Install a newer Python (https://www.python.org/downloads/) and re-run."
    exit 1
}

# -- Copy repo into the skill dir, excluding noisy paths ----------------------
# robocopy with /XD /XF is the PowerShell equivalent of `rsync --exclude`.
# Exit codes 0-7 are success for robocopy (8+ is a real error).
New-Item -ItemType Directory -Force -Path $SkillDir | Out-Null

$source = (Get-Location).Path
$excludedDirs  = @(".git", "__pycache__", ".venv", "node_modules")
$excludedFiles = @("*.pyc", ".DS_Store")

robocopy $source $SkillDir /E /XD @excludedDirs /XF @excludedFiles /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) {
    Write-Error "Error: robocopy failed with exit code $LASTEXITCODE."
    exit 1
}

# -- Bootstrap the virtualenv -------------------------------------------------
& python -m venv $Venv
& "$Venv\Scripts\pip" install --quiet --upgrade pip
& "$Venv\Scripts\pip" install --quiet -r requirements.txt

# -- Register skills ----------------------------------------------------------
$SkillsTarget = "$env:USERPROFILE\.claude\skills"
New-Item -ItemType Directory -Force -Path $SkillsTarget | Out-Null
foreach ($skill in Get-ChildItem -Path "skills" -Directory) {
    $target = Join-Path $SkillsTarget $skill.Name
    if (Test-Path $target) { Remove-Item $target -Force -Recurse }
    New-Item -ItemType Junction -Path $target -Value "$SkillDir\skills\$($skill.Name)" | Out-Null
}

Write-Host "Claude ECOM installed. Use /ecom audit <url> to start."
