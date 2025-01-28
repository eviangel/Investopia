// import React from 'react';
// import './AddExchange.css';
// // import BinanceLogo from './assets/binance-logo.png';
// // import BybitLogo from './assets/bybit-logo.png';
// // import BitgetLogo from './assets/bitget-logo.png';

// const AddExchange = ({ onClose }) => {
//   const handleExchangeClick = (exchange) => {
//     console.log(`${exchange} selected`);
//   };

//   const handleSubmit = () => {
//     console.log("Exchange submitted");
//     onClose(); // Close the popup after submission
//   };

//   return (
//     <div className="add-exchange-overlay">
//       <div className="add-exchange-container">
//         <h2 className="add-exchange-title">Add Exchange</h2>
//         <div className="exchange-buttons">
//           <button
//             className="exchange-button"
//             onClick={() => handleExchangeClick('Binance')}
//           >
//             <img src="../src/assets/binance-logo.png"  alt="Binance" className="exchange-logo" />
//           </button>
//           <button
//             className="exchange-button"
//             onClick={() => handleExchangeClick('Bybit')}
//           >
//             <img src="../src/assets/bybit-logo.png" alt="Bybit" className="exchange-logo" />
//           </button>
//           <button
//             className="exchange-button"
//             onClick={() => handleExchangeClick('Bitget')}
//           >
//             <img src="../src/assets/bitget-logo.png" alt="Bitget" className="exchange-logo" />
//           </button>
//         </div>
//         <div className="button-group">
//           <button className="submit-button" onClick={handleSubmit}>Submit</button>
//           <button className="cancel-button" onClick={onClose}>Cancel</button>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default AddExchange;

// import React, { useState } from 'react';
// import './AddExchange.css';

// const AddExchange = ({ onClose }) => {
//   const [showNextStep, setShowNextStep] = useState(false);
//   const [selectedExchange, setSelectedExchange] = useState(null);
//   const [apiKey, setApiKey] = useState('');

//   const handleExchangeClick = (exchange) => {
//     setSelectedExchange(exchange);
//     console.log(`${exchange} selected`);
//   };

//   const handleNext = () => {
//     if (selectedExchange) {
//       setShowNextStep(true);
//     } else {
//       alert('Please select an exchange before proceeding.');
//     }
//   };

//   const handleApiSubmit = () => {
//     console.log(`API Key for ${selectedExchange}:`, apiKey);
//     onClose(); // Close the popup after submission
//   };

//   return (
//     <div className="add-exchange-overlay">
//       <div className="add-exchange-container">
//         {!showNextStep ? (
//           <>
//             <h2 className="add-exchange-title">Add Exchange</h2>
//             <div className="exchange-buttons">
//               <button
//                 className="exchange-button"
//                 onClick={() => console.log('Binance selected')}
//               >
//                 <img src="../src/assets/binance-logo.png" alt="Binance" className="exchange-logo" />
//               </button>
//               <button
//                 className="exchange-button"
//                 onClick={() => console.log('Bybit selected')}
//               >
//                 <img src="../src/assets/bybit-logo.png" alt="Bybit" className="exchange-logo" />
//               </button>
//               <button
//                 className="exchange-button"
//                 onClick={() => console.log('Bitget selected')}
//               >
//                 <img src="../src/assets/bitget-logo.png" alt="Bitget" className="exchange-logo" />
//               </button>
//             </div>
//             <div className="button-group">
//               <button className="submit-button" onClick={handleNext}>Next</button>
//               <button className="cancel-button" onClick={onClose}>Cancel</button>
//             </div>
//           </>
//         ) : (
//           <>
//             <h2 className="add-exchange-title">Enter API Key</h2>
//             <div className="api-input-group">
//               <label htmlFor="api-key">API Key:</label>
//               <input
//                 type="text"
//                 id="api-key"
//                 value={apiKey}
//                 onChange={(e) => setApiKey(e.target.value)}
//               />
//             </div>
//             <div className="button-group">
//               <button className="submit-button" onClick={handleApiSubmit}>Submit</button>
//               <button className="cancel-button" onClick={onClose}>Cancel</button>
//             </div>
//           </>
//         )}
//       </div>
//     </div>
//   );
// };

// export default AddExchange;


import React, { useState } from 'react';
import './AddExchange.css';
// import BinanceLogo from './assets/binance-logo.png';
// import BybitLogo from './assets/bybit-logo.png';
// import BitgetLogo from './assets/bitget-logo.png';

const AddExchange = ({ onClose }) => {
  const [showNextStep, setShowNextStep] = useState(false);
  const [selectedExchange, setSelectedExchange] = useState(null);
  const [apiKey, setApiKey] = useState('');

  const handleExchangeClick = (exchange) => {
    setSelectedExchange(exchange);
    console.log(`${exchange} selected`);
  };

  const handleNext = () => {
    if (selectedExchange) {
      setShowNextStep(true);
    } else {
      alert('Please select an exchange before proceeding.');
    }
  };

  const handleApiSubmit = () => {
    console.log(`API Key for ${selectedExchange}:`, apiKey);
    onClose(); // Close the popup after submission
  };

  return (
    <div className="add-exchange-overlay">
      <div className="add-exchange-container">
        {!showNextStep ? (
          <>
            <h2 className="add-exchange-title">Add Exchange</h2>
            <div className="exchange-buttons">
              <button
                className={`exchange-button ${selectedExchange === 'Binance' ? 'selected' : ''}`}
                onClick={() => handleExchangeClick('Binance')}
              >
                <img src="../src/assets/binance-logo.png" alt="Binance" className="exchange-logo" />
              </button>
              <button
                className={`exchange-button ${selectedExchange === 'Bybit' ? 'selected' : ''}`}
                onClick={() => handleExchangeClick('Bybit')}
              >
                <img src="../src/assets/bybit-logo.png" alt="Bybit" className="exchange-logo" />
              </button>
              <button
                className={`exchange-button ${selectedExchange === 'Bitget' ? 'selected' : ''}`}
                onClick={() => handleExchangeClick('Bitget')}
              >
                <img src="../src/assets/bitget-logo.png" alt="Bitget" className="exchange-logo" />
              </button>
            </div>
            <div className="button-group">
              <button className="submit-button" onClick={handleNext}>Next</button>
              <button className="cancel-button" onClick={onClose}>Cancel</button>
            </div>
          </>
        ) : (
          <>
            <h2 className="add-exchange-title">Enter API Key</h2>
            <div className="api-input-group">
              <label htmlFor="api-key">API Key:</label>
              <input
                type="text"
                id="api-key"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
            </div>
            <div className="button-group">
              <button className="submit-button" onClick={handleApiSubmit}>Submit</button>
              <button className="cancel-button" onClick={onClose}>Cancel</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default AddExchange;
