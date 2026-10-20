# 2026-10-21：研究主题与选题理由

- [slides.md](slides.md)：日文可编辑原稿，共10页。
- [slides.pdf](slides.pdf)：发表、阅读用。
- [slides.html](slides.html)：浏览器演示，左右键翻页。

## 修改与导出

编辑 `slides.md`，用 `---` 分页。在本文件夹运行以下命令（需Node.js和Chrome系浏览器）：

```bash
npx --yes @marp-team/marp-cli@4.5.1 --no-config --html --pdf slides.md -o slides.pdf
npx --yes @marp-team/marp-cli@4.5.1 --no-config --html slides.md -o slides.html
```

导出后检查日文显示、换行和页数。PDF和HTML不会随原稿自动更新。
