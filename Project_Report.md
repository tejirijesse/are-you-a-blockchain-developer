# Project Report

## Abstract

This project delivers a complete ALU logo protection dApp that combines two Solidity contracts with a browser frontend. The application lets users connect a wallet, register a logo on-chain using its SHA-256 fingerprint, verify authenticity without any server, and view or distribute ALUT ownership shares through a simple web interface.

## Introduction

The smart contracts from Formative 1 already solved part of the problem: they created an immutable blockchain record for the ALU logo and represented ownership shares with tokens. The gap was usability. A student, administrator, or partner organisation would not normally use a terminal, run Hardhat commands, or call contract functions manually. This dApp fills that gap by turning the contracts into a usable product.

The frontend acts as the bridge between people and blockchain logic. It hides the complexity of contract calls behind a clean interface, uses wallet-based signatures only when needed, and keeps file hashing inside the browser so the logo itself never has to be uploaded to a server.

## Architecture Overview

The system has four parts:

- Browser frontend: built with plain HTML, CSS, and JavaScript.
- Web3 wallet: MetaMask or another injected browser wallet used for identity and transaction signing.
- `ALUAssetRegistry`: ERC-721 contract that stores the logo metadata and SHA-256 fingerprint.
- `ALULogoToken`: ERC-20 contract that stores ownership-share balances and protects `distributeShares()` with `onlyOwner`.

The frontend loads the ABI definitions and deployed contract addresses, creates `ethers.js` contract instances, and chooses between read-only provider calls or signer-backed transactions depending on the action.

Typical flow:

1. The user opens the dApp in the browser.
2. The frontend connects to the local Hardhat blockchain through either the wallet provider or a fallback JSON-RPC provider.
3. For read-only actions such as verification or dashboard statistics, the frontend calls the contracts without gas or signatures.
4. For write actions such as registering a logo or distributing shares, the frontend asks the wallet to sign a transaction.
5. The blockchain confirms the transaction and the frontend refreshes the UI with updated on-chain data.

## Feature Walkthrough

### Home page

The home page introduces the three main journeys of the dApp: register, verify, and dashboard. It also shows wallet state in the header and explains the role of in-browser hashing and tokenised ownership. This page gives non-technical users a clear entry point into the system.

### Register Logo page

The Register page implements the upload-and-register workflow.

- The user selects an image file.
- The browser reads the file locally and computes a SHA-256 digest with the Web Crypto API.
- The hash is formatted as a `0x`-prefixed `bytes32` value.
- The page previews the image and pre-fills the hash for submission.
- After wallet approval, the frontend calls `registerAsset()` and displays the minted token ID.

Generating the hash in the browser matters because the file never leaves the user's device. That keeps the design serverless and reduces privacy and trust concerns.

If a user tries to register the same hash twice, the smart contract rejects the transaction with `Asset hash already registered`, and the frontend surfaces that error clearly.

### Verify Logo page

The Verify page is the most public-facing part of the project.

- A user can upload a file or paste a known hash.
- The page computes the SHA-256 digest locally if a file is uploaded.
- The frontend calls `verifyLogoIntegrity()` using the official token ID.
- If the result is authentic, the page also reads metadata from `getAsset()` and shows the asset name, file type, registration date, and registering wallet.
- If the result fails, the page shows a red warning instead of technical error text.

This page does not require a wallet because it performs read-only blockchain calls. A read-only call only inspects on-chain data, so no state changes occur, no gas is spent, and no signature is needed.

A real-world use case would be a student club, external printer, or partner institution that receives a logo file and wants to check whether it matches ALU's official version before using it in a poster, website, or event banner.

### Token Dashboard page

The Dashboard page reads live data from `ALULogoToken`.

It shows:

- total token supply: `1,000,000 ALUT`
- connected wallet balance
- connected wallet ownership percentage
- contract owner address
- example ownership rows for sample Hardhat accounts

If the connected account is the owner, the page also shows a share-distribution form. That form validates the recipient address and amount, then calls `distributeShares()` and refreshes balances after confirmation.

The `onlyOwner` modifier protects this function at the smart contract level. If a non-owner wallet tries to call it, the transaction reverts and the token transfer never happens.

A concrete example is ALU allocating shares to a brand office, central administration team, or a governance body. Holding ALUT tokens would represent a stake in the tokenised ownership model used by the project.

If ALU wanted token holders to vote proportionally, the contract would need governance logic such as proposal creation, vote tracking, quorum rules, and vote weighting by token balance.

## Wallet and Web3 Integration

The frontend uses `ethers.js` as the Web3 library.

An ABI is the interface description of a smart contract. It tells the frontend which functions exist, what arguments they expect, and what values they return. Without the ABI, the browser would know the contract address but would not know how to encode calls or decode responses.

The dApp uses two kinds of blockchain interactions:

- Read-only calls: `totalSupply()`, `balanceOf()`, `owner()`, `ownershipPercentage()`, `verifyLogoIntegrity()`, and `getAsset()`. These use a provider and cost no gas.
- Transactions: `registerAsset()` and `distributeShares()`. These use a signer from the connected wallet and require the user to approve the action.

The user must sign transactions in the wallet because the wallet controls the private key. The application must never hold or use that private key on the user's behalf. Signing proves the user explicitly approved the state change.

## Verification Page

The verification workflow is fully serverless.

When a file is uploaded, the browser reads the raw bytes and passes them to the Web Crypto API for SHA-256 hashing. The digest is then converted into a hexadecimal `bytes32` string that can be compared directly with the on-chain value. Because the file hashing happens in the browser, there is no need for backend storage, upload handling, or server-side processing.

Users can trust the result because the comparison is made against an on-chain record that was created earlier and cannot be silently changed by the frontend. If the uploaded file matches the registered hash exactly, the dApp returns an authentic verdict. If the file differs by even one bit, the hash changes and verification fails.

## Token Dashboard

The token dashboard shows how the ERC-20 contract translates ownership into readable statistics.

The page reads the total supply and wallet balances directly from the blockchain, then calculates ownership percentages through the contract's `ownershipPercentage()` function. This means the frontend is not inventing percentages locally; it is displaying the contract's own result.

`distributeShares()` is protected by `onlyOwner`, which ensures only the token contract owner can send shares from the owner allocation. If a non-owner attempts the call, the transaction reverts and the balances remain unchanged.

## Test Results

The final test suite contains all thirteen required tests.

The original eight tests cover the contract logic:

1. successful asset registration
2. duplicate hash rejection
3. authentic hash verification
4. modified hash verification
5. metadata retrieval
6. full ALUT supply minted to the owner
7. successful share distribution
8. correct ownership percentage calculation

The five added tests cover frontend-aligned flows:

9. dashboard total supply reads as `1,000,000`
10. browser-style SHA-256 hashing returns a valid `bytes32`
11. verify page confirms the authentic logo
12. verify page flags an incorrect hash
13. owner dashboard distribution refreshes balances and percentages

## Conclusion

This assignment showed that smart contracts alone are not enough to make a blockchain solution useful to ordinary users. The most important learning outcome was how a frontend, wallet, and contracts work together: the frontend handles usability, the wallet handles identity and signatures, and the contracts enforce trust and rules.

With more time, the next improvements would be a public testnet deployment, stronger form validation, wallet options beyond injected providers, and a governance extension for token-holder voting.

## GitHub Link

[https://github.com/tejirijesse/are-you-a-blockchain-developer](https://github.com/tejirijesse/are-you-a-blockchain-developer)
