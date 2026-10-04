try {
  $app = [System.Runtime.InteropServices.Marshal]::GetActiveObject('Ket.Application')
  $app.DisplayAlerts = $false
  foreach ($wb in @($app.Workbooks)) {
    if ($wb.FullName -eq 'F:\warma百科\@Warma 相关.xlsx' -or $wb.FullName -eq 'F:\warma百科\@warma养鸽场 相关.xlsx') {
      if (-not $wb.Saved) { $wb.Save() }
      $wb.Close($false)
      Write-Output ("Closed: " + $wb.Name)
    }
  }
} catch { Write-Output "COM_ERROR: $($_.Exception.Message)"; exit 1 }
