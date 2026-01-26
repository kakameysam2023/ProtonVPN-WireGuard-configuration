# 🛡️ ProtonVPN WireGuard Config Auto-Fetcher

This project provides an automated solution using Python/Selenium and GitHub Actions to regularly fetch and update the latest **WireGuard** configuration files from a ProtonVPN account.

The downloaded configurations are automatically updated in this repository and are pushed to the corresponding Telegram channel for immediate access.

# 📢 Telegram Channel

All final results are automatically compressed into a ZIP file and uploaded to our Telegram channel:

🔹 **Main Channel:** [DeltaKroneckerFreedom](https://t.me/GitKroneckerDelta)  

---

## 💻 Usage Guide (Windows Focus)

These WireGuard configuration files (`.conf`) are optimized for seamless use in a Windows environment.

### 📌 Recommended Tool for Optimal Performance (Windows)

For the best performance, stability, and compatibility on Windows, it is **highly recommended** to use the following client instead of the official WireGuard application:

* **Wiresock VPN Client (Recommended)**
    * **Link:** [https://www.wiresock.net](https://www.wiresock.net)

Wiresock is a robust client that supports the WireGuard protocol, offering superior performance in connection management and traffic handling on Windows systems.

### ⬇️ Accessing the Config Files:

The files are available both on the GitHub repository and through the Telegram channel.

1.  **Download Source:** Choose your preferred method:
    * **Via GitHub:** Download the file directly from this repository:
      [**Download Full WireGuard Config Package**](https://github.com/Delta-Kronecker/ProtonVPN-WireGuard-configuration/raw/refs/heads/main/ProtonVPN_WireGuard_Configs.zip)
    * **Via Telegram:** Download the latest ZIP file uploaded to the channel [**ProtonConfigBot - VPN Configs**](https://t.me/GitKroneckerDelta).

2.  **Extraction:** Extract the downloaded ZIP file. The files are organized into folders by two-letter country codes (e.g., `US`, `DE`, `NL`).
3.  **Client Use:**
    * Ensure the Wiresock client is installed and running.
    * Import your desired `.conf` files from the country folders into Wiresock and connect.
