$WORKING_DIR = $PWD
$pathDict = Get-Content "path.json" | ConvertFrom-Json

# server.exe的目录
$SERVER_HOME = $pathDict.SERVER_HOME
$SERVER_HOME = "${PWD}/${SERVER_HOME}"

# 数据生成器的jar包目录
$DATA_GENERATOR_HOME = $pathDict.DATA_GENERATOR_HOME
$DATA_GENERATOR_HOME = "${PWD}/${DATA_GENERATOR_HOME}"
$JAR_FILE_NAME = $pathDict.JAR_FILE_NAME

$inputJSON = (Get-Content "input.json" | ConvertFrom-Json).mainConfig

# 将input.json复制到数据生成器目录
Copy-Item -Force .\input.json $DATA_GENERATOR_HOME
Set-Location $DATA_GENERATOR_HOME
java -jar $JAR_FILE_NAME
# 将生成的server与client各自的配置文件放到相应的目录
Move-Item -Force $inputJSON.serverConfData $SERVER_HOME
Move-Item -Force $inputJSON.clinetConfData "${WORKING_DIR}/client.json" # 不是故意要拼错，而是数据生成器的源码就离谱

Set-Location $SERVER_HOME
# 将测试文件放到指定的地方（这会与生成的server.json中的testData
# 所匹配，都由input.json的testData字段决定）
Move-Item -Force "${DATA_GENERATOR_HOME}/test.json" $inputJSON.testData
Set-Location $WORKING_DIR
