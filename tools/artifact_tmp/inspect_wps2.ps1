try {
  $app = [System.Runtime.InteropServices.Marshal]::GetActiveObject('Ket.Application')
  Write-Output ("Count: " + $app.Workbooks.Count)
  for ($i=1; $i -le $app.Workbooks.Count; $i++) {
    $wb=$app.Workbooks.Item($i)
    Write-Output ($wb.FullName + " Saved=" + $wb.Saved)
  }
} catch { Write-Output "COM_ERROR: $($_.Exception.Message)" }
