# Render slide 1 of a PPTX to PNG with PowerPoint (for visual QA of the poster layout). Usage:
#   powershell -ExecutionPolicy Bypass -File poster\export_png.ps1 -In poster\poster_editable.pptx -Out poster\poster_preview.png -Width 4800
param([Parameter(Mandatory=$true)][string]$In, [Parameter(Mandatory=$true)][string]$Out, [int]$Width = 4800)
$inPath = (Resolve-Path $In).Path
$outPath = [System.IO.Path]::GetFullPath($Out)
$ppt = New-Object -ComObject PowerPoint.Application
try {
    $pres = $ppt.Presentations.Open($inPath, $true, $false, $false)
    $ratio = $pres.PageSetup.SlideHeight / $pres.PageSetup.SlideWidth
    $pres.Slides.Item(1).Export($outPath, "PNG", $Width, [int]($Width * $ratio))
    $pres.Close()
    Write-Output "PNG written: $outPath"
} finally {
    $ppt.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
}
