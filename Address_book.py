import json
import re
import tkinter as tk
from tkinter import ttk
import os
import sys


class Interface:
    def __init__(self, address_book):
        self.address_book = address_book
        self.main_window = tk.Tk()
        self.main_window.title("Address Book")

        window_width = 750
        window_height = 550
        screen_width = self.main_window.winfo_screenwidth()
        screen_height = self.main_window.winfo_screenheight()
        w = (screen_width - window_width) // 2
        h = (screen_height - window_height) // 2
        self.main_window.geometry(f"{window_width}x{window_height}+{w}+{h}")

        self.build_treeview_interface()

    def build_treeview_interface(self):
        tk.Label(self.main_window, text="ADDRESS BOOK LIST",
                 font=("Arial", 18), fg="navy", bg="gainsboro").pack(pady=20, ipady=5, fill="x")

        search_frame = tk.Frame(self.main_window)
        search_frame.pack()
        search_label = tk.Label(search_frame, text="Search: ", font=("Segoe UI", 11))
        search_label.pack(side="left")
        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 12), width=30)
        self.search_entry.pack(side="left")

        self.search_entry.bind("<KeyRelease>", lambda event: self.treeview_search_results())

        self.treeview_contacts = ttk.Treeview(self.main_window,
                                              show="headings", columns=("c1", "c2", "c3", "c4", "c5"))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 12), foreground="dark blue")
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=30,
                        foreground="black", background="floral white", fieldbackground="floral white")
        style.map("Treeview", foreground=[("selected", "black")], background=[("selected", "powder blue")])

        self.treeview_contacts.heading("c1", text="Name", anchor="w")
        self.treeview_contacts.heading("c2", text="Middle Name", anchor="w")
        self.treeview_contacts.heading("c3", text="Phone (Mobile)", anchor="w")
        self.treeview_contacts.heading("c4", text="Email", anchor="w")
        self.treeview_contacts.heading("c5", text="")
        self.treeview_contacts.column("c1", width=100)
        self.treeview_contacts.column("c2", width=100)
        self.treeview_contacts.column("c3", width=100)
        self.treeview_contacts.column("c4", width=100)
        self.treeview_contacts.column("c5", width=0, stretch=False)
        self.treeview_contacts.pack(side="top", fill="both", expand=True, pady=(20, 0))

        self.refresh_treeview_contacts()

        btn_frame = tk.Frame(self.main_window)
        btn_frame.pack()
        add_button = tk.Button(btn_frame, text="ADD",
                               font=("Verdana", 11), command=lambda: self.build_add_edit_interface("add"), width=6)
        add_button.pack(side="left", padx=20, pady=20)

        self.edit_button = tk.Button(btn_frame, text="EDIT", font=("Verdana", 11), state="disabled", width=6,
                                     command=lambda: self.build_add_edit_interface("edit"))
        self.edit_button.pack(side="left", padx=20, pady=20)

        self.delete_button = tk.Button(btn_frame, text="DELETE", font=("Verdana", 11), state="disabled", width=6,
                                       command=self.confirm_delete_contact_selected)
        self.delete_button.pack(side="left", padx=20, pady=20)

        exit_button = tk.Button(btn_frame, text="EXIT", font=("Verdana", 11), command=self.main_window_exit, width=6)
        exit_button.pack(side="right", padx=20, pady=20)

        self.main_window.bind("<Delete>", lambda event: self.confirm_delete_contact_selected())
        self.treeview_contacts.bind("<<TreeviewSelect>>", self.on_contact_selected)
        self.main_window.bind("<Escape>", lambda event: self.main_window_exit())

    def build_add_edit_interface(self, mode):
        self.mode = mode
        if mode == "add":
            self.treeview_contacts.selection_remove(self.treeview_contacts.selection())
        contact_selected = self.get_contact_selected()
        if mode == "add" or mode == "edit" and contact_selected:
            self.main_window.withdraw()
            self.add_edit_window = tk.Toplevel(self.main_window)
            self.add_edit_window.title("Address Book")

            add_edit_window_width = 550
            add_edit_window_height = 340
            self.main_window.update_idletasks()
            parent_width = self.main_window.winfo_width()
            parent_height = self.main_window.winfo_height()
            parent_x = self.main_window.winfo_x()
            parent_y = self.main_window.winfo_y()
            w = parent_x + (parent_width - add_edit_window_width) // 2
            h = parent_y + (parent_height - add_edit_window_height) // 2
            self.add_edit_window.geometry(f"{add_edit_window_width}x{add_edit_window_height}+{w}+{h}")

            self.add_edit_window_title = tk.Label(self.add_edit_window, text="",
                                                  font=("Arial", 18), fg="navy", bg="gainsboro")
            self.add_edit_window_title.pack(pady=20, ipady=5, fill="x")
            if mode == "add":
                self.add_edit_window_title.config(text="ADD CONTACT")

            name_frame = tk.Frame(self.add_edit_window)
            name_frame.pack()
            name_label = tk.Label(name_frame, text="Name *  ",
                                  font=("Segoe UI", 11), anchor="e", width=22)
            name_label.pack(side="left", pady=10)
            self.name_entry = tk.Entry(name_frame, font=("Segoe UI", 11), width=30)
            self.name_entry.pack(side="right", pady=(0, 10))
            self.name_entry.focus_force()

            middle_name_frame = tk.Frame(self.add_edit_window)
            middle_name_frame.pack()
            middle_name_label = tk.Label(middle_name_frame, text="Middle Name (optional)   ",
                                         font=("Segoe UI", 11), anchor="e", width=22)
            middle_name_label.pack(side="left", pady=10)
            self.middle_name_entry = tk.Entry(middle_name_frame, font=("Segoe UI", 11), width=30)
            self.middle_name_entry.pack(side="right", pady=10)

            phone_frame = tk.Frame(self.add_edit_window)
            phone_frame.pack()
            phone_label = tk.Label(phone_frame, text="Phone *  ", font=("Segoe UI", 11), anchor="e", width=22)
            phone_label.pack(side="left", pady=10)
            self.phone_entry = tk.Entry(phone_frame, font=("Segoe UI", 11), width=30)
            self.phone_entry.pack(side="right", pady=10)

            email_frame = tk.Frame(self.add_edit_window)
            email_frame.pack()
            email_label = tk.Label(email_frame, text="Email (optional)   ", font=("Segoe UI", 11), anchor="e", width=22)
            email_label.pack(side="left", pady=10)
            self.email_entry = tk.Entry(email_frame, font=("Segoe UI", 11), width=30)
            self.email_entry.pack(side="right", pady=10)

            btn_frame = tk.Frame(self.add_edit_window)
            btn_frame.pack()

            save_button = tk.Button(btn_frame, text="SAVE", font=("Verdana", 11), width=5,
                                    command=self.save_contact)
            save_button.pack(side="left", padx=20, pady=20)

            close_button = tk.Button(btn_frame, text="CLOSE", font=("Verdana", 11), width=5,
                                     command=self.add_edit_window_close)
            close_button.pack(side="right", padx=20, pady=20)

            if mode == "edit" and contact_selected:
                self.add_edit_window_title.config(text="EDIT CONTACT")
                item = self.treeview_contacts.item(contact_selected[0])["values"]
                name = item[0]
                middle_name = item[1]
                phone = item[2]
                email = item[3]
                self.name_entry.insert(0, name)
                self.middle_name_entry.insert(0, middle_name)
                self.phone_entry.insert(0, phone)
                if "@" in email:
                    self.email_entry.insert(0, email)
                else:
                    self.email_entry.insert(0, "")

            self.add_edit_window.bind("<Return>", lambda event: self.save_contact())
            self.add_edit_window.bind("<Escape>", lambda event: self.add_edit_window_close())
            self.add_edit_window.protocol("WM_DELETE_WINDOW", self.add_edit_window_close)

    def build_alert_window(self):
        self.alert_window = tk.Toplevel(self.main_window)
        self.alert_window.title("Alert")

        alert_window_width = 350
        alert_window_height = 110
        self.main_window.update_idletasks()
        parent_width = self.main_window.winfo_width()
        parent_height = self.main_window.winfo_height()
        parent_x = self.main_window.winfo_x()
        parent_y = self.main_window.winfo_y()
        w = parent_x + (parent_width - alert_window_width) // 2
        h = parent_y + (parent_height - alert_window_height) // 2
        self.alert_window.geometry(f"{alert_window_width}x{alert_window_height}+{w}+{h}")

        self.alert_label = tk.Label(self.alert_window, text="", font=("Segoe UI", 12))
        self.alert_label.pack(pady=10)
        self.alert_close_button = tk.Button(self.alert_window, text="Close",
                                            font=("Verdana", 12), command=self.alert_window_close)
        self.alert_close_button.pack(pady=10)

        self.alert_window.bind("<Delete>", lambda event: self.alert_window_close())
        self.alert_window.bind("<Return>", lambda event: self.alert_window_close())
        self.alert_window.bind("<Escape>", lambda event: self.alert_window_close())

        self.alert_window.focus_force()
        self.alert_window.grab_set()

    def on_contact_selected(self, event):
        contact_selected = self.get_contact_selected()
        if contact_selected:
            self.edit_button.config(state="normal")
            self.delete_button.config(state="normal")
        else:
            self.edit_button.config(state="disabled")
            self.delete_button.config(state="disabled")

    def save_contact(self):
        name = self.name_entry.get()
        name = name.title()
        middle_name = self.middle_name_entry.get()
        middle_name = middle_name.title()
        phone = self.phone_entry.get()
        email = self.email_entry.get()

        is_valid = self.entry_validation(name, phone, email, middle_name)
        if not is_valid:
            return
        if not email:
            email = "Not Available"

        if self.mode == "add":
            self.address_book.add_contact(name, middle_name, phone, email)

        elif self.mode == "edit":
            contact_selected_id = self.get_contact_selected_id()
            self.address_book.edit_contact(name, middle_name, phone, email, contact_selected_id)

        self.refresh_treeview_contacts()
        self.treeview_contacts.selection_remove(self.treeview_contacts.selection())
        self.add_edit_window_close()

    def confirm_delete_contact_selected(self):
        self.build_alert_window()
        self.alert_label.config(text="Delete contact selected?")
        self.alert_close_button.pack_forget()

        frame_btn = tk.Frame(self.alert_window)
        frame_btn.pack()

        yes_delete_button = tk.Button(frame_btn, text="YES", width=5,
                                      font=("Segoe UI", 11), command=self.delete_contact_selected)
        yes_delete_button.pack(pady=5, padx=20, side="left")

        no_delete_button = tk.Button(frame_btn, text="NO", width=5,
                                     font=("Segoe UI", 11), command=self.alert_window_close)
        no_delete_button.pack(pady=5, padx=20, side="right")

        self.alert_window.bind("<Return>", lambda event: self.delete_contact_selected())

    def delete_contact_selected(self):
        self.alert_window_close()
        contact_selected_id = self.get_contact_selected_id()
        self.address_book.delete_contact(contact_selected_id)
        self.refresh_treeview_contacts()

    def entry_validation(self, name, phone, email, middle_name):
        required_fields = (name, phone)
        if not all(required_fields):
            self.build_alert_window()
            self.alert_label.config(text="Please fill in all required fields!")

            return False

        for contact in self.address_book.contacts_list:
            if (contact["name"] == name and contact["middle name"] == middle_name
                    and contact["phone"] == phone and contact["email"] == email):
                self.build_alert_window()
                self.alert_label.config(text="Duplicate contact!")
                return False

        regex_phone = re.match(r"^\d{3,4}$|^\d{9,10}$", phone)
        if phone:
            if not regex_phone:
                self.build_alert_window()
                self.alert_label.config(text="Invalid phone number!")
                return False

        regex_email = re.match(r"^[a-zA-Z\d]+[._]?[a-zA-Z\d]+[._]?[a-zA-Z\d]+@[a-zA-Z]+\.[a-z]{2,}$", email)
        if email:
            if not regex_email:
                self.build_alert_window()
                self.alert_label.config(text="Invalid email address!")
                return False
        return True

    def treeview_search_results(self):
        search_text = self.search_entry.get()
        search_text = search_text.lower()
        search_results = self.address_book.search_contact(search_text)
        for item in self.treeview_contacts.get_children():
            self.treeview_contacts.delete(item)
        for contact in search_results:
            self.treeview_contacts.insert("", "end", values=(contact["name"], contact["middle name"],
                                                             contact["phone"], contact["email"], contact["id"]))

    def refresh_treeview_contacts(self):
        for item in self.treeview_contacts.get_children():
            self.treeview_contacts.delete(item)
        for contact in self.address_book.contacts_list:
            self.treeview_contacts.insert("", "end", values=(contact["name"], contact["middle name"],
                                                             contact["phone"], contact["email"], contact["id"]))

    def get_contact_selected(self):
        return self.treeview_contacts.selection()

    def get_contact_selected_id(self):
        contact_selected = self.get_contact_selected()
        item = self.treeview_contacts.item(contact_selected[0])["values"]
        contact_selected_id = item[4]
        return contact_selected_id

    def main_window_exit(self):
        self.main_window.destroy()

    def add_edit_window_close(self):
        self.add_edit_window.destroy()
        self.main_window.deiconify()

    def alert_window_close(self):
        self.alert_window.destroy()

    def run(self):
        self.main_window.mainloop()


class AddressBook:
    def __init__(self):
        if getattr(sys, "frozen", False):
            self.base_path = os.path.dirname(sys.executable)
        else:
            self.base_path = os.path.dirname(__file__)

        self.path = os.path.join(self.base_path, "contacts.json")

        if not os.path.exists(self.path):
            with open(self.path, "w") as file:
                json.dump([], file)

        with open(self.path, "r") as file:
            self.contacts_list = json.load(file)

    def dump_json_file(self):
        path_tmp = os.path.join(self.base_path, "contacts_tmp.json")
        with open(path_tmp, "w") as file:
            json.dump(self.contacts_list, file, indent=4)
        os.replace(path_tmp, self.path)

    def get_new_id(self):
        if not self.contacts_list:
            new_id = 1
        else:
            id_max = 0
            for contact in self.contacts_list:
                if contact["id"] > id_max:
                    id_max = contact["id"]
            new_id = id_max + 1
        return new_id

    def add_contact(self, name, middle_name, phone, email):
        new_id = self.get_new_id()
        new_contact = {"name": name, "middle name": middle_name, "phone": phone, "email": email,
                       "id": new_id}
        self.contacts_list.append(new_contact)
        self.dump_json_file()

    def edit_contact(self, name, middle_name, phone, email, contact_selected_id):
        for contact in self.contacts_list:
            if contact["id"] == contact_selected_id:
                contact["name"] = name
                contact["middle name"] = middle_name
                contact["phone"] = phone
                contact["email"] = email
        self.dump_json_file()

    def delete_contact(self, contact_selected_id):
        new_contacts_list = []
        for contact in self.contacts_list:
            if contact["id"] != contact_selected_id:
                new_contacts_list.append(contact)
        self.contacts_list = new_contacts_list
        self.dump_json_file()

    def search_contact(self, search_text):
        search_results = []
        for contact in self.contacts_list:
            if ((search_text in contact["name"].lower()
                    or search_text in contact["middle name"].lower())
                    or search_text in contact["phone"]):
                search_results.append(contact)
        return search_results


address_book = AddressBook()
interface = Interface(address_book)
interface.run()