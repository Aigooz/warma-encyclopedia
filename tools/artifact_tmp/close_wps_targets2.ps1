try {
  $app = [System.Runtime.InteropServices.Marshal]::GetActiveObject('Ket.Application')
  $app.DisplayAlerts = $false
  for ($i = $app.Workbooks.Count; $i -ge 1; $i--) {
    $wb = $app.Workbooks.Item($i)
    if ($wb.FullName -in @('F:\warma百科\@Warma 相关.xlsx','F:\warma百科\@warma养鸽场 相关.xlsx')) {
      Write-Output ("Closing " + $wb.FullName + " Saved=" + $wb.Saved)
      if (-not $wb.Saved) {
        $wb.Save()
        Write-Output "Saved unsaved changes"
      }
      $wb.Close($false)
      Write-Output "Closed"
    }
  }
} catch { Write-Output "COM_ERROR: $($_.Exception.Message)"; exit 1 }
