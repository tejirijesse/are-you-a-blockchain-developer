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

  // --- Frontend integration scenarios ---------------------------------------
  // These mirror the exact flows the dApp performs in the browser: reading the
  // total supply for the dashboard, computing a SHA-256 bytes32 fingerprint the
  // same way the upload pages do, verifying a logo through a read-only call, and
  // distributing shares the way the owner dashboard does.

  it("dashboard read of total supply formats as 1,000,000", async function () {
    const { token } = await deployFixture();

    // The dashboard reads totalSupply() through a read-only contract call and
    // renders it with toLocaleString(), just like frontend/js/app.js.
    const totalSupply = await token.totalSupply();

    expect(totalSupply).to.equal(TOTAL_SUPPLY);
    expect(totalSupply.toLocaleString("en-US")).to.equal("1,000,000");
  });

  it("browser SHA-256 hashing produces the bytes32 stored on-chain", async function () {
    const { registry } = await deployFixture();

    // The register/verify pages hash raw file bytes with the Web Crypto API and
    // format the digest as a 0x-prefixed 32-byte hex string. ethers.sha256 gives
    // the identical result over the same bytes.
    const fileBytes = ethers.toUtf8Bytes("alu-logo-official");
    const browserHash = ethers.sha256(fileBytes);

    expect(browserHash).to.match(/^0x[a-fA-F0-9]{64}$/);
    expect(browserHash).to.equal(LOGO_HASH);

    await registry.registerAsset(ASSET_NAME, FILE_TYPE, browserHash);
    const asset = await registry.getAsset(1);

    expect(asset.contentHash).to.equal(browserHash);
  });

  it("verify page confirms an authentic logo through a read-only call", async function () {
    const { registry, owner } = await deployFixture();

    await registry.registerAsset(ASSET_NAME, FILE_TYPE, LOGO_HASH);

    // The verify page runs verifyLogoIntegrity via a read-only contract backed
    // by a provider (no signer). Connecting to ethers.provider exercises that
    // same provider-style read path without a signer.
    const readOnly = registry.connect(ethers.provider);
    const [isAuthentic, message] = await readOnly.verifyLogoIntegrity(1, LOGO_HASH);

    expect(isAuthentic).to.equal(true);
    expect(message).to.equal("Logo is authentic.");

    // On a match the page also renders the on-chain metadata card.
    const asset = await readOnly.getAsset(1);
    expect(asset.assetName).to.equal(ASSET_NAME);
    expect(asset.registeredBy).to.equal(owner.address);
  });

  it("verify page flags a modified logo when the pasted hash is wrong", async function () {
    const { registry } = await deployFixture();

    await registry.registerAsset(ASSET_NAME, FILE_TYPE, LOGO_HASH);

    // Pasting an unrelated hash (the "Option 2" flow) must produce the red
    // "does not match" verdict rather than reverting.
    const [isAuthentic, message] = await registry.verifyLogoIntegrity(1, WRONG_HASH);

    expect(isAuthentic).to.equal(false);
    expect(message).to.equal("Warning: logo does not match.");
  });

  it("owner dashboard distribution updates recipient balance and percentage", async function () {
    const { token, owner, recipient } = await deployFixture();

    // The dashboard's distribute form calls distributeShares() and then
    // re-reads balances and ownership percentage to refresh the stats.
    await token.distributeShares(recipient.address, 300_000);

    expect(await token.balanceOf(recipient.address)).to.equal(300_000);
    expect(await token.balanceOf(owner.address)).to.equal(700_000);
    expect(await token.ownershipPercentage(recipient.address)).to.equal(30);
    expect(await token.ownershipPercentage(owner.address)).to.equal(70);
  });
});
