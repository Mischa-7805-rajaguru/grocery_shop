import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from datetime import datetime, date
import os
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
import json

class GroceryShopApp:
    def __init__(self, root):
        """Initialize the Grocery Shop Application"""
        self.root = root
        self.root.title("Grocery Shop Accounting System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize data directory
        self.base_directory = "grocery_shop_data"
        self.create_directory_structure()
        
        # File paths
        self.inventory_file = os.path.join(self.base_directory, "inventory.xlsx")
        self.sales_file = os.path.join(self.base_directory, "sales_records.xlsx")
        self.customers_file = os.path.join(self.base_directory, "customers.xlsx")
        self.shopping_lists_file = os.path.join(self.base_directory, "shopping_lists.json")
        
        # Initialize data structures
        self.inventory = pd.DataFrame()
        self.sales_records = pd.DataFrame()
        self.customers = pd.DataFrame()
        self.shopping_lists = {}
        self.current_cart = []
        self.current_customer = None
        
        # Load existing data
        self.load_all_data()
        
        # Create GUI
        self.create_widgets()
        self.refresh_inventory_display()
        self.refresh_customer_list()
    
    def create_directory_structure(self):
        """Create necessary directories"""
        if not os.path.exists(self.base_directory):
            os.makedirs(self.base_directory)
    
    def load_all_data(self):
        """Load all existing data from files"""
        try:
            # Load inventory
            if os.path.exists(self.inventory_file):
                self.inventory = pd.read_excel(self.inventory_file)
            else:
                self.initialize_sample_inventory()
            
            # Load sales records
            if os.path.exists(self.sales_file):
                self.sales_records = pd.read_excel(self.sales_file)
            else:
                self.sales_records = pd.DataFrame(columns=[
                    'Sale_ID', 'Date', 'Time', 'Customer_ID', 'Customer_Name', 
                    'Product_ID', 'Product_Name', 'Quantity', 'Unit_Price', 'Total_Amount', 'Payment_Method'
                ])
            
            # Load customers  
            if os.path.exists(self.customers_file):
                self.customers = pd.read_excel(self.customers_file)
            else:
                self.customers = pd.DataFrame(columns=[
                    'Customer_ID', 'Customer_Name', 'Phone', 'Email', 'Address', 'Registration_Date', 'Total_Purchases'
                ])
            
            # Load shopping lists
            if os.path.exists(self.shopping_lists_file):
                with open(self.shopping_lists_file, 'r') as f:
                    self.shopping_lists = json.load(f)
            else:
                self.shopping_lists = {}
        
        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {str(e)}")
    
    def initialize_sample_inventory(self):
        """Initialize inventory with sample products"""
        sample_inventory = {
            'Product_ID': ['P001', 'P002', 'P003', 'P004', 'P005', 'P006', 'P007', 'P008', 'P009', 'P010'],
            'Product_Name': ['Rice (1kg)', 'Wheat Flour (1kg)', 'Sugar (1kg)', 'Cooking Oil (1L)', 
                           'Milk (1L)', 'Bread', 'Eggs (12pcs)', 'Tomatoes (1kg)', 'Onions (1kg)', 'Potatoes (1kg)'],
            'Category': ['Grains', 'Grains', 'Pantry', 'Pantry', 'Dairy', 'Bakery', 'Dairy', 'Vegetables', 'Vegetables', 'Vegetables'],
            'Unit_Price': [80.0, 45.0, 42.0, 120.0, 60.0, 25.0, 180.0, 40.0, 30.0, 35.0],
            'Stock_Quantity': [50, 30, 25, 20, 15, 40, 30, 50, 40, 60],
            'Min_Stock_Level': [10, 10, 5, 5, 5, 10, 10, 10, 10, 15],
            'Supplier': ['Supplier A', 'Supplier A', 'Supplier B', 'Supplier C', 'Supplier D', 
                        'Supplier E', 'Supplier D', 'Supplier F', 'Supplier F', 'Supplier F']
        }
        
        self.inventory = pd.DataFrame(sample_inventory)
        self.save_inventory()
    
    def create_widgets(self):
        """Create the main GUI interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_sales_tab()
        self.create_inventory_tab()
        self.create_customer_tab()
        self.create_shopping_list_tab()
        self.create_reports_tab()
    
    def create_sales_tab(self):
        """Create the sales/billing tab"""
        sales_frame = ttk.Frame(self.notebook)
        self.notebook.add(sales_frame, text="Sales & Billing")
        
        # Left frame for product selection
        left_frame = ttk.LabelFrame(sales_frame, text="Product Selection", padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Search products
        ttk.Label(left_frame, text="Search Product:").pack(anchor="w")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_products)
        search_entry = ttk.Entry(left_frame, textvariable=self.search_var, width=30)
        search_entry.pack(fill="x", pady=5)
        
        # Product list
        columns = ('ID', 'Name', 'Price', 'Stock')
        self.product_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=100)
        
        scrollbar1 = ttk.Scrollbar(left_frame, orient="vertical", command=self.product_tree.yview)
        self.product_tree.configure(yscroll=scrollbar1.set)
        
        self.product_tree.pack(side="left", fill="both", expand=True)
        scrollbar1.pack(side="right", fill="y")
        
        # Add to cart button
        ttk.Button(left_frame, text="Add to Cart", command=self.add_to_cart).pack(pady=10)
        
        # Right frame for cart and billing
        right_frame = ttk.LabelFrame(sales_frame, text="Shopping Cart & Billing", padding=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Customer selection
        customer_frame = ttk.Frame(right_frame)
        customer_frame.pack(fill="x", pady=5)
        
        ttk.Label(customer_frame, text="Customer:").pack(side="left")
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(customer_frame, textvariable=self.customer_var, width=20)
        self.customer_combo.pack(side="left", padx=5)
        ttk.Button(customer_frame, text="New Customer", command=self.add_new_customer).pack(side="left", padx=5)
        
        # Cart display
        cart_columns = ('Product', 'Qty', 'Price', 'Total')
        self.cart_tree = ttk.Treeview(right_frame, columns=cart_columns, show='headings', height=10)
        
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=80)
        
        scrollbar2 = ttk.Scrollbar(right_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscroll=scrollbar2.set)
        
        self.cart_tree.pack(side="left", fill="both", expand=True)
        scrollbar2.pack(side="right", fill="y")
        
        # Cart controls
        cart_controls = ttk.Frame(right_frame)
        cart_controls.pack(fill="x", pady=5)
        
        ttk.Button(cart_controls, text="Remove Item", command=self.remove_from_cart).pack(side="left", padx=5)
        ttk.Button(cart_controls, text="Clear Cart", command=self.clear_cart).pack(side="left", padx=5)
        
        # Total and payment
        total_frame = ttk.Frame(right_frame)
        total_frame.pack(fill="x", pady=10)
        
        ttk.Label(total_frame, text="Total Amount:").pack(side="left")
        self.total_var = tk.StringVar(value="₹0.00")
        ttk.Label(total_frame, textvariable=self.total_var, font=("Arial", 14, "bold")).pack(side="right")
        
        # Payment method
        payment_frame = ttk.Frame(right_frame)
        payment_frame.pack(fill="x", pady=5)
        
        ttk.Label(payment_frame, text="Payment Method:").pack(side="left")
        self.payment_var = tk.StringVar(value="Cash")
        payment_combo = ttk.Combobox(payment_frame, textvariable=self.payment_var, 
                                   values=["Cash", "Card", "UPI", "Online"], width=15)
        payment_combo.pack(side="left", padx=5)
        
        # Checkout button
        ttk.Button(right_frame, text="Process Sale", command=self.process_sale, 
                  style="Accent.TButton").pack(pady=10, fill="x")
    
    def create_inventory_tab(self):
        """Create the inventory management tab"""
        inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(inventory_frame, text="Inventory Management")
        
        # Controls frame
        controls_frame = ttk.Frame(inventory_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Add Product", command=self.add_product_dialog).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Update Stock", command=self.update_stock_dialog).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Refresh", command=self.refresh_inventory_display).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Export to Excel", command=self.export_inventory).pack(side="left", padx=5)
        
        # Inventory display
        inv_columns = ('ID', 'Name', 'Category', 'Price', 'Stock', 'Min Stock', 'Supplier')
        self.inventory_tree = ttk.Treeview(inventory_frame, columns=inv_columns, show='headings', height=20)
        
        for col in inv_columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=120)
        
        scrollbar3 = ttk.Scrollbar(inventory_frame, orient="vertical", command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscroll=scrollbar3.set)
        
        self.inventory_tree.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        scrollbar3.pack(side="right", fill="y", pady=5)
    
    def create_customer_tab(self):
        """Create the customer management tab"""
        customer_frame = ttk.Frame(self.notebook)
        self.notebook.add(customer_frame, text="Customer Management")
        
        # Controls
        controls_frame = ttk.Frame(customer_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Add Customer", command=self.add_customer_dialog).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="View Shopping List", command=self.view_customer_shopping_list).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Refresh", command=self.refresh_customer_list).pack(side="left", padx=5)
        
        # Customer display
        cust_columns = ('ID', 'Name', 'Phone', 'Email', 'Total Purchases')
        self.customer_tree = ttk.Treeview(customer_frame, columns=cust_columns, show='headings', height=20)
        
        for col in cust_columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=150)
        
        scrollbar4 = ttk.Scrollbar(customer_frame, orient="vertical", command=self.customer_tree.yview)
        self.customer_tree.configure(yscroll=scrollbar4.set)
        
        self.customer_tree.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        scrollbar4.pack(side="right", fill="y", pady=5)
    
    def create_shopping_list_tab(self):
        """Create the shopping list management tab"""
        shopping_frame = ttk.Frame(self.notebook)
        self.notebook.add(shopping_frame, text="Shopping Lists")
        
        # Left frame for customer selection and list
        left_frame = ttk.LabelFrame(shopping_frame, text="Customer Shopping Lists", padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Customer selection for shopping list
        cust_select_frame = ttk.Frame(left_frame)
        cust_select_frame.pack(fill="x", pady=5)
        
        ttk.Label(cust_select_frame, text="Select Customer:").pack(side="left")
        self.shopping_customer_var = tk.StringVar()
        self.shopping_customer_combo = ttk.Combobox(cust_select_frame, textvariable=self.shopping_customer_var, width=25)
        self.shopping_customer_combo.pack(side="left", padx=5)
        self.shopping_customer_combo.bind("<<ComboboxSelected>>", self.load_customer_shopping_list)
        
        # Shopping list display
        list_columns = ('Product', 'Quantity', 'Notes')
        self.shopping_list_tree = ttk.Treeview(left_frame, columns=list_columns, show='headings', height=15)
        
        for col in list_columns:
            self.shopping_list_tree.heading(col, text=col)
            self.shopping_list_tree.column(col, width=120)
        
        scrollbar5 = ttk.Scrollbar(left_frame, orient="vertical", command=self.shopping_list_tree.yview)
        self.shopping_list_tree.configure(yscroll=scrollbar5.set)
        
        self.shopping_list_tree.pack(side="left", fill="both", expand=True)
        scrollbar5.pack(side="right", fill="y")
        
        # Right frame for adding items to shopping list
        right_frame = ttk.LabelFrame(shopping_frame, text="Add to Shopping List", padding=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Product selection for shopping list
        ttk.Label(right_frame, text="Product:").pack(anchor="w")
        self.shopping_product_var = tk.StringVar()
        self.shopping_product_combo = ttk.Combobox(right_frame, textvariable=self.shopping_product_var, width=30)
        self.shopping_product_combo.pack(fill="x", pady=5)
        
        ttk.Label(right_frame, text="Quantity:").pack(anchor="w")
        self.shopping_qty_var = tk.StringVar(value="1")
        ttk.Entry(right_frame, textvariable=self.shopping_qty_var, width=10).pack(anchor="w", pady=5)
        
        ttk.Label(right_frame, text="Notes (optional):").pack(anchor="w")
        self.shopping_notes_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.shopping_notes_var, width=30).pack(fill="x", pady=5)
        
        # Buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="Add to List", command=self.add_to_shopping_list).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Remove from List", command=self.remove_from_shopping_list).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear List", command=self.clear_shopping_list).pack(side="left", padx=5)
        
        # Generate shopping cart from list
        ttk.Button(right_frame, text="Add List to Cart", command=self.add_shopping_list_to_cart, 
                  style="Accent.TButton").pack(pady=10, fill="x")
    
    def create_reports_tab(self):
        """Create the reports and analytics tab"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")
        
        # Report controls
        controls_frame = ttk.Frame(reports_frame)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(controls_frame, text="Daily Sales Report", command=self.generate_daily_report).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Low Stock Alert", command=self.show_low_stock).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Customer Report", command=self.generate_customer_report).pack(side="left", padx=5)
        
        # Report display area
        self.report_text = tk.Text(reports_frame, height=25, width=80)
        scrollbar6 = ttk.Scrollbar(reports_frame, orient="vertical", command=self.report_text.yview)
        self.report_text.configure(yscroll=scrollbar6.set)
        
        self.report_text.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        scrollbar6.pack(side="right", fill="y", pady=5)
    
    def filter_products(self, *args):
        """Filter products based on search term"""
        search_term = self.search_var.get().lower()
        
        # Clear current items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Add filtered items
        for _, row in self.inventory.iterrows():
            if search_term in row['Product_Name'].lower() or search_term in row['Product_ID'].lower():
                self.product_tree.insert('', 'end', values=(
                    row['Product_ID'], row['Product_Name'], f"₹{row['Unit_Price']:.2f}", row['Stock_Quantity']
                ))
    
    def refresh_inventory_display(self):
        """Refresh the inventory display"""
        # Clear current items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Add all products to both trees
        for _, row in self.inventory.iterrows():
            # Products tree
            self.product_tree.insert('', 'end', values=(
                row['Product_ID'], row['Product_Name'], f"₹{row['Unit_Price']:.2f}", row['Stock_Quantity']
            ))
            
            # Inventory tree
            stock_display = row['Stock_Quantity']
            if row['Stock_Quantity'] <= row['Min_Stock_Level']:
                stock_display = f"{row['Stock_Quantity']} (LOW!)"
            
            self.inventory_tree.insert('', 'end', values=(
                row['Product_ID'], row['Product_Name'], row['Category'], 
                f"₹{row['Unit_Price']:.2f}", stock_display, row['Min_Stock_Level'], row['Supplier']
            ))
        
        # Update shopping list product combo
        product_names = self.inventory['Product_Name'].tolist()
        self.shopping_product_combo['values'] = product_names
    
    def refresh_customer_list(self):
        """Refresh the customer display"""
        # Clear current items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        # Add customers
        customer_names = []
        for _, row in self.customers.iterrows():
            self.customer_tree.insert('', 'end', values=(
                row['Customer_ID'], row['Customer_Name'], row['Phone'], 
                row.get('Email', ''), f"₹{row.get('Total_Purchases', 0):.2f}"
            ))
            customer_names.append(f"{row['Customer_ID']} - {row['Customer_Name']}")
        
        # Update customer combos
        self.customer_combo['values'] = customer_names
        self.shopping_customer_combo['values'] = customer_names
    
    def add_to_cart(self):
        """Add selected product to shopping cart"""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product first!")
            return
        
        # Get selected product
        item = self.product_tree.item(selection[0])
        product_id = item['values'][0]
        
        # Find product in inventory
        product = self.inventory[self.inventory['Product_ID'] == product_id].iloc[0]
        
        # Ask for quantity
        qty_dialog = tk.Toplevel(self.root)
        qty_dialog.title("Enter Quantity")
        qty_dialog.geometry("250x150")
        qty_dialog.transient(self.root)
        qty_dialog.grab_set()
        
        ttk.Label(qty_dialog, text=f"Product: {product['Product_Name']}").pack(pady=10)
        ttk.Label(qty_dialog, text=f"Available: {product['Stock_Quantity']}").pack()
        ttk.Label(qty_dialog, text="Quantity:").pack(pady=5)
        
        qty_var = tk.StringVar(value="1")
        qty_entry = ttk.Entry(qty_dialog, textvariable=qty_var, width=10)
        qty_entry.pack()
        qty_entry.focus()
        
        def add_item():
            try:
                quantity = int(qty_var.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be positive!")
                    return
                
                if quantity > product['Stock_Quantity']:
                    messagebox.showerror("Error", "Not enough stock available!")
                    return
                
                # Add to cart
                cart_item = {
                    'product_id': product_id,
                    'product_name': product['Product_Name'],
                    'quantity': quantity,
                    'unit_price': product['Unit_Price'],
                    'total': quantity * product['Unit_Price']
                }
                
                self.current_cart.append(cart_item)
                self.update_cart_display()
                qty_dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity!")
        
        ttk.Button(qty_dialog, text="Add to Cart", command=add_item).pack(pady=10)
    
    def update_cart_display(self):
        """Update the shopping cart display"""
        # Clear current cart display
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add cart items
        total_amount = 0
        for item in self.current_cart:
            self.cart_tree.insert('', 'end', values=(
                item['product_name'], item['quantity'], 
                f"₹{item['unit_price']:.2f}", f"₹{item['total']:.2f}"
            ))
            total_amount += item['total']
        
        # Update total
        self.total_var.set(f"₹{total_amount:.2f}")
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove!")
            return
        
        # Get selected index
        item_index = self.cart_tree.index(selection[0])
        
        # Remove from cart
        self.current_cart.pop(item_index)
        self.update_cart_display()
    
    def clear_cart(self):
        """Clear the shopping cart"""
        self.current_cart.clear()
        self.update_cart_display()
    
    def process_sale(self):
        """Process the current sale"""
        if not self.current_cart:
            messagebox.showwarning("Warning", "Cart is empty!")
            return
        
        customer_info = self.customer_var.get()
        if not customer_info:
            messagebox.showwarning("Warning", "Please select a customer!")
            return
        
        try:
            # Extract customer ID
            customer_id = customer_info.split(' - ')[0]
            customer_name = customer_info.split(' - ')[1]
            
            # Generate sale ID
            sale_id = f"S{len(self.sales_records) + 1:04d}"
            current_time = datetime.now()
            
            # Process each item in cart
            total_sale_amount = 0
            for item in self.current_cart:
                # Add to sales records
                sale_record = {
                    'Sale_ID': sale_id,
                    'Date': current_time.strftime('%Y-%m-%d'),
                    'Time': current_time.strftime('%H:%M:%S'),
                    'Customer_ID': customer_id,
                    'Customer_Name': customer_name,
                    'Product_ID': item['product_id'],
                    'Product_Name': item['product_name'],
                    'Quantity': item['quantity'],
                    'Unit_Price': item['unit_price'],
                    'Total_Amount': item['total'],
                    'Payment_Method': self.payment_var.get()
                }
                
                self.sales_records = pd.concat([self.sales_records, pd.DataFrame([sale_record])], ignore_index=True)
                
                # Update inventory stock
                idx = self.inventory[self.inventory['Product_ID'] == item['product_id']].index[0]
                self.inventory.loc[idx, 'Stock_Quantity'] -= item['quantity']
                
                total_sale_amount += item['total']
            
            # Update customer total purchases
            cust_idx = self.customers[self.customers['Customer_ID'] == customer_id].index
            if len(cust_idx) > 0:
                current_total = self.customers.loc[cust_idx[0], 'Total_Purchases']
                self.customers.loc[cust_idx[0], 'Total_Purchases'] = current_total + total_sale_amount
            
            # Save all data
            self.save_all_data()
            
            # Clear cart and refresh displays
            self.clear_cart()
            self.refresh_inventory_display()
            self.refresh_customer_list()
            
            # Show success message
            messagebox.showinfo("Success", f"Sale processed successfully!\nSale ID: {sale_id}\nTotal: ₹{total_sale_amount:.2f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing sale: {str(e)}")
    
    def add_new_customer(self):
        """Add a new customer"""
        customer_dialog = tk.Toplevel(self.root)
        customer_dialog.title("Add New Customer")
        customer_dialog.geometry("400x300")
        customer_dialog.transient(self.root)
        customer_dialog.grab_set()
        
        # Customer form
        ttk.Label(customer_dialog, text="Customer Name:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(customer_dialog, textvariable=name_var, width=30).pack(pady=5)
        
        ttk.Label(customer_dialog, text="Phone:").pack(pady=5)
        phone_var = tk.StringVar()
        ttk.Entry(customer_dialog, textvariable=phone_var, width=30).pack(pady=5)
        
        ttk.Label(customer_dialog, text="Email:").pack(pady=5)
        email_var = tk.StringVar()
        ttk.Entry(customer_dialog, textvariable=email_var, width=30).pack(pady=5)
        
        ttk.Label(customer_dialog, text="Address:").pack(pady=5)
        address_text = tk.Text(customer_dialog, height=4, width=30)
        address_text.pack(pady=5)
        
        def save_customer():
            try:
                # Generate customer ID
                if len(self.customers) > 0:
                    last_id = self.customers['Customer_ID'].iloc[-1]
                    new_id_num = int(last_id[1:]) + 1
                    new_customer_id = f"C{new_id_num:03d}"
                else:
                    new_customer_id = "C001"
                
                # Create new customer record
                new_customer = {
                    'Customer_ID': new_customer_id,
                    'Customer_Name': name_var.get(),
                    'Phone': phone_var.get(),
                    'Email': email_var.get(),
                    'Address': address_text.get("1.0", tk.END).strip(),
                    'Registration_Date': datetime.now().strftime('%Y-%m-%d'),
                    'Total_Purchases': 0.0
                }
                
                if not new_customer['Customer_Name']:
                    messagebox.showerror("Error", "Customer name is required!")
                    return
                
                # Add to customers dataframe
                self.customers = pd.concat([self.customers, pd.DataFrame([new_customer])], ignore_index=True)
                
                # Save and refresh
                self.save_customers()
                self.refresh_customer_list()
                
                # Set as current customer
                self.customer_var.set(f"{new_customer_id} - {new_customer['Customer_Name']}")
                
                customer_dialog.destroy()
                messagebox.showinfo("Success", f"Customer added successfully!\nCustomer ID: {new_customer_id}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error adding customer: {str(e)}")
        
        ttk.Button(customer_dialog, text="Save Customer", command=save_customer).pack(pady=10)
    
    def add_product_dialog(self):
        """Dialog to add new product to inventory"""
        product_dialog = tk.Toplevel(self.root)
        product_dialog.title("Add New Product")
        product_dialog.geometry("400x400")
        product_dialog.transient(self.root)
        product_dialog.grab_set()
        
        # Product form
        ttk.Label(product_dialog, text="Product Name:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(product_dialog, textvariable=name_var, width=30).pack(pady=5)
        
        ttk.Label(product_dialog, text="Category:").pack(pady=5)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(product_dialog, textvariable=category_var, width=27,
                                    values=["Grains", "Vegetables", "Fruits", "Dairy", "Bakery", "Pantry", "Beverages", "Snacks"])
        category_combo.pack(pady=5)
        
        ttk.Label(product_dialog, text="Unit Price (₹):").pack(pady=5)
        price_var = tk.StringVar()
        ttk.Entry(product_dialog, textvariable=price_var, width=30).pack(pady=5)
        
        ttk.Label(product_dialog, text="Stock Quantity:").pack(pady=5)
        stock_var = tk.StringVar()
        ttk.Entry(product_dialog, textvariable=stock_var, width=30).pack(pady=5)
        
        ttk.Label(product_dialog, text="Minimum Stock Level:").pack(pady=5)
        min_stock_var = tk.StringVar()
        ttk.Entry(product_dialog, textvariable=min_stock_var, width=30).pack(pady=5)
        
        ttk.Label(product_dialog, text="Supplier:").pack(pady=5)
        supplier_var = tk.StringVar()
        ttk.Entry(product_dialog, textvariable=supplier_var, width=30).pack(pady=5)
        
        def save_product():
            try:
                # Generate product ID
                if len(self.inventory) > 0:
                    last_id = self.inventory['Product_ID'].iloc[-1]
                    new_id_num = int(last_id[1:]) + 1
                    new_product_id = f"P{new_id_num:03d}"
                else:
                    new_product_id = "P001"
                
                # Create new product
                new_product = {
                    'Product_ID': new_product_id,
                    'Product_Name': name_var.get(),
                    'Category': category_var.get(),
                    'Unit_Price': float(price_var.get()),
                    'Stock_Quantity': int(stock_var.get()),
                    'Min_Stock_Level': int(min_stock_var.get()),
                    'Supplier': supplier_var.get()
                }
                
                if not all([new_product['Product_Name'], new_product['Category'], 
                           new_product['Unit_Price'], new_product['Supplier']]):
                    messagebox.showerror("Error", "All fields are required!")
                    return
                
                # Add to inventory
                self.inventory = pd.concat([self.inventory, pd.DataFrame([new_product])], ignore_index=True)
                
                # Save and refresh
                self.save_inventory()
                self.refresh_inventory_display()
                
                product_dialog.destroy()
                messagebox.showinfo("Success", f"Product added successfully!\nProduct ID: {new_product_id}")
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for price and quantities!")
            except Exception as e:
                messagebox.showerror("Error", f"Error adding product: {str(e)}")
        
        ttk.Button(product_dialog, text="Save Product", command=save_product).pack(pady=10)
    
    def update_stock_dialog(self):
        """Dialog to update stock quantity"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product from inventory!")
            return
        
        # Get selected product
        item = self.inventory_tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        current_stock = item['values'][4].split(' ')[0]  # Remove (LOW!) if present
        
        stock_dialog = tk.Toplevel(self.root)
        stock_dialog.title("Update Stock")
        stock_dialog.geometry("300x200")
        stock_dialog.transient(self.root)
        stock_dialog.grab_set()
        
        ttk.Label(stock_dialog, text=f"Product: {product_name}").pack(pady=10)
        ttk.Label(stock_dialog, text=f"Current Stock: {current_stock}").pack(pady=5)
        ttk.Label(stock_dialog, text="New Stock Quantity:").pack(pady=5)
        
        stock_var = tk.StringVar(value=current_stock)
        stock_entry = ttk.Entry(stock_dialog, textvariable=stock_var, width=15)
        stock_entry.pack(pady=5)
        stock_entry.focus()
        
        def update_stock():
            try:
                new_quantity = int(stock_var.get())
                if new_quantity < 0:
                    messagebox.showerror("Error", "Stock quantity cannot be negative!")
                    return
                
                # Update inventory
                idx = self.inventory[self.inventory['Product_ID'] == product_id].index[0]
                self.inventory.loc[idx, 'Stock_Quantity'] = new_quantity
                
                # Save and refresh
                self.save_inventory()
                self.refresh_inventory_display()
                
                stock_dialog.destroy()
                messagebox.showinfo("Success", "Stock updated successfully!")
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number!")
            except Exception as e:
                messagebox.showerror("Error", f"Error updating stock: {str(e)}")
        
        ttk.Button(stock_dialog, text="Update Stock", command=update_stock).pack(pady=10)
    
    def add_customer_dialog(self):
        """Add customer from customer management tab"""
        self.add_new_customer()
    
    def view_customer_shopping_list(self):
        """View shopping list for selected customer"""
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer!")
            return
        
        # Get customer ID
        item = self.customer_tree.item(selection[0])
        customer_id = item['values'][0]
        customer_name = item['values'][1]
        
        # Switch to shopping list tab and load customer
        self.notebook.select(3)  # Shopping list tab index
        self.shopping_customer_var.set(f"{customer_id} - {customer_name}")
        self.load_customer_shopping_list()
    
    def load_customer_shopping_list(self, event=None):
        """Load shopping list for selected customer"""
        customer_info = self.shopping_customer_var.get()
        if not customer_info:
            return
        
        customer_id = customer_info.split(' - ')[0]
        
        # Clear current list display
        for item in self.shopping_list_tree.get_children():
            self.shopping_list_tree.delete(item)
        
        # Load customer's shopping list
        if customer_id in self.shopping_lists:
            for item in self.shopping_lists[customer_id]:
                self.shopping_list_tree.insert('', 'end', values=(
                    item['product'], item['quantity'], item.get('notes', '')
                ))
    
    def add_to_shopping_list(self):
        """Add item to customer's shopping list"""
        customer_info = self.shopping_customer_var.get()
        product_name = self.shopping_product_var.get()
        quantity = self.shopping_qty_var.get()
        notes = self.shopping_notes_var.get()
        
        if not customer_info or not product_name:
            messagebox.showwarning("Warning", "Please select customer and product!")
            return
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be positive!")
                return
            
            customer_id = customer_info.split(' - ')[0]
            
            # Initialize shopping list if doesn't exist
            if customer_id not in self.shopping_lists:
                self.shopping_lists[customer_id] = []
            
            # Add item to shopping list
            list_item = {
                'product': product_name,
                'quantity': quantity,
                'notes': notes
            }
            
            self.shopping_lists[customer_id].append(list_item)
            
            # Save and refresh
            self.save_shopping_lists()
            self.load_customer_shopping_list()
            
            # Clear form
            self.shopping_product_var.set('')
            self.shopping_qty_var.set('1')
            self.shopping_notes_var.set('')
            
            messagebox.showinfo("Success", "Item added to shopping list!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity!")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding to shopping list: {str(e)}")
    
    def remove_from_shopping_list(self):
        """Remove selected item from shopping list"""
        selection = self.shopping_list_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove!")
            return
        
        customer_info = self.shopping_customer_var.get()
        if not customer_info:
            return
        
        customer_id = customer_info.split(' - ')[0]
        item_index = self.shopping_list_tree.index(selection[0])
        
        # Remove from shopping list
        if customer_id in self.shopping_lists and item_index < len(self.shopping_lists[customer_id]):
            self.shopping_lists[customer_id].pop(item_index)
            
            # Save and refresh
            self.save_shopping_lists()
            self.load_customer_shopping_list()
            
            messagebox.showinfo("Success", "Item removed from shopping list!")
    
    def clear_shopping_list(self):
        """Clear entire shopping list for customer"""
        customer_info = self.shopping_customer_var.get()
        if not customer_info:
            messagebox.showwarning("Warning", "Please select a customer!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the entire shopping list?"):
            customer_id = customer_info.split(' - ')[0]
            self.shopping_lists[customer_id] = []
            
            # Save and refresh
            self.save_shopping_lists()
            self.load_customer_shopping_list()
            
            messagebox.showinfo("Success", "Shopping list cleared!")
    
    def add_shopping_list_to_cart(self):
        """Add all items from shopping list to current cart"""
        customer_info = self.shopping_customer_var.get()
        if not customer_info:
            messagebox.showwarning("Warning", "Please select a customer!")
            return
        
        customer_id = customer_info.split(' - ')[0]
        
        if customer_id not in self.shopping_lists or not self.shopping_lists[customer_id]:
            messagebox.showwarning("Warning", "Shopping list is empty!")
            return
        
        # Switch to sales tab
        self.notebook.select(0)
        
        # Set customer
        self.customer_var.set(customer_info)
        
        # Add each item to cart
        items_added = 0
        for list_item in self.shopping_lists[customer_id]:
            # Find product in inventory
            product_match = self.inventory[self.inventory['Product_Name'] == list_item['product']]
            
            if len(product_match) > 0:
                product = product_match.iloc[0]
                
                # Check stock availability
                if product['Stock_Quantity'] >= list_item['quantity']:
                    cart_item = {
                        'product_id': product['Product_ID'],
                        'product_name': product['Product_Name'],
                        'quantity': list_item['quantity'],
                        'unit_price': product['Unit_Price'],
                        'total': list_item['quantity'] * product['Unit_Price']
                    }
                    
                    self.current_cart.append(cart_item)
                    items_added += 1
                else:
                    messagebox.showwarning("Stock Warning", 
                                         f"Not enough stock for {product['Product_Name']}. Available: {product['Stock_Quantity']}, Requested: {list_item['quantity']}")
        
        # Update cart display
        self.update_cart_display()
        
        if items_added > 0:
            messagebox.showinfo("Success", f"{items_added} items added to cart from shopping list!")
        else:
            messagebox.showwarning("Warning", "No items could be added to cart!")
    
    def generate_daily_report(self):
        """Generate daily sales report"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Filter today's sales
        if len(self.sales_records) > 0:
            today_sales = self.sales_records[self.sales_records['Date'] == today]
        else:
            today_sales = pd.DataFrame()
        
        report = f"DAILY SALES REPORT - {today}\n"
        report += "=" * 50 + "\n\n"
        
        if len(today_sales) > 0:
            total_sales = today_sales['Total_Amount'].sum()
            total_transactions = len(today_sales['Sale_ID'].unique())
            
            report += f"Total Sales: ₹{total_sales:.2f}\n"
            report += f"Total Transactions: {total_transactions}\n"
            report += f"Average Transaction: ₹{total_sales/total_transactions:.2f}\n\n"
            
            # Sales by payment method
            payment_summary = today_sales.groupby('Payment_Method')['Total_Amount'].sum()
            report += "Sales by Payment Method:\n"
            for method, amount in payment_summary.items():
                report += f"  {method}: ₹{amount:.2f}\n"
            
            report += "\n"
            
            # Top selling products
            product_summary = today_sales.groupby('Product_Name').agg({
                'Quantity': 'sum',
                'Total_Amount': 'sum'
            }).sort_values('Total_Amount', ascending=False)
            
            report += "Top Selling Products:\n"
            for product, data in product_summary.head(10).iterrows():
                report += f"  {product}: {data['Quantity']} units, ₹{data['Total_Amount']:.2f}\n"
        else:
            report += "No sales recorded for today.\n"
        
        # Display report
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)
    
    def show_low_stock(self):
        """Show low stock alert"""
        low_stock_items = []
        
        for _, row in self.inventory.iterrows():
            if row['Stock_Quantity'] <= row['Min_Stock_Level']:
                low_stock_items.append(row)
        
        report = "LOW STOCK ALERT\n"
        report += "=" * 30 + "\n\n"
        
        if low_stock_items:
            report += f"Found {len(low_stock_items)} items with low stock:\n\n"
            
            for item in low_stock_items:
                report += f"Product: {item['Product_Name']}\n"
                report += f"  Current Stock: {item['Stock_Quantity']}\n"
                report += f"  Minimum Level: {item['Min_Stock_Level']}\n"
                report += f"  Supplier: {item['Supplier']}\n"
                report += f"  Category: {item['Category']}\n\n"
        else:
            report += "All products are adequately stocked!\n"
        
        # Display report
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)
    
    def generate_customer_report(self):
        """Generate customer analysis report"""
        report = "CUSTOMER ANALYSIS REPORT\n"
        report += "=" * 40 + "\n\n"
        
        if len(self.customers) > 0:
            total_customers = len(self.customers)
            total_customer_purchases = self.customers['Total_Purchases'].sum()
            avg_purchase = total_customer_purchases / total_customers if total_customers > 0 else 0
            
            report += f"Total Customers: {total_customers}\n"
            report += f"Total Customer Purchases: ₹{total_customer_purchases:.2f}\n"
            report += f"Average Purchase per Customer: ₹{avg_purchase:.2f}\n\n"
            
            # Top customers
            top_customers = self.customers.sort_values('Total_Purchases', ascending=False)
            
            report += "Top 10 Customers by Purchase Amount:\n"
            for i, (_, customer) in enumerate(top_customers.head(10).iterrows(), 1):
                report += f"  {i}. {customer['Customer_Name']}: ₹{customer['Total_Purchases']:.2f}\n"
            
            report += "\n"
            
            # Customers with shopping lists
            customers_with_lists = len([cid for cid in self.shopping_lists if self.shopping_lists[cid]])
            report += f"Customers with Active Shopping Lists: {customers_with_lists}\n"
        else:
            report += "No customer data available.\n"
        
        # Display report
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)
    
    def export_inventory(self):
        """Export inventory to Excel file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Export Inventory"
            )
            
            if filename:
                self.inventory.to_excel(filename, index=False)
                messagebox.showinfo("Success", f"Inventory exported to {filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting inventory: {str(e)}")
    
    def save_all_data(self):
        """Save all data to files"""
        self.save_inventory()
        self.save_sales_records()
        self.save_customers()
        self.save_shopping_lists()
    
    def save_inventory(self):
        """Save inventory to Excel"""
        try:
            self.inventory.to_excel(self.inventory_file, index=False)
        except Exception as e:
            print(f"Error saving inventory: {str(e)}")
    
    def save_sales_records(self):
        """Save sales records to Excel"""
        try:
            self.sales_records.to_excel(self.sales_file, index=False)
        except Exception as e:
            print(f"Error saving sales records: {str(e)}")
    
    def save_customers(self):
        """Save customers to Excel"""
        try:
            self.customers.to_excel(self.customers_file, index=False)
        except Exception as e:
            print(f"Error saving customers: {str(e)}")
    
    def save_shopping_lists(self):
        """Save shopping lists to JSON"""
        try:
            with open(self.shopping_lists_file, 'w') as f:
                json.dump(self.shopping_lists, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving shopping lists: {str(e)}")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = GroceryShopApp(root)
    
    # Configure ttk styles
    style = ttk.Style()
    style.theme_use('clam')
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Application closed by user")
    except Exception as e:
        print(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()
