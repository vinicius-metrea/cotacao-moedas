$root = "C:\Users\METREA-002\Desktop\ProjetoClaudeCode"
$port = 8080
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
$listener.Start()
Write-Host "Servidor rodando em http://localhost:$port/" -ForegroundColor Green
Write-Host "Pressione Ctrl+C para parar." -ForegroundColor Yellow

$mimeTypes = @{
  ".html" = "text/html; charset=utf-8"
  ".css"  = "text/css"
  ".js"   = "application/javascript"
  ".png"  = "image/png"
  ".jpg"  = "image/jpeg"
}

function Send-Response($res, $body, $mime, $status = 200) {
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
  $res.StatusCode = $status
  $res.ContentType = $mime
  $res.Headers.Add("Access-Control-Allow-Origin", "*")
  $res.ContentLength64 = $bytes.Length
  $res.OutputStream.Write($bytes, 0, $bytes.Length)
  $res.OutputStream.Close()
}

try {
  while ($listener.IsListening) {
    $ctx = $listener.GetContext()
    $req = $ctx.Request
    $res = $ctx.Response
    $localPath = $req.Url.LocalPath

    # --- Proxy endpoints ---
    if ($localPath -match "^/api/(.+)$") {
      $apiPath = $Matches[1]
      $query   = $req.Url.Query
      $url     = "https://api.frankfurter.app/$apiPath$query"
      try {
        Write-Host "PROXY  $url"
        $wc = New-Object System.Net.WebClient
        $wc.Headers.Add("User-Agent", "Mozilla/5.0")
        $data = $wc.DownloadString($url)
        Send-Response $res $data "application/json"
      } catch {
        Send-Response $res '{"error":"proxy failed"}' "application/json" 500
        Write-Host "ERRO   $url  => $_"
      }
      continue
    }

    # --- Static files ---
    $path = $localPath.TrimStart('/')
    if ($path -eq "") { $path = "moedas.html" }
    $filePath = Join-Path $root $path

    if (Test-Path $filePath -PathType Leaf) {
      $ext  = [System.IO.Path]::GetExtension($filePath)
      $mime = if ($mimeTypes[$ext]) { $mimeTypes[$ext] } else { "application/octet-stream" }
      $bytes = [System.IO.File]::ReadAllBytes($filePath)
      $res.ContentType = $mime
      $res.Headers.Add("Access-Control-Allow-Origin", "*")
      $res.ContentLength64 = $bytes.Length
      $res.OutputStream.Write($bytes, 0, $bytes.Length)
      $res.OutputStream.Close()
      Write-Host "200    $localPath"
    } else {
      Send-Response $res "404 Not Found" "text/plain" 404
      Write-Host "404    $localPath"
    }
  }
} finally {
  $listener.Stop()
}
