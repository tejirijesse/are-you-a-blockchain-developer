// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract ALUAssetRegistry is ERC721 {
    struct AssetMetadata {
        string assetName;
        string fileType;
        bytes32 contentHash;
        address registeredBy;
        uint256 registeredAt;
    }

    uint256 private _nextTokenId;

    mapping(uint256 tokenId => AssetMetadata) private _assets;
    mapping(bytes32 contentHash => bool) public usedContentHashes;

    event AssetRegistered(
        uint256 indexed tokenId,
        string assetName,
        string fileType,
        bytes32 indexed contentHash,
        address indexed registeredBy,
        uint256 registeredAt
    );

    constructor() ERC721("ALU Asset Registry", "ALUAR") {}

    function registerAsset(
        string memory assetName,
        string memory fileType,
        bytes32 contentHash
    ) external returns (uint256) {
        require(!usedContentHashes[contentHash], "Asset hash already registered");

        _nextTokenId += 1;
        uint256 newTokenId = _nextTokenId;

        _safeMint(msg.sender, newTokenId);

        _assets[newTokenId] = AssetMetadata({
            assetName: assetName,
            fileType: fileType,
            contentHash: contentHash,
            registeredBy: msg.sender,
            registeredAt: block.timestamp
        });

        usedContentHashes[contentHash] = true;

        emit AssetRegistered(
            newTokenId,
            assetName,
            fileType,
            contentHash,
            msg.sender,
            block.timestamp
        );

        return newTokenId;
    }

    function verifyLogoIntegrity(
        uint256 tokenId,
        bytes32 suppliedHash
    ) external view returns (bool isAuthentic, string memory message) {
        AssetMetadata memory asset = _assets[tokenId];

        if (asset.registeredBy == address(0)) {
            return (false, "Warning: logo does not match.");
        }

        if (asset.contentHash == suppliedHash) {
            return (true, "Logo is authentic.");
        }

        return (false, "Warning: logo does not match.");
    }

    function getAsset(uint256 tokenId) external view returns (AssetMetadata memory) {
        require(_ownerOf(tokenId) != address(0), "Asset does not exist");
        return _assets[tokenId];
    }
}
