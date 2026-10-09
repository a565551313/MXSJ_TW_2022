# Loopback-only TCP capture listener for the local client connection test.
# It does not send application-protocol bytes or connect to any external host.

$ErrorActionPreference = 'Stop'
$ListenPort = 3134
$Listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $ListenPort)

try {
    $Listener.Start()
    Write-Host "Listening only on 127.0.0.1:$ListenPort"
    Write-Host 'Waiting for a client. Press Ctrl+C to stop.'
    Write-Host 'Received bytes are printed as hex and ASCII; no protocol response is sent.'

    while ($true) {
        $Client = $Listener.AcceptTcpClient()
        try {
            $Client.NoDelay = $true
            $Remote = $Client.Client.RemoteEndPoint
            $Stream = $Client.GetStream()
            [byte[]]$Buffer = New-Object byte[] 4096
            Write-Host "`nAccepted TCP connection from $Remote"

            while ($true) {
                # Poll for up to 250 ms. SelectRead plus Available=0 means the peer closed.
                if (-not $Client.Client.Poll(250000, [System.Net.Sockets.SelectMode]::SelectRead)) {
                    continue
                }

                if ($Client.Available -eq 0) {
                    Write-Host 'Client closed the connection.'
                    break
                }

                $ToRead = [Math]::Min($Buffer.Length, $Client.Available)
                $Count = $Stream.Read($Buffer, 0, $ToRead)
                if ($Count -le 0) {
                    Write-Host 'Client closed the connection.'
                    break
                }

                $Hex = [BitConverter]::ToString($Buffer, 0, $Count).Replace('-', ' ')
                $AsciiChars = for ($i = 0; $i -lt $Count; $i++) {
                    $b = $Buffer[$i]
                    if ($b -ge 0x20 -and $b -le 0x7e) { [char]$b } else { '.' }
                }
                $Ascii = -join $AsciiChars
                $Stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss.fff'
                Write-Host "[$Stamp] Received $Count byte(s)"
                Write-Host "HEX   $Hex"
                Write-Host "ASCII $Ascii"
            }
        }
        finally {
            $Client.Close()
        }
    }
}
finally {
    $Listener.Stop()
    Write-Host "Stopped listener on 127.0.0.1:$ListenPort"
}
