function InventoryList({ items, fetchItems, setEditingItem }) {

    // Delete an item
    const deleteItem = (id) => {

        if (!window.confirm("Are you sure you want to delete this item?")) {
            return;
        }

        fetch(`http://127.0.0.1:5000/items/${id}`, {
            method: "DELETE"
        })
            .then(() => {
                fetchItems();
            })
            .catch((error) => console.log(error));

    };

    return (

        <div>

            <h2>Inventory List</h2>

            <table className="inventory-table">

                <thead>

                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Barcode</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Category</th>
                        <th>Action</th>
                    </tr>

                </thead>

                <tbody>

                    {items.map((item) => (

                        <tr key={item.id}>

                            <td>{item.id}</td>
                            <td>{item.name}</td>
                            <td>{item.barcode}</td>
                            <td>{item.quantity}</td>
                            <td>{item.price}</td>
                            <td>{item.category}</td>

                            <td>

                             <button
                                 className="edit-btn"
                                    onClick={() => setEditingItem(item)}
                                >
                                    Edit
                                </button>

                             <button
                                    className="delete-btn"
                                     onClick={() => deleteItem(item.id)}
                                >
                                     Delete
                                </button>

                            </td>

                        </tr>

                    ))}

                </tbody>

            </table>

        </div>

    );

}

export default InventoryList;