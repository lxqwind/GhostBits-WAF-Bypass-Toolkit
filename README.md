# 👻 GhostBits WAF Bypass Toolkit

> Java `char→byte` 高位截断漏洞（幽灵比特位/Ghost Bits）WAF 绕过工具，专为文件读取/路径穿越场景设计。

---

## ✨ 功能特性
- **Bypass 生成**：一键替换敏感字符（如 `.` `/` `'` 等）为 Ghost Bits 替换体，生成绕过 payload
- **多格式输出**：支持原始字符、URL 编码、curl 命令三种格式，直接适配 Burp/curl 场景
- **Ghost 字符查询**：输入目标 ASCII 字符，快速获取所有低位匹配的 Unicode 替换体
- **原理说明**：内置漏洞原理与攻击链说明，帮助理解绕过逻辑

---

## 🚀 快速开始

### 环境依赖
```bash
# 安装依赖
pip install PyQt6
#使用命令
python3 ghost_bits.py




演示案例：史上最强靶场-好靶场
Ghost Bits Waf绕过 任意文件读取
![](https://github.com/lxqwind/GhostBits-WAF-Bypass-Toolkit/blob/main/images/03b25fbaabb316eda444dfe15a53f7c3.png)




