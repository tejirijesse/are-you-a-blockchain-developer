const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const logoHash = process.env.ALU_LOGO_HASH;

  if (!logoHash) {
    throw new Error("Set ALU_LOGO_HASH before deploying. Use npm run hash:logo to generate it.");
  }

  if (!/^0x[a-fA-F0-9]{64}$/.test(logoHash)) {
    throw new Error("ALU_LOGO_HASH must be a 32-byte hex value starting with 0x.");
  }

  console.log(`Deploying with account: ${deployer.address}`);

  const Registry = await hre.ethers.getContractFactory("ALUAssetRegistry");
  const registry = await Registry.deploy();
  await registry.waitForDeployment();

  console.log(`ALUAssetRegistry deployed to: ${await registry.getAddress()}`);

  const registerTx = await registry.registerAsset("ALU Official Logo", "png", logoHash);
  const registerReceipt = await registerTx.wait();
  const assetRegisteredEvent = registerReceipt.logs
    .map((log) => {
      try {
        return registry.interface.parseLog(log);
      } catch (error) {
        return null;
      }
    })
    .find((event) => event && event.name === "AssetRegistered");

  if (!assetRegisteredEvent) {
    throw new Error("AssetRegistered event not found in transaction receipt.");
  }

  const tokenId = assetRegisteredEvent.args.tokenId;
  console.log(`ALU logo registered with token ID: ${tokenId}`);

  const Token = await hre.ethers.getContractFactory("ALULogoToken");
  const logoToken = await Token.deploy(deployer.address);
  await logoToken.waitForDeployment();

  console.log(`ALULogoToken deployed to: ${await logoToken.getAddress()}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
