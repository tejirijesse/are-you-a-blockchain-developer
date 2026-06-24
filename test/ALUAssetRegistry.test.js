const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ALU blockchain project", function () {
  const ASSET_NAME = "ALU Official Logo";
  const FILE_TYPE = "png";
  const LOGO_HASH = ethers.sha256(ethers.toUtf8Bytes("alu-logo-official"));
  const WRONG_HASH = ethers.sha256(ethers.toUtf8Bytes("alu-logo-fake"));
  const TOTAL_SUPPLY = 1_000_000n;

  async function deployFixture() {
    const [owner, recipient] = await ethers.getSigners();

    const Registry = await ethers.getContractFactory("ALUAssetRegistry");
    const registry = await Registry.deploy();
    await registry.waitForDeployment();

    const Token = await ethers.getContractFactory("ALULogoToken");
    const token = await Token.deploy(owner.address);
    await token.waitForDeployment();

    return { registry, token, owner, recipient };
  }

  it("registers the ALU logo successfully and returns token ID 1", async function () {
    const { registry, owner } = await deployFixture();

    const tx = await registry.registerAsset(ASSET_NAME, FILE_TYPE, LOGO_HASH);
    const receipt = await tx.wait();
    const parsedLog = receipt.logs
      .map((log) => {
        try {
          return registry.interface.parseLog(log);
        } catch (error) {
          return null;
        }
      })
      .find((event) => event && event.name === "AssetRegistered");

    expect(parsedLog.args.tokenId).to.equal(1n);
    expect(await registry.ownerOf(1)).to.equal(owner.address);
  });

  it("rejects registering the same hash twice", async function () {
    const { registry } = await deployFixture();

    await registry.registerAsset(ASSET_NAME, FILE_TYPE, LOGO_HASH);

    await expect(
      registry.registerAsset(ASSET_NAME, FILE_TYPE, LOGO_HASH)
    ).to.be.revertedWith("Asset hash already registered");
  });

  it("returns true when verifyLogoIntegrity receives the correct hash", async function () {
    const { registry } = await deployFixture();

    await registry.registerAsset(ASSET_NAME, FILE_TYPE, LOGO_HASH);

    const [isAuthentic, message] = await registry.verifyLogoIntegrity(1, LOGO_HASH);
    expect(isAuthentic).to.equal(true);
    expect(message).to.equal("Logo is authentic.");
  });

  it("returns false when verifyLogoIntegrity receives an incorrect hash", async function () {
    const { registry } = await deployFixture();

    await registry.registerAsset(ASSET_NAME, FILE_TYPE, LOGO_HASH);

    const [isAuthentic, message] = await registry.verifyLogoIntegrity(1, WRONG_HASH);
    expect(isAuthentic).to.equal(false);
    expect(message).to.equal("Warning: logo does not match.");
  });

  it("returns the correct asset metadata for a registered token", async function () {
    const { registry, owner } = await deployFixture();

    await registry.registerAsset(ASSET_NAME, FILE_TYPE, LOGO_HASH);
    const asset = await registry.getAsset(1);

    expect(asset.assetName).to.equal(ASSET_NAME);
    expect(asset.fileType).to.equal(FILE_TYPE);
    expect(asset.contentHash).to.equal(LOGO_HASH);
    expect(asset.registeredBy).to.equal(owner.address);
  });

  it("mints the full ALUT supply to the owner on deployment", async function () {
    const { token, owner } = await deployFixture();

    expect(await token.totalSupply()).to.equal(TOTAL_SUPPLY);
    expect(await token.balanceOf(owner.address)).to.equal(TOTAL_SUPPLY);
  });

  it("distributeShares transfers the requested amount to the recipient", async function () {
    const { token, owner, recipient } = await deployFixture();

    await token.distributeShares(recipient.address, 250_000);

    expect(await token.balanceOf(recipient.address)).to.equal(250_000);
    expect(await token.balanceOf(owner.address)).to.equal(750_000);
  });

  it("ownershipPercentage returns the correct whole-number percentage", async function () {
    const { token, recipient } = await deployFixture();

    await token.distributeShares(recipient.address, 100_000);

    expect(await token.ownershipPercentage(recipient.address)).to.equal(10);
  });
});
