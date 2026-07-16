import { useEffect, useState } from "react";

function AddItem({fetchItems, editingItem, setEditingItem}) {

    const [formData, setFormData] = useState({
        name: "",
        barcode: "",
        quantity: "",
        price: "",
        category: ""
    });

    useEffect(() => {
        if (editingItem) {
            setFormData(editingItem);
        }
    }, [editingItem]);

    function handleChange(event) {

        setFormData({
            ...formData,
            [event.target.name]: event.target.value
        });

    }

   function handleSubmit(event){

    event.preventDefault();

    const url = editingItem
        ? `http://127.0.0.1:5000/items/${editingItem.id}`
        : "http://127.0.0.1:5000/items";

    const method = editingItem ? "PUT" : "POST";

    fetch(url,{

        method:method,

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify(formData)

    })
    .then(response=>response.json())
    .then(()=>{

        fetchItems();

        setEditingItem(null);

        setFormData({

            name:"",
            barcode:"",
            quantity:"",
            price:"",
            category:""

        });

    });

}

    return (

        <div>

            <h2>Add New Item</h2>

            <form onSubmit={handleSubmit} className="form">

                <input
                    type="text"
                    name="name"
                    placeholder="Product Name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                />

                <input
                    type="text"
                    name="barcode"
                    placeholder="Barcode"
                    value={formData.barcode}
                    onChange={handleChange}
                    required
                />

                <input
                    type="number"
                    name="quantity"
                    placeholder="Quantity"
                    value={formData.quantity}
                    onChange={handleChange}
                    required
                />

                <input
                    type="number"
                    name="price"
                    placeholder="Price"
                    value={formData.price}
                    onChange={handleChange}
                    required
                />

                <input
                    type="text"
                    name="category"
                    placeholder="Category"
                    value={formData.category}
                    onChange={handleChange}
                    required
                />

                <button type="submit">

                       {editingItem ? "Update Item" : "Add Item"}



                </button>

            </form>

        </div>

    );

}

export default AddItem;