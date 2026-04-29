👻 GhostBits WAF Bypass Toolkit
Java char→byte 高位截断漏洞（幽灵比特位/Ghost Bits）WAF 绕过工具，专为文件读取/路径穿越场景设计。

✨ 功能特性
● Bypass 生成：一键替换敏感字符（如 . / ' 等）为 Ghost Bits 替换体，生成绕过 payload
● 多格式输出：支持原始字符、URL 编码、curl 命令三种格式，直接适配 Burp/curl 场景
● Ghost 字符查询：输入目标 ASCII 字符，快速获取所有低位匹配的 Unicode 替换体
● 原理说明：内置漏洞原理与攻击链说明，帮助理解绕过逻辑

🚀 快速开始
环境依赖
# 安装依赖
pip install PyQt6
#使用命令
python3 ghost_bits.py




演示案例：史上最强靶场-好靶场
Ghost Bits Waf绕过 任意文件读取
<img width="1802" height="1138" alt="11" src="https://github.com/user-attachments/assets/0eae362c-7761-4a24-9a5d-ef9541ff3dff" />

打开靶场
<img width="1684" height="1282" alt="b5f7266fda622a8fd1ff5b675a7a0695" src="https://github.com/user-attachments/assets/edb32e93-e43c-4e41-8cfb-5aa6e26cb8fb" />
靶场提示/tmp/flag.txt
先丢进去看看反应 
<img width="1914" height="996" alt="6ac1e682066a1a497ff6e37233800b11" src="https://github.com/user-attachments/assets/62486b5a-d072-43f3-9686-eea53ec272a0" />
发现.被拦截了
直接掏出来我们的小工具一把嗦
<img width="1658" height="1282" alt="e94b7af29efafe8734c3f0d588e820fd" src="https://github.com/user-attachments/assets/81bdd29d-b0a5-45f0-a935-1d65f161f9d5" />
至于为什么加那么多../是因为flag在tmp下（/tmp目录是根目录下的一个临时目录） 现在我们处在其他目录 要跳到根目录查看 具体可以自己问ai。
<img width="1870" height="842" alt="03b25fbaabb316eda444dfe15a53f7c3" src="https://github.com/user-attachments/assets/e7116ed9-8a87-4095-b848-e7f495e8407f" />
也是很轻松就通关了。
以下是工具功能图片展示 ：

<img width="1640" height="1352" alt="bba4aa48-081a-4903-b6e4-94296ac99a05" src="https://github.com/user-attachments/assets/345b6d03-d627-4951-9cd7-79b19dcfdf2f" />
<img width="1606" height="1320" alt="df749882-403d-42c5-a65a-bfb33172673f" src="https://github.com/user-attachments/assets/f7c0883e-6b01-4337-a937-191f42117261" />
大家觉得好用的可以点点🌟 欢迎大佬指出bug 或者改进的地方。
最后好靶场还是遥遥领先啊！！！！！







