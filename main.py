import sys
import os
import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkinter import ttk
import database
import file_transfer
import uuid

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "Hokimiyat_Data")
if not os.path.exists(DATA_DIR):
    try: os.makedirs(DATA_DIR)
    except: pass

CONFIG_PATH = os.path.join(DATA_DIR, "config.json")

from datetime import datetime
from PIL import Image
import io

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

database.init_db()

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

import os
import json
from tkinter import simpledialog, messagebox

import json
import os
import threading
from tkinter import simpledialog

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hokimiyat Boshqaruv Tizimi - Cloud Edition")
        self.geometry("1600x900")
        self.minsize(1450, 850)
        self.configure(fg_color="#0f172a") # Deep slate background
        
        self.current_user = None
        self.is_active_view = 1

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        import database
        database.init_db()
        self.start_app()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def build_network_ui(self):
        pass

    def on_closing(self):
        self.destroy()

    def start_app(self):
        self.build_login_ui()
        self.bind_all('<Any-KeyPress>', self.reset_inactivity_timer)
        self.bind_all('<Any-Motion>', self.reset_inactivity_timer)
        self.reset_inactivity_timer()


    def reset_inactivity_timer(self, event=None):
        if hasattr(self, 'inactivity_id'):
            self.after_cancel(self.inactivity_id)
        # Always run the timer, but only logout if current_user is not None
        self.inactivity_id = self.after(900000, self.auto_logout)  # 15 minutes (900,000 ms)

    def auto_logout(self):
        if getattr(self, 'current_user', None):
            from tkinter import messagebox
            self.current_user = None
            if hasattr(self, 'main_container'):
                self.main_container.grid_forget()
            self.build_login_ui()
            messagebox.showwarning("Qulflangan", "15 daqiqa davomida hech qanday amal bajarilmagani uchun dastur qulflandi. Iltimos, qayta kiring.")


    def update_treeview_style(self):
        style = ttk.Style()
        style.theme_use("default")
        bg, fg, field_bg, sel_bg, sel_fg, head_bg, head_fg = "#1e293b", "#f8fafc", "#1e293b", "#334155", "#60a5fa", "#0f172a", "#94a3b8"

        style.configure("Treeview", background=bg, foreground=fg, rowheight=40, fieldbackground=field_bg, borderwidth=0, font=('Roboto', 12))
        style.map('Treeview', background=[('selected', sel_bg)], foreground=[('selected', sel_fg)])
        style.configure("Treeview.Heading", background=head_bg, foreground=head_fg, relief="flat", font=('Roboto', 12, 'bold'))
        style.map("Treeview.Heading", background=[('active', head_bg)])

    def build_login_ui(self):
        self.login_container = ctk.CTkFrame(self, fg_color="transparent")
        self.login_container.grid(row=0, column=0, sticky="nsew")
        self.login_container.grid_rowconfigure(0, weight=1)
        self.login_container.grid_columnconfigure(0, weight=1)
        
        card = ctk.CTkFrame(self.login_container, corner_radius=15, width=400, height=450, fg_color="#1e293b")
        card.grid(row=0, column=0)
        card.grid_propagate(False)
        card.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        card.grid_columnconfigure(0, weight=1)
        
        import database
        if getattr(sys, 'frozen', False):
            BASE_DIR = os.path.dirname(sys.executable)
        else:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            
        DATA_DIR = os.path.join(BASE_DIR, "Hokimiyat_Data")
        if not os.path.exists(DATA_DIR):
            try: os.makedirs(DATA_DIR)
            except: pass
            
        CONFIG_PATH = os.path.join(DATA_DIR, "config.json")

        try:
            users_count = database.get_users_count()
        except:
            users_count = 0
            
        if users_count == 0:
            ctk.CTkLabel(card, text="🏛️", font=("Roboto", 50)).grid(row=1, column=0)
            ctk.CTkLabel(card, text="Yangi Baza Sozlamasi", font=("Roboto", 24, "bold")).grid(row=2, column=0)
            ctk.CTkLabel(card, text="Dastlabki foydalanuvchini (Admin) yarating", font=("Roboto", 14), text_color="#cbd5e1").grid(row=2, column=0, sticky="s", pady=(0, 10))
            
            reg_user = ctk.CTkEntry(card, placeholder_text="Yangi Login", width=280, height=45, corner_radius=10)
            reg_user.grid(row=3, column=0)
            reg_pass = ctk.CTkEntry(card, placeholder_text="Yangi Parol", show="*", width=280, height=45, corner_radius=10)
            reg_pass.grid(row=4, column=0)
            
            def do_register(event=None):
                u = reg_user.get().strip()
                p = reg_pass.get().strip()
                if not u or not p: return
                database.add_user(u, p, "super_owner", 99)
                self.login_container.grid_forget()
                self.build_login_ui()
                
            reg_user.bind('<Return>', do_register)
            reg_pass.bind('<Return>', do_register)
            ctk.CTkButton(card, text="Yaratish", command=do_register, fg_color="#059669", width=280, height=45, corner_radius=10).grid(row=5, column=0, pady=(0, 30))
        else:
            ctk.CTkLabel(card, text="🏛️", font=("Roboto", 50)).grid(row=1, column=0)
            ctk.CTkLabel(card, text="Tizimga Kirish", font=("Roboto", 24, "bold")).grid(row=2, column=0)
            self.login_user = ctk.CTkEntry(card, placeholder_text="Login", width=280, height=45, corner_radius=10)
            self.login_user.grid(row=3, column=0)
            self.login_pass = ctk.CTkEntry(card, placeholder_text="Parol", show="*", width=280, height=45, corner_radius=10)
            self.login_pass.grid(row=4, column=0)
            self.login_user.bind('<Return>', self.do_login)
            self.login_pass.bind('<Return>', self.do_login)
            ctk.CTkButton(card, text="Kirish", command=self.do_login, width=280, height=45, corner_radius=10).grid(row=5, column=0, pady=(0, 10))
            

    def do_login(self, event=None):
        user = database.login(self.login_user.get(), self.login_pass.get())
        if user:
            self.current_user = {'id': user[0], 'username': user[1], 'role': user[2], 'access_level': user[3]}
            self.login_container.grid_forget()
            database.add_activity(f"Tizimga kirdi: {user[1]}", "update")
            self.build_main_ui()
        else:
            messagebox.showerror("Xato", "Xato login/parol!")

    def build_main_ui(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=1)

        # LEFT SIDEBAR
        self.sidebar = ctk.CTkFrame(self.main_container, width=280, corner_radius=0, fg_color="#1e293b", border_width=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(8, weight=1)
        
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(pady=30, padx=20, fill="x")
        ctk.CTkLabel(title_frame, text="🏛️ HOKIMIYAT TIZIMI", font=("Roboto", 20, "bold"), text_color="white").pack(anchor="w")

        btn_args = {"width": 240, "height": 45, "corner_radius": 10, "anchor": "w", "font": ("Roboto", 15, "bold")}
        self.sidebar_btns = []
        
        self.btn_dash = ctk.CTkButton(self.sidebar, text="🏠 Bosh Sahifa", command=self.show_dashboard, **btn_args)
        self.btn_dash.pack(pady=5, padx=20)
        self.sidebar_btns.append(self.btn_dash)

        self.btn_list = ctk.CTkButton(self.sidebar, text="📋 Faol Xodimlar", command=lambda: self.show_list(1), **btn_args)
        self.btn_list.pack(pady=5, padx=20)
        self.sidebar_btns.append(self.btn_list)

        self.btn_inactive = ctk.CTkButton(self.sidebar, text="🗃️ Maxsus Holatlar", command=lambda: self.show_list(0), **btn_args)
        self.btn_inactive.pack(pady=5, padx=20)
        self.sidebar_btns.append(self.btn_inactive)

        self.btn_orgs = ctk.CTkButton(self.sidebar, text="🏢 Tashkilotlar", command=self.show_orgs, **btn_args)
        self.btn_orgs.pack(pady=5, padx=20)
        self.sidebar_btns.append(self.btn_orgs)
        self.btn_meetings = ctk.CTkButton(self.sidebar, text="🤝 Majlislar", command=self.show_meetings, **btn_args)
        self.btn_meetings.pack(pady=5, padx=20)
        self.sidebar_btns.append(self.btn_meetings)

        self.btn_attendance = ctk.CTkButton(self.sidebar, text="📅 Davomat", command=self.show_attendance, **btn_args)
        self.btn_attendance.pack(pady=5, padx=20)
        self.sidebar_btns.append(self.btn_attendance)
        
        self.btn_search = ctk.CTkButton(self.sidebar, text="🔍 Kengaytirilgan Qidiruv", command=self.show_search, **btn_args)
        self.btn_search.pack(pady=5, padx=20)
        self.sidebar_btns.append(self.btn_search)
        
        if self.current_user['access_level'] >= 3:
            self.btn_settings = ctk.CTkButton(self.sidebar, text="⚙️ Xavfsizlik & Sozlama", command=self.show_settings, **btn_args)
            self.btn_settings.pack(pady=5, padx=20)
            self.sidebar_btns.append(self.btn_settings)

            self.btn_add = ctk.CTkButton(self.sidebar, text="➕ Yangi Qo'shish", border_width=1, border_color="#10b981", text_color="#10b981", fg_color="transparent", hover_color="#064e3b", width=240, height=45, corner_radius=10, anchor="w", font=("Roboto", 15, "bold"), command=lambda: self.open_add_modal(getattr(self, 'current_dept_filter', None)))
            self.btn_add.pack(pady=20, padx=20)

        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", pady=20, padx=20, fill="x")
        ctk.CTkLabel(bottom_frame, text=f"👤 {self.current_user['username']} | Lvl {self.current_user['access_level']}", text_color="#94a3b8", font=("Roboto", 14)).pack(anchor="w", pady=(0,10))
        ctk.CTkButton(bottom_frame, text="Chiqish", fg_color="#ef4444", hover_color="#dc2626", text_color="white", width=240, height=45, corner_radius=10, font=("Roboto", 15, "bold"), command=self.logout).pack()

        # RIGHT WORKSPACE
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        self.header_bar = ctk.CTkFrame(self.content_frame, fg_color="transparent", height=80)
        self.header_bar.grid(row=0, column=0, sticky="ew", padx=30, pady=(20,0))
        self.header_bar.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.header_bar, text="Welcome to the Hokimiyat Boshqaruv Tizimi", font=("Roboto", 28, "bold"), text_color="white").grid(row=0, column=0, sticky="w")
        
        search_frame = ctk.CTkFrame(self.header_bar, fg_color="transparent")
        search_frame.grid(row=0, column=1, sticky="e")
        self.global_search = ctk.CTkEntry(search_frame, placeholder_text="Umumiy qidiruv...", width=250, height=40, corner_radius=10, font=("Roboto", 14))
        self.global_search.pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Qidirish", width=90, height=40, corner_radius=10, font=("Roboto", 14, "bold"), command=self.do_search).pack(side="left")

        self.dash_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.list_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.settings_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.orgs_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.meetings_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.attendance_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.adv_search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        self.build_dashboard_content()
        self.build_list_content()
        self.build_orgs_content()
        self.build_meetings_content()
        self.build_attendance_content()
        self.build_search_content()
        if self.current_user['access_level'] >= 3:
            self.build_settings_content()
            
        self.update_treeview_style()
        self.show_dashboard()

    def set_active_btn(self, active_btn):
        self.active_btn = active_btn
        active_fg = "#dc2626" 
        for btn in self.sidebar_btns:
            if btn == self.active_btn:
                btn.configure(fg_color=active_fg, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color="#cbd5e1")

    # --- DASHBOARD CONTENT ---
    def build_dashboard_content(self):
        self.dash_frame.grid_rowconfigure(2, weight=1)
        self.dash_frame.grid_columnconfigure(0, weight=1)

        kpi_container = ctk.CTkFrame(self.dash_frame, fg_color="transparent")
        kpi_container.grid(row=1, column=0, sticky="ew", padx=30, pady=20)
        kpi_container.grid_columnconfigure((0,1,2,3), weight=1, uniform="kpi")

        self.kpi_active = self.create_kpi_card(kpi_container, 0, "Faol Xodimlar", "0", False)
        self.kpi_users = self.create_kpi_card(kpi_container, 1, "Tizim Foydalanuvchilari", "0", False)
        self.kpi_depts = self.create_kpi_card(kpi_container, 2, "Bo'limlar Soni", "0", True)
        self.kpi_roles = self.create_kpi_card(kpi_container, 3, "Ruxsat Darajalari", "0", False)

        data_container = ctk.CTkFrame(self.dash_frame, fg_color="transparent")
        data_container.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 20))
        data_container.grid_columnconfigure((0,1), weight=1, uniform="data")
        data_container.grid_rowconfigure(0, weight=1)

        chart_card = ctk.CTkFrame(data_container, fg_color="#1e293b", corner_radius=15, border_width=1, border_color="#334155")
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        chart_card.grid_columnconfigure(0, weight=1)
        chart_card.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(chart_card, text="BO'LIMLAR BO'YICHA TAQSIMOT", font=("Roboto", 16, "bold"), text_color="#94a3b8").grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        self.chart_container = ctk.CTkFrame(chart_card, fg_color="transparent")
        self.chart_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        feed_card = ctk.CTkFrame(data_container, fg_color="#1e293b", corner_radius=15, border_width=1, border_color="#334155")
        feed_card.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        feed_card.grid_columnconfigure(0, weight=1)
        feed_card.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(feed_card, text="OXIRGI FAOLIYAT", font=("Roboto", 16, "bold"), text_color="#94a3b8").grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        self.feed_scroll = ctk.CTkScrollableFrame(feed_card, fg_color="transparent")
        self.feed_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 15))

    def create_kpi_card(self, parent, col, title, value, show_new=False):
        card = ctk.CTkFrame(parent, fg_color="#1e293b", corner_radius=15, height=130, border_width=1, border_color="#334155")
        card.grid(row=0, column=col, sticky="ew", padx=10)
        card.grid_propagate(False)
        
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(20, 5))
        
        lbl_val = ctk.CTkLabel(top, text=value, font=("Roboto", 36, "bold"), text_color="white")
        lbl_val.pack(side="left")
        
        if show_new:
            badge = ctk.CTkLabel(top, text="NEW", fg_color="#ef4444", text_color="white", corner_radius=5, font=("Roboto", 10, "bold"), width=40, height=20)
            badge.pack(side="left", padx=10, pady=(10,0))
            
        ctk.CTkLabel(card, text=title, font=("Roboto", 14), text_color="#94a3b8").pack(anchor="w", padx=20)
        return lbl_val

    def load_dashboard_data(self):
        act_p, tot_u, tot_d, acc_l = database.get_dashboard_stats()
        self.kpi_active.configure(text=str(act_p))
        self.kpi_users.configure(text=str(tot_u))
        self.kpi_depts.configure(text=str(tot_d))
        self.kpi_roles.configure(text=str(acc_l))

        for w in self.chart_container.winfo_children(): w.destroy()
        
        depts_data = database.get_department_distribution()
        labels = [d[0] for d in depts_data]
        sizes = [d[1] for d in depts_data]
        
        if not sizes:
            labels = ["Bo'limlar yo'q"]
            sizes = [1]

        fig = Figure(figsize=(5, 5), dpi=100)
        fig.patch.set_facecolor('#1e293b')
        ax = fig.add_subplot(111)
        
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, textprops=dict(color="w"))
        
        centre_circle = matplotlib.patches.Circle((0,0),0.70,fc='#1e293b')
        fig.gca().add_artist(centre_circle)
        
        ax.axis('equal')  
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        for w in self.feed_scroll.winfo_children(): w.destroy()
        activities = database.get_recent_activities(15)
        for act in activities:
            msg = act[0]
            typ = act[1]
            ts = act[2]
            
            color = "#3b82f6"
            if typ == "add": color = "#10b981"
            elif typ == "delete": color = "#ef4444"
            
            row = ctk.CTkFrame(self.feed_scroll, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row, text="●", text_color=color, font=("Roboto", 18)).pack(side="left", padx=(5,10))
            ctk.CTkLabel(row, text=msg, text_color="white", font=("Roboto", 14), wraplength=400, justify="left").pack(side="left")
            ctk.CTkLabel(row, text=ts, text_color="#64748b", font=("Roboto", 12)).pack(side="right", padx=10)


    # --- LIST CONTENT AND FILTERS ---
    def build_list_content(self):
        self.list_frame.grid_rowconfigure(2, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)
        
        self.dept_tabs_container = ctk.CTkScrollableFrame(self.list_frame, orientation="horizontal", height=50, fg_color="transparent")
        self.dept_tabs_container.grid(row=0, column=0, sticky="ew", padx=30, pady=(10, 0))
        
        filter_frame = ctk.CTkFrame(self.list_frame, fg_color="#1e293b", corner_radius=10)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(10,10))
        
        ctk.CTkLabel(filter_frame, text="Yosh (dan):", text_color="#cbd5e1").pack(side="left", padx=(15,5), pady=10)
        self.age_min = ctk.CTkEntry(filter_frame, width=60, height=35, placeholder_text="18")
        self.age_min.pack(side="left")
        
        ctk.CTkLabel(filter_frame, text="Yosh (gacha):", text_color="#cbd5e1").pack(side="left", padx=(15,5))
        self.age_max = ctk.CTkEntry(filter_frame, width=60, height=35, placeholder_text="65")
        self.age_max.pack(side="left")

        ctk.CTkLabel(filter_frame, text="Ism qidiruv:", text_color="#cbd5e1").pack(side="left", padx=(15,5))
        self.name_filter = ctk.CTkEntry(filter_frame, width=220, height=35, placeholder_text="F.I.SH. bo'yicha qidirish...")
        self.name_filter.pack(side="left")

        ctk.CTkButton(filter_frame, text="🔍 Filtrlash", width=100, height=35, command=self.load_people, fg_color="#3b82f6").pack(side="left", padx=(15, 5))
        ctk.CTkButton(filter_frame, text="✖ Tozalash", width=100, height=35, fg_color="#64748b", command=self.clear_filters).pack(side="left")

        self.tree_container = ctk.CTkFrame(self.list_frame, corner_radius=15, fg_color="#1e293b", border_width=1, border_color="#334155")
        self.tree_container.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0,20))
        self.tree_container.grid_rowconfigure(1, weight=1)
        self.tree_container.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.tree_container, fg_color="transparent", height=40)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header_frame.grid_columnconfigure((1,3), weight=1)
        
        ctk.CTkLabel(header_frame, text="ID", font=("Roboto", 12, "bold"), text_color="#94a3b8", width=50).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(header_frame, text="F.I.SH & Holati", font=("Roboto", 12, "bold"), text_color="#94a3b8").grid(row=0, column=1, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(header_frame, text="YOSH", font=("Roboto", 12, "bold"), text_color="#94a3b8", width=60).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(header_frame, text="LAVOZIMI", font=("Roboto", 12, "bold"), text_color="#94a3b8").grid(row=0, column=3, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(header_frame, text="FAOLIYAT", font=("Roboto", 12, "bold"), text_color="#94a3b8", width=120).grid(row=0, column=4, padx=10, pady=10, sticky="w")

        self.roster_scroll = ctk.CTkScrollableFrame(self.tree_container, fg_color="transparent")
        self.roster_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.pagination_frame = ctk.CTkFrame(self.tree_container, fg_color="transparent", height=40)
        self.pagination_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        
        self.btn_prev_page = ctk.CTkButton(self.pagination_frame, text="◀ Oldingi", width=100, fg_color="#475569", command=self.prev_page)
        self.btn_prev_page.pack(side="left", padx=10)
        
        self.lbl_page_info = ctk.CTkLabel(self.pagination_frame, text="Sahifa: 1 / 1", font=("Roboto", 13, "bold"), text_color="white")
        self.lbl_page_info.pack(side="left", expand=True)
        
        self.btn_next_page = ctk.CTkButton(self.pagination_frame, text="Keyingi ▶", width=100, fg_color="#475569", command=self.next_page)
        self.btn_next_page.pack(side="right", padx=10)

    def prev_page(self):
        if getattr(self, 'current_page', 1) > 1:
            self.current_page -= 1
            self.load_people(reset_page=False)

    def next_page(self):
        if getattr(self, 'current_page', 1) < getattr(self, 'max_page', 1):
            self.current_page += 1
            self.load_people(reset_page=False)

    def clear_filters(self):
        self.age_min.delete(0, 'end')
        self.age_max.delete(0, 'end')
        self.name_filter.delete(0, 'end')
        self.load_people()

    # --- NAVIGATION ---
    
    def show_search(self):
        self.set_active_btn(self.btn_search)
        self.dash_frame.grid_forget()
        self.list_frame.grid_forget()
        self.orgs_frame.grid_forget()
        self.settings_frame.grid_forget()
        self.attendance_frame.grid_forget()
        if hasattr(self, 'meetings_frame'): self.meetings_frame.grid_forget()
        self.adv_search_frame.grid(row=1, column=0, sticky="nsew")
        self.execute_search()

    def build_search_content(self):
        self.adv_search_frame.grid_rowconfigure(1, weight=1)
        self.adv_search_frame.grid_columnconfigure(0, weight=1)
        
        # --- Top Filter Area ---
        header_frame = ctk.CTkFrame(self.adv_search_frame, fg_color="#1e293b", corner_radius=10)
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        
        title_lbl = ctk.CTkLabel(header_frame, text="🔍 Kengaytirilgan Qidiruv (Xodimlar kesimida)", font=("Roboto", 20, "bold"), text_color="white")
        title_lbl.grid(row=0, column=0, columnspan=4, pady=(15, 15), padx=20, sticky="w")
        
        # Variables
        self.search_var_name = ctk.StringVar()
        self.search_var_pos = ctk.StringVar(value="Barchasi")
        self.search_var_dept = ctk.StringVar(value="Barchasi")
        self.search_var_act = ctk.StringVar()
        self.search_var_event = ctk.StringVar(value="Barchasi")
        self.search_var_exp = ctk.StringVar()
        
        # Add trace for live search
        for v in [self.search_var_name, self.search_var_pos, self.search_var_dept, self.search_var_act, self.search_var_event, self.search_var_exp]:
            v.trace_add("write", lambda *args: self.execute_search())
        
        # Row 1 Labels
        ctk.CTkLabel(header_frame, text="F.I.O. (Masalan: Anvarov Bekzod):", text_color="#94a3b8").grid(row=1, column=0, padx=20, pady=(15, 0), sticky="w")
        ctk.CTkLabel(header_frame, text="Lavozim:", text_color="#94a3b8").grid(row=1, column=1, padx=20, pady=(15, 0), sticky="w")
        ctk.CTkLabel(header_frame, text="Bo'lim / Departament:", text_color="#94a3b8").grid(row=1, column=2, padx=20, pady=(15, 0), sticky="w")
        
        # Row 1 Inputs
        ctk.CTkEntry(header_frame, textvariable=self.search_var_name, width=200).grid(row=2, column=0, padx=20, pady=(5, 10), sticky="w")
        
        try:
            pos_list = ["Barchasi"] + (database.get_all_positions() or [])
        except:
            pos_list = ["Barchasi"]
        ctk.CTkComboBox(header_frame, variable=self.search_var_pos, values=pos_list, width=200).grid(row=2, column=1, padx=20, pady=(5, 10), sticky="w")
        
        try:
            depts = ["Barchasi"] + [d[1] for d in (database.get_internal_departments() or []) if len(d) > 1]
        except:
            depts = ["Barchasi"]
        ctk.CTkComboBox(header_frame, variable=self.search_var_dept, values=depts, width=200).grid(row=2, column=2, padx=20, pady=(5, 10), sticky="w")
        
        # Row 2 Labels
        ctk.CTkLabel(header_frame, text="Ish faoliyati turi (Masalan: Tadbir):", text_color="#94a3b8").grid(row=3, column=0, padx=20, pady=(5, 0), sticky="w")
        ctk.CTkLabel(header_frame, text="Tadbirlar ro'yxati:", text_color="#94a3b8").grid(row=3, column=1, padx=20, pady=(5, 0), sticky="w")
        ctk.CTkLabel(header_frame, text="Ish staji (Yillar) - Masalan: 5+:", text_color="#94a3b8").grid(row=3, column=2, padx=20, pady=(5, 0), sticky="w")
        
        # Row 2 Inputs
        ctk.CTkEntry(header_frame, textvariable=self.search_var_act, width=200).grid(row=4, column=0, padx=20, pady=(5, 15), sticky="w")
        
        try:
            meetings_db = database.get_all_meeting_titles() or []
            self.search_meetings_map = {m[1]: m[0] for m in meetings_db if len(m) > 1}
        except:
            self.search_meetings_map = {}
        evt_list = ["Barchasi"] + list(self.search_meetings_map.keys())
        ctk.CTkComboBox(header_frame, variable=self.search_var_event, values=evt_list, width=200).grid(row=4, column=1, padx=20, pady=(5, 15), sticky="w")
        
        ctk.CTkEntry(header_frame, textvariable=self.search_var_exp, width=200).grid(row=4, column=2, padx=20, pady=(5, 15), sticky="w")
        
        # Buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.grid(row=1, column=3, rowspan=4, padx=20, pady=10, sticky="e")
        
        ctk.CTkButton(btn_frame, text="🔍 Qidirish", fg_color="#3b82f6", hover_color="#2563eb", font=("Roboto", 14, "bold"), height=40, command=self.execute_search).pack(pady=10)
        
        def clear_search():
            self.search_var_name.set("")
            self.search_var_pos.set("Barchasi")
            self.search_var_dept.set("Barchasi")
            self.search_var_act.set("")
            self.search_var_event.set("Barchasi")
            self.search_var_exp.set("")
            self.execute_search()
            
        ctk.CTkButton(btn_frame, text="🗑 Tozalash", fg_color="#64748b", hover_color="#475569", font=("Roboto", 14, "bold"), height=40, command=clear_search).pack(pady=10)
        ctk.CTkButton(btn_frame, text="📥 Hujjatlarni Eksport Qilish", fg_color="#10b981", hover_color="#059669", font=("Roboto", 14, "bold"), height=40, command=self.export_search_documents).pack(pady=10)

        # --- Bottom Results Area ---
        self.search_results_container = ctk.CTkScrollableFrame(self.adv_search_frame, fg_color="transparent")
        self.search_results_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        

    def export_search_documents(self):
        if not hasattr(self, 'current_search_results') or not self.current_search_results:
            from tkinter import messagebox
            messagebox.showwarning("Ogohlantirish", "Eksport qilish uchun qidiruv natijasi yo'q!")
            return
            
        from tkinter import filedialog, messagebox
        import os
        folder = filedialog.askdirectory(title="Hujjatlarni saqlash uchun jildni tanlang")
        if not folder: return
        
        count = 0
        for p in self.current_search_results:
            doc, ext = database.get_person_document(p[0])
            if doc:
                ext = ext or ".docx"
                filename = f"{p[1]}_{p[2]}_Malumotnoma{ext}"
                filepath = os.path.join(folder, filename)
                i = 1
                while os.path.exists(filepath):
                    filepath = os.path.join(folder, f"{p[1]}_{p[2]}_Malumotnoma_{i}{ext}")
                    i += 1
                with open(filepath, "wb") as f:
                    f.write(doc)
                count += 1
                
        messagebox.showinfo("Muvaffaqiyat", f"{count} ta asl hujjat yuklab olindi!")

    def execute_search(self):
        people = database.get_people(self.current_user['access_level'], is_active=1)
        
        n_q = self.search_var_name.get().strip().lower()
        if n_q == "i am sure":
            if not getattr(self, '_iam_sure_notified', False):
                self._iam_sure_notified = True
                self.secret_unlocked = True
                from tkinter import messagebox
                messagebox.showinfo("Bajarildi", "Funksiya qo'shildi")
                if hasattr(self, 'btn_delete_all_orgs'):
                    self.btn_delete_all_orgs.pack(side="right", padx=(5, 0))
        else:
            self._iam_sure_notified = False
        pos_q = self.search_var_pos.get()
        dept_q = self.search_var_dept.get()
        act_q = self.search_var_act.get().strip().lower()
        evt_q = self.search_var_event.get()
        exp_q_str = self.search_var_exp.get().strip().replace("+", "")
        exp_target = None
        if exp_q_str.isdigit():
            exp_target = int(exp_q_str)
            
        evt_attendees = set()
        if evt_q != "Barchasi":
            mid = self.search_meetings_map.get(evt_q)
            if mid:
                att = database.get_meeting_attendees(mid, self.current_user['access_level'])
                evt_attendees = {a[1] for a in att} # a[1] is person_id
        
        from datetime import datetime
        results = []
        for p in people:
            fname = f"{p[1]} {p[2]} {p[3]}".lower()
            if n_q and not any(w.startswith(n_q) for w in fname.split()): continue
            
            if pos_q != "Barchasi" and p[9] != pos_q: continue
            
            if dept_q != "Barchasi" and dept_q != p[20]: continue
            
            # Using projects as 'Ish faoliyati turi' for text search
            act_text = (p[23] or "").lower()
            if act_q and not any(w.startswith(act_q) for w in act_text.split()): continue
            
            # Event filter
            if evt_q != "Barchasi" and p[0] not in evt_attendees: continue
            
            # Experience filter
            if exp_target is not None and p[13]:
                try:
                    joined = datetime.strptime(p[13], "%Y-%m-%d").date()
                    years = (datetime.now().date() - joined).days / 365.25
                    if years < exp_target:
                        continue
                except:
                    pass
            elif exp_target is not None and not p[13]:
                continue
                
            results.append(p)
            
        self.current_search_results = results
        for widget in self.search_results_container.winfo_children(): widget.destroy()
        
        if not results:
            ctk.CTkLabel(self.search_results_container, text="🔍 Hech qanday natija topilmadi.", font=("Roboto", 16), text_color="#94a3b8").pack(pady=50)
            return
            
        row_idx = 0
        col_idx = 0
        self.search_results_container.grid_columnconfigure((0,1,2,3), weight=1, uniform="card")
        
        for person in results:
            card = ctk.CTkFrame(self.search_results_container, fg_color="#1e293b", corner_radius=10, cursor="hand2")
            card.grid(row=row_idx, column=col_idx, padx=10, pady=10, sticky="nsew")
            
            fullname = f"{person[1]} {person[2]}"
            pos = person[9] or "Lavozim kiritilmagan"
            dept = person[20] or "Bo'lim yo'q"
            
            ctk.CTkLabel(card, text=fullname, font=("Roboto", 14, "bold"), text_color="white").pack(pady=(15, 5), padx=10)
            ctk.CTkLabel(card, text=pos, font=("Roboto", 12), text_color="#94a3b8").pack(pady=0, padx=10)
            ctk.CTkLabel(card, text=dept, font=("Roboto", 11), text_color="#64748b").pack(pady=(5, 15), padx=10)
            
            def bind_card(w, pid=person[0]):
                w.bind("<Button-1>", lambda e, p=pid: self.open_detail_window(person_id=p))
                for child in w.winfo_children(): bind_card(child, pid)
            bind_card(card)
            
            col_idx += 1
            if col_idx > 3:
                col_idx = 0
                row_idx += 1

    def show_dashboard(self):
        self.set_active_btn(self.btn_dash)
        self.list_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        self.settings_frame.grid_forget()
        self.orgs_frame.grid_forget()
        self.attendance_frame.grid_forget()
        if hasattr(self, 'meetings_frame'): self.meetings_frame.grid_forget()
        self.dash_frame.grid(row=1, column=0, sticky="nsew")
        self.load_dashboard_data()

    def show_list(self, is_active=1):
        if is_active != getattr(self, 'is_active_view', 1):
            self.current_dept_filter = None if is_active == 1 else "Bo'shaganlar"
        self.is_active_view = is_active
        if is_active == 1: self.set_active_btn(self.btn_list)
        else: self.set_active_btn(self.btn_inactive)
        self.dash_frame.grid_forget()
        self.settings_frame.grid_forget()
        self.orgs_frame.grid_forget()
        self.attendance_frame.grid_forget()
        if hasattr(self, 'meetings_frame'): self.meetings_frame.grid_forget()
        self.list_frame.grid(row=1, column=0, sticky="nsew")
        self.load_people()

    def show_orgs(self):
        self.set_active_btn(self.btn_orgs)
        self.dash_frame.grid_forget()
        self.list_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        self.settings_frame.grid_forget()
        self.attendance_frame.grid_forget()
        if hasattr(self, 'meetings_frame'): self.meetings_frame.grid_forget()
        self.orgs_frame.grid(row=1, column=0, sticky="nsew")
        self.load_organizations()

    def show_attendance(self):
        self.set_active_btn(self.btn_attendance)
        self.dash_frame.grid_forget()
        self.list_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        self.settings_frame.grid_forget()
        self.orgs_frame.grid_forget()
        if hasattr(self, 'meetings_frame'): self.meetings_frame.grid_forget()
        self.attendance_frame.grid(row=1, column=0, sticky="nsew")
        
        # Auto-update combobox values every time tab is opened
        from datetime import datetime
        now = datetime.now()
        months = []
        for i in range(-6, 3):
            m = now.month + i
            y = now.year
            while m < 1:
                m += 12
                y -= 1
            while m > 12:
                m -= 12
                y += 1
            months.append(f"{y}-{m:02d}")
            
        if hasattr(self, 'attendance_month_dropdown'):
            self.attendance_month_dropdown.configure(values=months)
            current = now.strftime("%Y-%m")
            if self.attendance_month_var.get() not in months or self.attendance_month_var.get() < current:
                self.attendance_month_var.set(current)
                
        self.load_attendance()

    def show_settings(self):
        if self.current_user['access_level'] < 3: return
        if not self.settings_frame.winfo_children():
            self.build_settings_content()
        self.set_active_btn(self.btn_settings)
        self.dash_frame.grid_forget()
        self.list_frame.grid_forget()
        if hasattr(self, 'adv_search_frame'): self.adv_search_frame.grid_forget()
        self.orgs_frame.grid_forget()
        self.attendance_frame.grid_forget()
        if hasattr(self, 'meetings_frame'): self.meetings_frame.grid_forget()
        self.settings_frame.grid(row=1, column=0, sticky="nsew")
        self.load_users()

    def do_search(self):
        q = self.global_search.get()
        self.name_filter.delete(0, 'end')
        self.name_filter.insert(0, q)
        self.show_list(1)

    def render_dept_tabs(self):
        if not hasattr(self, 'current_dept_filter'):
            self.current_dept_filter = None
            
        for widget in self.dept_tabs_container.winfo_children():
            widget.destroy()
            
        def set_filter(d_name):
            self.current_dept_filter = d_name
            self.load_people()

        if getattr(self, 'is_active_view', 1) == 0:
            special_categories = ["Bo'shaganlar", "Ta'tildagilar", "Jazodagilar"]
            if getattr(self, 'current_dept_filter', None) not in special_categories:
                self.current_dept_filter = "Bo'shaganlar"
                
            for c_name in special_categories:
                btn = ctk.CTkButton(self.dept_tabs_container, text=c_name, corner_radius=8, height=35,
                                    fg_color="#3b82f6" if self.current_dept_filter == c_name else "#1e293b",
                                    text_color="white" if self.current_dept_filter == c_name else "#94a3b8",
                                    command=lambda n=c_name: set_filter(n))
                btn.pack(side="left", padx=5)
            return
            
        depts = database.get_internal_departments()
            
        btn_all = ctk.CTkButton(self.dept_tabs_container, text="Barchasi", corner_radius=8, width=100, height=35,
                                fg_color="#3b82f6" if self.current_dept_filter is None else "#1e293b",
                                text_color="white" if self.current_dept_filter is None else "#94a3b8",
                                command=lambda: set_filter(None))
        btn_all.pack(side="left", padx=5)
        
        for d in depts:
            d_id, d_name = d
            btn = ctk.CTkButton(self.dept_tabs_container, text=d_name, corner_radius=8, height=35,
                                fg_color="#3b82f6" if self.current_dept_filter == d_name else "#1e293b",
                                text_color="white" if self.current_dept_filter == d_name else "#94a3b8",
                                command=lambda n=d_name: set_filter(n))
            btn.pack(side="left", padx=5)
            
            if self.current_user['access_level'] >= 5:
                def del_dept(did=d_id, dname=d_name):
                    from tkinter import messagebox
                    if messagebox.askyesno("Tasdiqlash", "Bu bo'limni o'chirasizmi?"):
                        database.delete_internal_department(did)
                        if self.current_dept_filter == dname: self.current_dept_filter = None
                        self.after(10, self.load_people)
                del_btn = ctk.CTkButton(self.dept_tabs_container, text="✕", width=20, height=35, fg_color="transparent", text_color="#ef4444", hover_color="#7f1d1d", command=del_dept)
                del_btn.pack(side="left", padx=(0, 5))
                
        def add_dept():
            add_modal = ctk.CTkToplevel(self)
            add_modal.title("🏢 Yangi Bo'lim Qo'shish")
            add_modal.geometry("400x260")
            add_modal.configure(fg_color="#0f172a")
            add_modal.resizable(False, False)
            add_modal.transient(self)
            add_modal.grab_set()

            ctk.CTkLabel(add_modal, text="🏢 Yangi Bo'lim Qo'shish", font=("Roboto", 16, "bold"), text_color="white").pack(pady=(20, 10))
            ctk.CTkLabel(add_modal, text="Bo'lim yoki Departament nomini kiriting:", font=("Roboto", 12), text_color="#94a3b8").pack(pady=(10, 5))

            name_var = ctk.StringVar()
            entry = ctk.CTkEntry(add_modal, textvariable=name_var, width=320, height=38, placeholder_text="Masalan: Axborot texnologiyalari bo'limi")
            entry.pack(pady=10)

            btn_frame = ctk.CTkFrame(add_modal, fg_color="transparent")
            btn_frame.pack(pady=(10, 20))

            def save_dept():
                new_dept = name_var.get().strip()
                if new_dept:
                    from tkinter import messagebox
                    if database.add_internal_department(new_dept):
                        add_modal.destroy()
                        self.after(10, self.load_people)
                    else:
                        messagebox.showerror("Xato", "Bu bo'lim allaqachon mavjud!", parent=add_modal)

            ctk.CTkButton(btn_frame, text="Saqlash", width=120, height=35, fg_color="#10b981", hover_color="#059669", command=save_dept).pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="Bekor qilish", width=120, height=35, fg_color="#64748b", hover_color="#475569", command=add_modal.destroy).pack(side="left", padx=10)

        if self.current_user['access_level'] >= 5:
            ctk.CTkButton(self.dept_tabs_container, text="➕ Bo'lim Qo'shish", corner_radius=8, fg_color="#10b981", hover_color="#059669", height=35, command=add_dept).pack(side="left", padx=15)

    def load_people(self, reset_page=True):
        if reset_page:
            self.current_page = 1
            
        self.render_dept_tabs()
        for widget in getattr(self, 'roster_scroll', ctk.CTkFrame(self)).winfo_children(): widget.destroy()
        if not hasattr(self, 'current_dept_filter'): self.current_dept_filter = None
        
        if getattr(self, 'is_active_view', 1) == 0:
            rows = database.get_special_people(self.current_user['access_level'], self.current_dept_filter)
        else:
            rows = database.get_people(self.current_user['access_level'], self.is_active_view, self.current_dept_filter)
        
        a_min = self.age_min.get()
        a_max = self.age_max.get()
        n_filt = self.name_filter.get().lower()

        filtered_rows = []
        for row in rows:
            fullname = f"{row[1]} {row[2]}".strip()
            birth = row[6]
            joined = row[11]
            
            age = "-"
            age_int = 0
            if birth:
                try:
                    b_date = datetime.strptime(birth, "%Y-%m-%d")
                    age_int = (datetime.now() - b_date).days // 365
                    age = str(age_int)
                except: pass

            if a_min.isdigit() and age_int < int(a_min): continue
            if a_max.isdigit() and age_int > int(a_max): continue
            if n_filt and n_filt not in fullname.lower(): continue

            is_new = False
            if joined:
                try:
                    j_date = datetime.strptime(joined, "%Y-%m-%d")
                    if (datetime.now() - j_date).days <= 30:
                        is_new = True
                except: pass

            if row[18] == 0:
                status_text = "Bo'shagan"
                status_color = "#ef4444"
            elif row[14] is not None and str(row[14]).strip() != "":
                status_text = "Ta'tilda"
                status_color = "#f59e0b"
            elif row[17] is not None and str(row[17]).strip() != "":
                status_text = "Jazoda"
                status_color = "#f97316"
            else:
                status_text = "Faol"
                status_color = "#10b981"

            filtered_rows.append((row, age, is_new, status_text, status_color, fullname))
            
        page_size = 50
        if not hasattr(self, 'current_page'): self.current_page = 1
        self.max_page = max(1, (len(filtered_rows) + page_size - 1) // page_size)
        if self.current_page > self.max_page: self.current_page = self.max_page
        
        if hasattr(self, 'lbl_page_info'):
            self.lbl_page_info.configure(text=f"Sahifa: {self.current_page} / {self.max_page}")
            self.btn_prev_page.configure(state="normal" if self.current_page > 1 else "disabled")
            self.btn_next_page.configure(state="normal" if self.current_page < self.max_page else "disabled")

        start_idx = (self.current_page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_rows = filtered_rows[start_idx:end_idx]

        for item in paginated_rows:
            row, age, is_new, status_text, status_color, fullname = item
            if not hasattr(self, 'roster_scroll'): continue
            
            row_frame = ctk.CTkFrame(self.roster_scroll, fg_color="#0f172a", corner_radius=8, cursor="hand2")
            row_frame.pack(fill="x", pady=4, padx=2)
            row_frame.grid_columnconfigure((1,3), weight=1)
            row_frame.bind("<Button-1>", lambda e, pid=row[0]: self.open_detail_window(person_id=pid))
            
            def bind_children(widget, pid=row[0]):
                widget.bind("<Button-1>", lambda e, p=pid: self.open_detail_window(person_id=p))
                for child in widget.winfo_children(): bind_children(child, pid)

            ctk.CTkLabel(row_frame, text=str(row[0]), text_color="#cbd5e1", width=50).grid(row=0, column=0, padx=10, pady=10, sticky="w")
            
            name_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            name_frame.grid(row=0, column=1, padx=10, pady=10, sticky="w")
            ctk.CTkLabel(name_frame, text=fullname, text_color="white", font=("Roboto", 13, "bold")).pack(side="left")
            if is_new:
                ctk.CTkLabel(name_frame, text="YANGI", fg_color="#3b82f6", text_color="white", corner_radius=6, font=("Roboto", 10, "bold"), width=50, height=20).pack(side="left", padx=10)

            ctk.CTkLabel(row_frame, text=age, text_color="#cbd5e1", width=60).grid(row=0, column=2, padx=10, pady=10, sticky="w")
            pos_text = row[9][:30] + ("..." if len(row[9])>30 else "") if row[9] else ""
            ctk.CTkLabel(row_frame, text=pos_text, text_color="#cbd5e1").grid(row=0, column=3, padx=10, pady=10, sticky="w")
            
            status_badge = ctk.CTkLabel(row_frame, text=status_text, fg_color=status_color, text_color="white", corner_radius=6, font=("Roboto", 11, "bold"), width=80, height=24)
            status_badge.grid(row=0, column=4, padx=10, pady=10, sticky="w")
            
            bind_children(row_frame)

    # --- MODALS AND DETAILS ---
    def open_detail_window(self, event=None, person_id=None):
        if person_id is not None:
            self.current_person_id = person_id
        else:
            sel = getattr(self, 'tree', None)
            if sel and sel.selection():
                self.current_person_id = sel.item(sel.selection())['values'][0]
            else:
                return
        self.render_detail_window()

    def render_detail_window(self):
        if not hasattr(self, 'detail_win') or not self.detail_win.winfo_exists():
            self.detail_win = ctk.CTkToplevel(self)
            self.detail_win.title("Xodim Ma'lumotnomasi")
            self.detail_win.geometry("900x800")
            self.detail_win.configure(fg_color="#0f172a")
            self.detail_win.transient(self)
            
        self.detail_win.lift()
        self.detail_win.focus_force()
        
        for widget in self.detail_win.winfo_children():
            widget.destroy()
        
        person_dict = database.get_person_objective(self.current_person_id)
        if not person_dict: return
        
        header_frame = ctk.CTkFrame(self.detail_win, fg_color="transparent")
        header_frame.pack(fill="x", pady=20, padx=30)
        
        ctk.CTkLabel(header_frame, text="📄 Ma'lumotnoma (Ob'ektivka)", font=("Roboto", 24, "bold"), text_color="white").pack(side="left")
        
        def download_original():
            from tkinter import filedialog, messagebox
            import os
            doc, ext = database.get_person_document(person_dict['id'])
            if isinstance(doc, str):
                doc = file_transfer.load_file_bytes(doc)
            if not doc:
                messagebox.showwarning("Ogohlantirish", "Asl hujjat yuklanmagan!")
                return
            ext = ext or ".docx"
            filename = f"{person_dict['first_name']}_{person_dict['last_name']}_Malumotnoma{ext}"
            path = filedialog.asksaveasfilename(defaultextension=ext, initialfile=filename, title="Hujjatni saqlash")
            if path:
                with open(path, "wb") as f:
                    f.write(doc)
                messagebox.showinfo("Muvaffaqiyat", "Asl hujjat yuklab olindi!")
        
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")
        
        ctk.CTkButton(btn_frame, text="📥 Asl Hujjatni Yuklash", fg_color="#10b981", hover_color="#059669", font=("Roboto", 14, "bold"), height=40, command=download_original).pack(side="left", padx=5)
        
        if self.current_user['access_level'] >= 4:
            # Reconstruct the tuple-like structure expected by open_modal just for the ID, or just pass tuple
            p_tuple = (self.current_person_id,)
            ctk.CTkButton(btn_frame, text="✏️ Tahrirlash", fg_color="#3b82f6", hover_color="#2563eb", font=("Roboto", 14, "bold"), height=40, command=lambda: self.open_modal(p_tuple)).pack(side="left", padx=5)
            
            p_full_name = f"{person_dict.get('first_name','')} {person_dict.get('last_name','')}"
            ctk.CTkButton(btn_frame, text="⚡ Holatni O'zgartirish", fg_color="#f59e0b", hover_color="#d97706", font=("Roboto", 14, "bold"), height=40, command=lambda: self.open_status_change_modal(self.current_person_id, p_full_name)).pack(side="left", padx=5)
            
            def del_p():
                self.confirm_delete_person(self.current_person_id)
            ctk.CTkButton(btn_frame, text="🗑️ O'chirish", fg_color="#ef4444", hover_color="#dc2626", font=("Roboto", 14, "bold"), height=40, command=del_p).pack(side="left", padx=5)
        
        scroll = ctk.CTkScrollableFrame(self.detail_win, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=30, pady=10)
        
        top_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        top_frame.pack(fill="x", pady=10)
        
        photo_frame = ctk.CTkFrame(top_frame, width=150, height=200, corner_radius=10, fg_color="#1e293b")
        photo_frame.pack(side="left", padx=(0, 20))
        photo_frame.pack_propagate(False)
        
        if person_dict.get('photo_person'):
            from PIL import Image
            import io
            try:
                photo_bytes = person_dict['photo_person']
                if isinstance(photo_bytes, str):
                    import base64
                    try: photo_bytes = base64.b64decode(photo_bytes)
                    except: photo_bytes = None
                img = Image.open(io.BytesIO(photo_bytes)) if (photo_bytes and isinstance(photo_bytes, bytes)) else None
                if img:
                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(150, 200))
                    ctk.CTkLabel(photo_frame, image=ctk_img, text="").pack(expand=True)
                else:
                    ctk.CTkLabel(photo_frame, text="Rasm yo'q", text_color="#64748b").pack(expand=True)
            except Exception as e:
                print(f"Photo render error: {e}")
                ctk.CTkLabel(photo_frame, text="Rasm yo'q", text_color="#64748b").pack(expand=True)
        else:
            ctk.CTkLabel(photo_frame, text="Rasm yo'q", text_color="#64748b").pack(expand=True)
            
        info_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        fullname = f"{person_dict['last_name']} {person_dict['first_name']} {person_dict.get('patronymic', '')}"
        ctk.CTkLabel(info_frame, text=fullname.upper(), font=("Roboto", 24, "bold"), text_color="white").pack(anchor="w", pady=(0,5))
        ctk.CTkLabel(info_frame, text=person_dict.get('position', 'Noma\'lum lavozim'), font=("Roboto", 16), text_color="#94a3b8").pack(anchor="w", pady=(0,15))
        
        grid = ctk.CTkFrame(info_frame, fg_color="transparent")
        grid.pack(fill="x")
        
        def add_field(r, c, label, value):
            f = ctk.CTkFrame(grid, fg_color="transparent")
            f.grid(row=r, column=c, padx=(0,40), pady=5, sticky="w")
            ctk.CTkLabel(f, text=label, font=("Roboto", 12), text_color="#94a3b8").pack(anchor="w")
            ctk.CTkLabel(f, text=str(value) if value else "-", font=("Roboto", 14, "bold"), text_color="white", wraplength=300).pack(anchor="w")
            
        add_field(0, 0, "Tug'ilgan yili:", person_dict.get('birth_date'))
        add_field(0, 1, "Tug'ilgan joyi:", person_dict.get('birth_place'))
        add_field(0, 2, "Millati:", person_dict.get('nationality'))
        add_field(1, 0, "Partiyaviyligi:", person_dict.get('party_membership'))
        add_field(1, 1, "Ma'lumoti:", person_dict.get('education'))
        add_field(1, 2, "Tamomlagan:", person_dict.get('graduated_from'))
        add_field(2, 0, "Mutaxassisligi:", person_dict.get('education_specialty'))
        add_field(2, 1, "Ilmiy darajasi:", person_dict.get('academic_degree'))
        add_field(2, 2, "Ilmiy unvoni:", person_dict.get('academic_title'))
        add_field(3, 0, "Chet tillari:", person_dict.get('languages'))
        add_field(3, 1, "Davlat mukofotlari:", person_dict.get('state_awards'))
        add_field(3, 2, "Deputatlik:", person_dict.get('deputy_status'))
        
        ctk.CTkLabel(scroll, text="MEHNAT FAOLIYATI", font=("Roboto", 18, "bold"), text_color="#3b82f6").pack(anchor="w", pady=(20,10))
        emp_hist = person_dict.get('employment_history', '')
        if not emp_hist: emp_hist = "Ma'lumot kiritilmagan"
        ctk.CTkLabel(scroll, text=emp_hist, font=("Roboto", 14), text_color="white", justify="left", wraplength=800).pack(anchor="w", padx=10)
        
        ctk.CTkLabel(scroll, text="YAQIN QARINDOSHLARI HAQIDA MA'LUMOT", font=("Roboto", 18, "bold"), text_color="#3b82f6").pack(anchor="w", pady=(30,10))
        relatives = database.get_relatives(person_dict['id'])
        
        if relatives:
            table_frame = ctk.CTkFrame(scroll, fg_color="#1e293b", corner_radius=10)
            table_frame.pack(fill="x", pady=10)
            
            headers = ["Qarindoshligi", "F.I.SH.", "Tug'ilgan yili va joyi", "Ish joyi va lavozimi", "Turar joyi"]
            for i, h in enumerate(headers):
                ctk.CTkLabel(table_frame, text=h, font=("Roboto", 12, "bold"), text_color="#94a3b8").grid(row=0, column=i, padx=10, pady=10, sticky="w")
                
            for r_idx, rel in enumerate(relatives):
                ctk.CTkLabel(table_frame, text=rel['relationship'], font=("Roboto", 12), text_color="white", wraplength=100).grid(row=r_idx+1, column=0, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(table_frame, text=rel['full_name'], font=("Roboto", 12), text_color="white", wraplength=200).grid(row=r_idx+1, column=1, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(table_frame, text=rel['birth_info'], font=("Roboto", 12), text_color="white", wraplength=150).grid(row=r_idx+1, column=2, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(table_frame, text=rel['work_info'], font=("Roboto", 12), text_color="white", wraplength=200).grid(row=r_idx+1, column=3, padx=10, pady=5, sticky="w")
                ctk.CTkLabel(table_frame, text=rel['residence'], font=("Roboto", 12), text_color="white", wraplength=150).grid(row=r_idx+1, column=4, padx=10, pady=5, sticky="w")
        else:
            ctk.CTkLabel(scroll, text="Qarindoshlari haqida ma'lumot yo'q", font=("Roboto", 14), text_color="#64748b").pack(anchor="w", padx=10)
            
        ctk.CTkLabel(scroll, text="QO'SHIMCHA (ICHKI) MA'LUMOTLAR", font=("Roboto", 18, "bold"), text_color="#3b82f6").pack(anchor="w", pady=(30,10))
        int_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        int_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        ctk.CTkLabel(int_frame, text=f"JSHSHIR: {person_dict.get('pinfl', '-')}", font=("Roboto", 14), text_color="#cbd5e1").pack(side="left", padx=10)
        ctk.CTkLabel(int_frame, text=f"Passport: {person_dict.get('passport', '-')}", font=("Roboto", 14), text_color="#cbd5e1").pack(side="left", padx=10)
        ctk.CTkLabel(int_frame, text=f"Telefon: {person_dict.get('phone', '-')}", font=("Roboto", 14), text_color="#cbd5e1").pack(side="left", padx=10)
        
        # --- Passport Photo Display ---
        if person_dict.get('photo_passport'):
            pass_title_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            pass_title_frame.pack(fill="x", pady=(30,10))
            
            ctk.CTkLabel(pass_title_frame, text="PASSPORT NUSXASI", font=("Roboto", 18, "bold"), text_color="#3b82f6").pack(side="left")
            
            def download_passport():
                from tkinter import filedialog, messagebox
                import os
                pass_data = person_dict['photo_passport']
                if isinstance(pass_data, str):
                    pass_data = file_transfer.load_file_bytes(pass_data)
                if not pass_data:
                    messagebox.showerror("Xato", "Fayl topilmadi!")
                    return
                path = filedialog.asksaveasfilename(defaultextension="", initialfile=f"{person_dict['first_name']}_Passport", title="Passportni saqlash", filetypes=[("All Files", "*.*")])
                if path:
                    with open(path, "wb") as f:
                        f.write(pass_data)
                    messagebox.showinfo("Muvaffaqiyat", "Passport yuklab olindi!")
                    
            ctk.CTkButton(pass_title_frame, text="YUKLAB OLISH", fg_color="#64748b", hover_color="#475569", height=30, command=download_passport).pack(side="right", padx=10)
            
            pass_frame = ctk.CTkFrame(scroll, fg_color="#1e293b", corner_radius=10)
            pass_frame.pack(fill="x", pady=10, padx=10)
            
            from PIL import Image
            import io
            try:
                pass_img = Image.open(io.BytesIO(person_dict['photo_passport']))
                # Resize proportionally to fit width of ~600px while maintaining aspect ratio
                width = 600
                ratio = width / float(pass_img.size[0])
                height = int(float(pass_img.size[1]) * float(ratio))
                ctk_pass = ctk.CTkImage(light_image=pass_img, dark_image=pass_img, size=(width, height))
                lbl = ctk.CTkLabel(pass_frame, image=ctk_pass, text="")
                lbl.pack(pady=20)
                # Keep reference to avoid garbage collection
                lbl.image = ctk_pass
            except Exception as e:
                # Fallback if it's a PDF or invalid image
                ctk.CTkLabel(pass_frame, text="Passport formati rasm emas (PDF bo'lishi mumkin).\nYuqoridagi tugma orqali yuklab oling.", text_color="#94a3b8", font=("Roboto", 14)).pack(pady=40)

    def open_status_change_modal(self, person_id, name):
        from datetime import datetime
        m = ctk.CTkToplevel(self)
        m.title("Holatni O'zgartirish (Faol / Ta'til / Jazo / Bo'shatish)")
        m.geometry("520x590")
        m.configure(fg_color="#1e293b")
        m.resizable(False, False)
        if hasattr(self, 'detail_win') and self.detail_win.winfo_exists():
            m.transient(self.detail_win)
        m.grab_set()

        ctk.CTkLabel(m, text=f"Holatni O'zgartirish: {name}", font=("Roboto", 18, "bold"), text_color="white").pack(pady=(20, 10))
        
        ctk.CTkLabel(m, text="Amal turini tanlang:", font=("Roboto", 13, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=40, pady=(5, 5))
        
        action_var = ctk.StringVar(value="faol")
        
        frame_type = ctk.CTkFrame(m, fg_color="#0f172a", corner_radius=10)
        frame_type.pack(fill="x", padx=40, pady=(0, 15))

        rb0 = ctk.CTkRadioButton(frame_type, text="❇️ Faol (Aktiv) holatga tiklash / Holatni tozalash", variable=action_var, value="faol", font=("Roboto", 13), text_color="#34d399")
        rb0.pack(anchor="w", padx=20, pady=8)
        
        rb1 = ctk.CTkRadioButton(frame_type, text="🌴 Ta'til berish", variable=action_var, value="tatil", font=("Roboto", 13))
        rb1.pack(anchor="w", padx=20, pady=8)
        
        rb2 = ctk.CTkRadioButton(frame_type, text="⚠️ Intizomiy jazo qo'llash", variable=action_var, value="jazo", font=("Roboto", 13))
        rb2.pack(anchor="w", padx=20, pady=8)
        
        rb3 = ctk.CTkRadioButton(frame_type, text="🚫 Ishdan bo'shatish", variable=action_var, value="boshatish", font=("Roboto", 13), text_color="#f87171")
        rb3.pack(anchor="w", padx=20, pady=8)
        
        # Start date
        lbl_start = ctk.CTkLabel(m, text="Boshlanish sanasi (YYYY-MM-DD):", text_color="#cbd5e1")
        lbl_start.pack(anchor="w", padx=40)
        s_ent = ctk.CTkEntry(m, width=440, height=35)
        s_ent.pack(pady=(0, 10))
        s_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # End date
        lbl_end = ctk.CTkLabel(m, text="Tugash sanasi (YYYY-MM-DD) - ixtiyoriy:", text_color="#cbd5e1")
        lbl_end.pack(anchor="w", padx=40)
        e_ent = ctk.CTkEntry(m, width=440, height=35)
        e_ent.pack(pady=(0, 10))
        
        # Reason / Description
        lbl_reason = ctk.CTkLabel(m, text="Sabab / Izoh:", text_color="#cbd5e1")
        lbl_reason.pack(anchor="w", padx=40)
        r_ent = ctk.CTkEntry(m, width=440, height=35, placeholder_text="Sababini kiriting...")
        r_ent.pack(pady=(0, 15))
        
        def toggle_fields(*args):
            act = action_var.get()
            if act in ["boshatish", "faol"]:
                lbl_start.configure(state="normal" if act == "boshatish" else "disabled")
                s_ent.configure(state="normal" if act == "boshatish" else "disabled")
                lbl_end.configure(state="disabled")
                e_ent.configure(state="disabled")
            else:
                lbl_start.configure(state="normal")
                s_ent.configure(state="normal")
                lbl_end.configure(state="normal")
                e_ent.configure(state="normal")
                
        action_var.trace_add("write", toggle_fields)
        toggle_fields()

        def save_status_change():
            act = action_var.get()
            s_val = s_ent.get().strip() or datetime.now().strftime("%Y-%m-%d")
            e_val = e_ent.get().strip() or None
            reason = r_ent.get().strip() or "Sabab ko'rsatilmadi"
            
            if act == "faol":
                database.activate_person(person_id)
                database.add_activity(f"Faol holatga qaytarildi (Ishga tiklandi): {name} - {reason}", "update")
            elif act == "tatil":
                database.set_vacation(person_id, s_val, e_val)
                database.add_activity(f"Ta'til berildi: {name} ({s_val} dan {e_val or 'noma\'lum'} gacha) - {reason}", "update")
            elif act == "jazo":
                database.set_punishment(person_id, s_val, e_val, reason)
                database.add_activity(f"Intizomiy jazo qo'llandi: {name} - {reason}", "delete")
            elif act == "boshatish":
                database.set_left_job(person_id, s_val)
                database.add_activity(f"Ishdan bo'shatildi: {name} - {reason}", "delete")
                
            m.destroy()
            if hasattr(self, 'detail_win') and self.detail_win.winfo_exists():
                self.render_detail_window()
            self.load_people()
            self.load_dashboard_data()

        ctk.CTkButton(m, text="Saqlash va Tasdiqlash", command=save_status_change, fg_color="#10b981", hover_color="#059669", font=("Roboto", 14, "bold"), width=240, height=40).pack(pady=10)

    def confirm_delete_person(self, p_id):
        from tkinter import messagebox
        if messagebox.askyesno("Tasdiqlash", "Haqiqatan ham bu xodimni o'chirmoqchimisiz?"):
            database.delete_person(p_id)
            if hasattr(self, 'detail_win') and self.detail_win.winfo_exists():
                self.detail_win.destroy()
            self.load_people()
            self.load_dashboard_data()


    def open_vacation_modal(self, p_id, name):
        m = ctk.CTkToplevel(self)
        m.title("Ta'til berish")
        m.geometry("400x350")
        m.configure(fg_color="#1e293b")
        m.transient(self.detail_win)
        m.grab_set()

        ctk.CTkLabel(m, text=f"Ta'til: {name}", font=("Roboto", 18, "bold")).pack(pady=20)
        ctk.CTkLabel(m, text="Boshlanish (YYYY-MM-DD):").pack(anchor="w", padx=40)
        s_ent = ctk.CTkEntry(m, width=320, height=35)
        s_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
        s_ent.pack(pady=(0,15))

        ctk.CTkLabel(m, text="Tugash (YYYY-MM-DD):").pack(anchor="w", padx=40)
        e_ent = ctk.CTkEntry(m, width=320, height=35)
        e_ent.pack(pady=(0,20))

        def save_vac():
            database.set_vacation(p_id, s_ent.get(), e_ent.get())
            database.add_activity(f"Ta'til berildi: {name} ({s_ent.get()} dan {e_ent.get()} gacha)", "update")
            m.destroy()
            self.render_detail_window()
            self.load_people()
            
        ctk.CTkButton(m, text="Saqlash", command=save_vac, fg_color="#10b981", height=40).pack()

    def open_punish_modal(self, p_id, name):
        m = ctk.CTkToplevel(self)
        m.title("Jazo qo'llash")
        m.geometry("400x420")
        m.configure(fg_color="#1e293b")
        m.transient(self.detail_win)
        m.grab_set()

        ctk.CTkLabel(m, text=f"Jazo: {name}", font=("Roboto", 18, "bold")).pack(pady=20)
        
        ctk.CTkLabel(m, text="Boshlanish (YYYY-MM-DD):").pack(anchor="w", padx=40)
        s_ent = ctk.CTkEntry(m, width=320, height=35)
        s_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
        s_ent.pack(pady=(0,10))

        ctk.CTkLabel(m, text="Tugash (bo'sh bo'lsa muddatsiz):").pack(anchor="w", padx=40)
        e_ent = ctk.CTkEntry(m, width=320, height=35)
        e_ent.pack(pady=(0,10))
        
        ctk.CTkLabel(m, text="Sababi:").pack(anchor="w", padx=40)
        r_ent = ctk.CTkEntry(m, width=320, height=35)
        r_ent.pack(pady=(0,20))

        def save_pun():
            database.set_punishment(p_id, s_ent.get(), e_ent.get() or None, r_ent.get())
            database.add_activity(f"Intizomiy jazo: {name} - {r_ent.get()}", "delete")
            m.destroy()
            self.render_detail_window()
            self.load_people()
            
        ctk.CTkButton(m, text="Saqlash", command=save_pun, fg_color="#ef4444", height=40).pack()

    def open_fire_modal(self, p_id, name):
        m = ctk.CTkToplevel(self)
        m.title("Ishdan bo'shatish")
        m.geometry("400x250")
        m.configure(fg_color="#1e293b")
        m.transient(self.detail_win)
        m.grab_set()

        ctk.CTkLabel(m, text=f"Bo'shatish: {name}", font=("Roboto", 18, "bold"), text_color="#ef4444").pack(pady=20)
        ctk.CTkLabel(m, text="Bo'shagan sana (YYYY-MM-DD):").pack(anchor="w", padx=40)
        d_ent = ctk.CTkEntry(m, width=320, height=35)
        d_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
        d_ent.pack(pady=(0,20))

        def do_fire():
            database.set_left_job(p_id, d_ent.get())
            database.add_activity(f"Ishdan bo'shatildi: {name}", "delete")
            m.destroy()
            self.render_detail_window()
            self.load_people()
            self.load_dashboard_data()
            
        ctk.CTkButton(m, text="Tasdiqlash", command=do_fire, fg_color="#ef4444", height=40).pack()

    def open_add_modal(self, pre_selected_org=None):
        self.open_modal(None, pre_selected_org)

    def open_edit_modal(self, person):
        self.open_modal(person)

    def open_modal(self, person_tuple_or_id, pre_selected_org=None):
        modal = ctk.CTkToplevel(self)
        title = "Tahrirlash" if person_tuple_or_id else "Yangi Xodim Qo'shish"
        modal.title(title)
        modal.geometry("1100x850")
        modal.configure(fg_color="#0f172a")
        modal.transient(self)
        modal.grab_set()

        person_data = None
        relatives_data = []
        person_id = None
        if person_tuple_or_id:
            person_id = person_tuple_or_id[0]
            person_data = database.get_person_objective(person_id)
            relatives_data = database.get_relatives(person_id)

        ctk.CTkLabel(modal, text=title, font=("Roboto", 24, "bold"), text_color="white").pack(pady=20)
        
        scroll = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        self.new_photo_person = None
        self.new_photo_passport = None
        self.new_original_document = None
        self.new_original_document_ext = None

        def autofill_from_doc():
            from tkinter import filedialog, messagebox
            path = filedialog.askopenfilename(filetypes=[("Word Document", "*.docx")])
            if path:
                from doc_parser import parse_person_document
                data = parse_person_document(path)
                if data:
                    if data.get('first_name'): self.var_fn.set(data['first_name'])
                    if data.get('last_name'): self.var_ln.set(data['last_name'])
                    if data.get('patronymic'): self.var_pt.set(data['patronymic'])
                    if data.get('passport'): self.var_pass.set(data['passport'])
                    if data.get('pinfl'): self.var_pnfl.set(data['pinfl'])
                    if data.get('birth_date'): self.var_bdate.set(data['birth_date'])
                    if data.get('position'): self.var_pos.set(data['position'])
                    if data.get('languages'): self.var_langs.set(data['languages'])
                    
                    if data.get('birth_place'): self.var_bplace.set(data['birth_place'])
                    if data.get('nationality'): self.var_nat.set(data['nationality'])
                    if data.get('party_membership'): self.var_party.set(data['party_membership'])
                    if data.get('education'): self.var_edu.set(data['education'])
                    if data.get('graduated_from'): self.var_grad.set(data['graduated_from'])
                    if data.get('education_specialty'): self.var_spec.set(data['education_specialty'])
                    if data.get('academic_degree'): self.var_degree.set(data['academic_degree'])
                    if data.get('academic_title'): self.var_title.set(data['academic_title'])
                    if data.get('state_awards'): self.var_awards.set(data['state_awards'])
                    if data.get('deputy_status'): self.var_deputy.set(data['deputy_status'])
                    
                    if data.get('employment'):
                        self.txt_emp.delete("1.0", "end")
                        self.txt_emp.insert("1.0", data['employment'])
                        
                    if data.get('relatives'):
                        for rf in self.relatives_frames:
                            if rf.winfo_exists():
                                rf.destroy()
                        self.relatives_frames.clear()
                        for rel in data['relatives']:
                            add_relative_row(rel)
                            
                    if data.get('photo_person'):
                        self.new_photo_person = data['photo_person']
                        self.btn_photo.configure(text="Rasm yuklandi ✅", text_color="#10b981", fg_color="transparent", border_width=1, border_color="#10b981")
                
                with open(path, "rb") as f:
                    self.new_original_document = f.read()
                self.new_original_document_ext = ".docx"
                
                messagebox.showinfo("Muvaffaqiyat", "Hujjat yuklandi va ma'lumotlar to'ldirildi!")

        if not person_data:
            ctk.CTkButton(scroll, text="📄 Hujjat Yuklash (Avtomatik to'ldirish)", command=autofill_from_doc, fg_color="#3b82f6", hover_color="#2563eb", font=("Roboto", 14, "bold"), height=40).pack(pady=(0,10))

        grid = ctk.CTkFrame(scroll, fg_color="#1e293b", corner_radius=15)
        grid.pack(fill="both", expand=True, padx=10, pady=10)
        grid.grid_columnconfigure((0,1,2,3), weight=1)

        def make_entry(r, c, label, var, width=None, colspan=1):
            lbl = ctk.CTkLabel(grid, text=label, font=("Roboto", 13, "bold"), text_color="#cbd5e1")
            lbl.grid(row=r, column=c, padx=15, pady=(15,5), sticky="w")
            e = ctk.CTkEntry(grid, textvariable=var, height=35, corner_radius=8, font=("Roboto", 13))
            if width: e.configure(width=width)
            e.grid(row=r+1, column=c, columnspan=colspan, padx=15, pady=(0,10), sticky="ew")
            return e

        # Variables
        self.var_fn = ctk.StringVar(value=person_data.get('first_name', '') if person_data else "")
        self.var_ln = ctk.StringVar(value=person_data.get('last_name', '') if person_data else "")
        self.var_pt = ctk.StringVar(value=person_data.get('patronymic', '') if person_data else "")
        self.var_pos = ctk.StringVar(value=person_data.get('position', '') if person_data else "")
        self.var_dept = ctk.StringVar(value=person_data.get('department', '') if person_data else (pre_selected_org or ""))
        
        self.var_bdate = ctk.StringVar(value=person_data.get('birth_date', '') if person_data else "")
        self.var_bplace = ctk.StringVar(value=person_data.get('birth_place', '') if person_data else "")
        self.var_nat = ctk.StringVar(value=person_data.get('nationality', '') if person_data else "")
        self.var_party = ctk.StringVar(value=person_data.get('party_membership', '') if person_data else "")
        
        self.var_edu = ctk.StringVar(value=person_data.get('education', '') if person_data else "")
        self.var_grad = ctk.StringVar(value=person_data.get('graduated_from', '') if person_data else "")
        self.var_spec = ctk.StringVar(value=person_data.get('education_specialty', '') if person_data else "")
        
        self.var_degree = ctk.StringVar(value=person_data.get('academic_degree', '') if person_data else "Yo'q")
        self.var_title = ctk.StringVar(value=person_data.get('academic_title', '') if person_data else "Yo'q")
        self.var_langs = ctk.StringVar(value=person_data.get('languages', '') if person_data else "")
        
        self.var_awards = ctk.StringVar(value=person_data.get('state_awards', '') if person_data else "Yo'q")
        self.var_deputy = ctk.StringVar(value=person_data.get('deputy_status', '') if person_data else "Yo'q")
        
        self.var_pass = ctk.StringVar(value=person_data.get('passport', '') if person_data else "")
        self.var_pnfl = ctk.StringVar(value=person_data.get('pinfl', '') if person_data else "")
        self.var_phone = ctk.StringVar(value=person_data.get('phone', '') if person_data else "")
        self.var_secret = ctk.StringVar(value=str(person_data.get('secret_level', '1')) if person_data else "1")
        self.var_join = ctk.StringVar(value=person_data.get('joined_date', '') if person_data else "")

        file_frame = ctk.CTkFrame(grid, fg_color="transparent")
        file_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=15, pady=10)
        self.btn_photo = ctk.CTkButton(file_frame, text="🖼️ Profil rasmini yuklash", height=40, command=self.upload_photo)
        self.btn_photo.pack(side="left", padx=10)
        self.btn_pass_copy = ctk.CTkButton(file_frame, text="📄 Passport nusxasini yuklash", height=40, command=self.upload_passport)
        self.btn_pass_copy.pack(side="left", padx=10)

        ctk.CTkLabel(grid, text="1. SHAXSIY MA'LUMOTLAR", text_color="#3b82f6", font=("Roboto", 16, "bold")).grid(row=1, column=0, columnspan=4, sticky="w", padx=15, pady=(15,0))
        make_entry(2, 0, "Familiya", self.var_ln)
        make_entry(2, 1, "Ism", self.var_fn)
        make_entry(2, 2, "Sharifi", self.var_pt)
        make_entry(2, 3, "Telefon", self.var_phone)
        
        make_entry(4, 0, "Tug'ilgan sana (Y-M-D)", self.var_bdate)
        make_entry(4, 1, "Tug'ilgan joyi", self.var_bplace)
        make_entry(4, 2, "Millati", self.var_nat)
        make_entry(4, 3, "Partiyaviyligi", self.var_party)

        ctk.CTkLabel(grid, text="2. TA'LIM VA MALAKA", text_color="#3b82f6", font=("Roboto", 16, "bold")).grid(row=6, column=0, columnspan=4, sticky="w", padx=15, pady=(15,0))
        make_entry(7, 0, "Ma'lumoti", self.var_edu)
        make_entry(7, 1, "Tamomlagan", self.var_grad)
        make_entry(7, 2, "Mutaxassisligi", self.var_spec)
        make_entry(7, 3, "Chet tillari", self.var_langs)
        
        make_entry(9, 0, "Ilmiy darajasi", self.var_degree)
        make_entry(9, 1, "Ilmiy unvoni", self.var_title)
        make_entry(9, 2, "Davlat mukofotlari", self.var_awards)
        make_entry(9, 3, "Deputatlik", self.var_deputy)

        ctk.CTkLabel(grid, text="3. LAVOZIM VA ICHKI TIZIM", text_color="#3b82f6", font=("Roboto", 16, "bold")).grid(row=11, column=0, columnspan=4, sticky="w", padx=15, pady=(15,0))
        make_entry(12, 0, "Lavozim", self.var_pos, colspan=2)
        
        lbl_dept = ctk.CTkLabel(grid, text="Bo'lim / Departament", font=("Roboto", 13, "bold"), text_color="#cbd5e1")
        lbl_dept.grid(row=12, column=2, padx=15, pady=(15,5), sticky="w")
        int_depts = [d[1] for d in database.get_internal_departments()]
        cb_dept = ctk.CTkComboBox(grid, variable=self.var_dept, values=int_depts if int_depts else [""], height=35, corner_radius=8, font=("Roboto", 13))
        cb_dept.grid(row=13, column=2, padx=15, pady=(0,10), sticky="ew")

        make_entry(12, 3, "JSHSHIR", self.var_pnfl)
        make_entry(14, 0, "Passport", self.var_pass)
        make_entry(14, 1, "Ishga kirgan sana", self.var_join)

        lbl_sec = ctk.CTkLabel(grid, text="Maxfiylik Level", font=("Roboto", 13, "bold"), text_color="#cbd5e1")
        lbl_sec.grid(row=14, column=2, padx=15, pady=(15,5), sticky="w")
        cb_sec = ctk.CTkComboBox(grid, variable=self.var_secret, values=["1", "2", "3", "4", "5", "6"], height=35, corner_radius=8)
        cb_sec.grid(row=15, column=2, padx=15, pady=(0,10), sticky="ew")

        ctk.CTkLabel(grid, text="4. MEHNAT FAOLIYATI", text_color="#3b82f6", font=("Roboto", 16, "bold")).grid(row=16, column=0, columnspan=4, sticky="w", padx=15, pady=(15,5))
        self.txt_emp = ctk.CTkTextbox(grid, height=120, font=("Roboto", 14), corner_radius=8)
        self.txt_emp.grid(row=17, column=0, columnspan=4, sticky="ew", padx=15, pady=(0,10))
        if person_data and person_data.get('employment_history'):
            self.txt_emp.insert("1.0", person_data['employment_history'])

        ctk.CTkLabel(grid, text="5. YAQIN QARINDOSHLARI HAQIDA", text_color="#3b82f6", font=("Roboto", 16, "bold")).grid(row=18, column=0, columnspan=4, sticky="w", padx=15, pady=(15,5))
        
        self.relatives_frames = []
        relatives_container = ctk.CTkFrame(grid, fg_color="transparent")
        relatives_container.grid(row=19, column=0, columnspan=4, sticky="ew", padx=15, pady=5)
        
        def add_relative_row(rel=None):
            rf = ctk.CTkFrame(relatives_container, fg_color="#334155", corner_radius=8)
            rf.pack(fill="x", pady=5)
            
            v_rel = ctk.StringVar(value=rel['relationship'] if rel else "")
            v_name = ctk.StringVar(value=rel['full_name'] if rel else "")
            v_birth = ctk.StringVar(value=rel['birth_info'] if rel else "")
            v_work = ctk.StringVar(value=rel['work_info'] if rel else "")
            v_res = ctk.StringVar(value=rel['residence'] if rel else "")
            
            ctk.CTkEntry(rf, textvariable=v_rel, placeholder_text="Qarindoshligi", width=100, height=30).pack(side="left", padx=5, pady=5)
            ctk.CTkEntry(rf, textvariable=v_name, placeholder_text="F.I.SH", width=200, height=30).pack(side="left", padx=5, pady=5)
            ctk.CTkEntry(rf, textvariable=v_birth, placeholder_text="Tug'. yili va joyi", width=150, height=30).pack(side="left", padx=5, pady=5)
            ctk.CTkEntry(rf, textvariable=v_work, placeholder_text="Ish joyi va lavozimi", width=200, height=30).pack(side="left", padx=5, pady=5)
            ctk.CTkEntry(rf, textvariable=v_res, placeholder_text="Turar joyi", width=150, height=30).pack(side="left", padx=5, pady=5)
            
            btn_del = ctk.CTkButton(rf, text="X", width=30, height=30, fg_color="#ef4444", hover_color="#b91c1c", command=lambda: rf.destroy())
            btn_del.pack(side="right", padx=5, pady=5)
            
            rf.vars = (v_rel, v_name, v_birth, v_work, v_res)
            self.relatives_frames.append(rf)

        if relatives_data:
            for r in relatives_data:
                add_relative_row(r)
        else:
            add_relative_row() # Empty row
            
        ctk.CTkButton(grid, text="+ Qarindosh qo'shish", width=150, fg_color="#64748b", hover_color="#475569", command=add_relative_row).grid(row=20, column=0, columnspan=4, pady=10)

        def save_and_close():
            pinfl_val = self.var_pnfl.get().strip()
            if pinfl_val and (not pinfl_val.isdigit() or len(pinfl_val) != 14):
                from tkinter import messagebox
                messagebox.showerror("Xato", "JSHSHIR faqat 14 ta raqamdan iborat bo'lishi kerak!")
                return
            
            self.btn_save.configure(state="disabled")
            
            f_fn = self.var_fn.get()
            f_ln = self.var_ln.get()
            f_pt = self.var_pt.get()
            f_pass = self.var_pass.get()
            f_bdate = self.var_bdate.get()
            f_phone = self.var_phone.get()
            f_pos = self.var_pos.get()
            f_sec = self.var_secret.get()
            f_join = self.var_join.get()
            f_dept = self.var_dept.get()
            f_bplace = self.var_bplace.get()
            f_nat = self.var_nat.get()
            f_party = self.var_party.get()
            f_edu = self.var_edu.get()
            f_grad = self.var_grad.get()
            f_spec = self.var_spec.get()
            f_degree = self.var_degree.get()
            f_title = self.var_title.get()
            f_langs = self.var_langs.get()
            f_awards = self.var_awards.get()
            f_deputy = self.var_deputy.get()
            f_emp = self.txt_emp.get("1.0", "end").strip()
            
            rel_data = []
            for rf in self.relatives_frames:
                if rf.winfo_exists():
                    r_rel, r_name, r_birth, r_work, r_res = rf.vars
                    if r_name.get().strip():
                        rel_data.append({
                            'relationship': r_rel.get(), 'full_name': r_name.get(),
                            'birth_info': r_birth.get(), 'work_info': r_work.get(), 'residence': r_res.get()
                        })
                        
            import uuid
            new_photo = f"file_{uuid.uuid4().hex}.jpg" if isinstance(self.new_photo_person, bytes) else self.new_photo_person
            new_pass = f"file_{uuid.uuid4().hex}.jpg" if isinstance(self.new_photo_passport, bytes) else self.new_photo_passport
            ext = self.new_original_document_ext or '.docx'
            new_doc = f"file_{uuid.uuid4().hex}{ext}" if isinstance(self.new_original_document, bytes) else self.new_original_document
            
            data = {
                'first_name': f_fn, 'last_name': f_ln, 'patronymic': f_pt,
                'passport': f_pass, 'pinfl': pinfl_val, 'birth_date': f_bdate,
                'phone': f_phone, 'position': f_pos, 'secret_level': f_sec,
                'photo_person': new_photo, 'photo_passport': new_pass,
                'joined_date': f_join, 'department': f_dept,
                'birth_place': f_bplace, 'nationality': f_nat, 'party_membership': f_party,
                'education': f_edu, 'graduated_from': f_grad, 'education_specialty': f_spec,
                'academic_degree': f_degree, 'academic_title': f_title, 'languages': f_langs,
                'state_awards': f_awards, 'deputy_status': f_deputy,
                'employment_history': f_emp,
                'original_document': new_doc, 'original_document_ext': self.new_original_document_ext
            }
            
            # Attach actual bytes for the server to save directly
            if isinstance(self.new_photo_person, bytes): data['photo_person_bytes'] = self.new_photo_person
            if isinstance(self.new_photo_passport, bytes): data['photo_passport_bytes'] = self.new_photo_passport
            if isinstance(self.new_original_document, bytes): data['original_document_bytes'] = self.new_original_document

            def bg_save():
                if not person_data:
                    res = database.add_person_objective(data, rel_data)
                    act = f"Xodim qo'shildi: {f_fn} {f_ln}"
                    act_type = "add"
                else:
                    res = database.update_person_objective(person_id, data, rel_data)
                    act = f"Ma'lumot yangilandi: {f_fn} {f_ln}"
                    act_type = "update"
                    
                def on_finish():
                    if res is not None and not (isinstance(res, dict) and "error" in res):
                        database.add_activity(act, act_type)
                        from tkinter import messagebox
                        messagebox.showinfo("Muvaffaqiyat", "Ma'lumotlar saqlandi!")
                        modal.destroy()
                        self.load_dashboard_data()
                        if hasattr(self, 'active_btn'):
                            if self.active_btn == getattr(self, 'btn_list', None):
                                self.load_people()
                            elif self.active_btn == getattr(self, 'btn_orgs', None):
                                self.load_organizations()
                                if getattr(self, 'current_selected_org', None):
                                    self.load_org_people()
                        if hasattr(self, 'current_person_id') and person_data:
                            self.render_detail_window()
                    else:
                        self.btn_save.configure(state="normal")
                        from tkinter import messagebox
                        err_msg = res["error"] if isinstance(res, dict) and "error" in res else "Noma'lum xato."
                        messagebox.showerror("Xato", f"Xatolik yuz berdi:\n\n{err_msg}")
                        
                self.after(0, on_finish)
                
            import threading
            threading.Thread(target=bg_save, daemon=True).start()

        self.btn_save = ctk.CTkButton(grid, text="Saqlash", command=save_and_close, height=50, corner_radius=10, font=("Roboto", 16, "bold"), fg_color="#10b981", hover_color="#059669")
        self.btn_save.grid(row=21, column=0, columnspan=4, pady=30, padx=15, sticky="ew")

    def upload_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            with open(path, "rb") as f:
                self.new_photo_person = f.read()
            self.btn_photo.configure(text="Rasm yuklandi ✅", text_color="#10b981", fg_color="transparent", border_width=1, border_color="#10b981")

    def upload_passport(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.pdf")])
        if path:
            with open(path, "rb") as f:
                self.new_photo_passport = f.read()
            self.btn_pass_copy.configure(text="Passport yuklandi ✅", text_color="#10b981", fg_color="transparent", border_width=1, border_color="#10b981")


    def show_meetings(self):
        self.set_active_btn(self.btn_meetings)
        for f in [self.dash_frame, self.list_frame, self.settings_frame, self.orgs_frame, self.attendance_frame, self.meetings_frame, getattr(self, 'adv_search_frame', None)]: f.grid_forget()
        self.meetings_frame.grid(row=1, column=0, sticky="nsew")
        self.header_bar.winfo_children()[0].configure(text="Majlislar Boshqaruvi")
        self.load_meetings()

    def build_orgs_content(self):
        self.orgs_frame.grid_rowconfigure(1, weight=1)
        self.orgs_frame.grid_columnconfigure(0, weight=30, minsize=420)
        self.orgs_frame.grid_columnconfigure(1, weight=70, minsize=980)
        
        # --- Left Panel: Tashkilotlar ---
        left_panel = ctk.CTkFrame(self.orgs_frame, fg_color="#1e293b", corner_radius=10)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=20)
        left_panel.grid_rowconfigure(2, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        
        header_l = ctk.CTkFrame(left_panel, fg_color="transparent")
        header_l.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        ctk.CTkLabel(header_l, text="🏢 Tashkilotlar", font=("Roboto", 20, "bold"), text_color="white").pack(side="left")
        if self.current_user['access_level'] >= 4:
            self.btn_delete_all_orgs = ctk.CTkButton(header_l, text="🗑️ O'chirish", fg_color="#dc2626", hover_color="#991b1b", font=("Roboto", 12, "bold"), width=85, height=32, command=self.delete_all_organizations_action)
            if getattr(self, 'secret_unlocked', False):
                self.btn_delete_all_orgs.pack(side="right", padx=2)
            ctk.CTkButton(header_l, text="📁 Word", fg_color="#3b82f6", hover_color="#2563eb", font=("Roboto", 12, "bold"), width=75, height=32, command=self.import_organizations_docx).pack(side="right", padx=2)
            ctk.CTkButton(header_l, text="➕ Yangi", fg_color="#10b981", hover_color="#059669", font=("Roboto", 12, "bold"), width=70, height=32, command=self.add_org).pack(side="right", padx=2)
        
        self.org_search_var = ctk.StringVar()
        self.org_search_var.trace("w", lambda *args: self.load_organizations())
        search_entry = ctk.CTkEntry(left_panel, textvariable=self.org_search_var, placeholder_text="Tashkilotni qidirish...", height=35)
        search_entry.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        
        self.orgs_list_frame = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.orgs_list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # --- Right Panel: Xodimlar ---
        right_panel = ctk.CTkFrame(self.orgs_frame, fg_color="#1e293b", corner_radius=10)
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=20)
        right_panel.grid_rowconfigure(2, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        header_r = ctk.CTkFrame(right_panel, fg_color="transparent")
        header_r.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        self.org_people_lbl = ctk.CTkLabel(header_r, text="Tashkilot tanlang", font=("Roboto", 22, "bold"), text_color="white")
        self.org_people_lbl.pack(side="left")
        
        if self.current_user['access_level'] >= 5:
            self.btn_add_org_person = ctk.CTkButton(header_r, text="➕ Odam Biriktirish", fg_color="#3b82f6", hover_color="#2563eb", font=("Roboto", 14, "bold"), command=self.add_person_to_selected_org, state="disabled")
            self.btn_add_org_person.pack(side="right")
        
        grid_header = ctk.CTkFrame(right_panel, fg_color="#334155", corner_radius=5, height=40)
        grid_header.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 5))
        grid_header.grid_propagate(False)
        grid_header.grid_columnconfigure(0, weight=0, minsize=45)
        grid_header.grid_columnconfigure(1, weight=1)
        grid_header.grid_columnconfigure(2, weight=0, minsize=140)
        grid_header.grid_columnconfigure(3, weight=0, minsize=340)
        
        ctk.CTkLabel(grid_header, text="№", font=("Roboto", 13, "bold"), text_color="#cbd5e1", width=45).grid(row=0, column=0, padx=(10, 5), pady=8)
        ctk.CTkLabel(grid_header, text="F.I.SH & Lavozimi", font=("Roboto", 13, "bold"), text_color="#cbd5e1", anchor="w").grid(row=0, column=1, padx=10, pady=8, sticky="w")
        ctk.CTkLabel(grid_header, text="Telefon", font=("Roboto", 13, "bold"), text_color="#cbd5e1", anchor="w", width=140).grid(row=0, column=2, padx=10, pady=8, sticky="w")
        ctk.CTkLabel(grid_header, text="Amallar", font=("Roboto", 13, "bold"), text_color="#cbd5e1", anchor="center", width=340).grid(row=0, column=3, padx=10, pady=8, sticky="e")
        
        self.org_people_grid = ctk.CTkScrollableFrame(right_panel, fg_color="transparent")
        self.org_people_grid.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        self.current_selected_org = None
        self.org_cards = []

    def load_organizations(self):
        for widget in self.orgs_list_frame.winfo_children(): widget.destroy()
        self.org_cards.clear()
        orgs = database.get_organizations()
        orgs.sort(key=lambda o: (o[1] or "").strip().lower())
        
        q = self.org_search_var.get().lower()
        idx = 1
        for o in orgs:
            org_id, name, sector = o[0], o[1], o[2]
            if q and q not in name.lower() and q not in (sector or "").lower(): continue
            count = len(database.get_people_by_org(name, self.current_user['access_level']))
            
            card = ctk.CTkFrame(self.orgs_list_frame, fg_color="#334155", corner_radius=10, border_width=1, border_color="#334155")
            card.pack(fill="x", pady=5, padx=5)
            
            def on_click(event, org_name=name, c=card): self.select_org(org_name, c)
            card.bind("<Button-1>", on_click)
            
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=12, pady=(10, 2))
            top_row.bind("<Button-1>", on_click)
            
            title_lbl = ctk.CTkLabel(top_row, text=f"{idx}. {name}", font=("Roboto", 14, "bold"), text_color="white", anchor="w", justify="left", wraplength=210)
            title_lbl.pack(side="left", fill="x", expand=True)
            title_lbl.bind("<Button-1>", on_click)
            
            badge = ctk.CTkFrame(top_row, fg_color="#10b981" if count > 0 else "#64748b", corner_radius=8, height=22)
            badge.pack(side="right", padx=(5, 0))
            badge.bind("<Button-1>", on_click)
            
            badge_lbl = ctk.CTkLabel(badge, text=f"{count} ta xodim", font=("Roboto", 11, "bold"), text_color="white")
            badge_lbl.pack(padx=6, pady=2)
            badge_lbl.bind("<Button-1>", on_click)
            
            bot_frame = ctk.CTkFrame(card, fg_color="transparent")
            bot_frame.pack(fill="x", padx=12, pady=(2, 8))
            bot_frame.bind("<Button-1>", on_click)
            
            sec_text = sector or "Soha ko'rsatilmagan"
            sector_lbl = ctk.CTkLabel(bot_frame, text=sec_text, font=("Roboto", 11), text_color="#94a3b8", anchor="w", justify="left", wraplength=170)
            sector_lbl.pack(side="left", fill="x", expand=True)
            sector_lbl.bind("<Button-1>", on_click)
            
            if self.current_user['access_level'] >= 4:
                def del_org(oid=org_id, oname=name):
                    from tkinter import messagebox
                    if messagebox.askyesno("Tasdiqlash", f"Rostdan ham '{oname}' tashkilotini va unga biriktirilgan barcha xodimlarni o'chirasizmi?"):
                        database.delete_organization(oid)
                        if self.current_selected_org == oname:
                            self.current_selected_org = None
                            self.org_people_lbl.configure(text="Tashkilot tanlang")
                            self.btn_add_org_person.configure(state="disabled")
                            for w in self.org_people_grid.winfo_children(): w.destroy()
                        self.load_organizations()
                        self.load_org_people()
                
                def edit_org_fn(oid=org_id, oname=name, osec=sector, olead=o[3] if len(o)>3 and o[3] else "", oph=o[4] if len(o)>4 and o[4] else "", oaddr=o[5] if len(o)>5 and o[5] else ""):
                    self.open_edit_org_modal(oid, oname, osec, olead, oph, oaddr)

                ctk.CTkButton(bot_frame, text="✏️", fg_color="transparent", text_color="#3b82f6", hover_color="#1d4ed8", width=26, height=22, font=("Roboto", 13), command=edit_org_fn).pack(side="right", padx=2)
                ctk.CTkButton(bot_frame, text="🗑️", fg_color="transparent", text_color="#ef4444", hover_color="#7f1d1d", width=26, height=22, font=("Roboto", 13), command=del_org).pack(side="right", padx=2)
                
            self.org_cards.append((name, card))
            idx += 1

    def open_edit_org_modal(self, org_id, old_name, old_sector, old_leader, old_phone, old_address):
        m = ctk.CTkToplevel(self)
        m.title("Tashkilotni Tahrirlash")
        m.geometry("500x580")
        m.resizable(False, False)
        m.configure(fg_color="#0f172a")
        m.transient(self)
        m.grab_set()

        container = ctk.CTkFrame(m, fg_color="#1e293b", corner_radius=15)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="✏️ Tashkilotni Tahrirlash", font=("Roboto", 20, "bold"), text_color="white").pack(pady=(15, 5))
        
        divider = ctk.CTkFrame(container, fg_color="#334155", height=1)
        divider.pack(fill="x", padx=20, pady=10)

        form = ctk.CTkScrollableFrame(container, fg_color="transparent", height=380)
        form.pack(fill="both", expand=True, padx=10)

        ctk.CTkLabel(form, text="Tashkilot nomi:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10, pady=(5,0))
        n_ent = ctk.CTkEntry(form, width=400, height=35)
        n_ent.pack(pady=(5, 10), padx=10)
        n_ent.insert(0, old_name or "")

        ctk.CTkLabel(form, text="Soha / Tarmoq:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10)
        s_ent = ctk.CTkEntry(form, width=400, height=35)
        s_ent.pack(pady=(5, 10), padx=10)
        s_ent.insert(0, old_sector or "")

        ctk.CTkLabel(form, text="Tashkilot rahbari:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10)
        l_ent = ctk.CTkEntry(form, width=400, height=35)
        l_ent.pack(pady=(5, 10), padx=10)
        l_ent.insert(0, old_leader or "")

        ctk.CTkLabel(form, text="Telefon (Aloqa):", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10)
        p_ent = ctk.CTkEntry(form, width=400, height=35)
        p_ent.pack(pady=(5, 10), padx=10)
        p_ent.insert(0, old_phone or "")

        ctk.CTkLabel(form, text="Manzili:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10)
        a_ent = ctk.CTkEntry(form, width=400, height=35)
        a_ent.pack(pady=(5, 10), padx=10)
        a_ent.insert(0, old_address or "")

        def save_edit():
            new_name = n_ent.get().strip()
            if not new_name: return
            database.update_organization(org_id, new_name, s_ent.get().strip(), l_ent.get().strip(), p_ent.get().strip(), a_ent.get().strip())
            m.destroy()
            if self.current_selected_org == old_name:
                self.current_selected_org = new_name
            self.load_organizations()

        btn_f = ctk.CTkFrame(container, fg_color="transparent")
        btn_f.pack(fill="x", pady=15)
        ctk.CTkButton(btn_f, text="Saqlash", command=save_edit, fg_color="#10b981", hover_color="#059669", font=("Roboto", 14, "bold"), width=160, height=40).pack(side="right", padx=(10, 20))
        ctk.CTkButton(btn_f, text="Bekor qilish", command=m.destroy, fg_color="#475569", font=("Roboto", 14), width=120, height=40).pack(side="right")

    def select_org(self, org_name, active_card):
        self.current_selected_org = org_name
        self.btn_add_org_person.configure(state="normal")
        self.org_people_lbl.configure(text=f"{org_name} xodimlari")
        for _, card in self.org_cards:
            if card.winfo_exists(): card.configure(border_color="#334155")
        if active_card.winfo_exists(): active_card.configure(border_color="#3b82f6")
        self.load_org_people()

    def add_org(self):
        m = ctk.CTkToplevel(self)
        m.title("🏢 Yangi Tashkilot Qo'shish")
        m.geometry("500x600")
        m.resizable(False, False)
        m.configure(fg_color="#0f172a")
        m.transient(self)
        m.grab_set()
        
        container = ctk.CTkFrame(m, fg_color="#1e293b", corner_radius=15)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        ctk.CTkLabel(container, text="🏢 Yangi Tashkilot Qo'shish", font=("Roboto", 20, "bold"), text_color="white").pack(pady=(15, 5))
        ctk.CTkLabel(container, text="Hokimiyat tizimidagi boshqarma yoki korxona ma'lumotlarini kiriting", font=("Roboto", 11), text_color="#94a3b8").pack()
        
        divider = ctk.CTkFrame(container, fg_color="#334155", height=1)
        divider.pack(fill="x", padx=20, pady=15)
        
        form_frame = ctk.CTkScrollableFrame(container, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=10)
        
        # Field 1
        ctk.CTkLabel(form_frame, text="1. Tashkilot / Boshqarma Nomi:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10, pady=(10, 0))
        name_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=name_var, placeholder_text="Masalan: Viloyat Moliya Boshqarmasi", width=400, height=35).pack(pady=(4, 10), padx=10)
        
        # Field 2
        ctk.CTkLabel(form_frame, text="2. Tizim Sohasi / Yo'nalishi:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10)
        sector_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=sector_var, placeholder_text="Masalan: Qurilish, kommunal va ekologiya", width=400, height=35).pack(pady=(4, 10), padx=10)
        
        # Field 3
        ctk.CTkLabel(form_frame, text="3. Tashkilot Rahbari (F.I.SH.):", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10)
        leader_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=leader_var, placeholder_text="Masalan: Alisherov Botir Alisherovich", width=400, height=35).pack(pady=(4, 10), padx=10)
        
        # Field 4
        ctk.CTkLabel(form_frame, text="4. Rasmiy Telefon Raqami / Kantselyariya:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10)
        phone_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=phone_var, placeholder_text="Masalan: +998 69 220 00 00", width=400, height=35).pack(pady=(4, 10), padx=10)
        
        # Field 5
        ctk.CTkLabel(form_frame, text="5. Tashkilot Manzili:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10)
        address_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=address_var, placeholder_text="Masalan: Namangan sh., Mustaqillik shoh ko'chasi, 5-uy", width=400, height=35).pack(pady=(4, 10), padx=10)
        
        def save():
            name = name_var.get().strip()
            sector = sector_var.get().strip()
            leader = leader_var.get().strip()
            phone = phone_var.get().strip()
            address = address_var.get().strip()
            
            if name:
                res = database.add_organization(name, sector, leader, phone, address)
                from tkinter import messagebox
                if res is None:
                    messagebox.showerror("Xato", "Tarmoq bilan aloqa uzildi yoki xatolik yuz berdi!")
                elif res:
                    self.load_organizations()
                    m.destroy()
                else:
                    messagebox.showerror("Xato", "Bunday nomdagi tashkilot allaqachon mavjud!")
            else:
                from tkinter import messagebox
                messagebox.showwarning("Ogohlantirish", "Tashkilot nomi bo'sh bo'lishi mumkin emas!")
                
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(btn_frame, text="Saqlash", command=save, fg_color="#059669", hover_color="#047857", font=("Roboto", 14, "bold"), text_color="white", width=180, height=40).pack(side="right", padx=(10, 30))
        ctk.CTkButton(btn_frame, text="Bekor qilish", command=m.destroy, fg_color="#475569", hover_color="#334155", font=("Roboto", 14), text_color="white", width=120, height=40).pack(side="right")

    def add_person_to_selected_org(self):
        if not self.current_selected_org: return
        self.open_assign_person_modal(self.current_selected_org)

    def open_assign_person_modal(self, org_name):
        m = ctk.CTkToplevel(self)
        m.title(f"Xodim qo'shish - {org_name}")
        m.geometry("400x480")
        m.configure(fg_color="#1e293b")
        m.transient(self)
        m.grab_set()
        
        ctk.CTkLabel(m, text=f"👤 Xodimni kiriting", font=("Roboto", 20, "bold"), text_color="white").pack(pady=(20, 20))
        
        ctk.CTkLabel(m, text="To'liq ismi (F.I.SH):", font=("Roboto", 14), text_color="#cbd5e1").pack(anchor="w", padx=50)
        name_entry = ctk.CTkEntry(m, placeholder_text="Masalan: G'aniyev Alisher", width=300, height=40)
        name_entry.pack(pady=(0, 15))
        
        ctk.CTkLabel(m, text="Telefon raqami:", font=("Roboto", 14), text_color="#cbd5e1").pack(anchor="w", padx=50)
        phone_entry = ctk.CTkEntry(m, placeholder_text="+998 90 123 45 67", width=300, height=40)
        phone_entry.pack(pady=(0, 15))
        
        ctk.CTkLabel(m, text="Lavozimi:", font=("Roboto", 14), text_color="#cbd5e1").pack(anchor="w", padx=50)
        pos_entry = ctk.CTkEntry(m, placeholder_text="Masalan: Bosh mutaxassis", width=300, height=40)
        pos_entry.pack(pady=(0, 20))
        
        def do_assign():
            fullname = name_entry.get().strip()
            phone = phone_entry.get().strip()
            pos = pos_entry.get().strip()
            if not fullname: return
            database.add_guest(fullname, org_name, phone, pos)
            m.destroy()
            self.load_organizations()
            self.load_org_people()
            
        ctk.CTkButton(m, text="✅ Qo'shish", font=("Roboto", 15, "bold"), command=do_assign, fg_color="#10b981", hover_color="#059669", width=200, height=45).pack(pady=10)

    def load_org_people(self):
        for widget in self.org_people_grid.winfo_children(): widget.destroy()
        if not self.current_selected_org: return
        people = database.get_people_by_org(self.current_selected_org, self.current_user['access_level'])
        people.sort(key=lambda p: f"{p[1]} {p[2]}".strip().lower())
        
        idx = 1
        for p in people:
            p_id, fname, pos, phone = p[0], f"{p[1]} {p[2]}".strip(), p[3] or "Lavozim yo'q", p[4] or "Raqam yo'q"
            row_frame = ctk.CTkFrame(self.org_people_grid, fg_color="#0f172a", corner_radius=8)
            row_frame.pack(fill="x", pady=4, padx=5)
            row_frame.grid_columnconfigure(0, weight=0, minsize=45)
            row_frame.grid_columnconfigure(1, weight=1)
            row_frame.grid_columnconfigure(2, weight=0, minsize=140)
            row_frame.grid_columnconfigure(3, weight=0, minsize=340)

            # Col 0: Index Number
            ctk.CTkLabel(row_frame, text=str(idx), font=("Roboto", 13, "bold"), text_color="#94a3b8", width=45).grid(row=0, column=0, padx=(10, 5), pady=10)

            # Col 1: Name & Position
            info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            info_frame.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
            ctk.CTkLabel(info_frame, text=fname, font=("Roboto", 14, "bold"), text_color="white", anchor="w", justify="left", wraplength=400).pack(anchor="w", fill="x")
            ctk.CTkLabel(info_frame, text=pos, font=("Roboto", 12), text_color="#94a3b8", anchor="w", justify="left", wraplength=400).pack(anchor="w", fill="x")

            # Col 2: Phone Number
            ctk.CTkLabel(row_frame, text=phone, font=("Roboto", 13), text_color="#cbd5e1", anchor="w", width=140).grid(row=0, column=2, padx=10, pady=10, sticky="w")

            # Col 3: Action Buttons Container (Fixed Width)
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=340)
            actions_frame.grid(row=0, column=3, padx=10, pady=8, sticky="e")

            def assign_to_meeting(person_id=p_id, person_name=fname):
                self.open_assign_to_meeting_modal(person_id, person_name)
            ctk.CTkButton(actions_frame, text="🤝 Vakil qilish", fg_color="#10b981", hover_color="#059669", font=("Roboto", 12, "bold"), width=110, height=32, command=assign_to_meeting).pack(side="left", padx=3)

            if self.current_user['access_level'] >= 4:
                def edit_person(pid=p_id, p_fn=p[1], p_ln=p[2], p_pos=p[3] or "", p_ph=p[4] or ""):
                    self.open_edit_external_person_modal(pid, p_fn, p_ln, p_pos, p_ph)
                ctk.CTkButton(actions_frame, text="✏️ Tahrirlash", fg_color="#3b82f6", hover_color="#1d4ed8", font=("Roboto", 12, "bold"), width=100, height=32, command=edit_person).pack(side="left", padx=3)

                def del_person(pid=p_id):
                    from tkinter import messagebox
                    if messagebox.askyesno("O'chirish", "Ushbu xodimni o'chirishni tasdiqlaysizmi?"):
                        database.delete_person(pid)
                        self.load_org_people()
                        self.load_organizations()
                ctk.CTkButton(actions_frame, text="🗑️", fg_color="#ef4444", hover_color="#7f1d1d", font=("Roboto", 13), width=36, height=32, command=del_person).pack(side="left", padx=3)
            idx += 1

    def open_edit_external_person_modal(self, person_id, first_name, last_name, position, phone):
        m = ctk.CTkToplevel(self)
        m.title("Tashkilot Xodimi / Vakilini Tahrirlash")
        m.geometry("480x480")
        m.resizable(False, False)
        m.configure(fg_color="#0f172a")
        m.transient(self)
        m.grab_set()

        container = ctk.CTkFrame(m, fg_color="#1e293b", corner_radius=15)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="✏️ Xodim / Vakilni Tahrirlash", font=("Roboto", 20, "bold"), text_color="white").pack(pady=(15, 5))

        divider = ctk.CTkFrame(container, fg_color="#334155", height=1)
        divider.pack(fill="x", padx=20, pady=10)

        form = ctk.CTkFrame(container, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20)

        ctk.CTkLabel(form, text="Ismi:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", pady=(5,0))
        fn_ent = ctk.CTkEntry(form, width=380, height=35)
        fn_ent.pack(pady=(5, 10))
        fn_ent.insert(0, first_name or "")

        ctk.CTkLabel(form, text="Familiyasi:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w")
        ln_ent = ctk.CTkEntry(form, width=380, height=35)
        ln_ent.pack(pady=(5, 10))
        ln_ent.insert(0, last_name or "")

        ctk.CTkLabel(form, text="Lavozimi:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w")
        pos_ent = ctk.CTkEntry(form, width=380, height=35)
        pos_ent.pack(pady=(5, 10))
        pos_ent.insert(0, position or "")

        ctk.CTkLabel(form, text="Telefon raqami:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w")
        ph_ent = ctk.CTkEntry(form, width=380, height=35)
        ph_ent.pack(pady=(5, 15))
        ph_ent.insert(0, phone or "")

        def save_person_edit():
            fn = fn_ent.get().strip()
            ln = ln_ent.get().strip()
            if not fn: return
            database.update_external_person(person_id, fn, ln, pos_ent.get().strip(), ph_ent.get().strip())
            m.destroy()
            self.load_org_people()

        btn_f = ctk.CTkFrame(container, fg_color="transparent")
        btn_f.pack(fill="x", pady=15)
        ctk.CTkButton(btn_f, text="Saqlash", command=save_person_edit, fg_color="#10b981", hover_color="#059669", font=("Roboto", 14, "bold"), width=160, height=40).pack(side="right", padx=(10, 20))
        ctk.CTkButton(btn_f, text="Bekor qilish", command=m.destroy, fg_color="#475569", font=("Roboto", 14), width=120, height=40).pack(side="right")

    def open_assign_to_meeting_modal(self, person_id, person_name):
        m = ctk.CTkToplevel(self)
        m.title("Majlisga Vakil qilish")
        m.geometry("400x250")
        m.configure(fg_color="#1e293b")
        m.transient(self)
        m.grab_set()
        
        ctk.CTkLabel(m, text=f"{person_name} ni vakil qilish", font=("Roboto", 16, "bold"), text_color="white").pack(pady=(20, 10))
        
        meetings = database.get_meetings()
        if not meetings:
            ctk.CTkLabel(m, text="Faol majlislar yo'q!", text_color="#ef4444").pack(pady=10)
            return
            
        meeting_dict = {m[1]: m[0] for m in meetings}
        meeting_names = list(meeting_dict.keys())
        
        sel_meeting = ctk.StringVar(value=meeting_names[0])
        ctk.CTkOptionMenu(m, variable=sel_meeting, values=meeting_names, width=300).pack(pady=10)
        
        def save():
            m_id = meeting_dict[sel_meeting.get()]
            database.add_meeting_attendee(m_id, person_id)
            from tkinter import messagebox
            messagebox.showinfo("Muvaffaqiyat", "Xodim majlisga vakil sifatida qo'shildi!")
            m.destroy()
            
        ctk.CTkButton(m, text="Qo'shish", command=save, fg_color="#10b981", height=40).pack(pady=20)

    # ========================== MAJLISLAR MODULE ==========================
    def build_meetings_content(self):
        self.meetings_frame.grid_rowconfigure(1, weight=1)
        self.meetings_frame.grid_columnconfigure(0, weight=30)
        self.meetings_frame.grid_columnconfigure(1, weight=70)
        
        # --- Left Panel: Majlislar Ro'yxati ---
        left_panel = ctk.CTkFrame(self.meetings_frame, fg_color="#1e293b", corner_radius=10)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=20)
        left_panel.grid_rowconfigure(2, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        
        header_l = ctk.CTkFrame(left_panel, fg_color="transparent")
        header_l.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        ctk.CTkLabel(header_l, text="🤝 Majlislar", font=("Roboto", 22, "bold"), text_color="white").pack(side="left")
        
        if self.current_user['access_level'] >= 5:
            ctk.CTkButton(left_panel, text="➕ Yangi Majlis Ochish", fg_color="#3b82f6", hover_color="#2563eb", font=("Roboto", 14, "bold"), command=self.open_add_meeting_modal, height=45).grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        
        self.meetings_list_frame = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.meetings_list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # --- Right Panel: Majlis Detallari ---
        right_panel = ctk.CTkFrame(self.meetings_frame, fg_color="#1e293b", corner_radius=10)
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=20)
        right_panel.grid_rowconfigure(2, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        header_r = ctk.CTkFrame(right_panel, fg_color="transparent")
        header_r.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        self.meeting_title_lbl = ctk.CTkLabel(header_r, text="Majlis tanlang", font=("Roboto", 22, "bold"), text_color="white")
        self.meeting_title_lbl.pack(side="left")
        
        self.meeting_counter_lbl = ctk.CTkLabel(header_r, text="Majlisda: 0 / 0 kishi keldi", font=("Roboto", 16, "bold"), text_color="#10b981")
        self.meeting_counter_lbl.pack(side="left", padx=20)
        
        actions_r = ctk.CTkFrame(header_r, fg_color="transparent")
        actions_r.pack(side="right")
        
        self.btn_export_meeting = ctk.CTkButton(actions_r, text="📊 Majlis Hisoboti", fg_color="transparent", border_width=1, border_color="#3b82f6", text_color="#3b82f6", hover_color="#1e3a8a", font=("Roboto", 14, "bold"), command=self.export_meeting_report, state="disabled")
        self.btn_export_meeting.pack(side="left", padx=10)
        
        self.btn_add_attendee = ctk.CTkButton(actions_r, text="➕ Xodimni Chaqirish", fg_color="#10b981", hover_color="#059669", font=("Roboto", 14, "bold"), command=self.open_add_attendee_modal, state="disabled")
        self.btn_add_attendee.pack(side="left")
        
        grid_header = ctk.CTkFrame(right_panel, fg_color="#334155", corner_radius=5, height=40)
        grid_header.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 5))
        grid_header.grid_propagate(False)
        grid_header.grid_columnconfigure(1, weight=3)
        grid_header.grid_columnconfigure(2, weight=1)
        grid_header.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(grid_header, text="ID", font=("Roboto", 14, "bold"), width=50).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkLabel(grid_header, text="Vakil (Tashkilot Nomidan)", font=("Roboto", 14, "bold"), anchor="w").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(grid_header, text="Aloqa", font=("Roboto", 14, "bold"), anchor="w").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(grid_header, text="Davomat (Ishtirok)", font=("Roboto", 14, "bold"), anchor="center").grid(row=0, column=3, padx=10, pady=5)
        
        self.meeting_attendees_grid = ctk.CTkScrollableFrame(right_panel, fg_color="transparent")
        self.meeting_attendees_grid.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        self.current_selected_meeting_id = None
        self.meeting_cards = []

    def load_meetings(self):
        for widget in self.meetings_list_frame.winfo_children(): widget.destroy()
        self.meeting_cards.clear()
        
        meetings = database.get_meetings()
        for m in meetings:
            m_id, title, m_type, dt, loc, chair, agenda = m
            card = ctk.CTkFrame(self.meetings_list_frame, fg_color="#334155", corner_radius=10, border_width=1, border_color="#334155")
            card.pack(fill="x", pady=5, padx=5)
            
            def on_click(event, meeting_id=m_id, m_title=title, c=card):
                self.select_meeting(meeting_id, m_title, c)
                
            card.bind("<Button-1>", on_click)
            
            title_lbl = ctk.CTkLabel(card, text=title, font=("Roboto", 16, "bold"), text_color="white", anchor="w")
            title_lbl.pack(fill="x", padx=15, pady=(10, 2))
            title_lbl.bind("<Button-1>", on_click)
            
            bot_frame = ctk.CTkFrame(card, fg_color="transparent")
            bot_frame.pack(fill="x", padx=15, pady=(0, 10))
            bot_frame.bind("<Button-1>", on_click)
            
            type_lbl = ctk.CTkLabel(bot_frame, text=f"🏷 {m_type}", font=("Roboto", 12), text_color="#93c5fd")
            type_lbl.pack(side="left")
            type_lbl.bind("<Button-1>", on_click)
            
            dt_lbl = ctk.CTkLabel(bot_frame, text=f" 🕒 {dt}", font=("Roboto", 12), text_color="#cbd5e1")
            dt_lbl.pack(side="left", padx=10)
            dt_lbl.bind("<Button-1>", on_click)
            
            if self.current_user['access_level'] >= 5:
                def del_meeting(mid=m_id):
                    from tkinter import messagebox
                    if messagebox.askyesno("Tasdiqlash", "Bu majlisni o'chirib tashlaysizmi?"):
                        database.delete_meeting(mid)
                        if self.current_selected_meeting_id == mid:
                            self.current_selected_meeting_id = None
                            self.meeting_title_lbl.configure(text="Majlis tanlang")
                            self.meeting_counter_lbl.configure(text="Majlisda: 0 / 0 kishi keldi")
                            self.btn_add_attendee.configure(state="disabled")
                            self.btn_export_meeting.configure(state="disabled")
                            for w in self.meeting_attendees_grid.winfo_children(): w.destroy()
                        self.load_meetings()
                ctk.CTkButton(bot_frame, text="🗑️", fg_color="transparent", text_color="#ef4444", hover_color="#7f1d1d", width=30, height=20, font=("Roboto", 14), command=del_meeting).pack(side="right")
            
            self.meeting_cards.append((m_id, card))

    def select_meeting(self, meeting_id, title, active_card):
        self.current_selected_meeting_id = meeting_id
        self.btn_add_attendee.configure(state="normal")
        self.btn_export_meeting.configure(state="normal")
        self.meeting_title_lbl.configure(text=title)
        
        for _, card in self.meeting_cards:
            if card.winfo_exists(): card.configure(border_color="#334155")
        if active_card.winfo_exists(): active_card.configure(border_color="#3b82f6")
        
        self.load_meeting_attendees()

    def load_meeting_attendees(self):
        for widget in self.meeting_attendees_grid.winfo_children(): widget.destroy()
        if not self.current_selected_meeting_id: return
        
        attendees = database.get_meeting_attendees(self.current_selected_meeting_id, self.current_user['access_level'])
        
        total = len(attendees)
        present = sum(1 for a in attendees if a[6] == "✔ KELDI")
        self.meeting_counter_lbl.configure(text=f"Majlisda: {present} / {total} kishi keldi")
        
        internals = [a for a in attendees if len(a) > 8 and a[8] == 0]
        externals = [a for a in attendees if len(a) > 8 and a[8] == 1]
        if not internals and not externals:
            internals = attendees

        from collections import defaultdict
        external_groups = defaultdict(list)
        for a in externals:
            group_name = a[9] if len(a) > 9 and a[9] else a[5]
            if not group_name: group_name = "Boshqa tashkilotlar"
            external_groups[group_name].append(a)

        def render_attendee(a, show_badge=True):
            p_id, fname, lname, pos, phone, org, status = a[:7]
            fullname = f"{fname} {lname}".strip()
            
            row_frame = ctk.CTkFrame(self.meeting_attendees_grid, fg_color="#0f172a", corner_radius=5)
            row_frame.pack(fill="x", pady=4, padx=5)
            row_frame.grid_columnconfigure(1, weight=3)
            row_frame.grid_columnconfigure(2, weight=1)
            row_frame.grid_columnconfigure(3, weight=1)
            
            ctk.CTkLabel(row_frame, text=str(p_id), font=("Roboto", 14), width=50).grid(row=0, column=0, padx=10, pady=10)
            
            info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            info_frame.grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            top_line = ctk.CTkFrame(info_frame, fg_color="transparent")
            top_line.pack(anchor="w")
            
            display_org = org if org else "Tashkilot yo'q"
            ctk.CTkLabel(top_line, text=fullname, font=("Roboto", 15, "bold"), text_color="white").pack(side="left")
            
            if show_badge:
                ctk.CTkLabel(top_line, text=" — ", font=("Roboto", 15, "bold"), text_color="#cbd5e1").pack(side="left")
                org_badge = ctk.CTkFrame(top_line, fg_color="#1e40af", corner_radius=8, height=20)
                org_badge.pack(side="left")
                ctk.CTkLabel(org_badge, text=f"🏢 [{display_org}]", font=("Roboto", 12, "bold"), text_color="white").pack(padx=8, pady=2)
            
            ctk.CTkLabel(info_frame, text=pos or "Lavozim yo'q", font=("Roboto", 12), text_color="#94a3b8", anchor="w").pack(anchor="w")
            
            ctk.CTkLabel(row_frame, text=phone or "Raqam yo'q", font=("Roboto", 14), text_color="#cbd5e1", anchor="w").grid(row=0, column=2, padx=10, pady=10, sticky="w")
            
            status_btn = ctk.CTkButton(row_frame, text=status, width=120, height=35, font=("Roboto", 13, "bold"), corner_radius=8)
            status_btn.grid(row=0, column=3, padx=10, pady=10)
            
            def apply_status_style(btn, st):
                if "KELDI" in st and "KELMADI" not in st: btn.configure(text=st, fg_color="#059669", hover_color="#047857", text_color="white")
                elif "KELMADI" in st: btn.configure(text=st, fg_color="#e11d48", hover_color="#be123c", text_color="white")
                elif "SABABLI" in st: btn.configure(text=st, fg_color="#2563eb", hover_color="#1d4ed8", text_color="white")
                else: btn.configure(text="⏳ Kutilmoqda", fg_color="#d97706", hover_color="#b45309", text_color="white")

            apply_status_style(status_btn, status)
            status_btn._current_status = status

            def on_toggle(btn=status_btn, person_id=p_id):
                cs = btn._current_status
                if "Kutilmoqda" in cs: ns = "✔ KELDI"
                elif "KELDI" in cs and "KELMADI" not in cs: ns = "✖ KELMADI"
                elif "KELMADI" in cs: ns = "📝 SABABLI"
                else: ns = "✔ KELDI"
                
                database.set_meeting_attendee_status(self.current_selected_meeting_id, person_id, ns)
                btn._current_status = ns
                apply_status_style(btn, ns)
                
                att = database.get_meeting_attendees(self.current_selected_meeting_id, self.current_user['access_level'])
                tot = len(att)
                pres = sum(1 for a in att if "KELDI" in a[6] and "KELMADI" not in a[6])
                self.meeting_counter_lbl.configure(text=f"Majlisda: {pres} / {tot} kishi keldi")

            if self.current_user['access_level'] >= 4:
                status_btn.configure(command=on_toggle)
                def remove_attendee(person_id=p_id, person_name=fullname):
                    from tkinter import messagebox
                    if messagebox.askyesno("Majlisdan chiqarish", f"Rostdan ham '{person_name}' ni ushbu majlisdan chiqarib tashlaysizmi?"):
                        database.delete_meeting_attendee(self.current_selected_meeting_id, person_id)
                        self.load_meeting_attendees()
                ctk.CTkButton(row_frame, text="🗑️", fg_color="transparent", text_color="#ef4444", hover_color="#7f1d1d", width=35, height=35, font=("Roboto", 14), command=remove_attendee).grid(row=0, column=4, padx=5, pady=10)

        for a in internals:
            render_attendee(a, show_badge=False)

        for group_name, group_attendees in external_groups.items():
            header_frame = ctk.CTkFrame(self.meeting_attendees_grid, fg_color="#38bdf8", corner_radius=5)
            header_frame.pack(fill="x", pady=(10, 4), padx=5)
            
            gn = group_name
            if "tashkilot" not in gn.lower() and "taalluqli" not in gn.lower():
                gn += " masalalariga taalluqli tashkilotlar"
                
            ctk.CTkLabel(header_frame, text=gn.upper(), font=("Roboto", 14, "bold"), text_color="#0f172a").pack(pady=8)
            
            for a in group_attendees:
                render_attendee(a, show_badge=False)


    def import_organizations_docx(self):
        from tkinter import filedialog, messagebox
        import docx
        import difflib
        import re

        path = filedialog.askopenfilename(
            title="Word Hujjatini Tanlang (.docx)",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        if not path:
            return

        def cyrillic_to_latin(text):
            if not text: return ""
            replacements = [
                ("Е", "Ye"), ("е", "ye"), ("Ё", "Yo"), ("ё", "yo"),
                ("Ю", "Yu"), ("ю", "yu"), ("Я", "Ya"), ("я", "ya"),
                ("Ш", "Sh"), ("ш", "sh"), ("Ч", "Ch"), ("ч", "ch"),
                ("Ғ", "G'"), ("ғ", "g'"), ("Ў", "O'"), ("ў", "o'"),
                ("Қ", "Q"),  ("қ", "q"),  ("Ҳ", "H"),  ("ҳ", "h"),
                ("Ц", "Ts"), ("ц", "ts"),
            ]
            text = re.sub(r'(^|\s)Е', r'\g<1>Ye', text)
            text = re.sub(r'(^|\s)е', r'\g<1>ye', text)
            for cyr, lat in replacements:
                text = text.replace(cyr, lat)
            char_map = {
                'А': 'A', 'а': 'a', 'Б': 'B', 'б': 'b', 'В': 'V', 'в': 'v',
                'Г': 'G', 'г': 'g', 'Д': 'D', 'д': 'd', 'Е': 'E', 'е': 'e',
                'Ж': 'J', 'ж': 'j', 'З': 'Z', 'з': 'z', 'И': 'I', 'и': 'i',
                'Й': 'Y', 'й': 'y', 'К': 'K', 'к': 'k', 'Л': 'L', 'л': 'l',
                'М': 'M', 'м': 'm', 'Н': 'N', 'н': 'n', 'О': 'O', 'о': 'o',
                'П': 'P', 'п': 'p', 'Р': 'R', 'р': 'r', 'С': 'S', 'с': 's',
                'Т': 'T', 'т': 't', 'У': 'U', 'у': 'u', 'Ф': 'F', 'ф': 'f',
                'Х': 'X', 'х': 'x', 'Э': 'E', 'э': 'e', 'ъ': "'", 'Ъ': "'",
                'ь': '', 'Ь': ''
            }
            res = []
            for ch in text:
                res.append(char_map.get(ch, ch))
            return "".join(res)

        try:
            doc = docx.Document(path)
        except Exception as e:
            messagebox.showerror("Xato", f"Word hujjatini ochishda xatolik: {e}")
            return

        added_orgs_cnt = 0
        updated_orgs_cnt = 0
        added_people_cnt = 0
        updated_people_cnt = 0

        current_sector = "Umumiy soha"

        pos_suffixes = [
            "boshlig'i", "boshliqi", "boshlig'i v.b.", "rahbari", "direktori", "o'rinbosari",
            "mudiiri", "mudiri", "bosh yuriskonsulti", "bosh yurist", "mutaxassisi",
            "inspektori", "konsulti", "bosh muhandisi", "bosh shifokori", "maslahatchisi"
        ]

        for table in doc.tables:
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells]
                first_cell = ""
                for c in cells:
                    if c.strip():
                        first_cell = c.strip()
                        break
                
                first_cell_lat = cyrillic_to_latin(first_cell)
                if len(cells) < 3 or "masalalariga taalluqli" in first_cell_lat.lower() or "tashkilotlar" in first_cell_lat.lower() or "масалаларига" in first_cell.lower():
                    clean_sec = re.sub(r'masalalariga\s+taalluqli\s+tashkilotlar', '', first_cell_lat, flags=re.IGNORECASE).strip()
                    clean_sec = clean_sec.strip('",\'«» ')
                    if clean_sec and len(clean_sec) > 3:
                        current_sector = clean_sec
                    continue

                if len(cells) >= 3:
                    c1_name = cells[1].strip()
                    c2_pos = cells[2].strip()

                    if not c1_name or "Фамилияси" in c1_name or "вакант" in c1_name.lower() or "vakant" in c1_name.lower():
                        continue

                    name_lat = cyrillic_to_latin(c1_name).strip()
                    pos_lat = cyrillic_to_latin(c2_pos).strip()

                    # Organization Name = Clean Sector / Organization Category Header Banner
                    target_org_name = current_sector

                    # Keep name in exact original order without swapping words
                    first_name = name_lat
                    last_name = ""

                    # Full held position string from Column 2
                    full_position = pos_lat

                    existing_orgs = database.get_organizations()
                    found_org = None
                    for o in existing_orgs:
                        sim = difflib.SequenceMatcher(None, o[1].lower(), target_org_name.lower()).ratio()
                        if o[1].lower() == target_org_name.lower() or sim > 0.85:
                            found_org = o
                            break

                    org_name_to_use = target_org_name
                    if not found_org:
                        res = database.add_organization(target_org_name, sector=target_org_name)
                        if res:
                            added_orgs_cnt += 1
                    else:
                        org_name_to_use = found_org[1]
                        updated_orgs_cnt += 1

                    existing_people = database.get_people_by_org(org_name_to_use, 5)
                    found_person = None
                    for p in existing_people:
                        full_p_name = f"{p[1]} {p[2]}".strip().lower()
                        full_new_name = name_lat.lower()
                        sim = difflib.SequenceMatcher(None, full_p_name, full_new_name).ratio()
                        if full_p_name == full_new_name or sim > 0.85:
                            found_person = p
                            break

                    if found_person:
                        database.update_external_person(found_person[0], first_name, last_name, full_position, found_person[4] or "")
                        updated_people_cnt += 1
                    else:
                        database.add_external_person(first_name, last_name, org_name_to_use, full_position, "")
                        added_people_cnt += 1

        self.load_organizations()
        self.load_org_people()

        messagebox.showinfo(
            "Yuklash Yakunlandi",
            f"Word hujjatidan ma'lumotlar muvaffaqiyatli yuklandi!\n\n"
            f"🏢 Tashkilotlar: {added_orgs_cnt} ta yangi qo'shildi, {updated_orgs_cnt} ta aniqlandi.\n"
            f"👤 Xodimlar: {added_people_cnt} ta yangi qo'shildi, {updated_people_cnt} ta ma'lumotlari yangilandi."
        )

    def delete_all_organizations_action(self):
        from tkinter import messagebox
        if messagebox.askyesno("O'chirishni tasdiqlang", "ROSTDAN HAM BARCHA TASHKILOTLAR VA UNGA BIRIKTIRILGAN VAKILLARNI BAZADAN BUTUNLAY O'CHIRIB TASHLAMAKCHIMISIZ?\n\nBu amalni ortga qaytarib bo'lmaydi!"):
            database.delete_all_organizations()
            self.current_selected_org = None
            if hasattr(self, 'org_search_var'):
                self.org_search_var.set("")
            self.org_people_lbl.configure(text="Tashkilot tanlang")
            if hasattr(self, 'btn_add_org_person'):
                self.btn_add_org_person.configure(state="disabled")
            for w in self.org_people_grid.winfo_children(): w.destroy()
            self.load_organizations()
            self.load_org_people()
            messagebox.showinfo("Bajarildi", "Barcha tashkilotlar va xodimlar muvaffaqiyatli o'chirildi!")

    def open_add_meeting_modal(self):
        m = ctk.CTkToplevel(self)
        m.title("🤝 Yangi Majlis Ochish")
        m.geometry("550x700")
        m.resizable(False, False)
        m.configure(fg_color="#0f172a")
        m.transient(self)
        m.grab_set()
        
        container = ctk.CTkFrame(m, fg_color="#1e293b", corner_radius=15)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        ctk.CTkLabel(container, text="🤝 Yangi Majlis Ochish", font=("Roboto", 20, "bold"), text_color="white").pack(pady=(15, 5))
        ctk.CTkLabel(container, text="Majlis o'tkazish bo'yicha rasmiy ma'lumotlarni to'liq kiriting", font=("Roboto", 12), text_color="#94a3b8").pack()
        
        divider = ctk.CTkFrame(container, fg_color="#334155", height=1)
        divider.pack(fill="x", padx=20, pady=15)
        
        form_frame = ctk.CTkScrollableFrame(container, fg_color="transparent", height=450)
        form_frame.pack(fill="both", expand=True, padx=10)
        
        # Field 1
        ctk.CTkLabel(form_frame, text="1. Majlis Nomi / Mavzusi:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10, pady=(10, 0))
        title_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=title_var, placeholder_text="Masalan: Navbatdagi Kengash Yig'ilishi", width=450, height=35).pack(pady=(6, 12), padx=10)
        
        # Field 2
        ctk.CTkLabel(form_frame, text="2. Majlis Turi:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10)
        type_var = ctk.StringVar(value="Apparat yig'ilishi")
        ctk.CTkOptionMenu(form_frame, variable=type_var, values=["Apparat yig'ilishi", "Video-selektor", "Shoshilinch yig'ilish", "Sayyor qabul", "Kengash"], width=450, height=35).pack(pady=(6, 12), padx=10)
        
        # Field 3
        ctk.CTkLabel(form_frame, text="3. Sana va Boshlanish Vaqti:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10)
        dt_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=dt_var, placeholder_text="Masalan: 2026-07-15 | 10:00", width=450, height=35).pack(pady=(6, 12), padx=10)
        
        # Field 4
        ctk.CTkLabel(form_frame, text="4. O'tkazilish Joyi / Zal:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10)
        loc_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=loc_var, placeholder_text="Masalan: 3-qavat, Katta majlislar zali", width=450, height=35).pack(pady=(6, 12), padx=10)
        
        # Field 5
        ctk.CTkLabel(form_frame, text="5. Raislik Qiluvchi (Chairman):", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10)
        chair_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=chair_var, placeholder_text="Masalan: Viloyat Hokimi", width=450, height=35).pack(pady=(6, 12), padx=10)
        
        # Field 6
        ctk.CTkLabel(form_frame, text="6. Kun Tartibi va Qisqacha Mazmuni:", font=("Roboto", 13, "bold"), text_color="white").pack(anchor="w", padx=10)
        agenda_tb = ctk.CTkTextbox(form_frame, width=450, height=80, border_width=1, border_color="#334155")
        agenda_tb.pack(pady=(6, 12), padx=10)
        
        def save():
            t = title_var.get().strip()
            if not t: return
            
            d_val = dt_var.get().strip()
            if d_val:
                import re
                if not re.match(r'^\d{4}-\d{2}-\d{2}', d_val):
                    from tkinter import messagebox
                    messagebox.showerror("Xato", "Sana noto'g'ri formatda! Iltimos 'YYYY-MM-DD' formatida kiriting (Masalan: 2026-07-15 | 10:00)")
                    return
            
            ag = agenda_tb.get("1.0", "end-1c").strip()
            database.add_meeting(t, type_var.get(), d_val, loc_var.get(), chair_var.get(), ag)
            m.destroy()
            self.load_meetings()
            
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(btn_frame, text="Saqlash", command=save, fg_color="#059669", hover_color="#047857", font=("Roboto", 14, "bold"), text_color="white", width=200, height=40).pack(side="right", padx=(10, 30))
        ctk.CTkButton(btn_frame, text="Bekor qilish", command=m.destroy, fg_color="#475569", hover_color="#334155", font=("Roboto", 14), text_color="white", width=120, height=40).pack(side="right")

    def open_add_attendee_modal(self):
        if not self.current_selected_meeting_id:
            from tkinter import messagebox
            messagebox.showwarning("Ogohlantirish", "Iltimos, avval majlisni tanlang!")
            return

        m = ctk.CTkToplevel(self)
        m.title("Majlisga xodimlarni jalb qilish")
        m.geometry("750x550")
        m.configure(fg_color="#0f172a")
        m.transient(self)
        m.grab_set()
        
        container = ctk.CTkFrame(m, fg_color="#1e293b", corner_radius=15)
        container.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(container, text="📢 Majlisga xodimlarni jalb qilish / Chaqirish", font=("Roboto", 18, "bold"), text_color="white").pack(pady=(15, 5))
        
        orgs = database.get_organizations()
        org_names = [o[1] for o in orgs]
        org_names.insert(0, "(Ichki) Barcha xodimlar")
        internal_depts = database.get_internal_departments()
        for d in internal_depts:
            org_names.append(f"(Ichki) {d[1]}")
        
        top_frame = ctk.CTkFrame(container, fg_color="transparent")
        top_frame.pack(fill="x", padx=15, pady=10)
        
        selected_org = ctk.StringVar()
        if org_names: selected_org.set(org_names[0])
        
        om = ctk.CTkOptionMenu(top_frame, variable=selected_org, values=org_names, width=280, height=35)
        om.pack(side="left", padx=(0, 10))
        
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(top_frame, textvariable=search_var, placeholder_text="🔍 Ismi yoki familiyasi bo'yicha qidirish...", width=340, height=35)
        search_entry.pack(side="left", fill="x", expand=True)

        grid_frame = ctk.CTkScrollableFrame(container, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        def load_emp(*args):
            for w in grid_frame.winfo_children(): w.destroy()
            org = selected_org.get()
            q = search_var.get().strip().lower()
            
            people = database.get_people_by_org(org, self.current_user['access_level'])
            current_attendees = database.get_meeting_attendees(self.current_selected_meeting_id, self.current_user['access_level'])
            added_ids = {a[0] for a in current_attendees}
            
            count = 0
            for p in people:
                pid, fname, lname = p[0], p[1], p[2]
                pos = p[3] or "Lavozimsiz"
                fullname = f"{fname} {lname}".strip()
                
                if q and q not in fullname.lower() and q not in pos.lower():
                    continue
                
                count += 1
                f = ctk.CTkFrame(grid_frame, fg_color="#334155", corner_radius=8)
                f.pack(fill="x", pady=4, padx=2)
                
                info_box = ctk.CTkFrame(f, fg_color="transparent")
                info_box.pack(side="left", padx=12, pady=8, fill="x", expand=True)
                
                ctk.CTkLabel(info_box, text=fullname, font=("Roboto", 14, "bold"), text_color="white", anchor="w").pack(anchor="w")
                ctk.CTkLabel(info_box, text=pos, font=("Roboto", 12), text_color="#cbd5e1", anchor="w").pack(anchor="w")
                
                def add_this(person_id=pid, btn=None):
                    database.add_meeting_attendee(self.current_selected_meeting_id, person_id)
                    added_ids.add(person_id)
                    if btn and btn.winfo_exists():
                        btn.configure(text="Chaqirilgan ✅", fg_color="#059669", state="disabled")
                    self.load_meeting_attendees()
                
                if pid in added_ids:
                    ctk.CTkButton(f, text="Chaqirilgan ✅", width=120, fg_color="#059669", state="disabled", font=("Roboto", 12, "bold")).pack(side="right", padx=10, pady=8)
                else:
                    abtn = ctk.CTkButton(f, text="➕ Chaqirish", width=120, fg_color="#3b82f6", hover_color="#2563eb", font=("Roboto", 12, "bold"))
                    abtn.configure(command=lambda p_id=pid, b=abtn: add_this(p_id, b))
                    abtn.pack(side="right", padx=10, pady=8)

            if count == 0:
                ctk.CTkLabel(grid_frame, text="Xodimlar topilmadi", font=("Roboto", 14), text_color="#94a3b8").pack(pady=30)
                
        selected_org.trace("w", load_emp)
        search_var.trace("w", load_emp)
        if org_names: load_emp()

    def export_meeting_report(self):
        if not self.current_selected_meeting_id: return
        try:
            from tkinter import filedialog, messagebox, simpledialog
            import docx
            from docx.shared import Pt, Cm
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            from docx.enum.table import WD_TABLE_ALIGNMENT
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn
            import re
            
            def latin_to_cyrillic(text):
                if not text: return ""
                mapping = {
                    "Sh": "Ш", "sh": "ш", "Ch": "Ч", "ch": "ч",
                    "O'": "Ў", "o'": "ў", "G'": "Ғ", "g'": "ғ", "O‘": "Ў", "o‘": "ў", "G‘": "Ғ", "g‘": "ғ",
                    "Yo": "Ё", "yo": "ё", "Yu": "Ю", "yu": "ю", "Ya": "Я", "ya": "я",
                    "Ts": "Ц", "ts": "ц", "A": "А", "a": "а", "B": "Б", "b": "б",
                    "D": "Д", "d": "д", "E": "Е", "e": "е", "F": "Ф", "f": "ф",
                    "G": "Г", "g": "г", "H": "Ҳ", "h": "ҳ", "I": "И", "i": "и",
                    "J": "Ж", "j": "ж", "K": "К", "k": "к", "L": "Л", "l": "л",
                    "M": "М", "m": "м", "N": "Н", "n": "н", "O": "О", "o": "о",
                    "P": "П", "p": "п", "Q": "Қ", "q": "қ", "R": "Р", "r": "р",
                    "S": "С", "s": "с", "T": "Т", "t": "т", "U": "У", "u": "у",
                    "V": "В", "v": "в", "X": "Х", "x": "х", "Y": "Й", "y": "й",
                    "Z": "З", "z": "з", "'": "Ъ", "`": "Ъ"
                }
                text = re.sub(r'(^|\s)E', r'\g<1>Э', text)
                text = re.sub(r'(^|\s)e', r'\g<1>э', text)
                for lat, cyr in mapping.items():
                    text = text.replace(lat, cyr)
                return text

            meeting = database.get_meeting(self.current_selected_meeting_id)
            if not meeting: return
            
            m_title, m_date = meeting[1], meeting[3]
            
            month_names = ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust", "sentyabr", "oktyabr", "noyabr", "dekabr"]
            default_date_str = m_date
            try:
                date_part = m_date.split(" ")[0]
                y, m, d = date_part.split("-")
                default_date_str = f"{y} yil {int(d)} {month_names[int(m)-1]}"
            except: pass
            
            import customtkinter as ctk
            dialog = ctk.CTkInputDialog(text="Hujjat uchun majlis sanasini kiriting (Masalan: 2026 yil 24 mart):", title="Sana kiritish")
            user_date = dialog.get_input()
            
            if user_date is None: 
                return
            
            date_str = user_date.strip() if user_date.strip() else default_date_str
            date_str = latin_to_cyrillic(date_str)
            m_title = latin_to_cyrillic(m_title)
            
            attendees = database.get_meeting_attendees(self.current_selected_meeting_id, self.current_user['access_level'])
            
            path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word Document", "*.docx")], initialfile=f"Majlis_Royxati.docx")
            if not path: return
            
            doc = docx.Document()
            
            sections = doc.sections
            for section in sections:
                section.top_margin = Cm(1.5)
                section.bottom_margin = Cm(1.5)
                section.left_margin = Cm(1.5)
                section.right_margin = Cm(1.5)
                
            style = doc.styles['Normal']
            style.font.name = 'Times New Roman'
            style.font.size = Pt(14)
            
            header_para = doc.add_paragraph()
            header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r1 = header_para.add_run(latin_to_cyrillic("Tuman hokimligida ") + date_str + latin_to_cyrillic(" kuni o'tkazilgan\n"))
            r1.bold = True
            r2 = header_para.add_run(f"“{m_title}” " + latin_to_cyrillic("yig'ilishida ishtirok etish\n"))
            r2.bold = True
            r3 = header_para.add_run(latin_to_cyrillic("RO'YXATI"))
            r3.bold = True
            
            doc.add_paragraph()
            
            table = doc.add_table(rows=1, cols=4)
            table.style = 'Table Grid'
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.autofit = False
            
            def set_col_widths(tbl):
                widths = (Cm(1.0), Cm(7.2), Cm(8.0), Cm(1.8))
                try:
                    for i, w in enumerate(widths):
                        tbl.columns[i].width = w
                except: pass
                for row in tbl.rows:
                    for idx, width in enumerate(widths):
                        row.cells[idx].width = width

            def set_cell_bg(cell, hex_color):
                tcPr = cell._tc.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:val'), 'clear')
                shd.set(qn('w:color'), 'auto')
                shd.set(qn('w:fill'), hex_color)
                tcPr.append(shd)
                
            headers = ["№", latin_to_cyrillic("Familiyasi, ismi va otasining\nismi"), latin_to_cyrillic("Egallab turgan lavozimi"), latin_to_cyrillic("изоҳ")]
            hdr_cells = table.rows[0].cells
            for i in range(4):
                hdr_cells[i].text = headers[i]
                p = hdr_cells[i].paragraphs[0]
                p.runs[0].bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                set_cell_bg(hdr_cells[i], "92CDDC")
                
            set_col_widths(table)
                
            def add_attendee_row(a, idx):
                row_cells = table.add_row().cells
                row_cells[0].text = str(idx) + "."
                fullname = f"{a[2]} {a[1]} {a[7] if len(a) > 7 and a[7] else ''}".strip()
                row_cells[1].text = latin_to_cyrillic(fullname)
                row_cells[2].text = latin_to_cyrillic(a[3] or "")
                
                status_text = a[6]
                if "KELDI" in status_text.upper():
                    status_text = ""
                else:
                    status_text = re.sub(r'[^\w\s\-]', '', status_text).strip()
                    status_text = latin_to_cyrillic(status_text)
                
                row_cells[3].text = status_text
                
                alignments = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER]
                for j in range(4):
                    p = row_cells[j].paragraphs[0]
                    p.alignment = alignments[j]
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(0)

            internals = [a for a in attendees if len(a) > 8 and a[8] == 0]
            externals = [a for a in attendees if len(a) > 8 and a[8] == 1]
            
            # If for some reason index 8 is missing (e.g. old data or cache), fallback
            if not internals and not externals:
                internals = attendees

            from collections import defaultdict
            external_groups = defaultdict(list)
            for a in externals:
                group_name = a[9] if len(a) > 9 and a[9] else a[5]
                if not group_name: group_name = "Boshqa tashkilotlar"
                external_groups[group_name].append(a)

            counter = 1
            for a in internals:
                add_attendee_row(a, counter)
                counter += 1

            for group_name, group_attendees in external_groups.items():
                row = table.add_row()
                merged_cell = row.cells[0].merge(row.cells[-1])
                gn = latin_to_cyrillic(group_name)
                if "ташкилот" not in gn.lower() and "таълуқли" not in gn.lower():
                    gn += " масалаларига таълуқли ташкилотлар"
                merged_cell.text = gn
                p = merged_cell.paragraphs[0]
                p.runs[0].bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                set_cell_bg(merged_cell, "92CDDC")
                
                for a in group_attendees:
                    add_attendee_row(a, counter)
                    counter += 1

            set_col_widths(table)
                
            doc.save(path)
            messagebox.showinfo("Muvaffaqiyat", "Majlis ro'yxati (Word) krill alifbosida saqlandi!")
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Xato", f"Xatolik: {e}")

    def export_attendance_excel(self):
        from datetime import datetime as dt
        import calendar
        from tkinter import filedialog, messagebox

        month_str = self.attendance_month_var.get()
        try:
            year, month = map(int, month_str.split('-'))
        except:
            messagebox.showerror("Xato", "Noma'lum oy formati!")
            return

        num_days = calendar.monthrange(year, month)[1]

        workdays = []
        for d in range(1, num_days + 1):
            date_obj = dt(year, month, d)
            if date_obj.weekday() < 6: # Mon..Sat
                workdays.append(d)

        people_raw = database.get_all_people_full(self.current_user['access_level'])
        dept_filter = getattr(self, 'current_att_dept_filter', None)
        search_query = getattr(self, 'att_search_var', ctk.StringVar()).get().lower().strip()

        filtered_people = []
        for p in people_raw:
            pid, full_name, dept, pos = p[0], f"{p[1]} {p[2]}", p[8] or "", p[9] or ""
            if dept_filter and dept != dept_filter:
                continue
            if search_query and search_query not in full_name.lower():
                continue
            filtered_people.append((pid, full_name, dept, pos))

        if not filtered_people:
            messagebox.showwarning("Ogohlantirish", "Eksport qilish uchun xodimlar topilmadi!")
            return

        att_records = database.get_attendance_for_month(month_str)
        att_map = {(r[0], r[1]): r[2] for r in att_records}

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Fayl (*.xlsx)", "*.xlsx"), ("CSV Fayl (*.csv)", "*.csv")],
            initialfile=f"Davomat_{month_str}.xlsx",
            title="Davomat hisobotini saqlash"
        )
        if not path: return

        try:
            if path.endswith(".csv"):
                import csv
                with open(path, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.writer(f)
                    header = ["T/r", "F.I.O.", "Bo'lim", "Lavozim"] + [f"{d}-kun" for d in workdays] + ["Kelgan kunlar (+)", "Kelmagan kunlar (-)", "Ta'til/Sababli (L/S)", "Jami ish kunlari", "Davomat (%)"]
                    writer.writerow(header)

                    tot_p, tot_a, tot_l = 0, 0, 0
                    for idx, (pid, name, dept, pos) in enumerate(filtered_people, 1):
                        row = [idx, name, dept, pos]
                        p_cnt, a_cnt, l_cnt = 0, 0, 0
                        for d in workdays:
                            d_str = f"{month_str}-{d:02d}"
                            st = att_map.get((pid, d_str), "")
                            if st == "+":
                                row.append("+")
                                p_cnt += 1
                            elif st == "-":
                                row.append("-")
                                a_cnt += 1
                            elif st in ["L", "S"]:
                                row.append(st)
                                l_cnt += 1
                            else:
                                row.append("")
                        tot_w = len(workdays)
                        pct = f"{round((p_cnt / tot_w) * 100, 1)}%" if tot_w > 0 else "0%"
                        row.extend([p_cnt, a_cnt, l_cnt, tot_w, pct])
                        writer.writerow(row)

                        tot_p += p_cnt
                        tot_a += a_cnt
                        tot_l += l_cnt

                    tot_possible = len(filtered_people) * len(workdays)
                    overall_pct = f"{round((tot_p / tot_possible) * 100, 1)}%" if tot_possible > 0 else "0%"
                    writer.writerow([])
                    writer.writerow(["UMUMIY NATIJA", "", "", ""] + [""]*len(workdays) + [tot_p, tot_a, tot_l, tot_possible, overall_pct])
                messagebox.showinfo("Muvaffaqiyat", f"Davomat CSV shaklida muvaffaqiyatli saqlandi:\n{path}")

            else:
                import openpyxl
                from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = f"Davomat_{month_str}"

                ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4 + len(workdays) + 5)
                title_cell = ws.cell(row=1, column=1, value=f"HOKIMIYAT BOSHQARUV TIZIMI — DAVOMAT HISOBOTI ({month_str})")
                title_cell.font = Font(name="Arial", size=14, bold=True, color="FFFFFF")
                title_cell.fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
                title_cell.alignment = Alignment(horizontal="center", vertical="center")
                ws.row_dimensions[1].height = 40

                headers = ["T/r", "F.I.O.", "Bo'lim", "Lavozim"] + [f"{d}" for d in workdays] + ["Kelgan (+)", "Kelmagan (-)", "Ta'til/Sabab (L/S)", "Jami kun", "Foiz (%)"]
                ws.append([])
                ws.append(headers)
                
                header_fill = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid")
                header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
                thin_border = Border(left=Side(style='thin', color='CBD5E1'),
                                     right=Side(style='thin', color='CBD5E1'),
                                     top=Side(style='thin', color='CBD5E1'),
                                     bottom=Side(style='thin', color='CBD5E1'))

                for col_num, h in enumerate(headers, 1):
                    cell = ws.cell(row=3, column=col_num)
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = thin_border
                ws.row_dimensions[3].height = 25

                fill_green = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
                font_green = Font(name="Arial", size=11, color="065F46", bold=True)
                fill_red = PatternFill(start_color="FFE4E6", end_color="FFE4E6", fill_type="solid")
                font_red = Font(name="Arial", size=11, color="881337", bold=True)
                fill_yellow = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
                font_yellow = Font(name="Arial", size=11, color="92400E", bold=True)

                tot_p, tot_a, tot_l = 0, 0, 0
                for idx, (pid, name, dept, pos) in enumerate(filtered_people, 1):
                    r_idx = 3 + idx
                    row_data = [idx, name, dept, pos]
                    p_cnt, a_cnt, l_cnt = 0, 0, 0
                    day_statuses = []
                    for d in workdays:
                        d_str = f"{month_str}-{d:02d}"
                        st = att_map.get((pid, d_str), "")
                        if st == "+":
                            day_statuses.append("+")
                            p_cnt += 1
                        elif st == "-":
                            day_statuses.append("-")
                            a_cnt += 1
                        elif st in ["L", "S"]:
                            day_statuses.append(st)
                            l_cnt += 1
                        else:
                            day_statuses.append("")

                    tot_w = len(workdays)
                    pct = f"{round((p_cnt / tot_w) * 100, 1)}%" if tot_w > 0 else "0%"
                    full_row = row_data + day_statuses + [p_cnt, a_cnt, l_cnt, tot_w, pct]
                    ws.append(full_row)

                    for c_idx in range(1, len(full_row) + 1):
                        c = ws.cell(row=r_idx, column=c_idx)
                        c.border = thin_border
                        val = str(c.value or "")
                        if val == "+":
                            c.fill = fill_green; c.font = font_green; c.alignment = Alignment(horizontal="center")
                        elif val == "-":
                            c.fill = fill_red; c.font = font_red; c.alignment = Alignment(horizontal="center")
                        elif val in ["L", "S"]:
                            c.fill = fill_yellow; c.font = font_yellow; c.alignment = Alignment(horizontal="center")
                        elif c_idx > 4:
                            c.alignment = Alignment(horizontal="center")

                    tot_p += p_cnt
                    tot_a += a_cnt
                    tot_l += l_cnt

                # Summary Row
                tot_possible = len(filtered_people) * len(workdays)
                overall_pct = f"{round((tot_p / tot_possible) * 100, 1)}%" if tot_possible > 0 else "0%"
                sum_row_idx = 4 + len(filtered_people)
                
                sum_row = ["UMUMIY NATIJA", "", "", ""] + [""] * len(workdays) + [tot_p, tot_a, tot_l, tot_possible, overall_pct]
                ws.append(sum_row)

                sum_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
                sum_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
                for c_idx in range(1, len(sum_row) + 1):
                    c = ws.cell(row=sum_row_idx, column=c_idx)
                    c.fill = sum_fill
                    c.font = sum_font
                    c.border = thin_border
                    c.alignment = Alignment(horizontal="center" if c_idx > 4 else "left")

                ws.column_dimensions['A'].width = 6
                ws.column_dimensions['B'].width = 28
                ws.column_dimensions['C'].width = 22
                ws.column_dimensions['D'].width = 22
                for i in range(5, 5 + len(workdays)):
                    col_letter = openpyxl.utils.get_column_letter(i)
                    ws.column_dimensions[col_letter].width = 4
                for i in range(5 + len(workdays), 5 + len(workdays) + 5):
                    col_letter = openpyxl.utils.get_column_letter(i)
                    ws.column_dimensions[col_letter].width = 16

                wb.save(path)
                messagebox.showinfo("Muvaffaqiyat", f"Davomat hisoboti Excel fayliga muvaffaqiyatli saqlandi:\n{path}")
        except Exception as err:
            messagebox.showerror("Xato", f"Eksport qilishda xatolik: {err}")

    def build_attendance_content(self):
        from datetime import datetime
        self.attendance_frame.grid_rowconfigure(3, weight=1)
        self.attendance_frame.grid_columnconfigure(0, weight=1)
        
        kpi_container = ctk.CTkFrame(self.attendance_frame, fg_color="transparent")
        kpi_container.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 0))
        kpi_container.grid_columnconfigure((0,1,2,3), weight=1, uniform="kpi")

        self.att_kpi_percent = self.create_kpi_card(kpi_container, 0, "Bugungi Davomat", "0%", False)
        self.att_kpi_total = self.create_kpi_card(kpi_container, 1, "Jami Xodimlar", "0", False)
        self.att_kpi_absent = self.create_kpi_card(kpi_container, 2, "Kelmaganlar", "0", True)
        self.att_kpi_leave = self.create_kpi_card(kpi_container, 3, "Sababli/Ta'til", "0", False)

        header = ctk.CTkFrame(self.attendance_frame, fg_color="transparent")
        header.grid(row=1, column=0, sticky="ew", padx=30, pady=(20, 10))
        
        self.attendance_month_var = ctk.StringVar(value=datetime.now().strftime("%Y-%m"))
        ctk.CTkLabel(header, text="📅 Davomat (Keldi-Ketdi)", font=("Roboto", 24, "bold"), text_color="white").pack(side="left")
        
        self.att_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(header, textvariable=self.att_search_var, placeholder_text="Xodim ismini qidirish...", width=200)
        search_entry.pack(side="right", padx=10)
        search_entry.bind("<KeyRelease>", lambda e: self.load_attendance())
        
        now = datetime.now()
        months = []
        for i in range(-6, 3):
            m = now.month + i
            y = now.year
            while m < 1:
                m += 12
                y -= 1
            while m > 12:
                m -= 12
                y += 1
            months.append(f"{y}-{m:02d}")
            
        self.attendance_month_dropdown = ctk.CTkComboBox(header, variable=self.attendance_month_var, values=months, command=lambda e: self.load_attendance())
        self.attendance_month_dropdown.pack(side="right", padx=10)
        
        btn_att_export = ctk.CTkButton(header, text="📊 Excel Eksport", fg_color="#10b981", hover_color="#059669", font=("Roboto", 14, "bold"), height=35, command=self.export_attendance_excel)
        btn_att_export.pack(side="right", padx=10)
        
        self.att_dept_tabs_container = ctk.CTkScrollableFrame(self.attendance_frame, fg_color="transparent", height=50, orientation="horizontal")
        self.att_dept_tabs_container.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 10))
        
        self.att_grid_container = ctk.CTkScrollableFrame(self.attendance_frame, corner_radius=15, fg_color="#1e293b", border_width=1, border_color="#334155", orientation="vertical")
        self.att_grid_container.grid(row=3, column=0, sticky="nsew", padx=30, pady=(0, 20))
        
        self.att_summary_labels = {}
        self.att_cell_buttons = {}

    def get_badge_style(self, st):
        if st in ['+', '✅']: return {"text": "✔", "fg_color": "#065f46", "text_color": "#34d399", "hover_color": "#047857", "db_val": "+"}
        if st in ['-', '❌']: return {"text": "✖", "fg_color": "#881337", "text_color": "#fb7185", "hover_color": "#be123c", "db_val": "-"}
        if st in ['L', '🕒']: return {"text": "L", "fg_color": "#854d0e", "text_color": "#fcd34d", "hover_color": "#713f12", "db_val": "L"}
        if st in ['S', '🏖️']: return {"text": "V", "fg_color": "#1e3a8a", "text_color": "#93c5fd", "hover_color": "#1e40af", "db_val": "S"}
        return {"text": "·", "fg_color": "#1e293b", "text_color": "#94a3b8", "hover_color": "#334155", "db_val": ""}

    def render_att_dept_tabs(self):
        if not hasattr(self, 'current_att_dept_filter'):
            self.current_att_dept_filter = None
            
        for widget in self.att_dept_tabs_container.winfo_children():
            widget.destroy()
            
        depts = database.get_internal_departments()
        
        def set_filter(d_name):
            self.current_att_dept_filter = d_name
            self.load_attendance()
            
        btn_all = ctk.CTkButton(self.att_dept_tabs_container, text="Barchasi", corner_radius=8, width=100, height=35,
                                fg_color="#3b82f6" if self.current_att_dept_filter is None else "#1e293b",
                                text_color="white" if self.current_att_dept_filter is None else "#94a3b8",
                                command=lambda: set_filter(None))
        btn_all.pack(side="left", padx=5)
        
        for d in depts:
            d_name = d[1]
            btn = ctk.CTkButton(self.att_dept_tabs_container, text=d_name, corner_radius=8, height=35,
                                fg_color="#3b82f6" if self.current_att_dept_filter == d_name else "#1e293b",
                                text_color="white" if self.current_att_dept_filter == d_name else "#94a3b8",
                                command=lambda n=d_name: set_filter(n))
            btn.pack(side="left", padx=5)

    def load_attendance(self):
        self.render_att_dept_tabs()
            
        for widget in self.att_grid_container.winfo_children():
            widget.destroy()
            
        self.att_summary_labels.clear()
        self.att_cell_buttons.clear()

        month_str = self.attendance_month_var.get()
        today_str = datetime.now().strftime("%Y-%m-%d")
        if month_str == today_str[:7]:
            database.mark_absent_for_past_days(month_str, today_str)
            
        from datetime import datetime as dt
        import calendar
        
        year, month = map(int, month_str.split('-'))
        num_days = calendar.monthrange(year, month)[1]
        
        workdays = []
        for d in range(1, num_days + 1):
            date_obj = dt(year, month, d)
            if date_obj.weekday() < 6:
                workdays.append(d)
                
        header_frame = ctk.CTkFrame(self.att_grid_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(5, 10))
        
        ctk.CTkLabel(header_frame, text="ID", width=40, font=("Roboto", 12, "bold"), text_color="#94a3b8").pack(side="left", padx=2)
        ctk.CTkLabel(header_frame, text="F.I.SH & Lavozim", width=220, font=("Roboto", 12, "bold"), text_color="#94a3b8", anchor="w").pack(side="left", padx=(5, 10))
        
        for d in workdays:
            ctk.CTkLabel(header_frame, text=str(d), width=35, font=("Roboto", 12, "bold"), text_color="#94a3b8").pack(side="left", padx=1)
            
        ctk.CTkLabel(header_frame, text="Keldi", width=50, font=("Roboto", 12, "bold"), text_color="#34d399").pack(side="left", padx=(10, 2))
        ctk.CTkLabel(header_frame, text="Kelmadi", width=60, font=("Roboto", 12, "bold"), text_color="#fb7185").pack(side="left", padx=2)
        ctk.CTkLabel(header_frame, text="Foiz %", width=50, font=("Roboto", 12, "bold"), text_color="#60a5fa").pack(side="left", padx=2)
        
        if getattr(self, 'current_att_dept_filter', None):
            people = database.get_people(self.current_user['access_level'], 1, self.current_att_dept_filter)
        else:
            people = database.get_people(self.current_user['access_level'], 1)
            
        search_q = self.att_search_var.get().lower()
        if search_q:
            people = [p for p in people if search_q in f"{p[1]} {p[2]}".lower()]

        att_data = database.get_attendance(month_str)
        att_dict = {}
        for row in att_data:
            pid, dstr, st = row
            d = int(dstr.split('-')[2])
            if pid not in att_dict: att_dict[pid] = {}
            att_dict[pid][d] = st
            
        for p in people:
            pid = p[0]
            fname = f"{p[1]} {p[2]} | {p[3]}"
            
            row_frame = ctk.CTkFrame(self.att_grid_container, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row_frame, text=str(pid), width=40, text_color="#cbd5e1").pack(side="left", padx=2)
            name_lbl = ctk.CTkLabel(row_frame, text=fname, width=220, text_color="white", anchor="w")
            name_lbl.pack(side="left", padx=(5, 10))
            
            present_c = 0
            absent_c = 0
            leave_c = 0
            
            for d in workdays:
                st = att_dict.get(pid, {}).get(d, "")
                style = self.get_badge_style(st)
                
                if style["db_val"] == "+": present_c += 1
                elif style["db_val"] == "-": absent_c += 1
                elif style["db_val"] in ["L", "S"]: leave_c += 1
                
                btn = ctk.CTkButton(row_frame, text=style["text"], width=35, height=30, corner_radius=6, 
                                    font=("Roboto", 14, "bold"),
                                    fg_color=style["fg_color"], text_color=style["text_color"], hover_color=style["hover_color"])
                btn.pack(side="left", padx=1)
                
                date_str = f"{year}-{month:02d}-{d:02d}"
                btn.configure(command=lambda e_pid=pid, e_dstr=date_str, e_btn=btn: self.on_att_single_click(e_pid, e_dstr, e_btn))
                btn.bind("<Double-Button-1>", lambda event, e_pid=pid, e_dstr=date_str, e_btn=btn: self.on_att_double_click(e_pid, e_dstr, e_btn))
                
                self.att_cell_buttons[(pid, date_str)] = btn
                btn._db_val = style["db_val"]
                
            total_days = present_c + absent_c + leave_c
            percent = int((present_c / total_days) * 100) if total_days > 0 else 0
            
            lbl_p = ctk.CTkLabel(row_frame, text=str(present_c), width=50, font=("Roboto", 13, "bold"), text_color="#34d399")
            lbl_p.pack(side="left", padx=(10, 2))
            lbl_a = ctk.CTkLabel(row_frame, text=str(absent_c), width=60, font=("Roboto", 13, "bold"), text_color="#fb7185")
            lbl_a.pack(side="left", padx=2)
            lbl_pct = ctk.CTkLabel(row_frame, text=f"{percent}%", width=50, font=("Roboto", 13, "bold"), text_color="#60a5fa")
            lbl_pct.pack(side="left", padx=2)
            
            self.att_summary_labels[pid] = (lbl_p, lbl_a, lbl_pct)

        self.update_top_kpis()

    def update_top_kpis(self):
        month_str = self.attendance_month_var.get()
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        people = database.get_people(self.current_user['access_level'], 1)
        att_data = database.get_attendance(month_str)
        
        today_present = 0
        today_absent = 0
        today_leave = 0
        
        if month_str == today_str[:7]:
            today_day = int(today_str.split('-')[2])
            for row in att_data:
                pid, dstr, st = row
                d = int(dstr.split('-')[2])
                if d == today_day:
                    if st in ['+', '✅']: today_present += 1
                    elif st in ['-', '❌']: today_absent += 1
                    elif st in ['S', '🏖️', 'L', '🕒']: today_leave += 1
        
        total_employees = len(people)
        self.att_kpi_total.winfo_children()[1].configure(text=str(total_employees))
        
        if month_str == today_str[:7] and total_employees > 0:
            today_percent = int((today_present / total_employees) * 100)
            self.att_kpi_percent.winfo_children()[1].configure(text=f"{today_percent}%")
            self.att_kpi_absent.winfo_children()[1].configure(text=str(today_absent))
            self.att_kpi_leave.winfo_children()[1].configure(text=str(today_leave))
        else:
            self.att_kpi_percent.winfo_children()[1].configure(text="-")
            self.att_kpi_absent.winfo_children()[1].configure(text="-")
            self.att_kpi_leave.winfo_children()[1].configure(text="-")

    def on_att_single_click(self, pid, date_str, btn):
        current_val = getattr(btn, '_db_val', "")
        if current_val == "+":
            new_val = "-"
        else:
            new_val = "+"
        self.update_btn_and_db(pid, date_str, btn, new_val)

    def on_att_double_click(self, pid, date_str, btn):
        current_val = getattr(btn, '_db_val', "")
        
        if current_val == "+": new_val = "-"
        elif current_val == "-": new_val = "L"
        elif current_val == "L": new_val = "S"
        else: new_val = "+"
            
        self.update_btn_and_db(pid, date_str, btn, new_val)

    def update_btn_and_db(self, pid, date_str, btn, new_val):
        if self.current_user['access_level'] < 5:
            from tkinter import messagebox
            messagebox.showerror("Xato", "Sizda ma'lumotlarni o'zgartirish huquqi yo'q!")
            return
            
        database.set_attendance(pid, date_str, new_val)
        style = self.get_badge_style(new_val)
        btn.configure(text=style["text"], fg_color=style["fg_color"], text_color=style["text_color"], hover_color=style["hover_color"])
        btn._db_val = new_val
        self.recalc_person_summary(pid, date_str[:7])
        self.update_top_kpis()

    def recalc_person_summary(self, pid, month_str):
        if pid not in self.att_summary_labels: return
        
        from datetime import datetime as dt
        import calendar
        year, month = map(int, month_str.split('-'))
        num_days = calendar.monthrange(year, month)[1]
        
        present_c = 0
        absent_c = 0
        leave_c = 0
        
        for d in range(1, num_days + 1):
            dstr = f"{year}-{month:02d}-{d:02d}"
            if (pid, dstr) in self.att_cell_buttons:
                val = getattr(self.att_cell_buttons[(pid, dstr)], '_db_val', "")
                if val == "+": present_c += 1
                elif val == "-": absent_c += 1
                elif val in ["L", "S"]: leave_c += 1
                
        total_days = present_c + absent_c + leave_c
        percent = int((present_c / total_days) * 100) if total_days > 0 else 0
        
        lbl_p, lbl_a, lbl_pct = self.att_summary_labels[pid]
        lbl_p.configure(text=str(present_c))
        lbl_a.configure(text=str(absent_c))
        lbl_pct.configure(text=f"{percent}%")
    def build_settings_content(self):
        self.settings_frame.grid_rowconfigure(1, weight=1)
        self.settings_frame.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        
        ctk.CTkLabel(header, text="Tizim Foydalanuvchilari (Accounts)", font=("Roboto", 24, "bold"), text_color="white").pack(side="left")
        ctk.CTkButton(header, text="➕ Yangi Foydalanuvchi Qo'shish", fg_color="#10b981", hover_color="#059669", font=("Roboto", 14, "bold"), height=40, command=self.open_user_modal).pack(side="right")
        
        self.users_tree_container = ctk.CTkFrame(self.settings_frame, corner_radius=15, fg_color="#1e293b", border_width=1, border_color="#334155")
        self.users_tree_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self.users_tree_container.grid_rowconfigure(0, weight=1)
        self.users_tree_container.grid_columnconfigure(0, weight=1)

        self.users_tree = ttk.Treeview(self.users_tree_container, show='headings', selectmode="browse")
        self.users_tree['columns'] = ('id', 'username', 'role', 'level', 'action')
        self.users_tree.heading('id', text='ID')
        self.users_tree.heading('username', text='LOGIN')
        self.users_tree.heading('role', text='ROL')
        self.users_tree.heading('level', text='RUXSAT (LEVEL)')
        self.users_tree.heading('action', text='AMALLAR')
        
        self.users_tree.column('id', width=60, anchor='center')
        self.users_tree.column('username', width=200)
        self.users_tree.column('role', width=200)
        self.users_tree.column('level', width=120, anchor='center')
        self.users_tree.column('action', width=150, anchor='center')
        
        self.users_tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.users_tree.bind('<Double-1>', self.on_user_dbl_click)
        
        scroll = ttk.Scrollbar(self.users_tree_container, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscroll=scroll.set)
        scroll.grid(row=0, column=1, sticky='ns')

    def load_users(self):
        for item in self.users_tree.get_children(): self.users_tree.delete(item)
        users = database.get_all_users()
        for u in users:
            action_text = "(Ikki marta bosing)"
            self.users_tree.insert('', 'end', values=(u[0], u[1], u[2], u[3], action_text))

    def on_user_dbl_click(self, event):
        sel = self.users_tree.selection()
        if not sel: return
        u_id = self.users_tree.item(sel)['values'][0]
        u_data = database.get_user_by_id(u_id)
        if u_data:
            self.open_user_modal(u_data)

    def open_user_modal(self, user_data=None):
        if self.current_user['access_level'] < 3 and user_data and user_data[3] >= 3:
            messagebox.showerror("Xato", "Siz Super Admin ma'lumotlarini o'zgartira olmaysiz!")
            return

        m = ctk.CTkToplevel(self)
        m.title("Foydalanuvchini Tahrirlash" if user_data else "Yangi Foydalanuvchi")
        m.geometry("500x550")
        m.configure(fg_color="#1e293b")
        m.grab_set()

        ctk.CTkLabel(m, text="Akkaunt Sozlamalari", font=("Roboto", 20, "bold")).pack(pady=20)

        ctk.CTkLabel(m, text="Login:").pack(anchor="w", padx=40)
        l_ent = ctk.CTkEntry(m, width=420, height=35)
        if user_data: 
            l_ent.insert(0, user_data[1])
            l_ent.configure(state="disabled")
        l_ent.pack(pady=(0,15))

        if not user_data:
            ctk.CTkLabel(m, text="Parol:").pack(anchor="w", padx=40)
            p_ent = ctk.CTkEntry(m, width=420, height=35, show="*")
            p_ent.pack(pady=(0,15))

        ctk.CTkLabel(m, text="Rol (Masalan: Kuzatuvchi, HR, Admin):").pack(anchor="w", padx=40)
        r_ent = ctk.CTkEntry(m, width=420, height=35)
        if user_data: r_ent.insert(0, user_data[2])
        r_ent.pack(pady=(0,15))

        ctk.CTkLabel(m, text="Ruxsat Darajasi (Level 1 - 3):").pack(anchor="w", padx=40)
        lvl_ent = ctk.CTkEntry(m, width=420, height=35)
        if user_data: lvl_ent.insert(0, str(user_data[3]))
        lvl_ent.pack(pady=(0,20))

        def save_u():
            try:
                lvl = int(lvl_ent.get())
                if not user_data:
                    res = database.add_user(l_ent.get(), p_ent.get(), r_ent.get(), lvl)
                    if not res:
                        messagebox.showerror("Xato", "Bu login band!")
                        return
                else:
                    database.update_user_role(user_data[0], r_ent.get(), lvl)
                self.load_users()
                m.destroy()
            except ValueError:
                messagebox.showerror("Xato", "Level faqat son bo'lishi kerak!")

        def delete_u():
            if user_data[1] == 'admin':
                messagebox.showerror("Xato", "Asosiy adminni o'chirib bo'lmaydi!")
                return
            if messagebox.askyesno("Tasdiqlash", "Haqiqatan ham o'chirasizmi?"):
                database.delete_user(user_data[0])
                self.load_users()
                m.destroy()

        btns = ctk.CTkFrame(m, fg_color="transparent")
        btns.pack(pady=10)
        
        ctk.CTkButton(btns, text="Saqlash", command=save_u, fg_color="#10b981", height=40).pack(side="left", padx=10)
        if user_data:
            ctk.CTkButton(btns, text="O'chirish", command=delete_u, fg_color="#ef4444", height=40).pack(side="left", padx=10)


    def logout(self):
        self.main_container.grid_forget()
        self.login_container.grid(row=0, column=0, sticky="nsew")
        self.current_user = None

    def export_to_docx(self, person, images):
        path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word Document", "*.docx")], title="Ma'lumotnomani saqlash")
        if not path: return
        
        try:
            import docx
            from docx.shared import Inches, Pt
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            from docx.enum.table import WD_TABLE_ALIGNMENT
            import tempfile
            import os

            doc = docx.Document()
            
            head = doc.add_heading("🏛️ HOKIMIYAT BOSHQARUV TIZIMI", level=1)
            head.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            title = doc.add_paragraph()
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = title.add_run("XODIM HAQIDA RASMIY MA'LUMOTNOMA\n(SHAXSIY VARAQA)")
            run.bold = True
            run.font.size = Pt(16)
            
            sub = doc.add_paragraph()
            sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
            sub_run = sub.add_run("SHAXSIY MA'LUMOTLAR")
            sub_run.bold = True
            sub_run.font.size = Pt(12)
            
            table = doc.add_table(rows=1, cols=2)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            cell_pic = table.cell(0,0)
            cell_info = table.cell(0,1)
            
            if images and images[0]:
                tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                tmp_img.write(images[0])
                tmp_img.close()
                p = cell_pic.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run()
                r.add_picture(tmp_img.name, width=Inches(1.5))
                os.unlink(tmp_img.name)
            else:
                cell_pic.text = "Rasm yuklanmagan"
                
            fname = f"{person[1]} {person[2]}"
            pos = person[9] or "Noma'lum"
            dept = person[21] or ""
            joined = person[11] or ""
            kpi = person[25] or 0
            status = "FAOL" if person[18]==1 else "BO'SHAGAN"
            
            info_text = f"F.I.SH.: {fname}\n"
            info_text += f"Asosiy Lavozimi: {pos} ({dept})\n"
            info_text += f"Status: {status}\n"
            info_text += f"Ishga kirgan sanasi: {joined}\n"
            info_text += f"Samaradorlik (KPI): {kpi}%"
            
            cell_info.text = info_text
            
            doc.add_paragraph("\n")
            
            h1 = doc.add_paragraph()
            h1.add_run("JADVAL 1: SHAXSIY VA ALOQA MA'LUMOTLARI").bold = True
            
            t1 = doc.add_table(rows=4, cols=4)
            t1.style = 'Table Grid'
            t1.cell(0,0).text = "JSHSHIR"
            t1.cell(0,1).text = person[5] or "-"
            t1.cell(0,2).text = "Yashash manzili"
            t1.cell(0,3).text = person[7] or "-"
            
            t1.cell(1,0).text = "Tug'ilgan sana"
            t1.cell(1,1).text = person[6] or "-"
            t1.cell(1,2).text = "Oila ahvoli"
            t1.cell(1,3).text = person[20] or "-"
            
            t1.cell(2,0).text = "Telefon"
            t1.cell(2,1).text = person[8] or "-"
            t1.cell(2,2).text = "Pasport"
            t1.cell(2,3).text = person[4] or "-"
            
            t1.cell(3,0).text = "E-pochta"
            t1.cell(3,1).text = person[19] or "-"
            t1.cell(3,2).text = ""
            t1.cell(3,3).text = ""
            
            doc.add_paragraph("\n")
            
            h2 = doc.add_paragraph()
            h2.add_run("JADVAL 2: KASBIY FAOLIYAT, MALAKA VA YUTUQLAR").bold = True
            
            t2 = doc.add_table(rows=5, cols=2)
            t2.style = 'Table Grid'
            t2.cell(0,0).text = "Til bilish darajasi"
            t2.cell(0,1).text = person[22] or "-"
            
            t2.cell(1,0).text = "Malaka oshirish"
            t2.cell(1,1).text = person[23] or "-"
            
            t2.cell(2,0).text = "Asosiy loyihalari va yutuqlari"
            t2.cell(2,1).text = person[24] or "-"
            
            vac = "-"
            if person[13] and person[14]: vac = f"{person[13]} dan {person[14]} gacha"
            t2.cell(3,0).text = "Tizimdagi oxirgi ta'tili"
            t2.cell(3,1).text = vac
            
            punish = "-"
            if person[17]: punish = f"{person[17]} ({person[15]} - {person[16] or 'muddatsiz'})"
            t2.cell(4,0).text = "Intizomiy jazolari / Incident"
            t2.cell(4,1).text = punish
            
            doc.add_paragraph("\n")
            
            doc.add_paragraph("TASDIQLASH").runs[0].bold = True
            doc.add_paragraph("Bo'lim boshlig'i: _________________________ / (F.I.SH.)")
            doc.add_paragraph("Kadrlar bo'limi mas'uli: __________________ / (F.I.SH.)")
            doc.add_paragraph(f"Sana: ___ _________ {datetime.now().year} yil. (M.O'.)")
            
            doc.save(path)
            messagebox.showinfo("Muvaffaqiyat", "Ma'lumotnoma saqlandi!")
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Xato", f"Xatolik yuz berdi: {str(e)}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
