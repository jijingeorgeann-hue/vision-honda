import json
import os
from datetime import datetime

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.core.window import Window

APP_NAME = "Vision Honda Digital Sales Kit"
DATA_FILE = "vision_honda_data.json"

# Prices are intentionally blank/zero until the dealership's current price list is entered.
# No discounts are automatically applied.
VEHICLES = {
    "Amaze": ["V MT", "VX MT", "ZX MT", "V CVT", "VX CVT", "ZX CVT"],
    "City": ["SV MT", "V MT", "VX MT", "ZX MT", "V CVT", "VX CVT", "ZX CVT", "TOP MT", "TOP CVT"],
    "Elevate": ["SV MT", "V MT", "VX MT", "ZX MT", "SV CVT", "V CVT", "VX CVT", "ZX CVT"],
    "ZR-V": ["Variant to be configured"]
}

def number(value):
    try:
        return float(str(value).replace(",", "").replace("₹", "").strip() or 0)
    except ValueError:
        return 0.0

def money(value):
    return "₹{:,.2f}".format(value)

class Store:
    def __init__(self):
        self.data = {"customers": [], "quotations": []}
        self.load()

    def load(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self.data.update(loaded)
        except Exception:
            pass

    def save(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_box = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        self.add_widget(self.root_box)

    def heading(self, text):
        self.root_box.add_widget(Label(text=text, size_hint_y=None, height=dp(48),
                                       font_size="21sp", bold=True, color=(0.08, 0.16, 0.28, 1)))

    def field(self, hint, default="", multiline=False):
        widget = TextInput(hint_text=hint, text=str(default), multiline=multiline,
                           size_hint_y=None, height=dp(46 if not multiline else 90),
                           font_size="16sp", padding=dp(10))
        return widget

    def button(self, text, callback, color=(0.08, 0.25, 0.45, 1)):
        b = Button(text=text, size_hint_y=None, height=dp(48), font_size="16sp",
                   background_normal="", background_color=color)
        b.bind(on_release=lambda *_: callback())
        return b

    def message(self, title, text):
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(12))
        box.add_widget(Label(text=text))
        close = Button(text="OK", size_hint_y=None, height=dp(44))
        box.add_widget(close)
        popup = Popup(title=title, content=box, size_hint=(0.88, 0.45))
        close.bind(on_release=popup.dismiss)
        popup.open()

    def back_button(self):
        self.root_box.add_widget(self.button("← Home", lambda: setattr(self.manager, "current", "home")))

class HomeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.heading("VISION HONDA\nDigital Sales Kit")
        self.root_box.add_widget(Label(text="Sales tools in one place", size_hint_y=None, height=dp(32)))
        for title, target in [
            ("Car Catalogue", "catalogue"),
            ("On-Road Price Calculator", "quotation"),
            ("Customer Management", "customers"),
            ("EMI Calculator", "emi"),
            ("Saved Quotations", "saved"),
        ]:
            self.root_box.add_widget(self.button(title, lambda t=target: setattr(self.manager, "current", t)))
        self.root_box.add_widget(Label(
            text="Note: Enter verified dealership prices before preparing customer quotations.",
            size_hint_y=None, height=dp(58), font_size="12sp", color=(0.35, 0.35, 0.35, 1)
        ))

class CatalogueScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.heading("Honda Car Catalogue")
        scroll = ScrollView()
        content = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=dp(4))
        content.bind(minimum_height=content.setter("height"))
        for model, variants in VEHICLES.items():
            content.add_widget(Label(text=model, bold=True, font_size="18sp",
                                     size_hint_y=None, height=dp(36), color=(0.08, 0.16, 0.28, 1)))
            content.add_widget(Label(text="Variants: " + ", ".join(variants),
                                     size_hint_y=None, height=dp(72), halign="left", valign="middle"))
        scroll.add_widget(content)
        self.root_box.add_widget(scroll)
        self.root_box.add_widget(Label(text="Catalogue names are starter entries; verify current model/variant availability.",
                                       size_hint_y=None, height=dp(44), font_size="11sp"))
        self.back_button()

class QuotationScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.heading("On-Road Price Calculator")
        scroll = ScrollView()
        form = BoxLayout(orientation="vertical", spacing=dp(7), size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))
        self.customer = self.field("Customer name")
        self.phone = self.field("Phone number")
        self.model = Spinner(text="Amaze", values=tuple(VEHICLES.keys()), size_hint_y=None, height=dp(46))
        self.variant = Spinner(text=VEHICLES["Amaze"][0], values=tuple(VEHICLES["Amaze"]), size_hint_y=None, height=dp(46))
        self.model.bind(text=self.update_variants)
        form.add_widget(self.customer); form.add_widget(self.phone)
        form.add_widget(Label(text="Model", size_hint_y=None, height=dp(24)))
        form.add_widget(self.model)
        form.add_widget(Label(text="Variant", size_hint_y=None, height=dp(24)))
        form.add_widget(self.variant)
        self.inputs = {}
        labels = [
            ("ex_showroom", "Ex-showroom"),
            ("tcs", "TCS"),
            ("insurance", "Honda Assure Insurance"),
            ("zero_dep", "Bumper-to-Bumper / Nil Depreciation"),
            ("road_tax", "Road Tax"),
            ("registration", "Registration + Fastag (standard ₹2,160)"),
            ("accessories", "Basic Accessories Kit"),
            ("rsa", "RSA 1 Year"),
            ("discount", "Discount (enter only when specifically approved)"),
        ]
        for key, label in labels:
            form.add_widget(Label(text=label, size_hint_y=None, height=dp(24), halign="left"))
            default = "2160" if key == "registration" else ""
            field = self.field("Amount in ₹", default)
            self.inputs[key] = field
            form.add_widget(field)
        form.add_widget(self.button("Calculate On-Road Price", self.calculate))
        self.result = Label(text="Quotation total will appear here.", size_hint_y=None, height=dp(85))
        form.add_widget(self.result)
        form.add_widget(self.button("Save Quotation", self.save_quote, color=(0.10, 0.42, 0.25, 1)))
        scroll.add_widget(form)
        self.root_box.add_widget(scroll)
        self.back_button()

    def update_variants(self, spinner, model):
        variants = VEHICLES.get(model, ["Variant"])
        self.variant.values = tuple(variants)
        self.variant.text = variants[0]

    def calculate(self):
        values = {k: number(v.text) for k, v in self.inputs.items()}
        before_discount = sum(values[k] for k in values if k != "discount")
        discount = values["discount"]
        if discount < 0 or discount > before_discount:
            self.message("Check discount", "Please enter a valid discount amount.")
            return
        self.before_discount = before_discount
        self.discount = discount
        self.final_total = before_discount - discount
        self.result.text = (
            f"Pre-discount On-Road: {money(before_discount)}\n"
            f"Discount: {money(discount)}\n"
            f"Final Payable: {money(self.final_total)}"
        )

    def save_quote(self):
        if not hasattr(self, "final_total"):
            self.calculate()
            if not hasattr(self, "final_total"):
                return
        record = {
            "date": datetime.now().isoformat(timespec="minutes"),
            "customer": self.customer.text.strip(),
            "phone": self.phone.text.strip(),
            "model": self.model.text,
            "variant": self.variant.text,
            "components": {k: number(v.text) for k, v in self.inputs.items()},
            "pre_discount": self.before_discount,
            "discount": self.discount,
            "final_total": self.final_total,
        }
        self.manager.app.store.data["quotations"].append(record)
        self.manager.app.store.save()
        self.message("Saved", "Quotation saved on this device.")

class CustomerScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.heading("Customer Management")
        self.name = self.field("Customer name")
        self.phone = self.field("Phone number")
        self.interest = self.field("Interested Honda model / variant")
        self.followup = self.field("Follow-up date (e.g. 10-11-2026)")
        self.notes = self.field("Notes", multiline=True)
        for w in [self.name, self.phone, self.interest, self.followup, self.notes]:
            self.root_box.add_widget(w)
        self.root_box.add_widget(self.button("Save Customer", self.save_customer))
        self.listing = Label(text="", size_hint_y=None, height=dp(130))
        self.root_box.add_widget(self.listing)
        self.root_box.add_widget(self.button("Refresh Customer List", self.refresh))
        self.back_button()

    def save_customer(self):
        if not self.name.text.strip():
            self.message("Missing name", "Enter the customer name.")
            return
        self.manager.app.store.data["customers"].append({
            "name": self.name.text.strip(), "phone": self.phone.text.strip(),
            "interest": self.interest.text.strip(), "followup": self.followup.text.strip(),
            "notes": self.notes.text.strip()
        })
        self.manager.app.store.save()
        self.name.text = self.phone.text = self.interest.text = self.followup.text = self.notes.text = ""
        self.refresh()
        self.message("Saved", "Customer details saved on this device.")

    def refresh(self):
        customers = self.manager.app.store.data["customers"]
        lines = [f"{c.get('name','')} — {c.get('interest','')}" for c in customers[-8:]]
        self.listing.text = "\n".join(lines) if lines else "No customers saved yet."

class EmiScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.heading("EMI Calculator")
        self.loan = self.field("Loan amount (₹)")
        self.rate = self.field("Annual interest rate (%)")
        self.months = self.field("Loan tenure (months)")
        for w in [self.loan, self.rate, self.months]:
            self.root_box.add_widget(w)
        self.result = Label(text="Monthly EMI will appear here.", size_hint_y=None, height=dp(70))
        self.root_box.add_widget(self.button("Calculate EMI", self.calculate))
        self.root_box.add_widget(self.result)
        self.back_button()

    def calculate(self):
        principal = number(self.loan.text)
        annual_rate = number(self.rate.text)
        months = int(number(self.months.text))
        if principal <= 0 or months <= 0 or annual_rate < 0:
            self.message("Check values", "Enter a positive loan amount and tenure, and a valid interest rate.")
            return
        r = annual_rate / 1200
        emi = principal / months if r == 0 else principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
        self.result.text = f"Monthly EMI: {money(emi)}\nTotal payment: {money(emi * months)}"

class SavedScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.heading("Saved Quotations")
        self.listing = Label(text="", size_hint_y=None, height=dp(300), halign="left", valign="top")
        self.root_box.add_widget(self.listing)
        self.root_box.add_widget(self.button("Refresh", self.refresh))
        self.back_button()

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        quotes = self.manager.app.store.data["quotations"]
        lines = []
        for q in quotes[-20:][::-1]:
            lines.append(f"{q.get('date','')} | {q.get('customer','Walk-in')}\n"
                         f"{q.get('model','')} {q.get('variant','')} | {money(q.get('final_total',0))}\n")
        self.listing.text = "\n".join(lines) if lines else "No quotations saved yet."

class VisionHondaApp(App):
    def build(self):
        self.title = APP_NAME
        self.store = Store()
        Window.clearcolor = (0.96, 0.97, 0.98, 1)
        manager = ScreenManager()
        manager.app = self
        for name, screen in [
            ("home", HomeScreen(name="home")),
            ("catalogue", CatalogueScreen(name="catalogue")),
            ("quotation", QuotationScreen(name="quotation")),
            ("customers", CustomerScreen(name="customers")),
            ("emi", EmiScreen(name="emi")),
            ("saved", SavedScreen(name="saved")),
        ]:
            manager.add_widget(screen)
        return manager

if __name__ == "__main__":
    VisionHondaApp().run()
