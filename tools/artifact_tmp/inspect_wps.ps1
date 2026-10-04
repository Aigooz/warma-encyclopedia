try {
  $app = [System.Runtime.InteropServices.Marshal]::GetActiveObject('Ket.Application')
  foreach ($wb in $app.Workbooks) {
    [PSCustomObject]@{ Name=$wb.Name; FullName=$wb.FullName; Saved=$wb.Saved; ReadOnly=$wb.ReadOnly }
  }
} catch { Write-Output "COM_ERROR: $($_.Exception.GetType().FullName): $($_.Exception.Message)" }
