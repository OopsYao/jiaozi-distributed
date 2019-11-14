$WORKING_DIR = $PWD
# Server程序目录
$SERVER_HOME = "${WORKING_DIR}/server/cmake-build-debug"

# 创建logs目录
New-Item -ItemType Directory -Force -Path logs;

# 启动Server Job
$server = Start-Job -Name 'Server' -ScriptBlock {
    Set-Location $using:SERVER_HOME
    & ./server.exe
}

# 根据Server配置中的节点数目启动相应数目的Job
$nodeNum = (Get-Content "${SERVER_HOME}/server.json" | ConvertFrom-Json ).mainConfig.nodeCount
$array = 1..$nodeNum
foreach ($index in $array) {
    Start-Job -Name "Node${index}" -ScriptBlock {
        Set-Location $using:WORKING_DIR
        python main.py > "logs/node${using:index}.txt"
    }
}

# 在Server Job结束后删除节点的Job
# TODO 但好像不起作用?
$completed = Register-ObjectEvent -InputObject $server -EventName StateChanged -Action {
    python ./score.py
    Write-Host ('Job #{0} ({1}) complete.' -f $sender.Id, $sender.Name)
    Get-Job -Name Node*, Server | Remove-Job -Force
    $completed | Unregister-Event
}