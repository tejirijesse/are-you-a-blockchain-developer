# Project Report Draft

## Abstract

This project protects the ALU official logo by registering its file fingerprint on an Ethereum-compatible blockchain and issuing share tokens that represent ownership stakes in the logo. The solution combines an ERC-721 NFT for unique asset registration with an ERC-20 token for tokenised ownership, creating a tamper-resistant record that can be verified publicly.

## Introduction

ALU needs a reliable way to prove which logo file is the official version and when it was registered. A blockchain-based record helps because once data is written and confirmed it is extremely difficult to alter retroactively. That gives ALU stronger public verifiability than a private database, since anyone can compare a logo file hash to the value stored on-chain. It also complements ordinary copyright registration by adding a technical proof of integrity for the exact digital file.

## Question 1: Cryptocurrency Exchange Platform

This section still needs your personal observations, screenshots, and platform-specific details because the assignment requires you to create or explore an exchange account yourself.

Suggested structure:

1. Account creation and identity verification:
Describe the documents or details requested by the exchange. Explain that exchanges usually verify identity to comply with KYC and AML obligations that help prevent fraud, money laundering, and terrorist financing.

2. Platform exploration:
Pick three assets such as Bitcoin, Ethereum, and Solana. Explain what each is used for and how they differ.

3. Payment methods:
Compare debit card and bank transfer in terms of speed, cost, and convenience.

4. Simulated purchase:
Explain the difference between a market order and a limit order, then describe the steps you followed for a sample $100 purchase.

5. Transaction history:
Describe the date, asset, amount, fee, status, and transaction hash shown in the record.

6. Security features:
Explain features such as two-factor authentication and withdrawal confirmation.

## Blockchain Setup

The smart contract environment was built with Hardhat, a local Ethereum development framework for compiling, testing, and deploying Solidity contracts. Hardhat can start a local blockchain node on the developer's computer, which creates funded test accounts for safe experimentation without spending real ETH. Developers prefer a local blockchain during development because it is fast, free, and allows repeated testing and debugging without affecting the live Ethereum network.

A wallet address is a unique blockchain identifier that represents an account capable of holding assets, deploying contracts, or sending transactions. On the local Hardhat node, several test wallet addresses are generated automatically to simulate different users.

## Smart Contract Explanation

### ALUAssetRegistry

The `ALUAssetRegistry` contract extends the ERC-721 NFT standard because the ALU logo is a single unique asset rather than a pool of interchangeable units. Each registered asset stores:

- `assetName`: the human-readable asset name
- `fileType`: the file format, such as `png`
- `contentHash`: the SHA-256 hash of the exact logo file
- `registeredBy`: the wallet address that submitted the registration
- `registeredAt`: the Unix timestamp recorded at registration time

The contract uses one mapping to store metadata for each token ID and another mapping to prevent duplicate registration of the same file hash.

### registerAsset()

`registerAsset()` checks whether the same SHA-256 hash has already been used. If it has, the transaction is reverted with the message `Asset hash already registered`. If the hash is new, the contract increments the token ID counter, mints a new NFT to the caller, stores the metadata, marks the hash as used, emits an `AssetRegistered` event, and returns the token ID.

### verifyLogoIntegrity()

`verifyLogoIntegrity()` is a view function that compares a user-supplied file hash with the stored on-chain hash for a token ID. If they match, it returns `true` and the message `Logo is authentic.` If they do not match, it returns `false` and the message `Warning: logo does not match.` Because it only reads blockchain state, it does not consume gas when called locally.

### getAsset()

`getAsset()` returns the full metadata struct for a registered token so anyone can inspect its registration details at any time.

### SHA-256 Hash of the Logo

Replace this section with your real result after placing the official ALU logo file in the project as `alu-logo.png` and running:

```bash
npm run hash:logo
```

Record both the screenshot and the final value here:

`0xREPLACE_WITH_REAL_LOGO_HASH`

### Why SHA-256 Matters

A SHA-256 hash is a fixed-length fingerprint generated from file content. Even if only one pixel of the logo changes, the resulting hash changes completely. That makes the hash useful for verifying whether a file is the exact original version.

### Why Blockchain Data Is Hard to Change

Blockchain records are stored across many nodes and linked together cryptographically in blocks. Once a transaction is confirmed, changing it would require rewriting the chain history and reaching consensus again, which is what gives the stored data its immutability in normal practice.

## Tokenisation

Tokenisation means representing rights or ownership in a real or digital asset as blockchain tokens. In this project, the ALU logo itself is represented as a unique ERC-721 NFT, while shared ownership is represented separately using `ALULogoToken`, an ERC-20 token called ALUT.

ERC-721 was used for logo registration because the logo is one unique asset and each NFT has its own identity. ERC-20 was used for ownership shares because the shares are interchangeable and divisible as a group. If a faculty member holds 100,000 ALUT tokens out of a total supply of 1,000,000, that means the faculty member holds 10% of the tokenised ownership supply.

Possible stakeholders who could receive ALUT tokens include university administration, brand management staff, faculty, or other authorised institutional participants. In practice, those tokens could represent governance rights, revenue-sharing arrangements, or internal ownership tracking, depending on the policy rules ALU sets around them.

## Test Results

The project includes eight automated tests that cover:

1. Successful logo registration
2. Rejection of duplicate hashes
3. Successful integrity verification with the correct hash
4. Failed integrity verification with an incorrect hash
5. Correct metadata retrieval
6. Full token minting to the owner on deployment
7. Share distribution to a recipient
8. Correct ownership percentage calculation

Add a screenshot of all eight tests passing after running:

```bash
npm test
```

## Conclusion

This project demonstrates how blockchain can protect a digital asset by storing a permanent fingerprint and pairing that record with tokenised ownership. If more time were available, the next improvement would be to build the dApp interface mentioned in the assignment, add metadata storage links, and extend ownership logic with governance or transfer restrictions.

## GitHub Link

Replace this placeholder with your public repository URL:

`https://github.com/your-username/your-repository`

## Video Link

Add the video presentation link here before exporting the report to PDF.
