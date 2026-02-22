#!/usr/bin/env node

const core = require('@actions/core');
const github = require('@actions/github');
const axios = require('axios');

async function main() {
  try {
    const wallet = core.getInput('wallet', { required: true });
    const rustchainUrl = core.getInput('rustchain-url') || 'http://50.28.86.131:8099';
    
    // Get badge data from RustChain API
    const badgeUrl = `${rustchainUrl}/api/badge/${wallet}`;
    core.info(`Fetching badge data from: ${badgeUrl}`);
    
    const response = await axios.get(badgeUrl, { timeout: 10000 });
    const badgeData = response.data;
    
    if (!badgeData.schemaVersion) {
      throw new Error('Invalid badge data received from RustChain API');
    }
    
    // Update README with badge
    const fs = require('fs');
    const readmePath = 'README.md';
    
    if (fs.existsSync(readmePath)) {
      let readmeContent = fs.readFileSync(readmePath, 'utf8');
      
      // Create badge markdown
      const badgeMarkdown = `![RustChain Mining](https://img.shields.io/endpoint?url=${encodeURIComponent(badgeUrl)})`;
      
      // Check if badge already exists
      if (readmeContent.includes('![RustChain Mining]')) {
        // Replace existing badge
        readmeContent = readmeContent.replace(/!\[RustChain Mining\]\([^)]+\)/g, badgeMarkdown);
      } else {
        // Add badge to top of README
        readmeContent = `${badgeMarkdown}\n\n${readmeContent}`;
      }
      
      fs.writeFileSync(readmePath, readmeContent);
      core.info('README updated with RustChain mining badge');
    } else {
      core.warning('README.md not found, skipping README update');
    }
    
    // Set outputs
    core.setOutput('badge-data', JSON.stringify(badgeData));
    core.setOutput('badge-url', badgeUrl);
    core.setOutput('wallet', wallet);
    
    core.info(`Badge created successfully for wallet: ${wallet}`);
    core.info(`Mining status: ${badgeData.message}`);
    
  } catch (error) {
    core.setFailed(`Action failed with error: ${error.message}`);
    process.exit(1);
  }
}

main();