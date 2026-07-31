import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

SERVER = "http://127.0.0.1:5000"


class ShopApp(App):

    def build(self):

        self.user = ""
        self.cart = []

        self.root_layout = BoxLayout(orientation="vertical")

        self.message = Label(
            text="LOGIN TO CONTINUE",
            size_hint_y=0.1
        )

        self.root_layout.add_widget(self.message)

        self.screen_login()

        return self.root_layout

    # ================= LOGIN SCREEN =================

    def screen_login(self):

        self.username = TextInput(
            hint_text="Username",
            multiline=False
        )

        self.password = TextInput(
            hint_text="Password",
            password=True,
            multiline=False
        )

        login_btn = Button(text="LOGIN")
        login_btn.bind(on_press=self.login)

        self.root_layout.add_widget(self.username)
        self.root_layout.add_widget(self.password)
        self.root_layout.add_widget(login_btn)

    # ================= LOGIN =================

    def login(self, instance):

        try:

            data = {
                "username": self.username.text.strip(),
                "password": self.password.text.strip()
            }

            res = requests.post(
                SERVER + "/login",
                json=data
            ).json()

            if res.get("status") == "success":

                self.user = data["username"]

                self.message.text = (
                    f"Welcome {self.user}"
                )

                self.load_products()

            else:

                self.message.text = (
                    "LOGIN FAILED"
                )

        except Exception as e:

            self.message.text = (
                "SERVER ERROR"
            )

            print(e)

    # ================= PRODUCTS =================

    def load_products(self):

        self.root_layout.clear_widgets()

        self.root_layout.add_widget(self.message)

        scroll = ScrollView()

        grid = GridLayout(
            cols=1,
            size_hint_y=None
        )

        grid.bind(
            minimum_height=grid.setter("height")
        )

        try:

            res = requests.get(
                SERVER + "/products"
            ).json()

            if not res:

                grid.add_widget(
                    Label(
                        text="No products available"
                    )
                )

            else:

                for p in res:

                    box = BoxLayout(
                        orientation="horizontal",
                        size_hint_y=None,
                        height=70
                    )

                    label = Label(
                        text=f"{p['name']}\nPrice: {p['price']} Tsh"
                    )

                    btn = Button(
                        text="ADD TO CART",
                        size_hint_x=0.4
                    )

                    btn.bind(
                        on_press=lambda x, p=p:
                        self.add_to_cart(p)
                    )

                    box.add_widget(label)
                    box.add_widget(btn)

                    grid.add_widget(box)

        except Exception as e:

            grid.add_widget(
                Label(
                    text="Failed to load products"
                )
            )

            print(e)

        scroll.add_widget(grid)

        self.root_layout.add_widget(scroll)

        cart_btn = Button(
            text="VIEW CART",
            size_hint_y=None,
            height=50
        )

        cart_btn.bind(
            on_press=self.show_cart
        )

        self.root_layout.add_widget(cart_btn)

        logout_btn = Button(
            text="LOGOUT",
            size_hint_y=None,
            height=50
        )

        logout_btn.bind(
            on_press=self.logout
        )

        self.root_layout.add_widget(logout_btn)

    # ================= ADD TO CART =================

    def add_to_cart(self, product):

        self.cart.append(product)

        self.message.text = (
            f"{product['name']} added to cart"
        )

    # ================= VIEW CART =================

    def show_cart(self, instance):

        self.root_layout.clear_widgets()

        self.root_layout.add_widget(self.message)

        grid = GridLayout(
            cols=1,
            size_hint_y=None
        )

        grid.bind(
            minimum_height=grid.setter("height")
        )

        total = 0

        for item in self.cart:

            grid.add_widget(
                Label(
                    text=f"{item['name']} - {item['price']} Tsh"
                )
            )

            total += float(item["price"])

        grid.add_widget(
            Label(
                text=f"TOTAL = {total} Tsh"
            )
        )

        scroll = ScrollView()

        scroll.add_widget(grid)

        self.root_layout.add_widget(scroll)

        checkout_btn = Button(
            text="CHECKOUT",
            size_hint_y=None,
            height=50
        )

        checkout_btn.bind(
            on_press=self.checkout
        )

        self.root_layout.add_widget(checkout_btn)

        back_btn = Button(
            text="BACK TO PRODUCTS",
            size_hint_y=None,
            height=50
        )

        back_btn.bind(
            on_press=lambda x:
            self.load_products()
        )

        self.root_layout.add_widget(back_btn)

    # ================= CHECKOUT =================

    def checkout(self, instance):

        if not self.cart:

            self.message.text = (
                "Cart is empty"
            )

            return

        try:

            products = [
                item["name"]
                for item in self.cart
            ]

            data = {
                "user": self.user,
                "products": products
            }

            requests.post(
                SERVER + "/order",
                json=data
            )

            self.message.text = (
                "Order placed successfully"
            )

            self.cart.clear()

            self.load_products()

        except Exception as e:

            self.message.text = (
                "Checkout failed"
            )

            print(e)

    # ================= LOGOUT =================

    def logout(self, instance):

        self.user = ""

        self.cart.clear()

        self.root_layout.clear_widgets()

        self.message = Label(
            text="LOGIN TO CONTINUE",
            size_hint_y=0.1
        )

        self.root_layout.add_widget(
            self.message
        )

        self.screen_login()


if __name__ == "__main__":
    ShopApp().run()