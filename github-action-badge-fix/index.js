const core = require('@actions/core');
const github = require('@actions/github');
const axios = require('axios');

async function main() {
  try {
    const wallet = core.getInput('wallet', { required: true });
    const readmePath = core.getInput('readme-path') || 'README.md';
    
    // Get badge data from RustChain API
    const apiUrl = `https://50.28.86.131/api/badge/${encodeURIComponent(wallet)}`;
    const response = await axios.get(apiUrl);
    const badgeData = response.data;
    
    // Create badge URL
    const badgeUrl = `![RustChain Mining](https://img.shields.io/endpoint?url=${encodeURIComponent(apiUrl)})`;
    
    // Read README
    const fs = require('fs');
    let readmeContent = fs.readFileSync(readmePath, 'utf8');
    
    // Replace or add badge
    const badgeRegex = /!\[RustChain Mining\]\(https:\/\/img\.shields\.io\/endpoint\?url=[^)]+\)/;
    if (badgeRegex.test(readmeContent)) {
      readmeContent = readmeContent.replace(badgeRegex, badgeUrl);
    } else {
      // Add to top of README
      readmeContent = badgeUrl + '\n\n' + readmeContent;
    }
    
    // Write back to README
    fs.writeFileSync(readmePath, readmeContent);
    
    core.setOutput('badge-url', badgeUrl);
    core.info(`Badge updated for wallet: ${wallet}`);
    
  } catch (error) {
    core.setFailed(error.message);
  }
}

main();