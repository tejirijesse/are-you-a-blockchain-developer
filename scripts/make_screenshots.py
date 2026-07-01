#!/usr/bin/env python3
"""Render captured terminal output as terminal-styled PNG screenshots."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def find_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/Library/Fonts/Courier New.ttf",
        "/System/Library/Fonts/Courier.dfont",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def render_terminal(title, lines, out_path, width=1120):
    header_h = 34
    line_h = 20
    padding = 20
    body_h = padding * 2 + line_h * max(len(lines), 1)
    total_h = header_h + body_h

    img = Image.new("RGB", (width, total_h), (13, 17, 23))
    draw = ImageDraw.Draw(img)

    # title bar
    draw.rectangle([0, 0, width, header_h], fill=(30, 34, 42))
    # traffic lights
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = 18 + i * 22
        cy = header_h // 2
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=color)
    title_font = find_font(14)
    tw = draw.textlength(title, font=title_font)
    draw.text(((width - tw) / 2, 8), title, font=title_font, fill=(200, 205, 215))

    mono = find_font(14)
    y = header_h + padding
    for line in lines:
        color = (208, 216, 232)
        stripped = line.lstrip()
        if stripped.startswith("✔") or stripped.startswith("✓"):
            color = (46, 204, 113)
        elif stripped.startswith("$") or stripped.startswith(">"):
            color = (127, 255, 191)
        elif "passing" in stripped:
            color = (46, 204, 113)
        elif "SHA-256" in stripped or "bytes32" in stripped:
            color = (108, 210, 255)
        elif "WARNING" in stripped:
            color = (255, 189, 46)
        elif "Account" in stripped and "#" in stripped:
            color = (255, 210, 130)
        elif "Private Key" in stripped:
            color = (180, 180, 200)
        draw.text((padding, y), line, font=mono, fill=color)
        y += line_h

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"wrote {out_path}")


# 1. SHA-256 hash generation
hash_lines = [
    "$ npm run hash:logo",
    "",
    "> are-you-a-blockchain-developer@1.0.0 hash:logo",
    "> node scripts/hash-logo.js",
    "",
    "SHA-256: 727b0a610a5e22c083efc8b467c1580cad4b2626d8a6171d686a99d6a220a560",
    "bytes32: 0x727b0a610a5e22c083efc8b467c1580cad4b2626d8a6171d686a99d6a220a560",
]
render_terminal("SHA-256 of alu-logo.png", hash_lines, "screenshots/01_hash_logo.png")

# 2. Test results
test_lines = [
    "$ npm test",
    "",
    "> are-you-a-blockchain-developer@1.0.0 test",
    "> hardhat test",
    "",
    "",
    "  ALU blockchain project",
    "    ✔ registers the ALU logo successfully and returns token ID 1 (282ms)",
    "    ✔ rejects registering the same hash twice",
    "    ✔ returns true when verifyLogoIntegrity receives the correct hash",
    "    ✔ returns false when verifyLogoIntegrity receives an incorrect hash",
    "    ✔ returns the correct asset metadata for a registered token",
    "    ✔ mints the full ALUT supply to the owner on deployment",
    "    ✔ distributeShares transfers the requested amount to the recipient",
    "    ✔ ownershipPercentage returns the correct whole-number percentage",
    "",
    "",
    "  8 passing (343ms)",
]
render_terminal("All 8 automated tests passing", test_lines, "screenshots/02_tests_passing.png")

# 3. Hardhat node startup
node_lines = [
    "$ npx hardhat node",
    "Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/",
    "",
    "Accounts",
    "========",
    "",
    "WARNING: These accounts, and their private keys, are publicly known.",
    "Any funds sent to them on Mainnet or any other live network WILL BE LOST.",
    "",
    "Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)",
    "Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
    "",
    "Account #1: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 (10000 ETH)",
    "Private Key: 0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
    "",
    "Account #2: 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC (10000 ETH)",
    "Private Key: 0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
    "",
    "Account #3: 0x90F79bf6EB2c4f870365E785982E1f101E93b906 (10000 ETH)",
    "Private Key: 0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6",
    "",
    "Account #4: 0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65 (10000 ETH)",
    "Private Key: 0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a",
    "",
    "Account #5: 0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc (10000 ETH)",
    "Private Key: 0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba",
]
render_terminal("Local Hardhat node with test wallet addresses",
                node_lines, "screenshots/03_hardhat_node.png")

# 4. Deployment
deploy_lines = [
    "$ ALU_LOGO_HASH=0x727b0a...a220a560 npx hardhat run scripts/deploy.js",
    "",
    "Deploying with account: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "ALUAssetRegistry deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3",
    "ALU logo registered with token ID: 1",
    "ALULogoToken deployed to: 0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0",
]
render_terminal("Deploy script: both contracts + logo registered",
                deploy_lines, "screenshots/04_deploy.png")
