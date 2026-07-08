#!/usr/bin/env python3
"""Build Project_Report.pdf for Assignment 2 using reportlab."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Project_Report.pdf"
SHOTS = ROOT / "screenshots"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="TitleCenter",
    parent=styles["Title"],
    alignment=TA_CENTER,
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=28,
    textColor=colors.HexColor("#0f172a"),
))
styles.add(ParagraphStyle(
    name="SubtitleCenter",
    parent=styles["BodyText"],
    alignment=TA_CENTER,
    fontName="Helvetica",
    fontSize=12,
    leading=16,
    textColor=colors.HexColor("#475569"),
))
styles.add(ParagraphStyle(
    name="HeadingOneCustom",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=16,
    leading=20,
    textColor=colors.HexColor("#0f172a"),
    spaceBefore=10,
    spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="HeadingTwoCustom",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=15,
    textColor=colors.HexColor("#1e3a8a"),
    spaceBefore=6,
    spaceAfter=5,
))
styles.add(ParagraphStyle(
    name="BodyCustom",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=10.2,
    leading=14,
    textColor=colors.HexColor("#334155"),
    spaceAfter=7,
))
styles.add(ParagraphStyle(
    name="BulletCustom",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=10.2,
    leading=14,
    textColor=colors.HexColor("#334155"),
    leftIndent=14,
    firstLineIndent=-8,
    spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="CodeCustom",
    parent=styles["BodyText"],
    fontName="Courier",
    fontSize=9.5,
    leading=12,
    textColor=colors.HexColor("#1d4ed8"),
    spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="CaptionCustom",
    parent=styles["BodyText"],
    alignment=TA_CENTER,
    fontName="Helvetica-Oblique",
    fontSize=8.8,
    leading=11,
    textColor=colors.HexColor("#64748b"),
    spaceBefore=3,
    spaceAfter=10,
))

story = []


def p(text):
    story.append(Paragraph(text, styles["BodyCustom"]))


def h1(text):
    story.append(Paragraph(text, styles["HeadingOneCustom"]))


def h2(text):
    story.append(Paragraph(text, styles["HeadingTwoCustom"]))


def bullet(text):
    story.append(Paragraph(f"• {text}", styles["BulletCustom"]))


def code(text):
    story.append(Paragraph(text, styles["CodeCustom"]))


def image(name, caption, width=6.9):
    path = SHOTS / name
    if not path.exists():
        return
    img = Image(str(path), width=width * inch, height=width * inch * 0.72)
    img.hAlign = "CENTER"
    story.append(img)
    story.append(Paragraph(caption, styles["CaptionCustom"]))


def br(h=0.1):
    story.append(Spacer(1, h * inch))


story.append(Paragraph("Project Report", styles["TitleCenter"]))
story.append(Spacer(1, 0.08 * inch))
story.append(Paragraph("Individual Assignment 2 - DApp Integration with Smart Contract", styles["SubtitleCenter"]))
story.append(Paragraph("ALU Logo Registry & Ownership dApp", styles["SubtitleCenter"]))
br(0.15)

h1("Abstract")
p(
    "This project delivers a complete decentralized application that reuses the ALU logo smart contracts from "
    "Formative 1 and makes them usable through a web interface. Users can connect a wallet, register a logo "
    "on-chain using its SHA-256 fingerprint, verify authenticity without a server, and inspect or distribute ALUT "
    "ownership shares from the browser."
)

h1("Introduction")
p(
    "The smart contracts built earlier solved the blockchain side of the problem but not the usability side. "
    "Without a frontend, only someone comfortable with a terminal and Hardhat commands could interact with the "
    "logo record or token supply. The dApp fills that gap by becoming the front door to the contracts."
)
p(
    "The result is a more realistic Web3 product: the smart contracts remain the backend source of truth, the "
    "wallet provides identity and transaction signing, and the browser frontend makes the workflow understandable "
    "for non-technical users."
)

h1("Architecture Overview")
p(
    "The application is made of a plain JavaScript frontend, an injected browser wallet, a local Hardhat blockchain, "
    "and two deployed Solidity contracts. The frontend uses ethers.js and the contracts' ABI definitions to create "
    "contract instances for both read-only calls and signed transactions."
)
bullet("ALUAssetRegistry stores the unique ERC-721 record for the logo and its SHA-256 hash.")
bullet("ALULogoToken stores the ERC-20 ownership shares with a fixed supply of 1,000,000 ALUT.")
bullet("The Verify page uses read-only calls, so it works even without a wallet connection.")
bullet("The Register and Distribution flows require a signer because they change blockchain state.")

h1("Feature Walkthrough")
h2("Home Page")
p(
    "The landing page introduces the three main journeys in the dApp: register a logo, verify a logo, and inspect "
    "or distribute ownership shares. It also shows wallet status and ALUT balance in the header."
)
image("05_home_page.png", "Figure 1. Home page of the ALU Logo Registry & Ownership dApp.")

h2("Register Logo Page")
p(
    "The Register page reads the uploaded file locally, computes its SHA-256 digest in the browser, previews the "
    "selected logo, and pre-fills the bytes32 hash into the registration flow. After the wallet signs the transaction, "
    "the page calls registerAsset() and shows the minted token ID."
)
p(
    "Generating the hash in the browser is important because the file itself never needs to be uploaded to a server. "
    "If a duplicate hash is submitted, the smart contract rejects it and the frontend surfaces the error."
)
image("06_register_page.png", "Figure 2. Register page showing local hashing and the on-chain registration form.")

h2("Verify Logo Page")
p(
    "The Verify page supports both file upload and pasted hash verification. It computes the file digest locally when needed, "
    "calls verifyLogoIntegrity() with the known token ID, and presents a clear green authentic verdict or red modified warning."
)
p(
    "No wallet is required for this page because verifyLogoIntegrity() and getAsset() are read-only calls. They read existing "
    "blockchain data, do not change state, and therefore cost no gas."
)
image("07_verify_page.png", "Figure 3. Verify page showing a successful authentic-logo result and the on-chain metadata card.")

h2("Token Dashboard Page")
p(
    "The dashboard reads the total supply, current wallet balance, ownership percentage, and contract owner directly from "
    "ALULogoToken. When the owner wallet is connected, the page also enables the distributeShares() form so ownership can be "
    "transferred to another wallet."
)
p(
    "The onlyOwner modifier protects distributeShares() at the contract level. If a non-owner wallet attempts the call, the "
    "transaction reverts and balances remain unchanged."
)
image("08_dashboard_page.png", "Figure 4. Token dashboard showing ownership statistics and the owner-only share distribution form.")

h1("Wallet and Web3 Integration")
p(
    "The frontend uses ethers.js to talk to both contracts. The ABI is necessary because it tells the frontend which functions "
    "exist, how to encode inputs, and how to decode outputs. Without the ABI, the browser would have a contract address but "
    "no reliable way to interact with it."
)
p(
    "Read-only calls such as totalSupply(), balanceOf(), verifyLogoIntegrity(), getAsset(), owner(), and ownershipPercentage() "
    "do not require gas or signatures. Transactions such as registerAsset() and distributeShares() require the user to sign in "
    "their wallet because only the wallet should control the private key."
)

h1("Verification Page")
p(
    "The verification feature uses the Web Crypto API to compute SHA-256 over the raw file bytes directly in the browser. "
    "The digest is converted to a 0x-prefixed bytes32 string and compared to the hash stored on-chain. Because no backend is "
    "needed, the design is simple, private, and fully serverless."
)
p(
    "A realistic user of this page could be a design team, a student club, or an external printing vendor that needs to confirm "
    "the logo file they received is the authentic ALU version before publishing it."
)

h1("Token Dashboard")
p(
    "The dashboard translates the ERC-20 state into plain-language ownership information. Someone at ALU, such as the brand office "
    "or administration, could receive ALUT shares to represent a stake in the tokenised ownership model used by the project."
)
p(
    "If ALU wanted token holders to vote on decisions proportional to their holdings, the contract would need governance additions "
    "such as proposal creation, vote recording, quorum requirements, and token-weighted result calculation."
)

h1("Test Results")
p(
    "The final repository includes all thirteen required tests: the original eight contract tests plus five additional frontend-aligned "
    "integration tests. The added tests confirm the dashboard reads the 1,000,000 total supply correctly, browser-style SHA-256 hashing "
    "returns a valid bytes32 hash, the verify flow succeeds for the real hash and fails for an incorrect one, and share distribution "
    "updates balances and percentages."
)
image("02_tests_passing.png", "Figure 5. All thirteen automated tests passing.", width=6.6)

h1("Supporting Evidence")
p("The following terminal evidence captures the setup steps used by the dApp.")
image("01_hash_logo.png", "Figure 6. SHA-256 hash generation for alu-logo.png.", width=6.6)
image("03_hardhat_node.png", "Figure 7. Local Hardhat node with pre-funded test wallets.", width=6.6)
image("04_deploy.png", "Figure 8. Deployment of both contracts and registration of the official ALU logo.", width=6.6)

h1("Conclusion")
p(
    "This assignment demonstrated that a smart contract becomes much more useful when it is paired with a thoughtful frontend. "
    "The biggest lesson was how browser logic, wallet signatures, and on-chain state each play a different role in a complete Web3 product."
)
p(
    "With more time, the next improvements would be deploying to a public testnet, adding broader wallet support, strengthening validation, "
    "and extending ALUT into a governance-enabled token system."
)

h1("GitHub Link")
code("https://github.com/tejirijesse/are-you-a-blockchain-developer")


def add_page_number(canvas, doc):
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawCentredString(A4[0] / 2, 18, f"Page {doc.page}")


doc = SimpleDocTemplate(
    str(OUT),
    pagesize=A4,
    leftMargin=36,
    rightMargin=36,
    topMargin=40,
    bottomMargin=28,
)
doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
print(f"wrote {OUT}")
