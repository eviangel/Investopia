import React, { useState } from 'react';
import './AddTrade.css';

const AddTrade = ({ onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    buyPrice: '',
    sellPrice: '',
    date: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = () => {
    console.log('Form Submitted:', formData);
    onClose(); // Close the popup
  };

  return (
    <div className="add-trade-overlay">
      <div className="add-trade-container">
        <h2 className="add-trade-title">Add Trade</h2>
        <form className="add-trade-form">
          <label>
            Name of Pair:
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
            />
          </label>
          <label>
            Buy Price:
            <input
              type="number"
              name="buyPrice"
              value={formData.buyPrice}
              onChange={handleChange}
            />
          </label>
          <label>
            Sell Price:
            <input
              type="number"
              name="sellPrice"
              value={formData.sellPrice}
              onChange={handleChange}
            />
          </label>
          <label>
            Date:
            <input
              type="date"
              name="date"
              value={formData.date}
              onChange={handleChange}
            />
          </label>
          <div className="button-group">
            <button
              type="button"
              className="submit-button"
              onClick={handleSubmit}
            >
              Submit
            </button>
            <button
              type="button"
              className="cancel-button"
              onClick={onClose}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddTrade;