# ALU Logo Registry & Ownership dApp

This project is a complete decentralized application (dApp) built for Assignment 2. It reuses the Formative 1 smart contracts and adds a browser frontend so non-technical users can connect a wallet, register the ALU logo on-chain, verify a logo file without leaving the browser, and view or distribute ALUT ownership shares.

## What the dApp does

The solution has two blockchain contracts and one frontend application:

- `contracts/ALUAssetRegistry.sol`: ERC-721 contract that stores a unique on-chain record of a logo file using its SHA-256 hash.
- `contracts/ALULogoToken.sol`: ERC-20 contract that represents logo ownership shares as `1,000,000` ALUT tokens.
- `frontend/`: multi-page browser dApp built with plain HTML, CSS, and JavaScript using `ethers.js`.

The frontend talks to both contracts through their ABI definitions and deployed addresses:

- The Register page hashes the uploaded image locally in the browser and sends `registerAsset()` transactions to `ALUAssetRegistry`.
- The Verify page hashes a file locally or accepts a pasted hash, then calls `verifyLogoIntegrity()` and `getAsset()` as read-only blockchain calls.
- The Dashboard page reads `totalSupply()`, `balanceOf()`, `ownershipPercentage()`, and `owner()` from `ALULogoToken`, and lets the owner call `distributeShares()`.

## Registered ALU Logo Hash

The included `alu-logo.png` file is the logo used for deployment.

- SHA-256: `727b0a610a5e22c083efc8b467c1580cad4b2626d8a6171d686a99d6a220a560`
- `bytes32` value: `0x727b0a610a5e22c083efc8b467c1580cad4b2626d8a6171d686a99d6a220a560`

## Project Structure

- `contracts/ALUAssetRegistry.sol`
- `contracts/ALULogoToken.sol`
- `scripts/deploy.js`
- `scripts/hash-logo.js`
- `scripts/serve-frontend.js`
- `scripts/make_screenshots.py`
- `scripts/build_pdf.py`
- `test/ALUAssetRegistry.test.js`
- `frontend/index.html`
- `frontend/register.html`
- `frontend/verify.html`
- `frontend/dashboard.html`
- `alu-logo.png`
- `hardhat.config.js`
- `Project_Report.pdf`

## Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Generate the logo hash

```bash
npm run hash:logo
```

### 3. Compile the contracts

```bash
npm run compile
```

### 4. Run the automated tests

```bash
npm test
```

### 5. Start the local blockchain

```bash
npm run node
```

This starts a Hardhat JSON-RPC node at `http://127.0.0.1:8545` with pre-funded test wallets.

### 6. Deploy the contracts and register the official logo

In a second terminal:

```bash
ALU_LOGO_HASH=0x727b0a610a5e22c083efc8b467c1580cad4b2626d8a6171d686a99d6a220a560 npm run deploy -- --network localhost
```

The deploy script will:

- deploy `ALUAssetRegistry`
- register the official ALU logo as token ID `1`
- deploy `ALULogoToken`
- refresh `frontend/js/deployment.js` with the active contract addresses

### 7. Run the frontend development server

In a third terminal:

```bash
npm run frontend:serve
```

Then open:

- `http://127.0.0.1:4173`

## Wallet connection and frontend usage

### Connect a wallet

1. Open the dApp home page.
2. Click `Connect Wallet`.
3. Approve the connection in MetaMask, Coinbase Wallet, or another injected browser wallet.
4. If needed, switch the wallet to the local Hardhat network:
   - RPC URL: `http://127.0.0.1:8545`
   - Chain ID: `31337`
   - Currency symbol: `ETH`
5. Once connected, the header shows the shortened wallet address and the user's ALUT balance.

If no wallet is installed, the app disables the connect button and shows a helpful message.

### Use the Register page

1. Go to `Register Logo`.
2. Upload an image file.
3. The browser computes the SHA-256 hash locally with the Web Crypto API.
4. Confirm the image preview, asset name, and file type.
5. Click `Register Logo`.
6. Approve the transaction in the wallet.
7. After confirmation, the app shows the new token ID.

### Use the Verify page

This page works without a wallet.

1. Upload a file or paste a `0x`-prefixed SHA-256 hash.
2. Leave token ID as `1` for the official ALU logo, or enter another token ID.
3. Click `Verify Against Blockchain`.
4. The page shows a clear authentic or modified verdict.
5. If the hash matches, the page also shows the on-chain metadata.

### Use the Token Dashboard

1. Open `Token Dashboard`.
2. Read the total supply, contract owner, wallet balance, and ownership percentage.
3. View example ownership rows for sample Hardhat wallets.
4. If the connected account is the contract owner, use the distribution form to send ALUT shares to another wallet.
5. Approve the transaction in the wallet.
6. The dashboard refreshes the balances and percentages after confirmation.

## ABI and contract integration summary

The frontend uses the contracts' ABI definitions embedded in `frontend/js/config.js`.

- An ABI describes the callable functions, events, inputs, and outputs of a smart contract.
- `ethers.js` uses the ABI plus the deployed contract address to create JavaScript contract objects.
- Read-only calls such as `totalSupply()`, `balanceOf()`, `verifyLogoIntegrity()`, and `getAsset()` do not require gas or signatures.
- State-changing functions such as `registerAsset()` and `distributeShares()` require the user to approve and sign a transaction in their wallet.

## Automated tests

The project includes all thirteen required tests in `test/ALUAssetRegistry.test.js`:

- 8 smart contract tests from Formative 1
- 5 additional frontend integration-style tests for the Assignment 2 flows

The added tests cover:

- reading and formatting the `1,000,000` total supply
- browser-style SHA-256 hashing into `bytes32`
- successful verification with the correct logo hash
- failure verification with an incorrect hash
- updated balances and percentages after `distributeShares()`

## Versions used

- Node.js: `v25.9.0`
- Hardhat: `^2.22.10`
- Solidity: `0.8.24`
- OpenZeppelin Contracts: `^5.0.2`
- Frontend: plain `HTML/CSS/JavaScript`
- Web3 library: `ethers.js` via CDN `6.13.2`

## Known issues and limitations

- The dApp is configured for a local Hardhat network, not a public testnet or mainnet.
- WalletConnect is not implemented; the app currently relies on injected browser wallets.
- The example ownership table uses standard Hardhat sample addresses for demonstration.
- Contract addresses in `frontend/js/deployment.js` assume the current local deployment and should be regenerated after redeploying.

## External resources used

- Hardhat documentation for local blockchain development
- OpenZeppelin Contracts for ERC-721, ERC-20, and Ownable base contracts
- Ethers.js documentation for frontend wallet and contract interaction
