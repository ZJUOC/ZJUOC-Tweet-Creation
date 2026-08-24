# 首批水机素材生成记录

统一约束：浅色水机品牌色 `#6DA7CF #8CCCD3 #F09A7C #F2D6A2 #2E4148` 与白色；不使用深蓝；不生成文字、Logo、边框；以纯 `#F000F0` 隔离背景覆盖所有内部空隙，之后转为真透明 PNG。

- `cutout.watercolor.rov-bubble`：保留友好水彩 ROV、机械臂与气泡，移除棋盘格并隔离背景。
- `cutout.watercolor.thruster-wrench`：水彩推进器与扳手，紧凑工具组合。
- `cutout.watercolor.sonar-fish`：友好机器鱼穿过三层声呐弧线，附一个气泡。
- `cutout.watercolor.auv-glider`：可识别的自主水下滑翔机，俯冲姿态、传感器窗和气泡。
- `cutout.watercolor.smart-buoy`：太阳能板、天线、水下传感器舱和简洁波浪的智能浮标。
- `cutout.paper.robotic-arm-sample`：分层纸雕机械臂抓取贝壳样本，含海底小景。
- `cutout.paper.field-test-boat`：分层纸雕外场测试船、ROV 吊架、设备箱和入水电缆。

透明度处理：`scripts/chroma_to_alpha.sh`，默认 `similarity=0.40`、`blend=0.02`；最终通过 `scripts/assets.py validate` 检查真实 alpha、透明四角和文件完整性。
