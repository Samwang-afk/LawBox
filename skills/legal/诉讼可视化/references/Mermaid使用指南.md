# Mermaid使用指南

> **来源**: 诉讼可视化Skill - 第九部分：使用说明
> **用途**: 介绍如何查看和导出Mermaid图表的各种方式

---

## 如何查看Mermaid图表

### 1. 在线编辑器
访问 https://mermaid.live ，粘贴.mmd文件内容即可查看和导出

### 2. VS Code
安装 Markdown Preview Mermaid Support 插件

### 3. Typora/Obsidian
原生支持Mermaid渲染

### 4. 命令行导出
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i 图表名称.mmd -o 图表名称.png
```

---

## 图表更新说明

如案件信息有变化，重新运行诉讼可视化Skill即可更新图表。
