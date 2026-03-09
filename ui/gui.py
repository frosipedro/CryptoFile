"""
GUI — Interface gráfica com tkinter para o CryptoFile v1.0.
"""
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from crypto import REGISTRY
from crypto.aes_handler import AESHandler, MAGIC as AES_MAGIC
from crypto.des_handler import DESHandler, MAGIC as DES_MAGIC
from crypto.rsa_handler import RSAHandler, MAGIC as RSA_MAGIC

# ── Constante de chaves RSA (mesma do main.py) ──────────────────────
KEYS_DIR = Path.home() / '.cryptofile' / 'keys'

# ── Paleta de cores (tema escuro Catppuccin-like) ───────────────────
BG      = '#1e1e2e'
BG2     = '#2a2a3e'
BG3     = '#313147'
ACCENT  = '#89b4fa'
GREEN   = '#a6e3a1'
RED     = '#f38ba8'
YELLOW  = '#f9e2af'
PURPLE  = '#cba6f7'
TEXT    = '#cdd6f4'
DIM     = '#6c7086'
BORDER  = '#45475a'


# ── Utilidades puras (sem dependência de ui.terminal) ───────────────

def _human_size(n: float) -> str:
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if n < 1024:
            return f'{n:.1f} {unit}' if unit != 'B' else f'{int(n)} B'
        n /= 1024
    return f'{n:.1f} PB'


def _suggest_enc_path(src: Path) -> Path:
    return src.parent / (src.name + '.enc')


def _suggest_dec_path(src: Path) -> Path:
    name = src.name
    return src.parent / (name[:-4] if name.endswith('.enc') else name + '.dec')


def _detect_handler(src: Path):
    """Detecta algoritmo pelos magic bytes do arquivo cifrado."""
    try:
        with open(src, 'rb') as f:
            head = f.read(16)
    except Exception:
        return None
    mapping = {
        AES_MAGIC: REGISTRY['1'],
        DES_MAGIC: REGISTRY['2'],
        RSA_MAGIC: REGISTRY['3'],
    }
    for magic, handler in mapping.items():
        if head.startswith(magic):
            return handler
    return None


# ═══════════════════════════════════════════════════════════════════
#   JANELA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════

class CryptoFileGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('CryptoFile v1.0')
        self.root.geometry('740x700')
        self.root.minsize(640, 580)
        self.root.configure(bg=BG)

        self._setup_styles()
        self._build_ui()

    # ────────────────────────────────────────────────────────────────
    #   ESTILOS TTK
    # ────────────────────────────────────────────────────────────────

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use('clam')

        # Base
        s.configure('.',
            background=BG, foreground=TEXT,
            font=('Segoe UI', 10),
            bordercolor=BORDER,
            darkcolor=BG2, lightcolor=BG3,
            troughcolor=BG2,
            fieldbackground=BG2,
            insertcolor=TEXT,
            selectbackground=ACCENT,
            selectforeground=BG,
        )

        s.configure('TFrame', background=BG)
        s.configure('Card.TFrame', background=BG2)

        s.configure('TLabel', background=BG, foreground=TEXT)
        s.configure('Card.TLabel', background=BG2, foreground=TEXT)
        s.configure('Dim.TLabel', background=BG, foreground=DIM, font=('Segoe UI', 9))
        s.configure('Title.TLabel', background=BG, foreground=ACCENT,
                    font=('Segoe UI', 17, 'bold'))
        s.configure('Sub.TLabel', background=BG, foreground=DIM, font=('Segoe UI', 9))

        s.configure('TLabelframe', background=BG2, bordercolor=BORDER, relief='flat')
        s.configure('TLabelframe.Label', background=BG2, foreground=ACCENT,
                    font=('Segoe UI', 9, 'bold'))

        s.configure('TSeparator', background=BORDER)

        s.configure('TNotebook', background=BG, tabmargins=[2, 6, 2, 0])
        s.configure('TNotebook.Tab',
            background=BG2, foreground=DIM,
            padding=[18, 8], font=('Segoe UI', 10),
        )
        s.map('TNotebook.Tab',
            background=[('selected', BG3)],
            foreground=[('selected', ACCENT)],
            expand=[('selected', [1, 1, 1, 0])],
        )

        s.configure('TButton',
            background=BG3, foreground=TEXT,
            font=('Segoe UI', 10), relief='flat',
            padding=(10, 5), borderwidth=0,
        )
        s.map('TButton',
            background=[('active', '#3d3d57'), ('pressed', BG2)],
        )

        s.configure('Accent.TButton',
            background=ACCENT, foreground=BG,
            font=('Segoe UI', 10, 'bold'), relief='flat',
            padding=(14, 7), borderwidth=0,
        )
        s.map('Accent.TButton',
            background=[('active', '#74a8f0'), ('pressed', '#5d91d9')],
            foreground=[('active', BG)],
        )

        s.configure('TEntry',
            fieldbackground=BG2, foreground=TEXT,
            insertcolor=TEXT, relief='flat', padding=5,
        )
        s.configure('TCheckbutton', background=BG2, foreground=TEXT)
        s.map('TCheckbutton', background=[('active', BG2)])
        s.configure('TRadiobutton', background=BG2, foreground=TEXT)
        s.map('TRadiobutton', background=[('active', BG2)])

        s.configure('Horizontal.TProgressbar',
            troughcolor=BG2, background=ACCENT, thickness=4,
        )

    # ────────────────────────────────────────────────────────────────
    #   ESTRUTURA PRINCIPAL
    # ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = ttk.Frame(self.root, padding=(24, 18, 24, 12))
        hdr.pack(fill='x')
        ttk.Label(hdr, text='🔐  CryptoFile  v1.0', style='Title.TLabel').pack(anchor='w')
        ttk.Label(hdr,
            text='Criptografia de arquivos  ·  AES-256-GCM  ·  3DES-CBC  ·  RSA-2048',
            style='Sub.TLabel',
        ).pack(anchor='w', pady=(3, 0))

        ttk.Separator(self.root).pack(fill='x', padx=0)

        # Notebook de abas
        self.nb = ttk.Notebook(self.root, padding=(8, 8, 8, 0))
        self.nb.pack(fill='both', expand=True, padx=12, pady=(8, 0))

        self._build_encrypt_tab()
        self._build_decrypt_tab()
        self._build_keys_tab()
        self._build_about_tab()

        # Barra de progresso (visível durante operações)
        self._progress = ttk.Progressbar(
            self.root, mode='indeterminate',
            style='Horizontal.TProgressbar',
        )
        self._progress.pack(fill='x', padx=12, pady=(6, 0))

        ttk.Separator(self.root).pack(fill='x', padx=0, pady=(4, 0))

        # Área de log
        log_wrap = ttk.Frame(self.root, padding=(12, 4, 12, 12))
        log_wrap.pack(fill='x')

        ttk.Label(log_wrap, text='Log', style='Dim.TLabel').pack(anchor='w')

        log_box = tk.Frame(log_wrap, bg=BG2)
        log_box.pack(fill='x', pady=(4, 0))

        self._log_text = tk.Text(
            log_box, height=5,
            bg=BG2, fg=TEXT, insertbackground=TEXT,
            font=('Consolas', 9), relief='flat', bd=8,
            state='disabled', wrap='word',
        )
        sb = ttk.Scrollbar(log_box, command=self._log_text.yview)
        self._log_text.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        self._log_text.pack(side='left', fill='x', expand=True)

        self._log_text.tag_configure('ok',   foreground=GREEN)
        self._log_text.tag_configure('err',  foreground=RED)
        self._log_text.tag_configure('info', foreground=ACCENT)
        self._log_text.tag_configure('warn', foreground=YELLOW)

    # ────────────────────────────────────────────────────────────────
    #   ABA: CRIPTOGRAFAR
    # ────────────────────────────────────────────────────────────────

    def _build_encrypt_tab(self):
        frame = ttk.Frame(self.nb, padding=(4, 8))
        self.nb.add(frame, text='  Criptografar  ')

        # Algoritmo
        alg_lf = ttk.LabelFrame(frame, text='Algoritmo', padding=(14, 8))
        alg_lf.pack(fill='x', padx=4, pady=(0, 8))

        inner = ttk.Frame(alg_lf, style='Card.TFrame')
        inner.pack(fill='x')
        self._enc_algo = tk.StringVar(value='1')
        for key, h in REGISTRY.items():
            ttk.Radiobutton(
                inner,
                text=f'  {h.name}  —  {h.kind}',
                variable=self._enc_algo,
                value=key,
                command=self._on_enc_algo_change,
                style='TRadiobutton',
            ).pack(side='left', padx=(0, 16), pady=4)

        # Arquivo de entrada
        in_lf = ttk.LabelFrame(frame, text='Arquivo de Entrada', padding=(14, 8))
        in_lf.pack(fill='x', padx=4, pady=(0, 8))
        in_row = ttk.Frame(in_lf, style='Card.TFrame')
        in_row.pack(fill='x')
        self._enc_src = tk.StringVar()
        ttk.Entry(in_row, textvariable=self._enc_src).pack(
            side='left', fill='x', expand=True, pady=2)
        ttk.Button(in_row, text='Procurar…',
                   command=self._browse_enc_src).pack(side='left', padx=(8, 0), pady=2)

        # Arquivo de saída
        out_lf = ttk.LabelFrame(frame, text='Arquivo de Saída', padding=(14, 8))
        out_lf.pack(fill='x', padx=4, pady=(0, 8))
        out_row = ttk.Frame(out_lf, style='Card.TFrame')
        out_row.pack(fill='x')
        self._enc_dst = tk.StringVar()
        ttk.Entry(out_row, textvariable=self._enc_dst).pack(
            side='left', fill='x', expand=True, pady=2)
        ttk.Button(out_row, text='Salvar como…',
                   command=self._browse_enc_dst).pack(side='left', padx=(8, 0), pady=2)

        # Credenciais (frame mutável conforme algoritmo)
        self._enc_cred_lf = ttk.LabelFrame(frame, text='Chave / Senha', padding=(14, 8))
        self._enc_cred_lf.pack(fill='x', padx=4, pady=(0, 8))
        self._enc_cred_widgets: dict = {}
        self._build_enc_sym_creds()

        # Botão de ação
        btn_row = ttk.Frame(frame)
        btn_row.pack(fill='x', padx=4)
        ttk.Button(
            btn_row, text='🔒  Criptografar',
            style='Accent.TButton', command=self._run_encrypt,
        ).pack(side='right')

    def _build_enc_sym_creds(self):
        for w in self._enc_cred_lf.winfo_children():
            w.destroy()
        self._enc_cred_widgets.clear()
        parent = ttk.Frame(self._enc_cred_lf, style='Card.TFrame')
        parent.pack(fill='x')
        for label, key in [('Senha:', 'pwd1'), ('Confirmar senha:', 'pwd2')]:
            row = ttk.Frame(parent, style='Card.TFrame')
            row.pack(fill='x', pady=2)
            ttk.Label(row, text=label, width=18, style='Card.TLabel').pack(side='left')
            entry = ttk.Entry(row, show='•')
            entry.pack(side='left', fill='x', expand=True)
            self._enc_cred_widgets[key] = entry

    def _build_enc_rsa_creds(self):
        for w in self._enc_cred_lf.winfo_children():
            w.destroy()
        self._enc_cred_widgets.clear()
        parent = ttk.Frame(self._enc_cred_lf, style='Card.TFrame')
        parent.pack(fill='x')
        row = ttk.Frame(parent, style='Card.TFrame')
        row.pack(fill='x', pady=2)
        ttk.Label(row, text='Chave pública (.pem):', width=22,
                  style='Card.TLabel').pack(side='left')
        var = tk.StringVar()
        ttk.Entry(row, textvariable=var).pack(side='left', fill='x', expand=True)
        ttk.Button(row, text='Procurar…',
                   command=self._browse_enc_pub_key).pack(side='left', padx=(8, 0))
        self._enc_cred_widgets['pub_key'] = var

    def _on_enc_algo_change(self):
        h = REGISTRY[self._enc_algo.get()]
        if h.kind == 'simétrico':
            self._build_enc_sym_creds()
        else:
            self._build_enc_rsa_creds()

    def _browse_enc_src(self):
        p = filedialog.askopenfilename(title='Selecionar Arquivo para Criptografar')
        if p:
            self._enc_src.set(p)
            if not self._enc_dst.get():
                self._enc_dst.set(str(_suggest_enc_path(Path(p))))

    def _browse_enc_dst(self):
        p = filedialog.asksaveasfilename(
            title='Salvar Arquivo Criptografado',
            defaultextension='.enc',
            filetypes=[('Arquivo cifrado', '*.enc'), ('Todos os arquivos', '*.*')],
        )
        if p:
            self._enc_dst.set(p)

    def _browse_enc_pub_key(self):
        p = filedialog.askopenfilename(
            title='Selecionar Chave Pública RSA',
            filetypes=[('PEM', '*.pem'), ('Todos os arquivos', '*.*')],
            initialdir=str(KEYS_DIR) if KEYS_DIR.exists() else None,
        )
        if p:
            self._enc_cred_widgets['pub_key'].set(p)

    def _run_encrypt(self):
        src = self._enc_src.get().strip()
        dst = self._enc_dst.get().strip()
        handler = REGISTRY[self._enc_algo.get()]

        if not src:
            self._log('Selecione um arquivo de entrada.', 'warn'); return
        if not dst:
            self._log('Informe o caminho do arquivo de saída.', 'warn'); return

        src_path, dst_path = Path(src), Path(dst)
        if not src_path.is_file():
            self._log(f'Arquivo não encontrado: {src}', 'err'); return

        kwargs = {}
        if handler.kind == 'simétrico':
            pwd1 = self._enc_cred_widgets['pwd1'].get()
            pwd2 = self._enc_cred_widgets['pwd2'].get()
            if not pwd1:
                self._log('A senha não pode ser vazia.', 'warn'); return
            if pwd1 != pwd2:
                self._log('As senhas não conferem.', 'warn'); return
            kwargs['password'] = pwd1
        else:
            pub = self._enc_cred_widgets['pub_key'].get().strip()
            if not pub:
                self._log('Selecione a chave pública RSA.', 'warn'); return
            kwargs['public_key_path'] = Path(pub)

        self._log(f'Criptografando {src_path.name} com {handler.name}…', 'info')
        self._set_busy(True)

        def task():
            try:
                handler.encrypt_file(src_path, dst_path, **kwargs)
                size = _human_size(dst_path.stat().st_size)
                self._log(f'✔ Concluído → {dst_path.name}  ({size})', 'ok')
            except Exception as exc:
                self._log(f'✘ Erro: {exc}', 'err')
            finally:
                self._set_busy(False)

        threading.Thread(target=task, daemon=True).start()

    # ────────────────────────────────────────────────────────────────
    #   ABA: DESCRIPTOGRAFAR
    # ────────────────────────────────────────────────────────────────

    def _build_decrypt_tab(self):
        frame = ttk.Frame(self.nb, padding=(4, 8))
        self.nb.add(frame, text='  Descriptografar  ')

        # Arquivo de entrada
        in_lf = ttk.LabelFrame(frame, text='Arquivo Criptografado', padding=(14, 8))
        in_lf.pack(fill='x', padx=4, pady=(0, 8))
        in_row = ttk.Frame(in_lf, style='Card.TFrame')
        in_row.pack(fill='x')
        self._dec_src = tk.StringVar()
        ttk.Entry(in_row, textvariable=self._dec_src).pack(
            side='left', fill='x', expand=True, pady=2)
        ttk.Button(in_row, text='Procurar…',
                   command=self._browse_dec_src).pack(side='left', padx=(8, 0), pady=2)

        # Algoritmo
        alg_lf = ttk.LabelFrame(frame, text='Algoritmo', padding=(14, 8))
        alg_lf.pack(fill='x', padx=4, pady=(0, 8))
        inner_alg = ttk.Frame(alg_lf, style='Card.TFrame')
        inner_alg.pack(fill='x')

        top_row = ttk.Frame(inner_alg, style='Card.TFrame')
        top_row.pack(fill='x', pady=(0, 4))
        self._dec_auto = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            top_row, text='Detectar automaticamente',
            variable=self._dec_auto, command=self._on_dec_auto_change,
            style='TCheckbutton',
        ).pack(side='left')

        self._dec_algo_row = ttk.Frame(inner_alg, style='Card.TFrame')
        self._dec_algo_row.pack(fill='x')
        self._dec_algo = tk.StringVar(value='1')
        for key, h in REGISTRY.items():
            ttk.Radiobutton(
                self._dec_algo_row, text=f'  {h.name}',
                variable=self._dec_algo, value=key,
                command=self._on_dec_algo_change,
            ).pack(side='left', padx=(0, 16))
        self._on_dec_auto_change()

        # Arquivo de saída
        out_lf = ttk.LabelFrame(frame, text='Arquivo de Saída (Restaurado)', padding=(14, 8))
        out_lf.pack(fill='x', padx=4, pady=(0, 8))
        out_row = ttk.Frame(out_lf, style='Card.TFrame')
        out_row.pack(fill='x')
        self._dec_dst = tk.StringVar()
        ttk.Entry(out_row, textvariable=self._dec_dst).pack(
            side='left', fill='x', expand=True, pady=2)
        ttk.Button(out_row, text='Salvar como…',
                   command=self._browse_dec_dst).pack(side='left', padx=(8, 0), pady=2)

        # Credenciais
        self._dec_cred_lf = ttk.LabelFrame(frame, text='Chave / Senha', padding=(14, 8))
        self._dec_cred_lf.pack(fill='x', padx=4, pady=(0, 8))
        self._dec_cred_widgets: dict = {}
        self._build_dec_sym_creds()

        # Botão
        btn_row = ttk.Frame(frame)
        btn_row.pack(fill='x', padx=4)
        ttk.Button(
            btn_row, text='🔓  Descriptografar',
            style='Accent.TButton', command=self._run_decrypt,
        ).pack(side='right')

    def _build_dec_sym_creds(self):
        for w in self._dec_cred_lf.winfo_children():
            w.destroy()
        self._dec_cred_widgets.clear()
        parent = ttk.Frame(self._dec_cred_lf, style='Card.TFrame')
        parent.pack(fill='x')
        row = ttk.Frame(parent, style='Card.TFrame')
        row.pack(fill='x', pady=2)
        ttk.Label(row, text='Senha:', width=22, style='Card.TLabel').pack(side='left')
        entry = ttk.Entry(row, show='•')
        entry.pack(side='left', fill='x', expand=True)
        self._dec_cred_widgets['pwd'] = entry

    def _build_dec_rsa_creds(self):
        for w in self._dec_cred_lf.winfo_children():
            w.destroy()
        self._dec_cred_widgets.clear()
        parent = ttk.Frame(self._dec_cred_lf, style='Card.TFrame')
        parent.pack(fill='x')

        r1 = ttk.Frame(parent, style='Card.TFrame')
        r1.pack(fill='x', pady=2)
        ttk.Label(r1, text='Chave privada (.pem):', width=26,
                  style='Card.TLabel').pack(side='left')
        var_priv = tk.StringVar()
        ttk.Entry(r1, textvariable=var_priv).pack(side='left', fill='x', expand=True)
        ttk.Button(r1, text='Procurar…',
                   command=self._browse_dec_priv_key).pack(side='left', padx=(8, 0))
        self._dec_cred_widgets['priv_key'] = var_priv

        r2 = ttk.Frame(parent, style='Card.TFrame')
        r2.pack(fill='x', pady=2)
        ttk.Label(r2, text='Senha da chave (opcional):', width=26,
                  style='Card.TLabel').pack(side='left')
        var_pp = tk.StringVar()
        ttk.Entry(r2, textvariable=var_pp, show='•').pack(side='left', fill='x', expand=True)
        self._dec_cred_widgets['passphrase'] = var_pp

    def _on_dec_auto_change(self):
        state = 'disabled' if self._dec_auto.get() else 'normal'
        for child in self._dec_algo_row.winfo_children():
            child.configure(state=state)

    def _on_dec_algo_change(self):
        h = REGISTRY[self._dec_algo.get()]
        if h.kind == 'simétrico':
            self._build_dec_sym_creds()
        else:
            self._build_dec_rsa_creds()

    def _browse_dec_src(self):
        p = filedialog.askopenfilename(
            title='Selecionar Arquivo Criptografado',
            filetypes=[('Arquivo cifrado', '*.enc'), ('Todos os arquivos', '*.*')],
        )
        if not p:
            return
        self._dec_src.set(p)
        if not self._dec_dst.get():
            self._dec_dst.set(str(_suggest_dec_path(Path(p))))
        if self._dec_auto.get():
            h = _detect_handler(Path(p))
            if h:
                self._log(f'Algoritmo detectado automaticamente: {h.name}', 'info')
                for k, v in REGISTRY.items():
                    if v is h:
                        self._dec_algo.set(k)
                        self._on_dec_algo_change()
                        break
            else:
                self._log('Não foi possível detectar o algoritmo automaticamente.', 'warn')

    def _browse_dec_dst(self):
        p = filedialog.asksaveasfilename(title='Salvar Arquivo Restaurado')
        if p:
            self._dec_dst.set(p)

    def _browse_dec_priv_key(self):
        p = filedialog.askopenfilename(
            title='Selecionar Chave Privada RSA',
            filetypes=[('PEM', '*.pem'), ('Todos os arquivos', '*.*')],
            initialdir=str(KEYS_DIR) if KEYS_DIR.exists() else None,
        )
        if p:
            self._dec_cred_widgets['priv_key'].set(p)

    def _run_decrypt(self):
        src = self._dec_src.get().strip()
        dst = self._dec_dst.get().strip()

        if not src:
            self._log('Selecione um arquivo criptografado.', 'warn'); return
        if not dst:
            self._log('Informe o caminho do arquivo de saída.', 'warn'); return

        src_path, dst_path = Path(src), Path(dst)
        if not src_path.is_file():
            self._log(f'Arquivo não encontrado: {src}', 'err'); return

        if self._dec_auto.get():
            handler = _detect_handler(src_path)
            if handler is None:
                self._log(
                    'Algoritmo não detectado. Desmarque "Detectar automaticamente" '
                    'e selecione o algoritmo manualmente.', 'warn')
                return
        else:
            handler = REGISTRY[self._dec_algo.get()]

        kwargs = {}
        if handler.kind == 'simétrico':
            pwd = self._dec_cred_widgets['pwd'].get()
            if not pwd:
                self._log('A senha não pode ser vazia.', 'warn'); return
            kwargs['password'] = pwd
        else:
            priv = self._dec_cred_widgets['priv_key'].get().strip()
            if not priv:
                self._log('Selecione a chave privada RSA.', 'warn'); return
            kwargs['private_key_path'] = Path(priv)
            kwargs['passphrase'] = self._dec_cred_widgets['passphrase'].get()

        self._log(f'Descriptografando {src_path.name} com {handler.name}…', 'info')
        self._set_busy(True)

        def task():
            try:
                handler.decrypt_file(src_path, dst_path, **kwargs)
                size = _human_size(dst_path.stat().st_size)
                self._log(f'✔ Concluído → {dst_path.name}  ({size})', 'ok')
            except Exception as exc:
                self._log(f'✘ Erro: {exc}', 'err')
            finally:
                self._set_busy(False)

        threading.Thread(target=task, daemon=True).start()

    # ────────────────────────────────────────────────────────────────
    #   ABA: CHAVES RSA
    # ────────────────────────────────────────────────────────────────

    def _build_keys_tab(self):
        frame = ttk.Frame(self.nb, padding=(4, 8))
        self.nb.add(frame, text='  Chaves RSA  ')

        gen_lf = ttk.LabelFrame(frame, text='Gerar Novo Par de Chaves RSA-2048', padding=(14, 8))
        gen_lf.pack(fill='x', padx=4, pady=(0, 8))
        inner = ttk.Frame(gen_lf, style='Card.TFrame')
        inner.pack(fill='x')

        self._key_name = tk.StringVar(value='minhas_chaves')
        self._key_priv = tk.StringVar()
        self._key_pub  = tk.StringVar()
        self._key_pp   = tk.StringVar()

        def _update_paths(*_):
            name = self._key_name.get().strip() or 'minhas_chaves'
            self._key_priv.set(str(KEYS_DIR / f'{name}_private.pem'))
            self._key_pub.set(str(KEYS_DIR / f'{name}_public.pem'))

        self._key_name.trace_add('write', _update_paths)
        _update_paths()

        fields = [
            ('Nome do perfil:',            self._key_name, None),
            ('Chave privada (.pem):',      self._key_priv, None),
            ('Chave pública (.pem):',      self._key_pub,  None),
            ('Senha da chave (opcional):', self._key_pp,   '•'),
        ]
        for label, var, show in fields:
            row = ttk.Frame(inner, style='Card.TFrame')
            row.pack(fill='x', pady=2)
            ttk.Label(row, text=label, width=26, style='Card.TLabel').pack(side='left')
            kw = {'show': show} if show else {}
            ttk.Entry(row, textvariable=var, **kw).pack(side='left', fill='x', expand=True)

        btn_row = ttk.Frame(frame)
        btn_row.pack(fill='x', padx=4, pady=(0, 8))
        ttk.Button(
            btn_row, text='⚙  Gerar Par de Chaves',
            style='Accent.TButton', command=self._run_gen_keys,
        ).pack(side='left')
        ttk.Button(
            btn_row, text='↻  Atualizar lista',
            command=self._refresh_keys_list,
        ).pack(side='left', padx=(8, 0))

        list_lf = ttk.LabelFrame(frame, text='Chaves Disponíveis', padding=(14, 8))
        list_lf.pack(fill='both', expand=True, padx=4)
        inner_list = ttk.Frame(list_lf, style='Card.TFrame')
        inner_list.pack(fill='both', expand=True)

        self._keys_text = tk.Text(
            inner_list, height=6,
            bg=BG2, fg=TEXT, font=('Consolas', 9),
            relief='flat', state='disabled',
        )
        sb = ttk.Scrollbar(inner_list, command=self._keys_text.yview)
        self._keys_text.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        self._keys_text.pack(side='left', fill='both', expand=True)

        self._refresh_keys_list()

    def _run_gen_keys(self):
        priv = Path(self._key_priv.get().strip())
        pub  = Path(self._key_pub.get().strip())
        pp   = self._key_pp.get()

        if not self._key_priv.get().strip() or not self._key_pub.get().strip():
            self._log('Informe os caminhos para as chaves.', 'warn'); return

        self._log('Gerando par de chaves RSA-2048…', 'info')
        self._set_busy(True)

        def task():
            try:
                RSAHandler.generate_keypair(priv, pub, pp)
                self._log(f'✔ Chaves geradas!  {priv.name}  /  {pub.name}', 'ok')
                self.root.after(0, self._refresh_keys_list)
            except Exception as exc:
                self._log(f'✘ Erro ao gerar chaves: {exc}', 'err')
            finally:
                self._set_busy(False)

        threading.Thread(target=task, daemon=True).start()

    def _refresh_keys_list(self):
        pems = sorted(KEYS_DIR.glob('*.pem')) if KEYS_DIR.exists() else []
        self._keys_text.configure(state='normal')
        self._keys_text.delete('1.0', 'end')
        if pems:
            for p in pems:
                size = _human_size(p.stat().st_size)
                self._keys_text.insert('end', f'  {p.name}  ({size})\n')
        else:
            self._keys_text.insert('end', f'  Nenhuma chave encontrada em:\n  {KEYS_DIR}\n')
        self._keys_text.configure(state='disabled')

    # ────────────────────────────────────────────────────────────────
    #   ABA: SOBRE
    # ────────────────────────────────────────────────────────────────

    def _build_about_tab(self):
        frame = ttk.Frame(self.nb, padding=(12, 12))
        self.nb.add(frame, text='  Sobre  ')

        alg_lf = ttk.LabelFrame(frame, text='Algoritmos Suportados', padding=(14, 10))
        alg_lf.pack(fill='x', padx=4, pady=(0, 10))

        for h in REGISTRY.values():
            row = tk.Frame(alg_lf, bg=BG2)
            row.pack(fill='x', pady=4)

            kind_color = GREEN if h.kind == 'simétrico' else PURPLE
            tk.Label(row, text=h.name,
                     font=('Segoe UI', 11, 'bold'), bg=BG2, fg=ACCENT,
                     width=14, anchor='w').pack(side='left', padx=(0, 8))

            info_col = tk.Frame(row, bg=BG2)
            info_col.pack(side='left', fill='x', expand=True)
            tk.Label(info_col,
                     text=f'Tipo: {h.kind.capitalize()}  ·  {h.key_info}',
                     bg=BG2, fg=kind_color,
                     font=('Segoe UI', 9), anchor='w').pack(anchor='w')
            tk.Label(info_col, text=h.description,
                     bg=BG2, fg=TEXT, font=('Segoe UI', 9), anchor='w').pack(anchor='w')

        notes_lf = ttk.LabelFrame(frame, text='Recomendações', padding=(14, 8))
        notes_lf.pack(fill='x', padx=4)
        notes = [
            ('AES-256-GCM', 'Padrão recomendado. Rápido, seguro e autenticado.'),
            ('3DES-CBC',    'Legado. Use apenas por compatibilidade com sistemas antigos.'),
            ('RSA-2048',    'Ideal para troca de chaves cifradas entre partes diferentes.'),
        ]
        for algo, desc in notes:
            row = tk.Frame(notes_lf, bg=BG2)
            row.pack(fill='x', pady=1)
            tk.Label(row, text=f'  {algo}', bg=BG2, fg=ACCENT,
                     font=('Consolas', 9, 'bold'), width=14, anchor='w').pack(side='left')
            tk.Label(row, text=f'→  {desc}', bg=BG2, fg=DIM,
                     font=('Consolas', 9), anchor='w').pack(side='left')

    # ────────────────────────────────────────────────────────────────
    #   HELPERS
    # ────────────────────────────────────────────────────────────────

    def _log(self, msg: str, level: str = 'info'):
        def _write():
            self._log_text.configure(state='normal')
            self._log_text.insert('end', f'  {msg}\n', level)
            self._log_text.see('end')
            self._log_text.configure(state='disabled')
        self.root.after(0, _write)

    def _set_busy(self, busy: bool):
        def _update():
            if busy:
                self._progress.start(12)
                self.root.configure(cursor='wait')
            else:
                self._progress.stop()
                self.root.configure(cursor='')
        self.root.after(0, _update)


# ═══════════════════════════════════════════════════════════════════
#   PONTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════

def run():
    root = tk.Tk()
    CryptoFileGUI(root)
    root.mainloop()


if __name__ == '__main__':
    run()
