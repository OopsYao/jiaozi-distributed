$WORKING_DIR = $PWD
$SERVER_HOME = "${WORKING_DIR}/server/cmake-build-debug"

New-Item -ItemType Directory -Force -Path logs;

$server = Start-Job -Name 'Server' -ScriptBlock {
    Set-Location $using:SERVER_HOME
    & ./server.exe
}

$nodeNum = (Get-Content "${SERVER_HOME}/server.json" | ConvertFrom-Json ).mainConfig.nodeCount
$array = 1..$nodeNum
foreach ($index in $array) {
    Start-Job -Name "Node${index}" -ScriptBlock {
        Set-Location $using:WORKING_DIR
        python main.py > "logs/node${using:index}.txt"
    }
}

$completed = Register-ObjectEvent -InputObject $server -EventName StateChanged -Action {
    Write-Host ('Job #{0} ({1}) complete.' -f $sender.Id, $sender.Name)
    Get-Job -Name Node*, Server | Remove-Job -Force
    $completed | Unregister-Event
}