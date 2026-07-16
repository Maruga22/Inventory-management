import { useEffect, useState } from "react";

import Navbar from "./components/Navbar";
import InventoryList from "./components/InventoryList";
import AddItem from "./components/AddItem";
import SearchProduct from "./components/SearchProduct";
import Footer from "./components/Footer";

import "./App.css";

function App() {

    const [items, setItems] = useState([]);
    const [editingItem, setEditingItem] = useState(null);
    const fetchItems = () => {

        fetch("http://127.0.0.1:5000/items")
            .then((response) => response.json())
            .then((data) => setItems(data))
            .catch((error) => console.log(error));

    };

    useEffect(() => {

        fetchItems();

    }, []);

    return (

        <div className="app">

            <Navbar />

            <main className="container">

                <h2>Inventory Dashboard</h2>

                <p className="subtitle">

                    Manage your inventory and search products.

                </p>

                <div className="card">

                    <AddItem
                      fetchItems={fetchItems}
                      editingItem={editingItem}
                      setEditingItem={setEditingItem}
                    />

                </div>

                

                <div className="card">
                  <InventoryList
                      items={items}
                      fetchItems={fetchItems}
                      setEditingItem={setEditingItem}
                    />

                </div>

            </main>

            <Footer />

        </div>

    );

}

export default App;