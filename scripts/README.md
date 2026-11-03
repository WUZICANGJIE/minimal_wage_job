# 共用工具

在仓库根目录运行：

```bash
python scripts/build_teaching.py
python scripts/check_delivery.py
```

- `build_teaching.py`：从Marp源稿提取逐页讲稿。默认只更新当前的 `2026-11-04/speaker_notes.md`；也可传入指定的 `slides.md` 路径。
- `check_delivery.py`：检查当前15页稿和归档13页稿的结构、PDF文字、相对资源路径及原分析文件哈希。需要Poppler的 `pdfinfo`、`pdftotext`，输出写入 `.cache/delivery-check/verification.json`。

两个脚本均不重算分析。Marp导出命令见[本周README](../2026-11-04/README.md)；当前统计复核见[下周分析](../2026-11-11/analysis/README.md)。
