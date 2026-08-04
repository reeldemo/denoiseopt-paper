# Rebuild the titled PDF (output name != main.pdf).
# LaTeX cannot set the PDF filename from inside the .tex for pdflatex;
# use -jobname (or latexmk + .latexmkrc).
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
$JobName = "Unsupervised_Wrap-Discontinuity_Repair_in_Wavetable_Synthesis_via_Hybrid_GA-PPO_Meta-Search_v14"
& pdflatex "-jobname=$JobName" -interaction=nonstopmode main.tex | Out-Null
if ($LASTEXITCODE -ne 0) { throw "pdflatex pass 1 failed: $LASTEXITCODE" }
& pdflatex "-jobname=$JobName" -interaction=nonstopmode main.tex | Out-Null
if ($LASTEXITCODE -ne 0) { throw "pdflatex pass 2 failed: $LASTEXITCODE" }
if (-not (Test-Path "$JobName.pdf")) { throw "missing $JobName.pdf" }
Write-Host "Wrote $JobName.pdf"
