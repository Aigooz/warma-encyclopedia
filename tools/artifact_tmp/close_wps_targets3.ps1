try {
  $app = [System.Runtime.InteropServices.Marshal]::GetActiveObject('Ket.Application')
  $app.DisplayAlerts = $false
  for ($i = $app.Workbooks.Count; $i -ge 1; $i--) {
    $wb = $app.Workbooks.Item($i)
    $name = $wb.Name
    if ($name.StartsWith('@Warma') -or $name.StartsWith('@warma')) {
      Write-Output ("Closing " + $name + " Saved=" + $wb.Saved)
      if (-not $wb.Saved) {
        $wb.Save()
        Write-Output "Saved unsaved changes"
      }
      $wb.Close($false)
      Write-Output "Closed"
    }
  }
} catch { Write-Output "COM_ERROR: $($_.Exception.Message)"; exit 1 }
