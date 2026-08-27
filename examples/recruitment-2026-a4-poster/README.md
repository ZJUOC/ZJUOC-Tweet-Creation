# 2026 纳新 A4 宣传单

该示例从协会 Logo、原推文照片、已注册水彩切图和两张用户提供的二维码，确定性生成 2480×3508、300 dpi 的 PNG 与 A4 PDF。

```bash
../../.venv/bin/python build_recruitment_flyer.py
```

先在仓库根目录运行 `./scripts/bootstrap.sh` 安装 Pillow 与 ReportLab。脚本会自动寻找 macOS、Linux 或 Windows 上的常见中文字体；Linux 推荐安装 Noto Sans CJK。

文件说明：

- `assets/generated-ocean-robot-bg.png`：无文字海洋机器人底图。
- `assets/recruitment-questionnaire-qr.png`：纳新问卷二维码。
- `assets/qq-group-qr-source.jpg`：用户提供的 QQ 群二维码截图，仅在脚本中裁切和等比缩放。
- `zju-ocean-robot-association-recruitment-2026-a4.png`：已验证的印刷 PNG。

重新构建时还会生成同名 PDF。二维码不得生成、重绘、变形或换色。
