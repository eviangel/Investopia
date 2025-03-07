import React, { useState, useEffect } from "react";
import "./Notifications.scss"; // Import the SCSS file

const Notifications = ({userId}) => {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const fetchBestWorstAssets = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/portfolio/top-assets-significant?user_id=${userId}&min_price_change=5&top_n=5`); 
        const data = await response.json();
        // Extract best performing assets
        if (!Array.isArray(data.top_assets)) {
          console.error("Unexpected API structure", data);
          return;
        }

        console.log("Number of significant assets:", data.top_assets.length);
        if (data.top_assets.length > 0) {
          const newNotifications = data.top_assets.map(asset => ({
            id: asset.Asset,
            type: "gain",
            message: `${asset.Asset} has increased by ${asset.Price_Change_Percentage.toFixed(2)}% in the last 24 hours!`
          }));
          setNotifications(newNotifications);
        }
      } catch (error) {
        console.error("Error fetching best and worst assets:", error);
      }
    };

    // Fetch data initially and set interval to check every 5 minutes
    fetchBestWorstAssets();
    const interval = setInterval(fetchBestWorstAssets, 300000); // 300000 ms = 5 minutes

    return () => clearInterval(interval);
  }, []);

  const handleDismiss = (id) => {
    setNotifications(notifications.filter(notification => notification.id !== id));
  };

  const handleDismissAll = () => {
    setNotifications([]);
  };

  return (
    <div className="notification-container">
      <h2 className="text-center">My Notifications</h2>
      {notifications.length > 0 ? (
        <p className="dismiss text-right">
          <button id="dismiss-all" onClick={handleDismissAll}>Dismiss All</button>
        </p>
      ) : (
        <h4 className="text-center all-caught-up">All caught up!</h4>
      )}

      {notifications.map(({ id, type, message }) => (
        <div key={id} className={`card notification-card notification-${type}`}>
          <div className="card-body">
            <table>
              <tbody>
                <tr>
                  <td style={{ width: "70%" }}>
                    <div className="card-title">{message}</div>
                  </td>
                  <td style={{ width: "30%" }}>
                    <button className="btn btn-primary">View</button>
                    <button className="btn btn-danger dismiss-notification" onClick={() => handleDismiss(id)}>Dismiss</button>
                  </td>
                </tr>
                </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Notifications;
