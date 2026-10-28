# 2026-10-28：第二回发表——数据、假说与記述統計

## 已发表材料归档

用户提供并说明本次已按这些材料发表。原件不改写；转换版仅用于检索、逐页引用和后续核对，不是后续修订稿。

| 材料 | 原件 | 便于引用的转换版 |
|---|---|---|
| Slides（15页） | [slides.pdf](slides.pdf) | [slides_reference.md](slides_reference.md)：按PDF物理页码整理，表格转为Markdown；第9、10、13页图表保留在 [reference_images/](reference_images/) |
| 讲稿（约8分钟，附修改与排练备注） | [speech.html](speech.html) | [speech_reference.md](speech_reference.md)：保留逐页正文、提示及末尾备注 |

原始附件名分别为 `課題2 データと仮説.pdf` 和 `task2_speech_8min.html`；归档副本与附件逐字节相同，哈希和转换范围见 [archive_manifest.json](archive_manifest.json)。未收到原PPTX，因此没有可重新生成原版式的slides源稿；`slides_reference.md` 不作为Marp源稿使用。

### 后续引用注意

- 已发表比较：2025年11月的10月发效20县与12月以后发效14县，排除11月发效13县。
- 原假说基准期是2025年1—9月；第12页的4—9月是描述统计窗口，两者不要混用。
- Slides与讲稿分别保留，不互相覆盖。讲稿对季节性、前期走势和提前反应的表述更谨慎；引用时注明来自哪份材料、哪一页。
- 讲稿原HTML标为“修正版”。这里保存的是用户提供版本，不是现场逐字录音记录。
- 本目录不把发表后的两期模型、创新性调查或修改建议写回已发表材料。归档不代表新增因果识别结论，也不代表重新核验全部统计结果。

## 数据与描述统计

- [descriptive_stats.ipynb](descriptive_stats.ipynb)：第一次发表所用两份数据的描述统计（日文），重点是上次发表定下的「改定前の求人の動き」和「引上げ幅」。已含运行结果，GitHub上可直接查看。
- 数据说明见 [data/README.md](../data/README.md)；超出本次计划的发效后比较放在 [archive/](../archive/README.md)。

## 在Google Colab运行

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/WUZICANGJIE/minimal_wage_job/blob/main/2026-10-28/descriptive_stats.ipynb)

点上面的按钮打开，选「ランタイム → すべてのセルを実行」即可。第一个代码单元会从GitHub的 `main` 分支下载 `data/raw/` 的数据和日文字体，不需要另外上传文件。数据从 `main` 读取，因此合并到 `main` 之后才能在Colab运行。
