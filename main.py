import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import json  # JSON support
import uuid  # For generating unique order IDs

# Core entities
class Client:
    def __init__(self, full_name: str, contact: str, email_address: str):
        self.full_name = full_name
        self.contact = contact
        self.email_address = email_address

    @property
    def get_full_name(self):
        return self.full_name

    @property
    def get_contact(self):
        return self.contact

    @property
    def get_email_address(self):
        return self.email_address

class Inventory:
    def __init__(self, title: str, writer: str, cost: float):
        self.title = title
        self.writer = writer
        self.cost = cost

    @property
    def get_title(self):
        return self.title

    @property
    def get_writer(self):
        return self.writer

    @property
    def get_cost(self):
        return self.cost

class Purchase:
    def __init__(self, client: Client, inventory: Inventory):
        self.client = client
        self.inventory = inventory
        self.order_id = str(uuid.uuid4())  # Generate a unique order ID

    @property
    def get_client(self):
        return self.client

    @property
    def get_inventory(self):
        return self.inventory

    @property
    def get_order_id(self):
        return self.order_id

class Delivery:
    urgent_shipments = 0

    def __init__(self, purchase: Purchase, delivery_date: datetime.date):
        self.purchase = purchase
        self.delivery_date = delivery_date
        self.delivery_charge = 0.0

    @property
    def get_delivery_date(self):
        return self.delivery_date

    @property
    def get_delivery_charge(self):
        return self.delivery_charge

    def update_delivery_charge(self, charge: float):
        self.delivery_charge = charge

    def calculate_delivery_charge(self, priority: bool):
        if priority:
            self.delivery_charge = 6.50
            Delivery.urgent_shipments += 1
        else:
            self.delivery_charge = 4.20
        return self.delivery_charge

class Bill:
    def __init__(self, bill_id: str, inventory: Inventory, delivery: Delivery):
        self.bill_id = bill_id
        self.inventory = inventory
        self.delivery = delivery
        self.total_amount = 0.0

    @property
    def get_bill_id(self):
        return self.bill_id

    def calculate_total(self):
        self.total_amount = self.inventory.get_cost + self.delivery.get_delivery_charge
        return self.total_amount

class BookstoreManager:
    def __init__(self):
        self.clients = []
        self.items = []
        self.purchases = []
        self.bills = []
        self.load_store_data()  # Load saved data

    @property
    def all_bills(self):
        return self.bills

    def locate_bill(self, bill_id: str):
        for bill in self.bills:
            if bill.get_bill_id == bill_id:
                print(f"Bill found: {bill.get_bill_id}, Total: {bill.calculate_total():.2f}")
                return bill
        print("Bill not found.")
        return None

    def locate_purchase(self, order_id: str):
        for purchase in self.purchases:
            if purchase.get_order_id == order_id:
                return purchase
        return None

    def generate_bill(self, order_id: str):
        purchase = self.locate_purchase(order_id)
        if purchase:
            delivery_date = datetime.date.today()
            delivery = Delivery(purchase, delivery_date)
            bill_id = str(uuid.uuid4())
            bill = Bill(bill_id, purchase.inventory, delivery)
            self.bills.append(bill)
            return bill
        return None

    def remove_order_by_title(self, title: str):
        for purchase in self.purchases:
            if purchase.inventory.title.lower() == title.lower():
                self.purchases.remove(purchase)
                for bill in self.bills:
                    if bill.delivery.purchase == purchase:
                        self.bills.remove(bill)
                        break
                print(f"Order for {title} removed.")
                return True
        print("Order not found.")
        return False

    def delete_order_by_title(self, title: str):
        for purchase in self.purchases:
            if purchase.inventory.title.lower() == title.lower():
                self.purchases.remove(purchase)
                for bill in self.bills:
                    if bill.delivery.purchase == purchase:
                        self.bills.remove(bill)
                        break
                print(f"Order for {title} removed.")
                return True
        print("Order not found.")
        return False

    def delete_order_by_id(self, order_id: str):
        purchase = self.locate_purchase(order_id)
        if purchase:
            self.purchases.remove(purchase)
            for bill in self.bills:
                if bill.delivery.purchase == purchase:
                    self.bills.remove(bill)
                    break
            print(f"Order with ID {order_id} removed.")
            return True
        print("Order not found.")
        return False

    def integrate_shipping(self, bill_id: str, shipping_method: str):
        bill = self.locate_bill(bill_id)
        if bill:
            if shipping_method.lower() == "priority":
                bill.delivery.calculate_delivery_charge(priority=True)
            else:
                bill.delivery.calculate_delivery_charge(priority=False)
            print(f"Shipping method {shipping_method} applied to bill {bill_id}.")
            return True
        print("Bill not found.")
        return False

    def save_store_data(self):
        store_data = {
            "clients": [
                {
                    "full_name": client.full_name,
                    "contact": client.contact,
                    "email_address": client.email_address
                }
                for client in self.clients
            ],
            "items": [
                {
                    "title": item.title,
                    "writer": item.writer,
                    "cost": item.cost
                }
                for item in self.items
            ],
            "purchases": [
                {
                    "client": {
                        "full_name": purchase.client.full_name,
                        "contact": purchase.client.contact,
                        "email_address": purchase.client.email_address
                    },
                    "inventory": {
                        "title": purchase.inventory.title,
                        "writer": purchase.inventory.writer,
                        "cost": purchase.inventory.cost
                    },
                    "order_id": purchase.order_id
                }
                for purchase in self.purchases
            ],
            "bills": [
                {
                    "bill_id": bill.bill_id,
                    "inventory": {
                        "title": bill.inventory.title,
                        "writer": bill.inventory.writer,
                        "cost": bill.inventory.cost
                    },
                    "delivery": {
                        "purchase": {
                            "client": {
                                "full_name": bill.delivery.purchase.client.full_name,
                                "contact": bill.delivery.purchase.client.contact,
                                "email_address": bill.delivery.purchase.client.email_address
                            },
                            "inventory": {
                                "title": bill.delivery.purchase.inventory.title,
                                "writer": bill.delivery.purchase.inventory.writer,
                                "cost": bill.delivery.purchase.inventory.cost
                            },
                            "order_id": bill.delivery.purchase.order_id
                        },
                        "delivery_date": bill.delivery.delivery_date.isoformat(),
                        "delivery_charge": bill.delivery.delivery_charge
                    }
                }
                for bill in self.bills
            ]
        }
        with open("store_data.json", "w") as f:
            json.dump(store_data, f, indent=4)

    def load_store_data(self):
        try:
            with open("store_data.json", "r") as f:
                store_data = json.load(f)
                for client_info in store_data.get("clients", []):
                    self.clients.append(Client(client_info["full_name"], client_info["contact"], client_info["email_address"]))
                for item_info in store_data.get("items", []):
                    self.items.append(Inventory(item_info["title"], item_info["writer"], item_info["cost"]))
                for purchase_info in store_data.get("purchases", []):
                    client_data = purchase_info["client"]
                    client = Client(client_data["full_name"], client_data["contact"], client_data["email_address"])

                    inventory_data = purchase_info["inventory"]
                    item = Inventory(inventory_data["title"], inventory_data["writer"], inventory_data["cost"])

                    purchase = Purchase(client, item)
                    purchase.order_id = purchase_info["order_id"]  # Load the order ID

                    self.purchases.append(purchase)
                for bill_info in store_data.get("bills", []):
                    client_data = bill_info["delivery"]["purchase"]["client"]
                    client = Client(client_data["full_name"], client_data["contact"], client_data["email_address"])

                    inventory_data = bill_info["delivery"]["purchase"]["inventory"]
                    item = Inventory(inventory_data["title"], inventory_data["writer"], inventory_data["cost"])

                    purchase = Purchase(client, item)
                    purchase.order_id = bill_info["delivery"]["purchase"]["order_id"]  # Load the order ID

                    delivery_data = bill_info["delivery"]
                    delivery_date = datetime.date.fromisoformat(delivery_data["delivery_date"])
                    delivery = Delivery(purchase, delivery_date)
                    delivery.update_delivery_charge(delivery_data["delivery_charge"])

                    self.bills.append(Bill(bill_info["bill_id"], item, delivery))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error loading data: {e}")

    def save_orders_to_text(self):
        with open("student2_orders.txt", "w") as f:
            for bill in self.bills:
                f.write(f"Bill ID: {bill.get_bill_id}\n")
                f.write(f"Client: {bill.delivery.purchase.client.get_full_name}\n")
                f.write(f"Contact: {bill.delivery.purchase.client.get_contact}\n")
                f.write(f"Email: {bill.delivery.purchase.client.get_email_address}\n")
                f.write(f"Book Title: {bill.inventory.get_title}\n")
                f.write(f"Writer: {bill.inventory.get_writer}\n")
                f.write(f"Cost: {bill.inventory.get_cost}\n")
                f.write(f"Delivery Date: {bill.delivery.get_delivery_date}\n")
                f.write(f"Delivery Charge: {bill.delivery.get_delivery_charge}\n")
                f.write(f"Total Amount: {bill.calculate_total()}\n")
                f.write("\n")

# GUI Application
class BookstoreApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Bookstore Management")
        self.window.geometry("1000x800")
        self.window.configure(bg="#f0f0f0")

        # Manager instance
        self.manager = BookstoreManager()

        # Interface setup
        self.setup_client_section()
        self.setup_inventory_section()
        self.setup_purchase_section()
        self.setup_bill_section()

        self.window.protocol("WM_DELETE_WINDOW", self.on_exit)

    def setup_client_section(self):
        frame = tk.LabelFrame(self.window, text="Client Information", padx=10, pady=10, bg="#e0e0e0")
        frame.place(relx=0.5, rely=0.1, anchor="n")

        tk.Label(frame, text="Full Name:", bg="#e0e0e0").grid(row=0, column=0, sticky="w")
        self.client_name_input = tk.Entry(frame, width=50)
        self.client_name_input.grid(row=0, column=1, sticky="ew")

        tk.Label(frame, text="Contact:", bg="#e0e0e0").grid(row=1, column=0, sticky="w")
        self.client_contact_input = tk.Entry(frame, width=50)
        self.client_contact_input.grid(row=1, column=1, sticky="ew")

        tk.Label(frame, text="Email Address:", bg="#e0e0e0").grid(row=2, column=0, sticky="w")
        self.client_email_input = tk.Entry(frame, width=50)
        self.client_email_input.grid(row=2, column=1, sticky="ew")

        tk.Button(frame, text="Add Client", command=self.add_client, bg="#4CAF50", fg="white", width=20).grid(row=3, columnspan=2, pady=5)

    def setup_inventory_section(self):
        frame = tk.LabelFrame(self.window, text="Inventory Information", padx=10, pady=10, bg="#e0e0e0")
        frame.place(relx=0.5, rely=0.3, anchor="n")

        tk.Label(frame, text="Title:", bg="#e0e0e0").grid(row=0, column=0, sticky="w")
        self.inventory_title_input = tk.Entry(frame, width=50)
        self.inventory_title_input.grid(row=0, column=1, sticky="ew")

        tk.Label(frame, text="Writer:", bg="#e0e0e0").grid(row=1, column=0, sticky="w")
        self.inventory_writer_input = tk.Entry(frame, width=50)
        self.inventory_writer_input.grid(row=1, column=1, sticky="ew")

        tk.Label(frame, text="Cost:", bg="#e0e0e0").grid(row=2, column=0, sticky="w")
        self.inventory_cost_input = tk.Entry(frame, width=50)
        self.inventory_cost_input.grid(row=2, column=1, sticky="ew")

        tk.Button(frame, text="Add Inventory", command=self.add_inventory, bg="#4CAF50", fg="white", width=20).grid(row=3, columnspan=2, pady=5)

    def setup_purchase_section(self):
        frame = tk.LabelFrame(self.window, text="Purchase Information", padx=10, pady=10, bg="#e0e0e0")
        frame.place(relx=0.5, rely=0.5, anchor="n")

        tk.Label(frame, text="Client Name:", bg="#e0e0e0").grid(row=0, column=0, sticky="w")
        self.purchase_client_input = tk.Entry(frame, width=50)
        self.purchase_client_input.grid(row=0, column=1, sticky="ew")

        tk.Label(frame, text="Book Title:", bg="#e0e0e0").grid(row=1, column=0, sticky="w")
        self.purchase_title_input = tk.Entry(frame, width=50)
        self.purchase_title_input.grid(row=1, column=1, sticky="ew")

        tk.Button(frame, text="Add Purchase", command=self.add_purchase, bg="#4CAF50", fg="white", width=20).grid(row=2, columnspan=2, pady=5)

        tk.Label(frame, text="Order ID:", bg="#e0e0e0").grid(row=3, column=0, sticky="w")
        self.order_id_input = tk.Entry(frame, width=50)
        self.order_id_input.grid(row=3, column=1, sticky="ew")

        tk.Button(frame, text="Generate Bill", command=self.generate_bill, bg="#4CAF50", fg="white", width=20).grid(row=4, columnspan=2, pady=5)

    def setup_bill_section(self):
        frame = tk.LabelFrame(self.window, text="Bill Information", padx=10, pady=10, bg="#e0e0e0")
        frame.place(relx=0.5, rely=0.7, anchor="n")

        tk.Label(frame, text="Bill ID:", bg="#e0e0e0").grid(row=0, column=0, sticky="w")
        self.bill_id_input = tk.Entry(frame, width=50)
        self.bill_id_input.grid(row=0, column=1, sticky="ew")

        tk.Button(frame, text="Locate Bill", command=self.locate_bill, bg="#4CAF50", fg="white", width=20).grid(row=1, columnspan=2, pady=5)

        tk.Label(frame, text="Shipping Method:", bg="#e0e0e0").grid(row=2, column=0, sticky="w")
        self.shipping_method_input = tk.Entry(frame, width=50)
        self.shipping_method_input.grid(row=2, column=1, sticky="ew")

        tk.Button(frame, text="Apply Shipping", command=self.apply_shipping, bg="#4CAF50", fg="white", width=20).grid(row=3, columnspan=2, pady=5)

        tk.Label(frame, text="Order ID:", bg="#e0e0e0").grid(row=4, column=0, sticky="w")
        self.delete_order_id_input = tk.Entry(frame, width=50)
        self.delete_order_id_input.grid(row=4, column=1, sticky="ew")

        tk.Button(frame, text="Delete Order", command=self.delete_order, bg="#f44336", fg="white", width=20).grid(row=5, columnspan=2, pady=5)

    def add_client(self):
        full_name = self.client_name_input.get()
        contact = self.client_contact_input.get()
        email_address = self.client_email_input.get()
        client = Client(full_name, contact, email_address)
        self.manager.clients.append(client)
        messagebox.showinfo("Success", "Client added successfully")

    def add_inventory(self):
        title = self.inventory_title_input.get()
        writer = self.inventory_writer_input.get()
        cost = float(self.inventory_cost_input.get())
        item = Inventory(title, writer, cost)
        self.manager.items.append(item)
        messagebox.showinfo("Success", "Inventory item added successfully")

    def add_purchase(self):
        client_name = self.purchase_client_input.get()
        book_title = self.purchase_title_input.get()
        client = next((c for c in self.manager.clients if c.get_full_name == client_name), None)
        item = next((i for i in self.manager.items if i.get_title == book_title), None)
        if client and item:
            purchase = Purchase(client, item)
            self.manager.purchases.append(purchase)
            messagebox.showinfo("Success", f"Purchase added successfully. Order ID: {purchase.get_order_id}")
        else:
            messagebox.showerror("Error", "Client or Inventory item not found")

    def generate_bill(self):
        order_id = self.order_id_input.get()
        bill = self.manager.generate_bill(order_id)
        if bill:
            messagebox.showinfo("Success", f"Bill generated successfully. Bill ID: {bill.get_bill_id}")
        else:
            messagebox.showerror("Error", "Order not found")

    def locate_bill(self):
        bill_id = self.bill_id_input.get()
        bill = self.manager.locate_bill(bill_id)
        if bill:
            messagebox.showinfo("Bill Found", f"Bill ID: {bill.get_bill_id}\nTotal: {bill.calculate_total():.2f}")
        else:
            messagebox.showerror("Error", "Bill not found")

    def apply_shipping(self):
        bill_id = self.bill_id_input.get()
        shipping_method = self.shipping_method_input.get()
        if self.manager.integrate_shipping(bill_id, shipping_method):
            messagebox.showinfo("Success", f"Shipping method {shipping_method} applied to bill {bill_id}")
        else:
            messagebox.showerror("Error", "Bill not found")

    def delete_order(self):
        order_id = self.delete_order_id_input.get()
        if self.manager.delete_order_by_id(order_id):
            messagebox.showinfo("Success", f"Order with ID {order_id} deleted")
        else:
            messagebox.showerror("Error", "Order not found")

    def on_exit(self):
        self.manager.save_store_data()
        self.manager.save_orders_to_text()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BookstoreApp(root)
    root.mainloop()

import json

def load_data():
    with open('store_data.json', 'r') as file:
        return json.load(file)

def save_data(data):
    with open('store_data.json', 'w') as file:
        json.dump(data, file, indent=4)

def generate_bill(order_id):
    data = load_data()
    purchase = next((p for p in data['purchases'] if p['order_id'] == order_id), None)
    
    if not purchase:
        print(f"No purchase found with order_id: {order_id}")
        return
    
    client = data['clients'][purchase['client_id'] - 1]
    item = data['items'][purchase['item_id'] - 1]
    total_cost = item['cost'] * purchase['quantity']
    
    bill = {
        "order_id": order_id,
        "client_name": client['full_name'],
        "item_title": item['title'],
        "quantity": purchase['quantity'],
        "total_cost": total_cost
    }
    
    data['bills'].append(bill)
    save_data(data)
    print(f"Bill generated and saved for order_id: {order_id}")

if __name__ == "__main__":
    order_id = int(input("Enter order ID: "))
    generate_bill(order_id)
