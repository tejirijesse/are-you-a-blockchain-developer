// ---------------------------------------------------------------------------
// Shared wallet + contract integration for the ALU Logo dApp (Part A)
// ---------------------------------------------------------------------------
// Loaded on every page after config.js. Depends on ethers.js (v6, via CDN)
// and the global window.ALU_CONFIG object exposed by config.js.
//
// Responsibilities:
//   * Detect an injected web3 provider (MetaMask / Coinbase / others).
//   * Connect / disconnect the wallet and remember the connected account.
//   * Shorten and display the account address (0x1234...abcd).
//   * Read and display the connected wallet's ALUT balance.
//   * React to account and network changes.
//   * Build read-only and signer contract instances from the embedded ABIs.
// ---------------------------------------------------------------------------

(function () {
  "use strict";

  const CONFIG = window.ALU_CONFIG;
  if (!CONFIG) {
    console.error("ALU_CONFIG is missing. Make sure config.js loads before app.js.");
    return;
  }

  // Central place to keep everything a page might need about the session.
  const state = {
    provider: null, // ethers BrowserProvider wrapping the injected wallet
    signer: null, // ethers Signer for the connected account
    account: null, // checksum address string, or null when disconnected
    chainId: null, // number, the current network chainId
    isOwner: false, // whether the connected account owns the token contract
  };

  // Simple event bus so individual pages can react to wallet changes without
  // reaching into this module's internals.
  const listeners = {
    connect: [],
    disconnect: [],
    accountChanged: [],
    networkChanged: [],
  };

  function on(eventName, callback) {
    if (listeners[eventName]) {
      listeners[eventName].push(callback);
    }
  }

  function emit(eventName, payload) {
    (listeners[eventName] || []).forEach(function (cb) {
      try {
        cb(payload);
      } catch (err) {
        console.error("Listener for " + eventName + " threw:", err);
      }
    });
  }

  // -------------------------------------------------------------------------
  // Provider detection
  // -------------------------------------------------------------------------
  // MetaMask, Coinbase Wallet and most browser wallets inject window.ethereum.
  // When several wallets are installed they populate window.ethereum.providers,
  // so we prefer whichever one the user asks for but fall back to the default.
  function getInjectedProvider(preferred) {
    const injected = window.ethereum;
    if (!injected) {
      return null;
    }

    if (Array.isArray(injected.providers) && injected.providers.length) {
      if (preferred === "coinbase") {
        const cb = injected.providers.find(function (p) {
          return p.isCoinbaseWallet;
        });
        if (cb) return cb;
      }
      if (preferred === "metamask") {
        const mm = injected.providers.find(function (p) {
          return p.isMetaMask;
        });
        if (mm) return mm;
      }
      // Otherwise use the first provider the browser exposes.
      return injected.providers[0];
    }

    return injected;
  }

  function hasWallet() {
    return Boolean(window.ethereum);
  }

  // -------------------------------------------------------------------------
  // Formatting helpers
  // -------------------------------------------------------------------------
  function shortenAddress(address) {
    if (!address || address.length < 10) {
      return address || "";
    }
    return address.slice(0, 6) + "..." + address.slice(-4);
  }

  // MAX_SUPPLY is stored as a raw integer (no 18-decimal scaling), so token
  // amounts are whole numbers. We format with thousands separators for display.
  function formatTokenAmount(rawValue) {
    try {
      return BigInt(rawValue).toLocaleString("en-US");
    } catch (err) {
      return String(rawValue);
    }
  }

  // -------------------------------------------------------------------------
  // Contract factories
  // -------------------------------------------------------------------------
  // Read-only instances use a provider and never prompt for a signature; they
  // are used for view calls such as balanceOf, totalSupply and getAsset.
  function getRegistryReadContract(providerOverride) {
    const runner = providerOverride || state.provider || getFallbackProvider();
    return new ethers.Contract(
      CONFIG.CONTRACT_ADDRESSES.assetRegistry,
      CONFIG.ALU_ASSET_REGISTRY_ABI,
      runner
    );
  }

  function getTokenReadContract(providerOverride) {
    const runner = providerOverride || state.provider || getFallbackProvider();
    return new ethers.Contract(
      CONFIG.CONTRACT_ADDRESSES.logoToken,
      CONFIG.ALU_LOGO_TOKEN_ABI,
      runner
    );
  }

  // Signer instances are needed for state-changing transactions such as
  // registerAsset and distributeShares, which require gas and a signature.
  function getRegistryWriteContract() {
    if (!state.signer) {
      throw new Error("Connect a wallet before sending a transaction.");
    }
    return new ethers.Contract(
      CONFIG.CONTRACT_ADDRESSES.assetRegistry,
      CONFIG.ALU_ASSET_REGISTRY_ABI,
      state.signer
    );
  }

  function getTokenWriteContract() {
    if (!state.signer) {
      throw new Error("Connect a wallet before sending a transaction.");
    }
    return new ethers.Contract(
      CONFIG.CONTRACT_ADDRESSES.logoToken,
      CONFIG.ALU_LOGO_TOKEN_ABI,
      state.signer
    );
  }

  // The public verification page must work without a wallet, so it can read
  // the chain through a plain JSON-RPC provider pointed at the local node.
  function getFallbackProvider() {
    return new ethers.JsonRpcProvider(CONFIG.NETWORK.rpcUrl);
  }

  // -------------------------------------------------------------------------
  // Balance + ownership
  // -------------------------------------------------------------------------
  async function fetchBalance(address) {
    const token = getTokenReadContract();
    const balance = await token.balanceOf(address);
    return balance; // BigInt
  }

  async function refreshOwnership() {
    if (!state.account) {
      state.isOwner = false;
      return false;
    }
    try {
      const token = getTokenReadContract();
      const ownerAddress = await token.owner();
      state.isOwner =
        ownerAddress.toLowerCase() === state.account.toLowerCase();
    } catch (err) {
      console.error("Could not read contract owner:", err);
      state.isOwner = false;
    }
    return state.isOwner;
  }

  // Update any shared UI elements a page chooses to include. Elements are
  // optional: pages opt in by adding these ids to their markup.
  async function updateWalletUI() {
    const addressEl = document.getElementById("wallet-address");
    const balanceEl = document.getElementById("wallet-balance");
    const connectBtn = document.getElementById("connect-wallet");
    const statusEl = document.getElementById("wallet-status");

    if (!state.account) {
      if (addressEl) addressEl.textContent = "";
      if (balanceEl) balanceEl.textContent = "";
      if (statusEl) statusEl.textContent = "Not connected";
      if (connectBtn) connectBtn.textContent = "Connect Wallet";
      return;
    }

    if (addressEl) addressEl.textContent = shortenAddress(state.account);
    if (connectBtn) connectBtn.textContent = "Connected";
    if (statusEl) statusEl.textContent = "Connected";

    if (balanceEl) {
      balanceEl.textContent = "Loading...";
      try {
        const balance = await fetchBalance(state.account);
        balanceEl.textContent = formatTokenAmount(balance) + " ALUT";
      } catch (err) {
        console.error("Failed to load balance:", err);
        balanceEl.textContent = "Balance unavailable";
      }
    }
  }

  // -------------------------------------------------------------------------
  // Network handling
  // -------------------------------------------------------------------------
  function isCorrectNetwork() {
    return state.chainId === CONFIG.NETWORK.chainId;
  }

  function renderNetworkWarning() {
    const warningEl = document.getElementById("network-warning");
    if (!warningEl) return;

    if (state.account && !isCorrectNetwork()) {
      warningEl.style.display = "block";
      warningEl.textContent =
        "Wrong network. Please switch your wallet to " +
        CONFIG.NETWORK.chainName +
        " (chainId " +
        CONFIG.NETWORK.chainId +
        ").";
    } else {
      warningEl.style.display = "none";
      warningEl.textContent = "";
    }
  }

  // Ask the wallet to switch to the local Hardhat network. If the network is
  // unknown to the wallet, offer to add it.
  async function switchNetwork() {
    if (!state.provider) return;
    const injected = state.provider.provider || window.ethereum;
    try {
      await injected.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: CONFIG.NETWORK.chainIdHex }],
      });
    } catch (switchError) {
      if (switchError && switchError.code === 4902) {
        await injected.request({
          method: "wallet_addEthereumChain",
          params: [
            {
              chainId: CONFIG.NETWORK.chainIdHex,
              chainName: CONFIG.NETWORK.chainName,
              rpcUrls: [CONFIG.NETWORK.rpcUrl],
              nativeCurrency: {
                name: CONFIG.NETWORK.currencySymbol,
                symbol: CONFIG.NETWORK.currencySymbol,
                decimals: 18,
              },
            },
          ],
        });
      } else {
        throw switchError;
      }
    }
  }

  // -------------------------------------------------------------------------
  // Connect / disconnect
  // -------------------------------------------------------------------------
  async function connect(preferred) {
    if (!hasWallet()) {
      throw new Error(
        "No web3 wallet detected. Install MetaMask or Coinbase Wallet to continue."
      );
    }

    const injected = getInjectedProvider(preferred);
    if (!injected) {
      throw new Error("Could not find a compatible wallet provider.");
    }

    state.provider = new ethers.BrowserProvider(injected);

    // Prompt the user to grant account access.
    const accounts = await state.provider.send("eth_requestAccounts", []);
    if (!accounts || !accounts.length) {
      throw new Error("No accounts were authorised.");
    }

    state.signer = await state.provider.getSigner();
    state.account = ethers.getAddress(accounts[0]);

    const network = await state.provider.getNetwork();
    state.chainId = Number(network.chainId);

    // Wire up wallet events once per connection.
    attachWalletEvents(injected);

    await refreshOwnership();
    await updateWalletUI();
    renderNetworkWarning();

    emit("connect", { account: state.account, chainId: state.chainId });
    return state.account;
  }

  function disconnect() {
    state.provider = null;
    state.signer = null;
    state.account = null;
    state.chainId = null;
    state.isOwner = false;
    updateWalletUI();
    renderNetworkWarning();
    emit("disconnect", {});
  }

  let eventsAttached = false;
  function attachWalletEvents(injected) {
    if (eventsAttached || !injected || !injected.on) return;
    eventsAttached = true;

    injected.on("accountsChanged", async function (accounts) {
      if (!accounts || !accounts.length) {
        disconnect();
        return;
      }
      state.account = ethers.getAddress(accounts[0]);
      if (state.provider) {
        state.signer = await state.provider.getSigner();
      }
      await refreshOwnership();
      await updateWalletUI();
      renderNetworkWarning();
      emit("accountChanged", { account: state.account });
    });

    injected.on("chainChanged", async function (chainIdHex) {
      state.chainId = parseInt(chainIdHex, 16);
      // Rebuild the provider so ethers picks up the new network cleanly.
      if (window.ethereum) {
        state.provider = new ethers.BrowserProvider(injected);
        if (state.account) {
          state.signer = await state.provider.getSigner();
        }
      }
      await updateWalletUI();
      renderNetworkWarning();
      emit("networkChanged", { chainId: state.chainId });
    });
  }

  // If the user previously authorised this site, restore the session silently
  // (without popping up the wallet) so the address persists across pages.
  async function tryEagerConnect() {
    if (!hasWallet()) {
      const statusEl = document.getElementById("wallet-status");
      const connectBtn = document.getElementById("connect-wallet");
      if (statusEl) {
        statusEl.textContent =
          "No wallet detected — install MetaMask or Coinbase Wallet.";
      }
      if (connectBtn) {
        connectBtn.disabled = true;
      }
      updateWalletUI();
      return;
    }
    try {
      const injected = getInjectedProvider();
      const provider = new ethers.BrowserProvider(injected);
      const accounts = await provider.send("eth_accounts", []);
      if (accounts && accounts.length) {
        await connect();
      } else {
        updateWalletUI();
      }
    } catch (err) {
      console.error("Eager connect failed:", err);
      updateWalletUI();
    }
  }

  // -------------------------------------------------------------------------
  // Default wiring for a Connect Wallet button, if the page includes one.
  // -------------------------------------------------------------------------
  function wireConnectButton() {
    const connectBtn = document.getElementById("connect-wallet");
    if (!connectBtn) return;

    connectBtn.addEventListener("click", async function () {
      if (state.account) {
        // Already connected: a second click disconnects the session view.
        disconnect();
        return;
      }
      connectBtn.disabled = true;
      const previousText = connectBtn.textContent;
      connectBtn.textContent = "Connecting...";
      try {
        await connect();
      } catch (err) {
        console.error(err);
        alert(err.message || "Failed to connect wallet.");
        connectBtn.textContent = previousText;
      } finally {
        connectBtn.disabled = false;
      }
    });

    const switchBtn = document.getElementById("switch-network");
    if (switchBtn) {
      switchBtn.addEventListener("click", async function () {
        try {
          await switchNetwork();
        } catch (err) {
          console.error(err);
          alert(err.message || "Failed to switch network.");
        }
      });
    }
  }

  // Auto-initialise once the DOM is ready.
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      wireConnectButton();
      tryEagerConnect();
    });
  } else {
    wireConnectButton();
    tryEagerConnect();
  }

  // -------------------------------------------------------------------------
  // Public API used by the per-page scripts.
  // -------------------------------------------------------------------------
  window.ALU_APP = {
    state: state,
    on: on,
    connect: connect,
    disconnect: disconnect,
    switchNetwork: switchNetwork,
    hasWallet: hasWallet,
    isCorrectNetwork: isCorrectNetwork,
    shortenAddress: shortenAddress,
    formatTokenAmount: formatTokenAmount,
    fetchBalance: fetchBalance,
    refreshOwnership: refreshOwnership,
    updateWalletUI: updateWalletUI,
    getRegistryReadContract: getRegistryReadContract,
    getTokenReadContract: getTokenReadContract,
    getRegistryWriteContract: getRegistryWriteContract,
    getTokenWriteContract: getTokenWriteContract,
    getFallbackProvider: getFallbackProvider,
  };
})();
