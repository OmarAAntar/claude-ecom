$SkillDir = "$env:USERPROFILE\.claude\skills\ecom"
$Venv = "$SkillDir\.venv"

Write-Host "Installing Claude ECOM..."

New-Item -ItemType Directory -Force -Path $SkillDir | Out-Null
Copy-Item -Recurse -Force . $SkillDir

python -m venv $Venv
& "$Venv\Scripts\pip" install --quiet --upgrade pip
& "$Venv\Scripts\pip" install --quiet -r requirements.txt

$SkillsTarget = "$env:USERPROFILE\.claude\skills"
foreach ($skill in Get-ChildItem -Path "skills" -Directory) {
    $target = Join-Path $SkillsTarget $skill.Name
    if (Test-Path $target) { Remove-Item $target -Force }
    New-Item -ItemType Junction -Path $target -Value "$SkillDir\skills\$($skill.Name)" | Out-Null
}

Write-Host "Claude ECOM installed. Use /ecom audit <url> to start."
