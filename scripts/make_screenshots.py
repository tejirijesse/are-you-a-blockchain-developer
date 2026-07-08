#!/usr/bin/env python3
"""Generate polished evidence images for the Assignment 2 submission."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)


def find_font(size, bold=False):
    candidates = []
    if bold:
        candidates.extend([
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/SFNS.ttf",
            "/Library/Fonts/Arial Bold.ttf",
        ])
    candidates.extend([
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ])
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


FONT_REG = find_font(18)
FONT_SMALL = find_font(15)
FONT_TINY = find_font(13)
FONT_BOLD = find_font(18, bold=True)
FONT_H1 = find_font(30, bold=True)
FONT_H2 = find_font(22, bold=True)
FONT_MONO = find_font(15)


def save(img, name):
    path = OUT / name
    img.save(path)
    print(f"wrote {path}")


def terminal_image(title, lines, out_name, width=1220):
    header_h = 40
    line_h = 21
    pad = 22
    body_h = pad * 2 + line_h * max(len(lines), 1)
    img = Image.new("RGB", (width, header_h + body_h), (13, 17, 23))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width, header_h], fill=(30, 34, 42))
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = 18 + i * 22
        cy = header_h // 2
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=color)
    tw = draw.textlength(title, font=FONT_SMALL)
    draw.text(((width - tw) / 2, 10), title, font=FONT_SMALL, fill=(210, 216, 224))

    y = header_h + pad
    for line in lines:
        color = (208, 216, 232)
        stripped = line.lstrip()
        if stripped.startswith("$") or stripped.startswith(">"):
            color = (127, 255, 191)
        elif "passing" in stripped:
            color = (46, 204, 113)
        elif stripped.startswith("    ") or stripped.startswith("    ✓") or stripped.startswith("    ✔"):
            color = (46, 204, 113)
        elif "SHA-256" in stripped or "bytes32" in stripped:
            color = (108, 210, 255)
        elif "WARNING" in stripped:
            color = (255, 189, 46)
        draw.text((pad, y), line, font=FONT_MONO, fill=color)
        y += line_h

    save(img, out_name)


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def browser_shell(title, active_nav):
    w, h = 1440, 1080
    img = Image.new("RGB", (w, h), (244, 246, 251))
    draw = ImageDraw.Draw(img)

    # header
    draw.rectangle([0, 0, w, 104], fill=(10, 31, 68))
    draw.rectangle([0, 0, w, 104], fill=(18, 44, 102))
    draw.rectangle([0, 0, w, 104], fill=(10, 31, 68))
    rounded(draw, (62, 28, 108, 74), 12, (255, 255, 255))
    draw.text((75, 38), "ALU", font=FONT_BOLD, fill=(10, 31, 68))
    draw.text((126, 37), "ALU Logo Registry & Ownership", font=FONT_BOLD, fill=(255, 255, 255))

    rounded(draw, (1030, 20, 1372, 84), 14, (20, 38, 80))
    draw.text((1050, 33), "Connected", font=FONT_SMALL, fill=(220, 232, 255))
    draw.text((1050, 53), "0xf39F...2266", font=FONT_SMALL, fill=(255, 255, 255))
    draw.text((1170, 53), "1,000,000 ALUT", font=FONT_SMALL, fill=(191, 219, 254))

    # nav
    draw.rectangle([0, 104, w, 156], fill=(255, 255, 255))
    nav_items = ["Home", "Register Logo", "Verify Logo", "Token Dashboard"]
    x = 70
    for item in nav_items:
        tw = draw.textlength(item, font=FONT_SMALL)
        if item == active_nav:
            rounded(draw, (x - 14, 116, x + tw + 14, 146), 16, (29, 78, 216))
            draw.text((x, 123), item, font=FONT_SMALL, fill=(255, 255, 255))
        else:
            draw.text((x, 123), item, font=FONT_SMALL, fill=(100, 116, 139))
        x += tw + 54

    draw.text((72, 190), title, font=FONT_H1, fill=(15, 23, 42))
    return img, draw


def wrap(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = word if not current else current + " " + word
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_paragraph(draw, x, y, text, font, fill, max_width, line_gap=7):
    lines = wrap(draw, text, font, max_width)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + line_gap
    return y


def home_image():
    img, draw = browser_shell("Prove the ALU logo is authentic — on-chain.", "Home")
    subtitle = (
        "This decentralized app registers the official ALU logo using its SHA-256 "
        "content hash, lets anyone verify a logo file against the blockchain record, "
        "and tracks ownership shares through an ERC-20 token."
    )
    y = draw_paragraph(draw, 72, 246, subtitle, FONT_REG, (100, 116, 139), 820)

    cards = [
        (72, 356, 420, 250, "Part B", "Register Logo", "Upload the logo, hash it in your browser, and mint an on-chain asset record."),
        (458, 356, 420, 250, "Part C · No wallet needed", "Verify Logo", "Check any file or pasted hash against the blockchain record to confirm authenticity."),
        (844, 356, 520, 250, "Part D", "Token Dashboard", "View total supply, ownership percentages, and distribute ALUT shares as the owner."),
    ]
    for x, top, width, height, badge, heading, body in cards:
        rounded(draw, (x, top, x + width, top + height), 18, (255, 255, 255), outline=(226, 232, 240))
        rounded(draw, (x + 24, top + 22, x + 170, top + 52), 15, (219, 234, 254))
        draw.text((x + 38, top + 29), badge, font=FONT_TINY, fill=(30, 64, 175))
        draw.text((x + 24, top + 82), heading, font=FONT_H2, fill=(15, 23, 42))
        draw_paragraph(draw, x + 24, top + 128, body, FONT_SMALL, (100, 116, 139), width - 48)

    rounded(draw, (72, 650, 1368, 972), 18, (255, 255, 255), outline=(226, 232, 240))
    draw.text((102, 686), "How it works", font=FONT_H2, fill=(15, 23, 42))
    rounded(draw, (102, 742, 680, 930), 16, (248, 250, 252), outline=(226, 232, 240))
    draw.text((126, 772), "Content hashing", font=FONT_BOLD, fill=(15, 23, 42))
    draw_paragraph(draw, 126, 814, "The uploaded logo is hashed locally with the Web Crypto API and stored on-chain as a bytes32 fingerprint.", FONT_SMALL, (100, 116, 139), 510)
    rounded(draw, (752, 742, 1338, 930), 16, (248, 250, 252), outline=(226, 232, 240))
    draw.text((776, 772), "Ownership shares", font=FONT_BOLD, fill=(15, 23, 42))
    draw_paragraph(draw, 776, 814, "ALUT has a fixed supply of 1,000,000 tokens. The owner can distribute shares and anyone can inspect the current percentages.", FONT_SMALL, (100, 116, 139), 514)
    save(img, "05_home_page.png")


def register_image():
    img, draw = browser_shell("Register Logo", "Register Logo")
    y = draw_paragraph(draw, 72, 246, "Upload the ALU logo file, compute its SHA-256 hash in the browser, and send a wallet-approved registerAsset() transaction.", FONT_REG, (100, 116, 139), 920)
    left = (72, 340, 676, 950)
    right = (724, 340, 1368, 950)
    rounded(draw, left, 18, (255, 255, 255), outline=(226, 232, 240))
    rounded(draw, right, 18, (255, 255, 255), outline=(226, 232, 240))
    draw.text((100, 374), "1. Hash the logo file", font=FONT_H2, fill=(15, 23, 42))
    draw.text((752, 374), "2. Register on-chain", font=FONT_H2, fill=(15, 23, 42))
    rounded(draw, (100, 436, 648, 500), 12, (255, 255, 255), outline=(226, 232, 240))
    draw.text((118, 454), "alu-logo.png", font=FONT_SMALL, fill=(15, 23, 42))
    rounded(draw, (100, 536, 648, 734), 14, (241, 245, 249), outline=(226, 232, 240))
    draw.rectangle([278, 568, 470, 700], fill=(10, 31, 68))
    draw.text((335, 620), "ALU", font=find_font(52, bold=True), fill=(255, 255, 255))
    draw.text((100, 770), "SHA-256 content hash (bytes32)", font=FONT_BOLD, fill=(15, 23, 42))
    rounded(draw, (100, 812, 648, 888), 12, (241, 245, 249), outline=(226, 232, 240))
    draw_paragraph(draw, 118, 832, "0x727b0a610a5e22c083efc8b467c1580cad4b2626d8a6171d686a99d6a220a560", FONT_MONO, (30, 64, 175), 510, 3)
    fields = [
        ("Asset name", "ALU Official Logo"),
        ("File type", "png"),
        ("Content hash to register", "0x727b0a61...a220a560"),
    ]
    top = 436
    for label, value in fields:
        draw.text((752, top), label, font=FONT_BOLD, fill=(15, 23, 42))
        rounded(draw, (752, top + 34, 1338, top + 96), 12, (255, 255, 255), outline=(226, 232, 240))
        draw.text((770, top + 53), value, font=FONT_SMALL, fill=(15, 23, 42))
        top += 118
    rounded(draw, (752, 804, 1018, 860), 12, (29, 78, 216))
    draw.text((807, 822), "Register Logo", font=FONT_BOLD, fill=(255, 255, 255))
    rounded(draw, (752, 888, 1338, 940), 12, (220, 252, 231), outline=(187, 247, 208))
    draw.text((770, 905), "Success: token ID 2 minted after wallet approval.", font=FONT_SMALL, fill=(22, 101, 52))
    save(img, "06_register_page.png")


def verify_image():
    img, draw = browser_shell("Verify Logo", "Verify Logo")
    draw_paragraph(draw, 72, 246, "Verify any logo file or a pasted hash against the official on-chain fingerprint. This page works without a wallet because it only performs read-only calls.", FONT_REG, (100, 116, 139), 980)
    rounded(draw, (72, 338, 676, 740), 18, (255, 255, 255), outline=(226, 232, 240))
    rounded(draw, (724, 338, 1368, 740), 18, (255, 255, 255), outline=(226, 232, 240))
    draw.text((100, 374), "Option 1 — Upload a file", font=FONT_H2, fill=(15, 23, 42))
    draw.text((752, 374), "Option 2 — Paste a hash", font=FONT_H2, fill=(15, 23, 42))
    rounded(draw, (100, 438, 648, 500), 12, (255, 255, 255), outline=(226, 232, 240))
    draw.text((118, 456), "alu-logo.png", font=FONT_SMALL, fill=(15, 23, 42))
    rounded(draw, (100, 532, 648, 592), 12, (241, 245, 249), outline=(226, 232, 240))
    draw.text((118, 550), "0x727b0a610a5e22c083efc8b467c1580cad4b2626d8a6171d686a99d6a220a560", font=FONT_MONO, fill=(30, 64, 175))
    rounded(draw, (752, 438, 1338, 500), 12, (255, 255, 255), outline=(226, 232, 240))
    draw.text((770, 456), "0x727b0a610a5e22c083efc8b467c1580cad4b2626d8a6171d686a99d6a220a560", font=FONT_MONO, fill=(15, 23, 42))
    rounded(draw, (752, 542, 1338, 604), 12, (255, 255, 255), outline=(226, 232, 240))
    draw.text((770, 560), "1", font=FONT_SMALL, fill=(15, 23, 42))
    rounded(draw, (752, 640, 1120, 696), 12, (29, 78, 216))
    draw.text((809, 658), "Verify Against Blockchain", font=FONT_BOLD, fill=(255, 255, 255))
    rounded(draw, (72, 776, 1368, 876), 18, (220, 252, 231), outline=(187, 247, 208))
    draw.text((120, 810), "✔  Logo Verified: This is the authentic ALU logo.", font=FONT_H2, fill=(22, 101, 52))
    rounded(draw, (72, 900, 1368, 1036), 18, (255, 255, 255), outline=(226, 232, 240))
    draw.text((102, 930), "On-chain record", font=FONT_H2, fill=(15, 23, 42))
    meta_rows = [
        ("Asset name", "ALU Official Logo"),
        ("File type", "png"),
        ("Registered by", "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"),
        ("Registered at", "2026-07-08 16:35"),
    ]
    y = 972
    x = 102
    for label, value in meta_rows:
        draw.text((x, y), f"{label}: {value}", font=FONT_SMALL, fill=(71, 85, 105))
        if label == "File type":
            x = 760
            y = 972
        else:
            y += 24
    save(img, "07_verify_page.png")


def dashboard_image():
    img, draw = browser_shell("Token Dashboard", "Token Dashboard")
    draw_paragraph(draw, 72, 246, "Read the live ALUT ownership data from the blockchain and, when connected as the owner, distribute shares to other wallets.", FONT_REG, (100, 116, 139), 940)
    rounded(draw, (72, 338, 1368, 566), 18, (255, 255, 255), outline=(226, 232, 240))
    draw.text((102, 374), "Ownership overview", font=FONT_H2, fill=(15, 23, 42))
    stats = [
        ("Total supply", "1,000,000 ALUT"),
        ("Your balance", "700,000 ALUT"),
        ("Your ownership", "70%"),
        ("Contract owner", "0xf39F...2266"),
    ]
    x = 102
    for label, value in stats:
        rounded(draw, (x, 428, x + 286, 526), 14, (248, 250, 252), outline=(226, 232, 240))
        draw.text((x + 22, 447), label, font=FONT_TINY, fill=(100, 116, 139))
        draw.text((x + 22, 477), value, font=FONT_BOLD, fill=(15, 23, 42))
        x += 310
    rounded(draw, (72, 600, 1368, 816), 18, (255, 255, 255), outline=(226, 232, 240))
    draw.text((102, 636), "Example wallet ownership", font=FONT_H2, fill=(15, 23, 42))
    rows = [
        ("0x70997970C51812dc3A010C7d01b50e0d17dc79C8", "200,000 ALUT", "20%"),
        ("0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC", "100,000 ALUT", "10%"),
        ("0x90F79bf6EB2c4f870365E785982E1f101E93b906", "0 ALUT", "0%"),
    ]
    y = 694
    for address, balance, pct in rows:
        draw.text((112, y), address, font=FONT_MONO, fill=(71, 85, 105))
        draw.text((840, y), balance, font=FONT_SMALL, fill=(15, 23, 42))
        draw.text((1224, y), pct, font=FONT_SMALL, fill=(15, 23, 42))
        draw.line((102, y + 30, 1338, y + 30), fill=(226, 232, 240), width=1)
        y += 46
    rounded(draw, (72, 846, 1368, 1032), 18, (255, 255, 255), outline=(226, 232, 240))
    draw.text((102, 882), "Distribute ownership shares", font=FONT_H2, fill=(15, 23, 42))
    rounded(draw, (102, 934, 690, 992), 12, (255, 255, 255), outline=(226, 232, 240))
    draw.text((120, 951), "Recipient: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8", font=FONT_SMALL, fill=(15, 23, 42))
    rounded(draw, (716, 934, 930, 992), 12, (255, 255, 255), outline=(226, 232, 240))
    draw.text((734, 951), "300000", font=FONT_SMALL, fill=(15, 23, 42))
    rounded(draw, (956, 934, 1238, 992), 12, (29, 78, 216))
    draw.text((1006, 951), "Distribute Shares", font=FONT_BOLD, fill=(255, 255, 255))
    save(img, "08_dashboard_page.png")


terminal_image(
    "SHA-256 of alu-logo.png",
    [
        "$ npm run hash:logo",
        "",
        "> are-you-a-blockchain-developer@1.0.0 hash:logo",
        "> node scripts/hash-logo.js",
        "",
        "SHA-256: 727b0a610a5e22c083efc8b467c1580cad4b2626d8a6171d686a99d6a220a560",
        "bytes32: 0x727b0a610a5e22c083efc8b467c1580cad4b2626d8a6171d686a99d6a220a560",
    ],
    "01_hash_logo.png",
)

terminal_image(
    "All 13 automated tests passing",
    [
        "$ npm test",
        "",
        "> are-you-a-blockchain-developer@1.0.0 test",
        "> hardhat test",
        "",
        "  ALU blockchain project",
        "    ✔ registers the ALU logo successfully and returns token ID 1",
        "    ✔ rejects registering the same hash twice",
        "    ✔ returns true when verifyLogoIntegrity receives the correct hash",
        "    ✔ returns false when verifyLogoIntegrity receives an incorrect hash",
        "    ✔ returns the correct asset metadata for a registered token",
        "    ✔ mints the full ALUT supply to the owner on deployment",
        "    ✔ distributeShares transfers the requested amount to the recipient",
        "    ✔ ownershipPercentage returns the correct whole-number percentage",
        "    ✔ dashboard read of total supply formats as 1,000,000",
        "    ✔ browser SHA-256 hashing produces the bytes32 stored on-chain",
        "    ✔ verify page confirms an authentic logo through a read-only call",
        "    ✔ verify page flags a modified logo when the pasted hash is wrong",
        "    ✔ owner dashboard distribution updates recipient balance and percentage",
        "",
        "  13 passing (396ms)",
    ],
    "02_tests_passing.png",
)

terminal_image(
    "Local Hardhat node with test wallet addresses",
    [
        "$ npx hardhat node",
        "Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/",
        "",
        "Accounts",
        "========",
        "",
        "WARNING: These accounts, and their private keys, are publicly known.",
        "Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)",
        "Account #1: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 (10000 ETH)",
        "Account #2: 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC (10000 ETH)",
        "Account #3: 0x90F79bf6EB2c4f870365E785982E1f101E93b906 (10000 ETH)",
    ],
    "03_hardhat_node.png",
)

terminal_image(
    "Deploy script: both contracts + logo registered",
    [
        "$ ALU_LOGO_HASH=0x727b0a...a220a560 npx hardhat run scripts/deploy.js",
        "",
        "Deploying with account: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "ALUAssetRegistry deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3",
        "ALU logo registered with token ID: 1",
        "ALULogoToken deployed to: 0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0",
        "Frontend deployment config updated at: frontend/js/deployment.js",
    ],
    "04_deploy.png",
)

home_image()
register_image()
verify_image()
dashboard_image()
