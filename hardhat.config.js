require("@nomicfoundation/hardhat-toolbox");

const path = require("path");
const solc = require("solc");
const { subtask } = require("hardhat/config");
const {
  TASK_COMPILE_SOLIDITY_GET_SOLC_BUILD
} = require("hardhat/builtin-tasks/task-names");

subtask(TASK_COMPILE_SOLIDITY_GET_SOLC_BUILD, async (args, hre, runSuper) => {
  if (args.solcVersion === "0.8.24") {
    return {
      compilerPath: require.resolve("solc/soljson.js"),
      isSolcJs: true,
      version: "0.8.24",
      longVersion: solc.version()
    };
  }

  return runSuper();
});

module.exports = {
  solidity: {
    version: "0.8.24",
    settings: {
      evmVersion: "cancun",
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  paths: {
    cache: path.join(__dirname, ".cache", "hardhat"),
    artifacts: path.join(__dirname, "artifacts")
  }
};
