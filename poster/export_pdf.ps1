# Export a PPTX to a print-quality PDF with Microsoft PowerPoint (COM automation). Usage:
#   powershell -ExecutionPolicy Bypass -File poster\export_pdf.ps1 -In poster\poster_editable.pptx -Out poster\poster_final.pdf
param([Parameter(Mandatory=$true)][string]$In, [Parameter(Mandatory=$true)][string]$Out)
$inPath = (Resolve-Path $In).Path
$outPath = [System.IO.Path]::GetFullPath($Out)
$ppt = New-Object -ComObject PowerPoint.Application
try {
    # Open(FileName, ReadOnly, Untitled, WithWindow) — PowerShell booleans work; raw ints are rejected by this build
    $pres = $ppt.Presentations.Open($inPath, $true, $false, $false)
    # Print-intent PDF keeps high image resolution. Needs the typed enums from the Office interop assembly;
    # falls back to plain SaveAs (ppSaveAsPDF = 32) if the interop assembly is not registered.
    try {
        Add-Type -AssemblyName Microsoft.Office.Interop.PowerPoint -ErrorAction Stop
        $fmt = [Microsoft.Office.Interop.PowerPoint.PpFixedFormatType]::ppFixedFormatTypePDF
        $intent = [Microsoft.Office.Interop.PowerPoint.PpFixedFormatIntent]::ppFixedFormatIntentPrint
        $pres.ExportAsFixedFormat($outPath, $fmt, $intent)
        Write-Output "export mode: ExportAsFixedFormat (print intent)"
    } catch {
        Write-Output ("interop unavailable (" + $_.Exception.Message + ") -> SaveAs PDF")
        $pres.SaveAs($outPath, 32)
    }
    $pres.Close()
    Write-Output "PDF written: $outPath (note: SaveAs embeds images at ~200 ppi, sufficient for a 4 x 4 ft poster)"
} finally {
    $ppt.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
}
