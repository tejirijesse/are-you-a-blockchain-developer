// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract ALULogoToken is ERC20, Ownable {
    uint256 public constant MAX_SUPPLY = 1_000_000;

    constructor(address initialOwner)
        ERC20("ALU Logo Token", "ALUT")
        Ownable(initialOwner)
    {
        _mint(initialOwner, MAX_SUPPLY);
    }

    function distributeShares(address recipient, uint256 amount) external onlyOwner {
        require(amount > 0, "Amount must be greater than zero");
        _transfer(owner(), recipient, amount);
    }

    function ownershipPercentage(address account) external view returns (uint256) {
        return (balanceOf(account) * 100) / totalSupply();
    }
}
