# [创青春·交子杯——分布式赛道](https://www.dcjingsai.com/common/cmpt/2019%E5%B9%B4%E2%80%9C%E5%88%9B%E9%9D%92%E6%98%A5%C2%B7%E4%BA%A4%E5%AD%90%E6%9D%AF%E2%80%9D%E6%96%B0%E7%BD%91%E9%93%B6%E8%A1%8C%E9%AB%98%E6%A0%A1%E9%87%91%E8%9E%8D%E7%A7%91%E6%8A%80%E6%8C%91%E6%88%98%E8%B5%9B-%E5%88%86%E5%B8%83%E5%BC%8F%E7%AE%97%E6%B3%95%E8%B5%9B%E9%81%93_%E7%AB%9E%E8%B5%9B%E4%BF%A1%E6%81%AF.html)

## 本地测试(Windows)
### 配置
修改`./start.ps1`中的`$SERVER_HOME`以匹配本地测试服务器所在目录，并修改其目录下`server.json`中节点个数(`mainConfig.nodeCount`)。

### 启动测试
```powershell
& .\start.ps1
```
测试完毕后将在工作目录下的`./log/`文件夹内生成各个节点的输出信息。