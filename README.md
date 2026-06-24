# ALU Logo Blockchain Protection Project

This project protects the ALU official logo on Ethereum using two smart contracts. `ALUAssetRegistry` registers the logo as a unique ERC-721 NFT with a permanent SHA-256 fingerprint, while `ALULogoToken` issues ERC-20 ownership-share tokens that represent fractional ownership of that same asset.

## Registered ALU Logo Hash

The official ALU logo used in this project is included as `alu-logo.png`.

SHA-256:

`727b0a610a5e22c083efc8b467c1580cad4b2626d8a6171d686a99d6a220a560`

`bytes32` value passed to the contract:

`0x727b0a610a5e22c083efc8b467c1580cad4b2626d8a6171d686a99d6a220a560`

## Project Structure

- `contracts/ALUAssetRegistry.sol`: ERC-721 asset registration contract
- `contracts/ALULogoToken.sol`: ERC-20 tokenisation contract
- `scripts/hash-logo.js`: Generates the SHA-256 hash of `alu-logo.png`
- `scripts/deploy.js`: Deploys both contracts and registers the ALU logo
- `test/ALUAssetRegistry.test.js`: Eight automated tests
- `hardhat.config.js`: Hardhat configuration

## Setup

1. Install dependencies:

```bash
npm install
```

2. Add the real ALU logo file to the project root as `alu-logo.png`.

3. Generate the SHA-256 hash:

```bash
npm run hash:logo
```

4. Compile the contracts:

```bash
npm run compile
```

5. Run the automated tests:

```bash
npm test
```

6. Start a local blockchain:

```bash
npm run node
```

7. In a new terminal, deploy both contracts and register the logo:

```bash
ALU_LOGO_HASH=0x727b0a610a5e22c083efc8b467c1580cad4b2626d8a6171d686a99d6a220a560 npx hardhat run scripts/deploy.js --network localhost
```

## Versions Used

- Node.js: tested with `v25.9.0` locally available in this workspace
- Hardhat: `^2.22.10`
- Solidity: `0.8.24`
- OpenZeppelin Contracts: `^5.0.2`

## How the Contracts Relate

`ALUAssetRegistry` proves that a specific ALU logo file existed in a specific form at registration time. `ALULogoToken` builds on that by representing ownership shares of the registered logo with fungible ERC-20 tokens. The NFT identifies the asset itself, while the ERC-20 token models shared stake in that asset.

## Development Notes

- The deployment script intentionally requires `ALU_LOGO_HASH` so the exact file fingerprint used at submission time is explicit.
- The included `alu-logo.png` was downloaded from ALU's public website and hashed locally before being used in the project.
- The report and evidence files are included alongside the code for submission packaging.
